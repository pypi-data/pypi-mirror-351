# Copyright (c) 2005-2024 Real-Time Innovations, Inc.  All rights reserved.
# No duplications, whole or partial, manual or electronic, may be made
# without express written permission.  Any such copies, or revisions thereof,
# must display this notice unaltered.
# This code contains trade secrets of Real-Time Innovations, Inc.


from abc import ABC, ABCMeta, abstractmethod
import asyncio
import ctypes
import dataclasses
import functools
import inspect
import keyword
import types
import hashlib
from typing import Any, List, Optional, Union, Dict, Generic, TypeVar

import rti.connextdds as dds
import rti.types as idl
from rti.idl_impl.sample_interpreter import get_field_factory
from rti.idl_impl import reflection_utils
from rti.idl_impl.annotations import find_annotation

from rti.rpc import Requester, Replier
import rti.rpc._annotations as annotations

import rti.rpc._exceptions as exceptions

import rti.asyncio

# Define a generic type variable
T = TypeVar("T")


@dataclasses.dataclass
class ByRef(Generic[T]):
    """
    This class is designed to emulate pass-by-reference behavior in Python, which
    natively uses pass-by-value semantics for primitive types (like `int`, `float`,
    and `str`). It is used to implement the `rpc.out_param` and `rpc.inout_param`
    for the primitive types.

    For example for the following operation:
    ```
    void op(out long param);
    ```

    The Python equivalent will be:
    ```
    def op(self, param: rpc.ByRef[idl.int32]):
    ```

    This allows the modification of the parameter value in the service implementation,
    and this change will be reflected in the client side variable used to call the
    operation.
    ```param.value = 10```
    """
    value: T


def _calculate_hash(name: str) -> int:
    name_hash = hashlib.md5(name.encode("utf-8")).digest()
    hash = (
        ((name_hash[3]) << 24)
        | ((name_hash[2] << 16) & 0xFF0000)
        | (((name_hash[1]) << 8) & 0xFF00)
        | (name_hash[0] & 0xFF)
    )

    # The hash must be a value between int32_min and int32_max
    return ctypes.c_int32(hash).value


def _make_proto_dataclass(cls_name, fields, *, bases=(), namespace=None):
    """This function is the same as dataclasses.make_dataclass, except that it
    doesn't actually apply the dataclass decorator at the end (so it can be
    done by the caller at a later time).
    """

    if namespace is None:
        namespace = {}

    # While we're looking through the field names, validate that they
    # are identifiers, are not keywords, and not duplicates.
    seen = set()
    annotations = {}
    defaults = {}
    for item in fields:
        if isinstance(item, str):
            name = item
            tp = "typing.Any"
        elif len(item) == 2:
            (
                name,
                tp,
            ) = item
        elif len(item) == 3:
            name, tp, spec = item
            defaults[name] = spec
        else:
            raise TypeError(f"Invalid field: {item!r}")

        if not isinstance(name, str) or not name.isidentifier():
            raise TypeError(f"Field names must be valid identifiers: {name!r}")
        if keyword.iskeyword(name):
            raise TypeError(f"Field names must not be keywords: {name!r}")
        if name in seen:
            raise TypeError(f"Field name duplicated: {name!r}")

        seen.add(name)
        annotations[name] = tp

    # Update 'ns' with the user-supplied namespace plus our calculated values.
    def exec_body_callback(ns):
        ns.update(namespace)
        ns.update(defaults)
        ns["__annotations__"] = annotations

    # We use `types.new_class()` instead of simply `type()` to allow dynamic creation
    # of generic dataclasses.
    return types.new_class(cls_name, bases, {}, exec_body_callback)


def _make_parameter_field(name, parameter_type, parameter_annotations):
    """Returns a tuple with the name, type and field for a function parameter or
    return type
    """

    if reflection_utils.is_primitive_or_enum(parameter_type):
        field = dataclasses.field(default=0)
    elif parameter_type is str:
        field = dataclasses.field(default="")
    else:
        current_annotations = parameter_annotations.get(name, {})
        field = dataclasses.field(
            default_factory=get_field_factory(parameter_type, current_annotations)
        )

    return (name, parameter_type, field)


