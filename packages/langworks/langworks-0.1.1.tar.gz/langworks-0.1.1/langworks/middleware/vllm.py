# ##################################################################################################
#
# Title:
#
#   langworks.middleware.vllm.py
#
# License:
#
#   Copyright 2025 Rosaia B.V.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except 
#   in compliance with the License. You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software distributed under the 
#   License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#   express or implied. See the License for the specific language governing permissions and 
#   limitations under the License.
#
#   [Apache License, version 2.0]
#
# Description: 
#
#   Part of the Langworks framework, implementing middleware to leverage vLLM.
#
# ##################################################################################################

# ##################################################################################################
# Dependencies
# ##################################################################################################

# Python standard library ##########################################################################

# Fundamentals
from dataclasses import (
    dataclass,
    field
)

import typing
from typing import (
    Any,
    Callable,
    Literal
)

import warnings

# System
from threading import (
    Lock
)

# Text utilities
import json

# Utilities
import math
import statistics


# Third-party ######################################################################################

# OpenAI API (OpenAI)
try:
    import openai
except:
    pass

# transformers
try:
    from transformers import (
        AutoTokenizer
    )
except:
    pass


# Local ############################################################################################

from .. import (
    auth,
    caching,
    dsl
)

from ..messages import (
    Thread
)

from . import (
    generic
)


# ##################################################################################################
# Classes
# ##################################################################################################

# Params ###########################################################################################

@dataclass(frozen = True)
class SamplingParams(generic.SamplingParams):

    """
    Specifies additional sampling parameters to be used when passing a prompt to vLLM.
    """

    # Beam search ##################################################################################

    use_beam_search               : bool                      = field(default = False)
    """
    Flag specifying whether or not to apply beam search.
    """

    best_of                       : int                       = field(default = None)
    """
    The number of options to explore when applying beam search.
    """

    length_penalty                : float                     = field(default = 1.0)
    """
    A coeffient applied during beam search, controlling the length of the generated text.
    """

    early_stopping                : bool | Literal["never"]   = field(default = False)
    """
    Controls stopping behaviour during beam search. This parameter takes three values:

    - `True`, whereby generation is stopped when `best_of` candidates are acquired;
    - `False`, whereby generation continues as long as the probability remains high that better
      candidates may be found;
    - `"never"`, whereby generation continues as long as better candidates may be found;
    """

# Monkey patch in '__defaults__', a quick lookup map for default values ############################

SamplingParams.__defaults__ = generic.get_dataclass_defaults(SamplingParams)

# End of class 'Params' ############################################################################


# vLLM #############################################################################################

