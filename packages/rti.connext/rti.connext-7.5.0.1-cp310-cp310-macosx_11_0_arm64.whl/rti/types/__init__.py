# Copyright (c) 2005-2024 Real-Time Innovations, Inc.  All rights reserved.
# No duplications, whole or partial, manual or electronic, may be made
# without express written permission.  Any such copies, or revisions thereof,
# must display this notice unaltered.
# This code contains trade secrets of Real-Time Innovations, Inc.

from types import SimpleNamespace
from typing import List, Union, Any
from dataclasses import dataclass

# The following imports are intentionally exposed outside this module
import rti.idl_impl.annotations as annotations
import rti.idl_impl.type_utils as type_utils
from rti.idl_impl.type_plugin import (
    finalize_type_plugin_factory,
    TypeSupport,
    TypeSupportKind,
)

# The following imports are private for use in this file only
import rti.idl_impl.type_hints as _type_hints
import rti.idl_impl.sample_interpreter as _sample_interpreter
import rti.idl_impl.unions as _unions
import rti.idl_impl.decorators as _decorators
import rti.idl_impl.reflection_utils as _reflection_utils
from rti.connextdds import ExtensibilityKind as _ExtensibilityKind

try:
    from typing_extensions import dataclass_transform
except ImportError:

    def dataclass_transform():
        def decorator(cls):
            return cls

        return decorator


#
# This module contains the public interface for decorating Python classes
# as DDS/IDL types
#


# --- Custom type hints -------------------------------------------------------

# The following publicly exposes the type hints defined in the type_hints module
# They're not defined directly here because they're also used internally in
# idl_impl.

int8 = _type_hints.int8
uint8 = _type_hints.uint8

int16 = _type_hints.int16
uint16 = _type_hints.uint16

int32 = _type_hints.int32
uint32 = _type_hints.uint32

# int64 is provided for consistency, but int has the same meaning
int64 = _type_hints.int64
uint64 = _type_hints.uint64

# float64 is provided for consistency, but float has the same meaning
float32 = _type_hints.float32
float64 = _type_hints.float64

char = _type_hints.char
wchar = _type_hints.wchar

# --- Member annotations ------------------------------------------------------

key = annotations.KeyAnnotation(True)


def id(value: int) -> annotations.IdAnnotation:
    """Annotation that sets a explicit member ID. By default they're assigned
    automatically
    """
    return annotations.IdAnnotation(int(value))


def bound(value: int):
    """Annotation that sets the maximum size for a Sequence or a str field"""
    return annotations.BoundAnnotation(int(value))


unbounded = bound(annotations.UNBOUNDED)


def array(dimensions: Union[None, int, List[int]]):
    """Annotation that configures a Sequence field as an array with the given
    dimensions
    """
    return annotations.ArrayAnnotation(dimensions)


utf8 = annotations.CharEncodingAnnotation(annotations.CharEncoding.UTF8)
utf16 = annotations.CharEncodingAnnotation(annotations.CharEncoding.UTF16)


def element_annotations(value: List[Any]):
    """Sets the annotations for the element type of a sequence or array"""
    return annotations.ElementAnnotations(value)

def default(value: Any):
    """Sets the default value for a field"""
    return annotations.DefaultAnnotation(value)

def min(value: Any):
    """Sets the minimum value for a field"""
    return annotations.MinAnnotation(value)

def max(value: Any):
    """Sets the maximum value for a field"""
    return annotations.MaxAnnotation(value)

# --- Type annotations --------------------------------------------------------


extensible = annotations.ExtensibilityAnnotation(_ExtensibilityKind.EXTENSIBLE)
mutable = annotations.ExtensibilityAnnotation(_ExtensibilityKind.MUTABLE)
final = annotations.ExtensibilityAnnotation(_ExtensibilityKind.FINAL)


def allowed_data_representation(xcdr1=True, xcdr2=True):
    """Type annotation that specifies which serialized data representation the type supports"""
    value = annotations.AllowedDataRepresentationFlags.XCDR1 if xcdr1 else 0
    value |= annotations.AllowedDataRepresentationFlags.XCDR2 if xcdr2 else 0
    return annotations.AllowedDataRepresentationAnnotation(value)


def type_name(value: str):
    """Type annotation that sets the default type name when a Topic with this type is created"""
    return annotations.TypeNameAnnotation(value)


# --- Union cases -------------------------------------------------------------


def case(*args, **kwargs):
    """Returns a field descriptor that allows getting and setting a union
    case with the right discriminator
    """

    if kwargs.get("is_default", False):
        field_descriptor = _unions.DefaultCase(list(args))
    elif len(args) == 0:
        raise TypeError("At least one case label is required")
    elif len(args) > 1:
        field_descriptor = _unions.MultiCase(list(args))
    else:
        field_descriptor = _unions.Case(args[0])

    return field_descriptor