def _make_in_struct(
    interface_name: str,
    operation_name: str,
    in_parameters: Dict[str, type],
    operation_annotations,
    parameter_annotations,
):
    """Creates the python class for the IDL <Service>_<operation>_In struct.

    Given the arguments to an operation such as

    def attack(status: Status, id: int) -> Status: ...

    Create:

    @idl.struct
    class Robot_attack_In:
        status: Status = field(default_factory = Status)
        id: int = 0
    """

    fields = []
    for name, parameter_type in in_parameters.items():
        # skip self parameter
        if name == "self":
            continue

        if reflection_utils.get_origin(parameter_type) is ByRef:
            parameter_type = reflection_utils.get_underlying_type(parameter_type)
        field = _make_parameter_field(name, parameter_type, parameter_annotations)
        fields.append(field)

    return idl.struct(
        _make_proto_dataclass(f"{interface_name}_{operation_name}_In", fields),
        type_annotations=operation_annotations,
        member_annotations=parameter_annotations,
    )


def _make_out_struct(
    interface_name: str,
    operation_name: str,
    out_parameters: Dict[str, type],
    operation_annotations,
    parameter_annotations,
):
    """Creates the python class for the IDL <Service>_<operation>_Out struct.

    Given the arguments to an operation such as

    def attack(status: Status, id: int) -> Status: ...

    Create:

    @idl.struct
    class Robot_attack_Out:
        return_: Status = field(default_factory = Status)
    """

    fields = []
    for name, parameter_type in out_parameters.items():
        if reflection_utils.get_origin(parameter_type) is ByRef:
            parameter_type = reflection_utils.get_underlying_type(parameter_type)
        fields.append(
            _make_parameter_field(name, parameter_type, parameter_annotations)
        )

    return idl.struct(
        _make_proto_dataclass(f"{interface_name}_{operation_name}_Out", fields),
        type_annotations=operation_annotations,
        member_annotations=parameter_annotations,
    )


def _make_result_union(
    interface_name: str,
    operation_name: str,
    out_struct: type,
    exceptions: List[type],
    operation_annotations,
):
    """Creates the python class for the IDL <Service>_<operation>_Result union."""

    fields = [
        ("discriminator", idl.int32, dataclasses.field(default=0)),
        (
            "value",
            Union[out_struct, type(None)],
            dataclasses.field(default_factory=out_struct),
        ),
        ("result", out_struct, idl.case(0)),
    ]

    fields.extend(
        (
            f"{exception.__name__}_ex".lower(),
            exception,
            idl.case(_calculate_hash(exception.__name__)),
        )
        for exception in exceptions
    )

    result = idl.union(
        _make_proto_dataclass(f"{interface_name}_{operation_name}_Result", fields),
        type_annotations=operation_annotations,
    )
    result.out_struct = out_struct
    result.raises = exceptions

    return result


def _get_operations(cls: type):
    """Get the operations of a type as an iterator"""

    for name, member in cls.__dict__.items():
        if not getattr(member, "_is_rpc_operation", False):
            continue

        yield name, member


def _make_in_structs_for_interface(cls: type):
    """Creates the in structs for all operations in an interface."""

    in_structs = {}
    for name, member in _get_operations(cls):
        parameters = {}
        for k, v in member.__annotations__.items():
            if k == "return":
                continue

            parameter_kind = find_annotation(
                member._parameter_annotations.get(k, {}),
                cls=annotations.ParameterKindAnnotation,
            )
            if parameter_kind.value != annotations.ParameterKind.OUT:
                parameters[k] = v

        in_structs[_calculate_hash(name)] = (
            name,
            _make_in_struct(
                cls.__name__,
                name,
                parameters,
                member._operation_annotations,
                member._parameter_annotations,
            ),
        )

    return in_structs


