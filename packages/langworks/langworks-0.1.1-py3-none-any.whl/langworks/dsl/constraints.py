# ##################################################################################################
#
# Title:
#
#   langworks.dsl.constraints.py
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
#   Part of the Langworks framework, implementing various constraints to guide LLM generation.
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

from typing import (
    Any,
    Callable
)

# Text utilities.
import json


# Third party ######################################################################################

# cachetools (Thomas Kemmer)
import cachetools

# jinja2_simple_tags (Mihail Mishakin)
from jinja2_simple_tags import (
    ContainerTag,
    StandaloneTag
)


# Local ############################################################################################

from ..middleware.generic import (
    SamplingParams
)


# ##################################################################################################
# Globals
# ##################################################################################################

cache : cachetools.LRUCache[
    int, type["ConstraintRepr"]
] = cachetools.LRUCache(maxsize = 256)
"""Cache of constraint objects indexed by the hashes of these objects."""


# ##################################################################################################
# Functions
# ##################################################################################################

# __create_and_cache__ #############################################################################

def __create_and_cache__(cls : Any, *args, **kwargs):

    """
    Creates an intermediate representation using the given class, to be initialized with the passed
    arguments, caching the object, and return an escaped hash to access said object.
    """

    # Create an object for intermediate representation.
    obj = cls(*args, **kwargs)

    # Acquire hash of the object.
    try:

        # Try to hash the object.
        _hash = hash(obj)

    except:

        # If it fails, the object is mutable, and needs to be converted to a string before hashing.
        _hash = hash(str(obj))

    # Add object to cache.
    global cache
    cache[_hash] = obj

    # Return formatted reference.
    return f"|% {_hash} %|"

    # End of function '__create_and_cache__' #######################################################


# ##################################################################################################
# Classes
# ##################################################################################################

# Constraint #######################################################################################

@dataclass
class Constraint:

    """
    Specifies a generic constraint on the generation by an LLM, to be processed by a
    :py:class:`langworks.middleware.generic.Middleware`.
    """

    # Fields #######################################################################################

    spec    : Any                            = field(default = None)
    """
    The specification of the constraint.
    """

    var     : str | None                     = field(default = None)
    """
    Name of the variable used to store the content.
    """

    params  : SamplingParams                 = field(default = None)
    """
    Sampling parameters to apply when generating the content specified by this constraint.
    """

    finalizer : Callable[[Any], None] = field(default = None)
    """
    Callable that must be invoked by a :py:class:`langworks.middleware.generic.Middleware` upon
    generation of the text specified by the constraint, allowing for that output to be fed back
    into the parsing engine.
    """

    # End of class 'Constraint' ####################################################################


# ConstraintRepr ###################################################################################

@dataclass(frozen = True)
class ConstraintRepr:

    """
    Generic class implementing an intermediate representation of a generation constraint.
    """

    # Fields #######################################################################################

    spec    : Any                            = field(default = None)
    """
    Analog to :py:attr:`Constraint.spec`.
    """

    var     : str | None                     = field(default = None)
    """
    Analog to :py:attr:`Constraint.var`.
    """

    params  : SamplingParams                 = field(default = None)
    """
    Analog to :py:attr:`Constraint.params`.
    """


    # Methods ######################################################################################

    @staticmethod
    def instantiate(repr : type["ConstraintRepr"]) -> Constraint:

        """
        May be invoked to convert the intermediate representation to an actual Constraint object.
        """

        raise NotImplementedError()
    
        # End of method 'instantiate' ##############################################################

    # End of class 'ConstraintRepr' ################################################################


# Choice ###########################################################################################

@dataclass
class Choice(Constraint):

    """
    Specifies a limited list of options the LLM may choose from during generation.
    """

    # Fields #######################################################################################

    spec : tuple[str] = field(default = None)
    """
    The list of options that the LLM may choose from.
    """

    # End of class 'Choice' ########################################################################


# ChoiceRepr #######################################################################################

@dataclass(frozen = True)
class ChoiceRepr(ConstraintRepr):

    """
    Intermediate representation of a choice-based constraint.
    """

    # Fields #######################################################################################

    spec : tuple[str] = field(default = None)
    """
    Analog to :py:attr:`Choice.spec`.
    """


    # Methods ######################################################################################

    @staticmethod
    def instantiate(repr : type["ChoiceRepr"]) -> Choice:
        return Choice(spec = repr.spec, var = repr.var, params = repr.params)
    
        # End of method 'instantiate' ##############################################################


    # End of class 'ChoiceRepr' ####################################################################


# ChoiceTag ########################################################################################

