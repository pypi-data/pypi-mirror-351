# ##################################################################################################
#
# Title:
#
#   langworks.dsl.environment.py
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
#   Part of the Langworks framework, providing a single access point for rendering templated text.
#
# ##################################################################################################

# ##################################################################################################
# Dependencies
# ##################################################################################################

# Python standard library ##########################################################################

# Fundamentals
from collections import (
    deque
)

from dataclasses import (
    dataclass,
    field
)

from enum import (
    Enum
)

from typing import (
    Any,
    Callable,
    Iterator
)

import warnings

# Runtime
import threading

# Text utilities
import json
import re


# Third party ######################################################################################

# jinja2 (Pallets)
import jinja2


# Local ############################################################################################

# dsl.constraints
from . import constraints

# middleware
from ..middleware import (
    generic,
    vllm
)


# ##################################################################################################
# Globals
# ##################################################################################################

__d_environment__      : jinja2.Environment = None
"""Configured instance of a Jinja2 environment with all DSL extensions enabled."""

__d_environment_lock__ : threading.Lock     = threading.Lock()
"""Lock that governs access to `__d_environment__` global."""

__s_environment__      : jinja2.Environment = None
"""Configured instance of a Jinja2 environment limited to the static subset of the DSL."""

__s_environment_lock__ : threading.Lock     = threading.Lock()
"""Lock that governs access to `__s_environment__` global."""



# ##################################################################################################
# Classes
# ##################################################################################################

# RenderingMode ####################################################################################

class RenderingMode(Enum):

    """
    Specifies how :py:func:`langworks.dsl.environment.render` should process templates, either
    using the 'static' DSL, excluding constructs for guided generation, or using the 'dynamic' DSL,
    including such constructs, among which constraints.
    """

    # Options ######################################################################################

    STATIC  : int = 0
    """
    Renders template in static mode.
    """

    DYNAMIC : int = 1
    """
    Renders template in dynamic mode.
    """

    # End of class 'RenderingMode' #################################################################


# ##################################################################################################
# Functions
# ##################################################################################################

# render ###########################################################################################