def _make_result_types_for_interface(cls: type):
    """Creates the result types for all operations in an interface."""

    result_unions = {}
    for name, member in _get_operations(cls):
        parameters = {}
        for k, v in member.__annotations__.items():
            if k == "return":
                if v is not None:
                    parameters["return_"] = v
            else:
                parameter_kind = find_annotation(
                    member._parameter_annotations.get(k, {}),
                    cls=annotations.ParameterKindAnnotation,
                )
                if parameter_kind.value != annotations.ParameterKind.IN:
                    parameters[k] = v

        out_struct = _make_out_struct(
            cls.__name__,
            name,
            parameters,
            member._operation_annotations,
            member._parameter_annotations,
        )
        result_unions[_calculate_hash(name)] = (
            name,
            _make_result_union(
                cls.__name__,
                name,
                out_struct,
                member._raises,
                member._operation_annotations,
            ),
        )

    return result_unions


def _make_call_union(cls: type):
    """Creates the python class for the IDL <Service>_Call union.

    For a class like:

    class Robot:
        def attack(status: Status, id: int) -> Status: ...
        def retreat() -> None: ...

    Creates the following union type:

    @idl.union
    class Robot_Call:

        discriminator: idl.int32 = Robot_retreat_Hash
        value: Union[Robot_attack_In, Robot_retreat_In] = field(default_factory = Robot_retreat_In)

        attack: Robot_attack_In = idl.case(Robot_attack_Hash)
        retreat: Robot_retreat_In = idl.case(Robot_retreat_Hash)
    """

    in_structs = _make_in_structs_for_interface(cls)
    if len(in_structs) == 0:
        raise TypeError(f"{cls.__name__} has no @operation methods")

    fields = [
        ("discriminator", idl.int32, dataclasses.field(default=0)),
        ("value", Union, dataclasses.field(default=None)),
    ]

    for name, in_struct in in_structs.values():
        fields.append((name, in_struct, idl.case(_calculate_hash(name))))

    call_union = idl.union(_make_proto_dataclass(f"{cls.__name__}_Call", fields))
    call_union.in_structs = in_structs

    return call_union


def _make_return_union(cls: type):
    """Creates the python class for the IDL <Service>_Return union.

    For a class like:

    class Robot:
        def attack(status: Status, id: int) -> Status: ...
        def retreat() -> None: ...

    Creates the following union type:

    @idl.union
    class Robot_Return:

        discriminator: idl.int32 = Robot_retreat_Hash
        value: Union[Robot_attack_Result, Robot_retreat_Result] = field(default_factory = Robot_retreat_Result)

        attack: Robot_attack_Result = idl.case(Robot_attack_Hash)
        retreat: Robot_retreat_Result = idl.case(Robot_retreat_Hash)
    """

    result_unions = _make_result_types_for_interface(cls)

    fields = [
        ("discriminator", idl.int32, dataclasses.field(default=0)),
        ("value", Union, dataclasses.field(default=None)),
        ("remoteEx", idl.int32, idl.case(0)),
    ]

    for name, result_union in result_unions.values():
        fields.append((name, result_union, idl.case(_calculate_hash(name))))

    return_union = idl.union(_make_proto_dataclass(f"{cls.__name__}_Return", fields))
    return_union.result_unions = result_unions

    return return_union


def service(cls=None, *, type_annotations=[], member_annotations={}):
    """This decorator marks an abstract base class as a remote service interface.

    A class annotated with this decorator can be used to create a Client
    or to define the implementation to be run in a Service.

    The operations that will be remotely callable need to be marked with the
    @operation decorator.
    """

    def wrapper(cls):
        cls.call_type = _make_call_union(cls)
        cls.return_type = _make_return_union(cls)
        return cls

    if cls is None:
        # Decorator used with arguments
        return wrapper
    else:
        # Decorator used without arguments
        return wrapper(cls)


def operation(
    funcobj=None, *, raises=[], operation_annotations=[], parameter_annotations={}
):
    """This decorator marks a method as an remote operation of a service interface.

    It also marks it as an @abc.abstractmethod.

    Only methods marked with this decorator will be callable using an RPC Client
    or an RPC Service.
    """

    def wrapper(funcobj):
        funcobj._is_rpc_operation = True
        funcobj._raises = raises
        funcobj._operation_annotations = operation_annotations
        funcobj._parameter_annotations = parameter_annotations
        return abstractmethod(funcobj)

    if funcobj is None:
        # Decorator used with arguments
        return wrapper
    else:
        # Decorator used without arguments
        return wrapper(funcobj)