class ChoiceTag(StandaloneTag):

    """
    Implements a Jinja-tag for constructing constraints prescribing a limited list of choices. 
    In its minimal form, the constraint can be applied as follows::

        ```
        The sentiment is: {% choice ["positive", "negative"] %}.
        ```

    Any of the default constraint arguments may also be passed::

        ```
        The answer is {% 
            choice ["positive", "negative"], var = "sentiment", params = Params(max_tokens = 1) 
        %}
        ```
    """

    # ##############################################################################################
    # Class attributes
    # ##############################################################################################

    tags = {"choice"}


    # ##############################################################################################
    # Methods
    # ##############################################################################################

    # render #######################################################################################

    def render(self, options : list[str], var : str = None, params : SamplingParams = None):

        # Check validity of the passed content.
        if not (hasattr(options, "__len__") or hasattr(options, "__iter__")):

            raise ValueError(
                f"Object of type '{type(options)}' was passed for 'options'-argument of choice-tag"
                f" where list-like or iterable was expected;"
            )

        for i, option in enumerate(options):

            if not isinstance(option, str):

                raise ValueError(
                    f"Object of type '{type(option)}' was passed for 'options'-argument at index"
                    f" '{i}' where type 'string' was expected;"
                )

        # Delegate
        return __create_and_cache__(
            ChoiceRepr, spec = tuple(options), var = var, params = params
        )
    
        # End of method 'render' ###################################################################
    
    # End of class 'ChoiceTag' #####################################################################


# Gen ##############################################################################################

@dataclass
class Gen(Constraint):

    """
    A non-constraint, actually specifying no restriction on generation, instead expecting the LLM
    to generate as it sees fit.
    """

    pass # No additions

    # End of class 'Gen' ###########################################################################


# GenRepr ##########################################################################################

@dataclass(frozen = True)
class GenRepr(ConstraintRepr):

    """
    Intermediate representation of a non-constraint, a constraint that actually specifies no 
    restrictions on generation.
    """

    # Fields #######################################################################################

    # No additions.


    # Methods ######################################################################################

    @staticmethod
    def instantiate(repr : type["GenRepr"]) -> Gen:
        return Gen(spec = None, var = repr.var, params = repr.params)
    
        # End of method 'instantiate' ##############################################################


    # End of class 'GenRepr' #######################################################################
    

# GenTag ###########################################################################################

class GenTag(StandaloneTag):

    """
    Implements a Jinja-tag for constructing non-constraints, constraints that actually specify no
    content-wise restrictions for generation. They may be embedded in queries as follows::

        ```
        Today I'm feeling {% gen %}
        ```

    Any of the default constraint arguments may be passed, however::

        ```
        Today I'm feeling {% gen var = "answer", params = Params(max_tokens = 1) %}.
        ```
    """

    # ##############################################################################################
    # Class attributes
    # ##############################################################################################

    tags = {"gen"}


    # ##############################################################################################
    # Methods
    # ##############################################################################################

    def render(self, var : str = None, params : SamplingParams = None):

        return __create_and_cache__(GenRepr, spec = None, var = var, params = params)
    
    # End of class 'GenTag' ########################################################################


# Grammar ##########################################################################################

@dataclass
class Grammar(Constraint):

    """
    A constraint specifying a EBNF-grammar that the LLM must conform to during generation.
    """

    # Fields #######################################################################################

    spec : str = field(default = None)
    """
    The EBNF grammar that the generated content must conform to.
    """

    # End of class 'Grammar' #######################################################################


# GrammarRepr ######################################################################################

@dataclass(frozen = True)
class GrammarRepr(ConstraintRepr):

    """
    Intermediate representation of a grammar-based constraint.
    """

    # Fields #######################################################################################

    spec : str = field(default = None)
    """
    Analog to :py:attr:`Grammar.spec`.
    """


    # Methods ######################################################################################

    @staticmethod
    def instantiate(repr : type["GrammarRepr"]) -> Grammar:
        return Grammar(spec = repr.spec, var = repr.var, params = repr.params)
    
        # End of method 'instantiate' ##############################################################


    # End of class 'GrammarRepr' ###################################################################


# GrammarTag #######################################################################################
    
class GrammarTag(ContainerTag):

    """
    Implements a Jinja-tag for constructing constraints using a EBNF grammar. They may be embedded 
    in queries as follows::

        ```
        Present the number '7' with two leading zeroes: {% grammar %}
        ?start: "0" "0" NUMBER
        %import common.NUMBER
        {% endgrammar %}.
        ```

    Like all embeddable constraints, this contraint also accepts the default constraint arguments::

        ```
        {% grammar var = "num", params = Params(temperature = 0.0) %}...{% endgrammar %}
        ```
    """

    # ##############################################################################################
    # Class attributes
    # ##############################################################################################

    tags = {"grammar"}


    # ##############################################################################################
    # Methods
    # ##############################################################################################

    def render(self, var : str = None, params : SamplingParams = None, caller = None):

        # Validate content.
        content = str(caller()).encode()

        # Delegate
        return __create_and_cache__(GrammarRepr, spec = content, var = var, params = params)

    
    # End of class 'GrammarTag' ####################################################################