def render(
    template : str, 
    context  : dict[str, Any] , 
    mode     : RenderingMode  = RenderingMode.STATIC,
    nested   : bool           = True
) -> Iterator[str | constraints.Constraint]:
    
    """
    Processes the given template set against the context provided, using a Jinja2 environment 
    configured to apply Langwork's DSL.

    Parameters
    ----------

    template
        Template to process.

    context
        Context to reference when processing the template.

    mode
        Whether to apply Langwork's complete 'dynamic' DSL, or the restricted 'static' DSL.

        Also see: :py:class:`langworks.dsl.environment.RenderingMode`.

    nested 
        Flag that determines whether nested Jinja2 constructs are also rendered. If set to `True`
        nested constructs are rendered too, otherwise they are left unprocessed.

    """
    
    # ##############################################################################################
    # Preparation
    # ##############################################################################################

    # Predeclarations ##############################################################################
        
    # string: Holds chunks of text processed by Jinja.
    string : str = None

    # re_jinja_tag: Compiled regular expression to quickly find Jinja opening tags.
    re_jinja_tag : re.Pattern = re.compile(r"\{[\{\%}]")


    # Pre-processing ###############################################################################

    # Split off any text leading up to a Jinja open tag.
    jinja_tag_pos_match : re.Match | None = re_jinja_tag.search(template)

    if jinja_tag_pos_match is None:

        # When no opening tag can be found, the template needs no further processing, and can be
        # returned as-is.
        yield template
        return
    
    else:

        jinja_tag_pos : int = jinja_tag_pos_match.start()

        yield template[:jinja_tag_pos]
        template = template[jinja_tag_pos:]


    # Jinja ########################################################################################

    ### Acquire reference to Jinja environment #####################################################

    # Set-up variable to hold the Jinja environment.
    jinja_env : jinja2.Environment = None

    # Handle loading of dynamic environment:
    if mode == RenderingMode.DYNAMIC:

        # Access relevant globals to access unrestricted environment for rendering.
        global __d_environment__
        global __d_environment_lock__

        # Acquire lock to ensure threadsafe singleton behaviour.
        with __d_environment_lock__:

            # Check if the environment was instantiated before, if not instantiate it.
            if not __d_environment__:

                # Initialize environment.
                __d_environment__ = (
                    jinja2.Environment(

                        cache_size = 128,

                        extensions = [
                            constraints.ChoiceTag,
                            constraints.GenTag,
                            constraints.GrammarTag,
                            constraints.JSONTag,
                            constraints.RegexTag
                        ]
                    )
                )

                # Add globals.
                __d_environment__.globals.update(**{
                    "Params" : generic.SamplingParams,
                    "vllm"   : { "Params": vllm.SamplingParams }
                })

            # Get local reference.
            jinja_env : jinja2.Environment = __d_environment__

    else:

        # Check for unsupported arguments, warning as needed.
        if mode != RenderingMode.STATIC:

            warnings.warn(
                f"Parameter langworks.dsl.environment.render:mode' was set to '{mode}' where either"
                f" 'STATIC' or 'DYNAMIC' was expected; defaulting to 'static';"
            )

        # Access relevant globals to access restricted environment for rendering.
        global __s_environment__
        global __s_environment_lock__

        # Acquire lock to ensure threadsafe singleton behaviour.
        with __s_environment_lock__:

            # Check if the environment was instantiated before, if not instantiate it.
            if not __s_environment__:

                # Initialize environment.
                __s_environment__ = (
                    jinja2.Environment(
                        cache_size = 128,
                    )
                )

            # Get local reference.
            jinja_env : jinja2.Environment = __s_environment__


    ### Create shared context ######################################################################

    # Instantiate a Jinja template based on the given string template.
    jinja_template : jinja2.Template = jinja_env.from_string(template)

    # Create a separate context to hold output variables.
    output_context : dict = {}

    # Using the Jinja template, create a Jinja context object, to be reused by all sub-templates.
    jinja_context = jinja_template.new_context({**context, "output": output_context})


    # ##############################################################################################
    # Processing
    # ##############################################################################################

    # Create a deque to keep track of (sub-)template generators, adding to it the generator of the
    # Jinja template already instantiated.
    queue : deque[Iterator[str]] = deque([jinja_template.root_render_func(jinja_context)])

    # Keep running as long as there are generators that are not exhausted.
    while True:

        # Acquire next string chunk ################################################################

        # Attempt to acquire a generator, breaking if no more generators can be acquired.
        try:
            generator = queue.pop()
        except:
            break

        # Retrieve next string chunk, skipping to the next generator if not more chunks can be
        # retrieved from the current generator.
        string = next(generator, None)

        if string is None:
            continue

        # Put back the generator on the queue, for a next pass. In doing so, the queue is set-up to
        # give precedence to any sub-template generators.
        queue.append(generator)


        # Process chunk ############################################################################

        # Handle constraints.
        if string[:2] == "|%" and mode == RenderingMode.DYNAMIC:

            # Extract identifier of the constraint.
            constraint_hash = string[3:-3]

            # If so, retrieve the constraint object, and yield it.
            constraint : constraints.ConstraintRepr = (
                constraints.cache.get(int(constraint_hash), None)
            )

            # Yield the results.
            if constraint is not None:

                # Decode specs if needed.
                constraint : constraints.Constraint = type(constraint).instantiate(constraint)

                # Add finalizer.
                if constraint.var is not None:
                    constraint.finalizer = lambda x: output_context.update(**{constraint.var: x})

                # Yield result.
                yield constraint

        # Handle other kinds of strings.
        else:

            # Handle nesting as required.
            if nested is True:

                # Split off any text preceeding a Jinja opening tag, preserving computation.
                jinja_tag_pos_match = re_jinja_tag.search(string)

                if jinja_tag_pos_match is not None:

                    # Split up text.
                    jinja_tag_pos = jinja_tag_pos_match.start()

                    yield string[:jinja_tag_pos]
                    string = string[jinja_tag_pos:]

                    # Create a sub-template and accompanying generator, and add it to the queue.
                    jinja_template = jinja_env.from_string(string)
                    queue.append(jinja_template.root_render_func(jinja_context))

                    # Skip to the next cycle.
                    continue

            # Otherwise, return the string unaltered.
            yield string

    # End of function 'render' #####################################################################

# End of File ######################################################################################