def _arguments_to_in_struct(in_struct_type, method, args, kwargs):
    """
    This function takes all the arguments used to call a given
    method and extract and process the ones required for the request.
    """

    in_struct_values = {}

    idx = 0
    parameters = inspect.signature(method).parameters
    for param_name in parameters.keys():
        if param_name == "self":
            continue

        # if it's an rpc.out_param we skip it
        if param_name in getattr(in_struct_type, "__annotations__", {}):
            value = args[idx] if idx < len(args) else kwargs[param_name]
            # We need to convert the rpc.ByRef[inmutable] to
            # inmutable, so there is interoperability between
            # languages
            if isinstance(value, ByRef):
                value = value.value

            in_struct_values[param_name] = value

        idx += 1

    return in_struct_values


def _in_struct_to_arguments(method, in_struct, out_struct_type):
    """
    This function takes a in_struct and create/position the args
    and kargs that will be used to invoke the method in the service
    side.
    """
    result_kwargs = {}
    out_struct = None

    parameters = inspect.signature(method).parameters
    for param_name in parameters.keys():
        if param_name == "self":
            continue

        value = None
        argument_type = method.__annotations__[param_name]
        if hasattr(in_struct, param_name):
            value = getattr(in_struct, param_name)
        else:
            # If we find a parameter that is not in the in_struct
            # is because it is an rpc.out_param, and we need to build
            # it in the service side
            if out_struct is None:
                out_struct = out_struct_type()
            if hasattr(out_struct, param_name):
                value = getattr(out_struct, param_name)
            else:
                raise exceptions.RemoteUnknownExceptionError()

        if reflection_utils.get_origin(argument_type) is ByRef:
            value = argument_type(value)

        result_kwargs[param_name] = value

    return result_kwargs


def _arguments_to_out_struct(out_struct_type, kwargs, result):
    """
    This function is executed when the method in the service side has finished.
    It gathers the arguments values that need to be encapsulated into the reply,
    toguether with the return value if any.
    """
    out_struct_values = {}
    for field in dataclasses.fields(out_struct_type):

        value = None
        if field.name == "return_":
            value = result
        else:
            value = kwargs[field.name]

            # We need to convert the rpc.ByRef[inmutable] to
            # inmutable, so there is interoperability between
            # languages
            if isinstance(value, ByRef):
                value = value.value

        out_struct_values[field.name] = value

    return out_struct_values


def _out_struct_to_arguments(out_struct, method, args, kwargs):
    """
    Once the reply is received this function will take the received
    struct and update the rpc.out_param and rpc.inout_param arguments,
    and return the return value if any.
    """

    idx = 0
    parameters = inspect.signature(method).parameters
    for param_name, param in parameters.items():
        if param_name == "self":
            continue

        # if it's an rpc.in_param we skip it
        if hasattr(out_struct, param_name):
            value = getattr(out_struct, param_name)
            original_value = args[idx] if idx < len(args) else kwargs[param_name]
            if isinstance(original_value, ByRef):
                value = ByRef(value)

            if reflection_utils.is_sequence_type(param.annotation):
                original_value.clear()
                original_value.extend(value)
            else:
                reflection_utils.copy_fields(value, original_value)

        idx += 1

    return getattr(out_struct, "return_", None)