# JSON #############################################################################################

@dataclass
class JSON(Constraint):

    """
    A constraint specifying a JSON-schema that the LLM must conform to during generation.
    """

    # Fields #######################################################################################

    spec : dict = field(default = None)
    """
    The JSON schema that specifies the constraint.
    """
    

    # End of class 'JSON' ##########################################################################


# JSONRepr #########################################################################################

@dataclass(frozen = True)
class JSONRepr(ConstraintRepr):

    """
    Intermediate representation of a JSON-based constraint.
    """

    # Fields #######################################################################################

    spec : str = field(default = None)
    """
    The JSON schema that specifies the constraint, as string.
    """


    # Methods ######################################################################################

    @staticmethod
    def instantiate(repr : type["JSONRepr"]) -> type["JSON"]:
        return JSON(spec = json.loads(repr.spec), var = repr.var, params = repr.params)
    
        # End of method 'instantiate' ##############################################################


    # End of class 'JSONRepr' ######################################################################


# JsonTag ##########################################################################################
    
class JSONTag(ContainerTag):

    """
    Implements a Jinja-tag for constructing constraints using a JSON schema. They may be embedded in
    queries as follows::

        ```
        Ada Lovelace's personal profile can be represented in JSON as follows: 
        {% json %}
            {
                "title": "Profile",

                "type": "object",

                "properties": {
                
                    "first_name": {
                        "title": "First name",
                        "type": "string"
                    },

                    "last_name": {
                        "title": "Last name",
                        "type: "string
                    }

                },

                "required": ["first_name", "last_name"]
            }
        {% endjson %}.
        ```

    Additional constraints may be passed::

        ```
        {% json var = "profile", params = Params(temperature = 0.0) %}...{% endjson %}
        ```
    """

    # ##############################################################################################
    # Class attributes
    # ##############################################################################################

    tags = {"json"}


    # ##############################################################################################
    # Methods
    # ##############################################################################################

    def render(self, var : str = None, params : SamplingParams = None, caller = None):

        # Check validity of the passed content.
        obj = json.loads(str(caller()))

        # Delegate
        return __create_and_cache__(JSONRepr, spec = json.dumps(obj), var = var, params = params)
    
    
    # End of class 'JSONTag' #######################################################################


# Regex ############################################################################################

@dataclass
class Regex(Constraint):

    """
    A constraint specifying a regular expression that the LLM must conform to during generation.
    """

    # Fields #######################################################################################

    spec : str = field(default = None)
    """
    The regular expression that specifies the constraint.
    """

    # End of class 'Regex' #########################################################################


# RegexRepr ########################################################################################

@dataclass(frozen = True)
class RegexRepr(ConstraintRepr):

    """
    Intermediate representation of a regex-based constraint.
    """

    # Fields #######################################################################################

    spec : str = field(default = None)
    """
    Analog to :py:attr:`Regex.spec`.
    """


    # Methods ######################################################################################

    @staticmethod
    def instantiate(repr : type["RegexRepr"]) -> type["Regex"]:
        return Regex(spec = repr.spec, var = repr.var, params = repr.params)
    
        # End of method 'instantiate' ##############################################################


    # End of class 'RegexRepr' #####################################################################


# RegexTag #########################################################################################

class RegexTag(StandaloneTag):

    """
    Implements a Jinja-tag for constructing regex-based constraints. They may be embedded in
    queries as follows::

        ```
        The sentiment is: {% regex "(positive)|(negative)" %}.
        ```

    Any of the default constraint arguments may also be passed::

        ```
        The sentiment is: {% 
            regex "(positive)|(negative)", var = "sentiment", params = Params(max_tokens = 2) 
        %}
        ```
    """

    # ##############################################################################################
    # Class attributes
    # ##############################################################################################

    tags = {"regex"}


    # ##############################################################################################
    # Methods
    # ##############################################################################################

    # render #######################################################################################

    def render(self, regex : str, var : str = None, params : SamplingParams = None):
        return __create_and_cache__(RegexRepr, spec = regex, var = var, params = params)
    
        # End of method 'render' ###################################################################
    
    # End of class 'RegexTag' ######################################################################

# End of File ######################################################################################