class vLLM(generic.Middleware):

    """
    `vLLM <https://docs.vllm.ai/en/stable/>`_ is an open source library for efficiently serving
    various LLMs using self-managed hardware. Langworks' vLLM middleware provides a wrapper to 
    access these LLMs using vLLM's server API.
    """

    # ##############################################################################################
    # Attributes
    # ##############################################################################################

    # Private ######################################################################################

    # Cache of chat templates indexed by model name.
    __templates__ : dict[str, str] = dict()

    # Cache of special tokens indexed by model name.
    __special_tokens__ : dict[str, str] = dict()


    # ##############################################################################################
    # Class fundamentals
    # ##############################################################################################

    # __init__ #####################################################################################

    def __init__(
            
            self, 

            # Connection
            url           : str,
            model         : str,
            authenticator : auth.Authenticator | None = None,
            timeout       : int                       = 5,
            retries       : int                       = 2,
            
            # Configuration
            params        : SamplingParams            = None,
            output_cache  : caching.ScoredCache       = None
            
    ):
        
        """
        Initializes the vLLM middleware.

        Parameters
        ----------

        Connection
        ^^^^^^^^^^

        url
            URL of the vLLM-instance where the model may be accessed.

        model
            Name of the model as used in the Hugging Face repository.

        authenticator
            :py:class:`Authenticator` that may be used to acquire an authentication key when the 
            vLLM-instance requests for authentication.

        timeout
            The number of seconds the client awaits the response of the vLLM-instance.

        retries
            The number of times the client tries to submit the same request again *after* a timeout.


        Configuration
        ^^^^^^^^^^^^^

        params
            Default sampling parameters to use when processing a prompt, specified using an instance
            of `SamplingParams`.

        output_cache
            Cache to use for caching previous prompt outputs. Should be a `ScoredCache` or subclass.

        """

        # Initialize attributes ####################################################################

        # Argument passthrough
        self.url               : str                       = url
        self.model             : str                       = model
        self.authenticator     : auth.Authenticator | None = authenticator
        self.timeout           : int                       = timeout
        self.retries           : int                       = retries
        self.params            : SamplingParams            = params
        self.output_cache      : caching.ScoredCache       = output_cache

        # Pre-declare attributes
        self.client            : openai.OpenAI             = None

        self.chat_template     : str                       = None
        self.special_tokens    : dict[str, str]            = None

        self.output_cache_lock : Lock                      = Lock()

        # End of '__init__' ########################################################################


    # ##############################################################################################
    # Methods
    # ##############################################################################################
        
    # exec #########################################################################################
        
    def exec(
        self, 
        query      : str                        = None,
        role       : str                        = None,
        guidance   : str                        = None,
        history    : Thread                     = None,
        context    : dict                       = None,
        params     : SamplingParams             = None
    ) -> tuple[Thread, dict[str, Any]]:
        
        """
        Generate a new message, following up on the message passed using the given guidance and
        sampling parameters.

        Parameters
        ----------

        query
            The query to prompt the LLM with, optionally formatted using Langworks' static DSL.

        role
            The role of the agent stating this query, usually 'user', 'system' or 'assistant'.

        guidance
            Template for the message to be generated, formatted using Langworks' dyanmic DSL.

        history
            Conversational history (thread) to prepend to the prompt.

        context
            Context to reference when filling in the templated parts of the `query`, `guidance` and
            `history`. In case the `Langwork` or the input also define a context, the available 
            contexts are merged. When duplicate attributes are observed, the value is copied from 
            the most specific context, i.e. input context over `Query` context, and `Query` context
            over `Langwork` context.

        params
            Sampling parameters, wrapped by a `SamplingParams` object, specifying how the LLM should 
            select subsequent tokens.
        """
        
        # ##########################################################################################
        # Prepare initial prompt
        # ##########################################################################################

        # Render initial messages.
        messages : Thread = [
            # Construct new message.
            {
                # Maintaining original role.
                "role"   : message.get("role", None),
                # Replacing the content with the rendered variant.
                "content": (
                    # Join rendered chunks.
                    "".join(
                        # Pass to static DSL environment.
                        dsl.render(
                            message.get("content", None), context, mode = dsl.RenderingMode.STATIC
                        )
                    )
                )
            }
            # Process each message separately.
            for message in (
                # Append query to the history.
                (history or []) + [{"content": query or "", "role": role or "user"}]
            )
        ]

        # Convert thread to prompt ready for further generation.
        prompt : str = (
            # Join rendered chunks.
            "".join(
                # Pass to static DSL environment.
                dsl.render(

                    # Retrieve chat template.
                    self.get_chat_template(), 

                    # Populate the context.
                    dict(
                        **context,
                        messages              = messages,
                        add_generation_prompt = True,
                        **self.get_special_tokens()
                    ),

                    # Only the template itself needs to be rendered.
                    nested = False,

                    # Set mode to static.
                    mode = dsl.RenderingMode.STATIC
                )
            )
        )


        # ##########################################################################################
        # Prepare rendering
        # ##########################################################################################

        # Get connection with vLLM instance ########################################################

        # Check if the connection still needs to be initialized.
        if self.client is None:

            # Retrieve token if an authenticator was passed.
            token : str | None = None

            if self.authenticator is not None:
                
                details : auth.AuthenticationDetails = self.authenticator(self)

                if details is not None:
                    token = details.token

                if token is None:

                    warnings.warn(
                        f"Authenticator passed could not provide authentication details; defaulting"
                        " to token 'EMPTY';"
                    )
        
            # Import OpenAI client, and use it to make a connection to the vLLM instance.
            self.client = openai.OpenAI(base_url = self.url, api_key = token or "EMPTY")


        # Combine default sampling parameters ######################################################

        # Combine sampling parameters specified at different levels.
        params = (

            # Do NOT create a new SamplingParams object, maintaining instead a dictionary as to
            # minimize the required computation when mixin constraint-level sampling parameters
            # later on.
            {

                # Middleware
                **{
                    key: value 
                    for key, value in 
                    (self.params.__dict__ if self.params is not None else {}).items()
                    if value != SamplingParams.__defaults__.get(key, None)
                },

                # Input
                **{
                    key: value 
                    for key, value in 
                    (params.__dict__ if params is not None else {}).items()
                    if value != SamplingParams.__defaults__.get(key, None)
                }
            }

        )


        # ##########################################################################################
        # Rendering
        # ##########################################################################################

        # Define intermediate variables ############################################################

        # Variable to buffer the content of the message being generated.
        msg_content : str = ""

        # Variable to hold generated variables.
        vars : dict[str, Any] = dict()


        # Main logic ###############################################################################

        # Process the guide tag by tag.
        for chunk in dsl.render(
            guidance or "{% gen %}", context, mode = dsl.RenderingMode.DYNAMIC
        ):

            # Differentiate constraints and non-constraints ########################################

            # Add any strings to the buffer and prompt, and skip until a constraint is found.
            if isinstance(chunk, str):
                
                msg_content += chunk
                prompt += chunk

                continue

            # Check if a constraint was passed.
            elif not isinstance(chunk, dsl.Constraint):

                raise ValueError(
                    f"Object of type '{type(chunk)}' was passed where 'str' or subtype of 'dsl."
                    "constraints.Constraint was expected;"
                )


            # Mixin final sampling parameters ######################################################
            
            # Combine sampling parameters stored in the constraint with default constraints.
            prompt_params : SamplingParams = (

                SamplingParams(**{

                    **{
                        key: value for key, value in params.items()
                    },

                    **{
                        key: value 
                        for key, value in 
                        (chunk.params.__dict__ if chunk.params is not None else {}).items()
                        if value != SamplingParams.__defaults__.get(key, None)
                    }
                })

            )


            # Generate response ####################################################################

            # Predefine variable to hold text response.
            txt : str | None = None

            # Check cache to see if a response needs to be generated.
            if self.output_cache is not None:

                # Generate hash for the request.
                request_hash : int = hash(prompt + self.model + str(prompt_params))

                # Access cache, and attempt to retrieve response.
                with self.output_cache_lock:

                    try:
                        txt = self.output_cache[request_hash]
                    except:
                        pass

            # Only retrieve response, if a response was not previously cached.
            if txt is None:

                # Prepare an object, holding all request arguments.
                request : dict = dict(

                    model              = self.model,
                    prompt             = prompt,
                    timeout            = self.timeout,

                    max_tokens         = prompt_params.max_tokens,
                    stop               = prompt_params.stop,

                    temperature        = prompt_params.temperature,
                    top_p              = prompt_params.top_p,      
                    logit_bias         = prompt_params.logit_bias,
                    seed               = prompt_params.seed,
                    logprobs           = prompt_params.logprobs,

                    presence_penalty   = prompt_params.presence_penalty,
                    frequency_penalty  = prompt_params.frequency_penalty,

                    extra_body = {

                        "stop_token_ids"             : prompt_params.stop_tokens,
                        "include_stop_str_in_output" : prompt_params.include_stop,
                        "ignore_eos"                 : prompt_params.ignore_eos,

                        "min_p"                      : prompt_params.min_p,
                        "top_k"                      : prompt_params.top_k,

                        #"repetition_penalty"         : prompt_params.repetition_penalty,

                        "use_beam_search"            : prompt_params.use_beam_search,
                        "best_of"                    : prompt_params.best_of,
                        "length_penalty"             : prompt_params.length_penalty,
                        "early_stopping"             : prompt_params.early_stopping,
                    
                        **({
                            (
                                "guided_regex"        if isinstance(chunk,  dsl.Regex)
                                else "guided_json"    if isinstance(chunk,  dsl.JSON)
                                else "guided_choice"  if isinstance(chunk,  dsl.Choice)
                                else "guided_grammar" if isinstance(chunk,  dsl.Grammar)
                                else ValueError(f"Unknown constraint '{chunk}' was passed;")
                            ): chunk.spec
                        } if not isinstance(chunk, dsl.Gen) else {})
                    }

                )

                # Query the vLLM-instance.
                attempt : int = -1
                response : openai.types.Completion = None

                while attempt < self.retries:

                    try:
                        response = self.client.completions.create(**request)

                    except openai.APITimeoutError:

                        attempt += 1
                        continue

                    break

                if attempt >= self.retries:

                    raise TimeoutError(
                        f"Connection with '{self.url}' timed out despite {self.retries} retries;"
                    )

                # Get response text.
                txt : str = response.choices[0].text

                # Cache if needed.
                if self.output_cache is not None:

                    # Retrieve logprobs, to be used as the score for comparison.
                    logprobs = response.choices[0].logprobs

                    if logprobs is not None:
                        logprobs = logprobs.token_logprobs

                    logprobs = logprobs or []

                    # Convert to average p-value
                    p = math.exp(statistics.fmean(logprobs)) if len(logprobs) > 0 else 0.0

                    # Add to cache.
                    with self.output_cache_lock:
                        self.output_cache[request_hash] = caching.ScoredItem(txt, p)


            # Process response #####################################################################

            # Append response to message.
            msg_content += txt

            # Append response to prompt.
            prompt += txt

            # Store response if needed.
            if isinstance(chunk, dsl.constraints.Constraint) and chunk.var is not None:

                # Handle JSON objects.
                if isinstance(chunk, dsl.constraints.JSON):
                    vars[chunk.var] = json.loads(txt)

                # Handle other objects.
                else:
                    vars[chunk.var] = txt

                # Invoke finalize.
                if chunk.finalizer is not None:
                    chunk.finalizer(txt)


        # ##########################################################################################
        # Return result
        # ##########################################################################################

        return (
            messages + [{"role": "assistant", "content": msg_content}],
            vars
        )
    
        # End of method 'exec' #####################################################################

        
    # get_chat_template ############################################################################
    
    def get_chat_template(self) -> str:

        """
        Retrieves chat template associated with the model to which this middleware provides access.
        """

        # Attempt to retrieve from cache ###########################################################

        chat_template = vLLM.__templates__.get(self.model, None)

        if chat_template is not None:
            return chat_template
        
        # Add to cache and return ################################################################## 

        # Delegate
        self.__get_chat_format_arguments__()

        # Return chat template.
        return vLLM.__templates__.get(self.model, None)
    
        # End of method 'get_chat_template' ########################################################
        

    # get_special_tokens ###########################################################################

    def get_special_tokens(self) -> dict[str, str]:

        """
        Retrieves special tokens associated with the model to which this middleware provides access.
        """

        # Attempt to retrieve from cache ###########################################################

        special_tokens = vLLM.__special_tokens__.get(self.model, None)

        if special_tokens is not None:
            return special_tokens
        
        # Add to cache and return ################################################################## 

        # Delegate
        self.__get_chat_format_arguments__()

        # Return special tokens.
        return vLLM.__special_tokens__.get(self.model, None)
    
        # End of method 'get_chat_template' ########################################################


    # __get_chat_format_arguments__ ################################################################

    def __get_chat_format_arguments__(self):

        """
        Retrieve and cache arguments used to format a human readable thread as a prompt that can be
        processed by the specified model.
        """

        # Retrieve and cache arguments #############################################################

        # Access the tokenizer for the given model.
        tokenizer = AutoTokenizer.from_pretrained(self.model)

        # Retrieve the chat template from the tokenizer, and cache it.
        vLLM.__templates__[self.model]  = (
            tokenizer.chat_template or tokenizer.default_chat_template
        )

        # Retrieve special tokens from the tokenizer, and cache them.
        vLLM.__special_tokens__[self.model] = tokenizer.special_tokens_map or {} 


        # End of method 'get_chat_template' ########################################################

# End of File ######################################################################################