class _ClientMeta(ABCMeta):
    """This meta-class injects the code necessary to call RPC operations on a
    DDS domain.
    """

    def __new__(cls, name, bases, attrs):
        # This is the generic implementation of all operations, which will be
        # partially bound below for each @operation method in the class being
        # created.

        async def call_remote_operation_impl(self, method, in_struct, *args, **kwargs):
            # Send request with the operation arguments
            sample = type(self).call_type()

            in_struct_fields = _arguments_to_in_struct(in_struct, method, args, kwargs)

            setattr(sample, method.__name__, in_struct(**in_struct_fields))
            request_id = self.requester.send_request(sample)

            # Wait for the reply
            if not await self.requester.wait_for_replies_async(
                self.max_wait_per_call, 1, request_id
            ):
                self.failed_request_collector.add_failed_request(request_id)
                raise dds.TimeoutError(
                    f"{type(self).__name__}.{method.__name__} timed out waiting for reply"
                )

            reply = self.requester.take_replies(request_id)[0]
            if not reply.info.valid:
                raise dds.Error("Invalid return value received")

            if reply.data.discriminator != sample.discriminator:
                if reply.data.discriminator == 0:
                    exceptions.throw_from_remote_ex_code(reply.data.value)
                else:
                    raise dds.Error("Received result for invalid operation")

            out_value = reply.data.value
            if out_value.discriminator == 0:
                out_value = out_value.value

                # Return the received return value or none for operations
                # without a return value and/or modify the rpc.out_param and
                # rpc.inout_param arguments
                return _out_struct_to_arguments(out_value, method, args, kwargs)
            elif out_value.value is not None:
                # Rethrow a remote exception
                raise out_value.value
            else:
                raise exceptions.RemoteUnknownExceptionError()

        if name == "ClientBase":
            # The metaclass is being applied to ClientBase itself, so we don't
            # do anything. Only ClientBase subclasses need to be modified.
            return super().__new__(cls, name, bases, attrs)

        if len(bases) == 0 or not hasattr(bases[0], "call_type"):
            raise TypeError("An RPC Client must inherit from an @rti.rpc.service class")

        service_cls = bases[0]
        in_structs = service_cls.call_type.in_structs.values()
        for method_name, method in _get_operations(service_cls):
            in_struct = None
            for search_name, search in in_structs:
                if search_name == method_name:
                    in_struct = search
                    break
            if in_struct is None:
                raise TypeError(f"Method {method_name} is not an operation of {name}")

            # Create a new version of send_request_impl for each method_name:
            attrs[method_name] = functools.partialmethod(
                call_remote_operation_impl, method, in_struct
            )

        return super().__new__(cls, name, bases, attrs)


class FailedRequestCollector:
    def __init__(self, requester: Requester, max_size: int):
        self.requester = requester
        self.max_size = max_size
        self.failed_requests = []

    def add_failed_request(self, request_id: dds.SampleIdentity):
        self.purge()

        self.failed_requests.append(request_id)
        if len(self.failed_requests) >= self.max_size:
            self.failed_requests.pop(0)

    def purge(self):
        for request_id in self.failed_requests:
            samples = self.requester.take_replies(request_id)
            if len(samples) > 0:
                self.failed_requests.remove(request_id)


class ClientBase(ABC, metaclass=_ClientMeta):
    """Base class for RPC clients.

    An actual Client must inherit from a service interface and from this class,
    for example:

    ```
    class RobotClient(Robot, rpc.ClientBase): ...
    ```

    This base class injects an implementation for all the @operation methods
    found in Robot, which uses a Requester to make RPC calls and
    return the values it receives.

    The base class also provides an __init__, close and other methods.
    """

    def __init__(
        self,
        participant: dds.DomainParticipant,
        service_name: str,
        max_wait_per_call: dds.Duration = dds.Duration(10),
        datawriter_qos: Optional[dds.DataWriterQos] = None,
        datareader_qos: Optional[dds.DataReaderQos] = None,
        publisher: Optional[dds.Publisher] = None,
        subscriber: Optional[dds.Subscriber] = None,
        require_matching_service_on_send_request: bool = True,
    ) -> None:
        """Creates the DDS entities needed by this client using the given
        participant and service name.

        The ``max_wait_per_call`` is an optional argument that allows configuring
        how much a client will wait for a return value before timing out. The
        default is 10 seconds. Note that the tasks returned by client operations
        can also be cancelled by the application, so a large maximum wait
        (even ``dds.Duration.infinite``) can also be set.

        The rest of optional arguments are used to create the underlying
        ``Requester``.
        """
        self.requester = Requester(
            type(self).call_type,
            type(self).return_type,
            participant=participant,
            service_name=service_name,
            datawriter_qos=datawriter_qos,
            datareader_qos=datareader_qos,
            publisher=publisher,
            subscriber=subscriber,
            require_matching_service_on_send_request=require_matching_service_on_send_request,
        )
        self.max_wait_per_call = max_wait_per_call
        self.failed_request_collector = FailedRequestCollector(self.requester, 200)

    def close(self):
        """Closes the DDS entities used by this client."""
        self.requester.close()

    async def wait_for_service_async(self, max_wait: dds.Duration) -> bool:
        """Waits for a service to be discovered.

        This method returns True if a service is discovered and
        ready to receive requests within the specified maximum wait. It
        returns False if it times out.
        """
        return await self.requester.wait_for_service_async(max_wait)

    @property
    def matched_service_count(self) -> int:
        """The number of RPC services that match this client."""
        return self.requester.matched_replier_count