# --- Dataclass factories -----------------------------------------------------


def array_factory(element_type: type, size: Union[int, List[int]] = 0):
    # Note that type_utils.array_factory can be set with a custom factory
    return type_utils.array_factory(element_type, size)


list_factory = type_utils.list_factory  # list_factory can't be customized

# --- Exceptions --------------------------------------------------------------

FieldSerializationError = _sample_interpreter.FieldSerializationError

# --- Utility functions -------------------------------------------------------

to_array = type_utils.to_array
to_char = type_utils.to_char
to_wchar = type_utils.to_wchar
from_char = type_utils.from_char
from_wchar = type_utils.from_wchar

# --- Decorators --------------------------------------------------------------


@dataclass_transform()
def struct(cls=None, *, type_annotations=[], member_annotations={}):
    """This decorator makes a Python class usable as DDS topic-type defined as
    an IDL struct.
    """

    def wrapper(cls):
        actual_cls = dataclass(cls)
        actual_cls.type_support = TypeSupport(
            actual_cls,
            TypeSupportKind.STRUCT,
            type_annotations,
            member_annotations,
            sample_program_options=_decorators._get_current_sample_program_options(),
        )
        return actual_cls

    if cls is None:
        # Decorator used with arguments:
        #  @idl.struct(type_annotations={...}, ...)
        #  class Foo:
        return wrapper
    else:
        # Decorator used without arguments:
        #  @idl.struct
        #  class Foo:
        return wrapper(cls)


def union(cls=None, *, type_annotations=[], member_annotations={}):
    """This decorator makes a Python class usable as DDS topic-type defined as
    an IDL union.

    The class requires two instance members: discriminator and value, plus
    an idl.case field for each union case.
    """

    def wrapper(cls):
        _unions.configure_union_class(cls)
        cls.type_support = TypeSupport(
            cls,
            TypeSupportKind.UNION,
            type_annotations,
            member_annotations,
            sample_program_options=_decorators._get_current_sample_program_options(),
        )

        return cls

    if cls is None:
        return wrapper
    else:
        return wrapper(cls)


@dataclass_transform()
def alias(cls=None, *, annotations=[]):
    """This decorator maps a Python class with a single field to an IDL alias;
    the type of the field refers to the aliased type.
    """

    def wrapper(cls):
        actual_cls = dataclass(cls)
        if isinstance(annotations, list):
            member_annotations = {"value": annotations}
        else:
            member_annotations = annotations

        actual_cls.type_support = TypeSupport(
            actual_cls,
            TypeSupportKind.ALIAS,
            type_annotations=None,
            member_annotations=member_annotations,
            sample_program_options=_decorators._get_current_sample_program_options(),
        )
        return actual_cls

    if cls is None:
        return wrapper
    else:
        return wrapper(cls)


def enum(cls=None, *, type_annotations=[]):
    """This decorator makes a Python IntEnum usable as an IDL enum"""

    def wrapper(cls):
        if not _reflection_utils.is_enum(cls):
            raise TypeError(f"{cls} is not an IntEnum")

        cls.type_support = TypeSupport(cls, TypeSupportKind.ENUM, type_annotations)
        return cls

    if cls is None:
        # Decorator used with arguments:
        #  @idl.enum(type_annotations={...}, ...)
        #  class Foo(IntEnum):
        return wrapper
    else:
        # Decorator used without arguments:
        #  @idl.enum
        #  class Foo(IntEnum):
        return wrapper(cls)


serialization_options = _decorators.serialization_options
SerializationOptions = _decorators.SerializationOptions

_idl_modules = {}


def get_module(name: str) -> SimpleNamespace:
    """Returns a SimpleNamespace that contains types defined in an IDL module
    for a given name. The syntax is '::MyModule' or '::MyModule::MySubmodule'.
    """

    # Return the module if it already exists or create it if it doesn't
    return _idl_modules.setdefault(name, SimpleNamespace())


def get_type_support(cls: type) -> TypeSupport:
    if not hasattr(cls, "type_support"):
        raise TypeError(f"{cls} is not an IDL type")
    return cls.type_support


# --- Other utilties ----------------------------------------------------------


def finalize_globals() -> None:
    """Optionally finalize global state before the application ends.

    This method can only be used after all other DDS entities have been closed.

    Most applications don't need to call this function. It is useful when
    profiling native memory usage to ensure that the application ends with no
    in-use memory.
    """

    finalize_type_plugin_factory()