def _create_return_reply(
    cls: type, operation_id: int, operation_result: Any, is_exception: bool = False
):
    """Creates a reply for a given operation id, and return value."""

    return_value = cls.return_type()
    return_value.discriminator = operation_id

    if operation_id == 0:
        # Replying to a request for an unknown operation (discriminator set to remoteEx)
        return_value.value = exceptions.RemoteExceptionCode.UNKNOWN_OPERATION.value
        return return_value

    result_union = cls.return_type.result_unions[operation_id][1]
    if is_exception:
        if not isinstance(operation_result, tuple(result_union.raises)):
            # Return a built-in RPC exception when the exception type is not
            # declared in the interface
            return_value.discriminator = 0  # selects the remoteEx member
            return_value.value = exceptions.get_remote_ex_code_from_ex(operation_result)
            return return_value

        # Throw an exception declared in the interface
        ex_field = f"{type(operation_result).__name__}_ex".lower()
        result = result_union()
        setattr(result, ex_field, operation_result)

    else:
        # Regular non-exception result
        if operation_result is not None:
            result = result_union(result=result_union.out_struct(**operation_result))
        else:
            result = result_union(result=result_union.out_struct())

    return_value.value = result
    return return_value


class Service:
    """A service allows running a service_instance in a DDS domain using asyncio.

    The service useses a Replier to receive RPC calls and then dispatches them
    to the service_instance, calling the appropriate method. The value returned
    by the method is then sent back to the remote caller.

    The service runs asynchronously (run method) until the task is cancelled.
    """

    def __init__(
        self,
        service_instance: ABC,
        participant: dds.DomainParticipant,
        service_name: str,
        task_count: int = 4,
        datawriter_qos: Optional[dds.DataWriterQos] = None,
        datareader_qos: Optional[dds.DataReaderQos] = None,
        publisher: Optional[dds.Publisher] = None,
        subscriber: Optional[dds.Subscriber] = None,
    ) -> None:
        """Creates a new service for a service_instance in a DDS domain.

        The ``task_count`` is an optional argument that allows setting the number
        of tasks that will be used to process the requests. The default is 4.

        The rest of optional arguments are used to create the underlying
        ``Replier``.
        """

        if not hasattr(service_instance, "call_type"):
            raise TypeError("service_instance is not a @service interface")

        self.service_instance = service_instance
        self.service_interface = type(service_instance)
        self.in_structs = self.service_interface.call_type.in_structs
        self.result_unions = self.service_interface.return_type.result_unions
        self.task_count = task_count
        self.queue = asyncio.Queue(task_count * 4)
        self.replier = Replier(
            request_type=self.service_interface.call_type,
            reply_type=self.service_interface.return_type,
            participant=participant,
            service_name=service_name,
            datawriter_qos=datawriter_qos,
            datareader_qos=datareader_qos,
            publisher=publisher,
            subscriber=subscriber,
        )
        self.running = False

    async def _read_requests(self):
        """Reads requests from the replier and puts them in self.queue for
        _process_requests to process.

        When the queue is full, this method awaits until there is space and
        stops reading data from the DataReader.
        """

        async for request_sample in self.replier.request_datareader.take_async():
            if not request_sample.info.valid:
                continue

            await self.queue.put(request_sample)

    async def _process_requests(self):
        """Retrieves the requests from self.queue, calls the corresponding operation
        on the service_instance and sends the return value as a reply.
        """

        while self.running:
            operation_name = None
            operation_id = 0
            request_sample = await self.queue.get()

            try:
                request = request_sample.data
                operation_id = request.discriminator
                operation = self.in_structs.get(operation_id)
                if operation is not None:
                    operation_name = self.in_structs[operation_id][0]
                    operation = getattr(self.service_interface, operation_name)

                    out_struct = self.result_unions[operation_id][1].out_struct
                    # Unpack the in_struct dataclass fields in a list
                    kargs = _in_struct_to_arguments(
                        operation, request.value, out_struct
                    )

                    try:
                        # Call the operation on the service instance with the
                        # unpacked parameters
                        result = operation(self.service_instance, **kargs)
                        if inspect.isawaitable(result):
                            result = await result

                        out_parameters = _arguments_to_out_struct(
                            out_struct, kargs, result
                        )

                        # Create a return reply with the value returned by the
                        # operation on the service instance
                        reply = _create_return_reply(
                            self.service_interface, operation_id, out_parameters
                        )
                    except Exception as e:
                        # If the operation raises an exception, create a return
                        # reply with the exception
                        reply = _create_return_reply(
                            self.service_interface, operation_id, e, is_exception=True
                        )
                else:
                    reply = _create_return_reply(
                        self.service_interface, operation_id=0, operation_result=None
                    )

                # Send the reply containing the return value or an exception to
                # the client (requester)
                self.replier.send_reply(reply, request_sample.info)

            except Exception as e1:
                msg = (
                    f"Exception while processing {self.service_interface.__name__}.{operation_name}: {e1}"
                    if operation_name is not None
                    else f"Exception in {self.service_interface.__name__}: {e1}"
                )
                dds.Logger.instance.error(msg)

                # Send a reply with an exception to the client, if we haven't
                # been able to serialize the reply, so the client doesn't hang
                try:
                    reply = _create_return_reply(
                        self.service_interface,
                        operation_id,
                        operation_result=exceptions.RemoteUnknownExceptionError(),
                        is_exception=True,
                    )
                    self.replier.send_reply(reply, request_sample.info)
                except Exception as e2:
                    msg = (
                        f"Exception while replying with RemoteUnknownExceptionError for {self.service_interface.__name__}.{operation_name}: {e2}"
                        if operation_name is not None
                        else f"Exception while replying with RemoteUnknownExceptionError in {self.service_interface.__name__}: {e2}"
                    )
                    dds.Logger.instance.error(msg)
            finally:
                self.queue.task_done()

    async def run(self, close_on_cancel: bool = False):
        """Starts receiving RPC calls (requests) and processing them.

        This method runs until the task it returns is cancelled.

        If close_on_cancel is True, the service will close the DDS entities when
        the task is canceled. By default it is False, which means you can call
        run() again after a run() task is cancelled.

        Exceptions raised during the execution of the service are logged as
        warnings module and do not stop the execution of the service.
        """
        if self.replier.closed:
            raise dds.AlreadyClosedError()

        self.running = True
        try:
            # Run the task that reads requests and as many tasks to process
            # (call the service_instance methods) as specified by task_count
            await asyncio.gather(
                self._read_requests(),
                *(self._process_requests() for _ in range(self.task_count)),
            )
        except asyncio.CancelledError:
            pass  # Cancellation is the expected way to stop the service
        finally:
            self.running = False
            if close_on_cancel:
                self.close()

    def close(self):
        """Closes the DDS entities used by this service."""

        if self.running:
            raise dds.PreconditionNotMetError(
                "Cannot close a running service. Cancel the run() task first."
            )

        self.replier.close()

    @property
    def matched_client_count(self) -> int:
        """The number of RPC clients that match this service."""
        return self.replier.matched_requester_count


def get_interface_types(interface: type) -> List[type]:
    """Returns a list of all the IDL types used by this interface (call, return, in, out, result)"""

    types = [interface.call_type, interface.return_type]

    for operation in interface.call_type.in_structs.values():
        types.append(operation[1])

    for operation in interface.return_type.result_unions.values():
        types.append(operation[1])
        types.append(operation[1].out_struct)

    return types


def print_interface_idl_types(interface: type):
    """Prints the IDL types used by this interface (call, return, in, out, result)"""

    for type in get_interface_types(interface):
        print(idl.get_type_support(type).dynamic_type)
