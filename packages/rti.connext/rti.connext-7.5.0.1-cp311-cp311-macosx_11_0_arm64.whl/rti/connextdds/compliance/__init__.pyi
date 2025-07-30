"""rti.connextdds.compliance contains APIs to configure compliance with certain standard specifications."""
import rti.connextdds.compliance
import typing
import builtins

class RpcMask():
    def __and__(self, arg0: rti.connextdds.compliance.RpcMask) -> rti.connextdds.compliance.RpcMask: 
        """
        Bitwise logical AND of masks.
        """
    def __bool__(self) -> bool: 
        """
        Test if any bits are set.
        """
    def __contains__(self, arg0: rti.connextdds.compliance.RpcMask) -> bool: ...
    def __eq__(self, arg0: rti.connextdds.compliance.RpcMask) -> bool: 
        """
        Compare masks for equality.
        """
    def __getitem__(self, arg0: int) -> bool: 
        """
        Get individual mask bit.
        """
    def __iand__(self, arg0: rti.connextdds.compliance.RpcMask) -> rti.connextdds.compliance.RpcMask: 
        """
        Set mask to logical AND with another mask.
        """
    def __ilshift__(self, arg0: int) -> rti.connextdds.compliance.RpcMask: 
        """
        Left shift bits in mask.
        """
    @typing.overload
    def __init__(self) -> None: 
        """
        Create an RpcMask with no bits set.
        """
    @typing.overload
    def __init__(self, value: int) -> None: 
        """
        Creates a mask from the bits in an integer.
        """
    def __int__(self) -> int: 
        """
        Convert mask to int.
        """
    def __ior__(self, arg0: rti.connextdds.compliance.RpcMask) -> rti.connextdds.compliance.RpcMask: 
        """
        Set mask to logical OR with another mask.
        """
    def __irshift__(self, arg0: int) -> rti.connextdds.compliance.RpcMask: 
        """
        Right shift bits in mask.
        """
    def __ixor__(self, arg0: rti.connextdds.compliance.RpcMask) -> rti.connextdds.compliance.RpcMask: 
        """
        Set mask to logical XOR with another mask.
        """
    def __lshift__(self, arg0: int) -> rti.connextdds.compliance.RpcMask: 
        """
        Left shift bits in mask.
        """
    def __ne__(self, arg0: rti.connextdds.compliance.RpcMask) -> bool: 
        """
        Compare masks for inequality.
        """
    def __or__(self, arg0: rti.connextdds.compliance.RpcMask) -> rti.connextdds.compliance.RpcMask: 
        """
        Bitwise logical OR of masks.
        """
    def __repr__(self) -> str: 
        """
        Convert mask to string.
        """
    def __rshift__(self, arg0: int) -> rti.connextdds.compliance.RpcMask: 
        """
        Right shift bits in mask.
        """
    def __setitem__(self, arg0: int, arg1: bool) -> None: 
        """
        Set individual mask bit
        """
    def __str__(self) -> str: 
        """
        Convert mask to string.
        """
    def __xor__(self, arg0: rti.connextdds.compliance.RpcMask) -> rti.connextdds.compliance.RpcMask: 
        """
        Bitwise logical XOR of masks.
        """
    @typing.overload
    def flip(self) -> rti.connextdds.compliance.RpcMask: 
        """
        Flip all bits in the mask.
        """
    @typing.overload
    def flip(self, pos: int) -> rti.connextdds.compliance.RpcMask: 
        """
        Flip the mask bit at the specified position.
        """
    @typing.overload
    def reset(self) -> rti.connextdds.compliance.RpcMask: 
        """
        Clear all bits in the mask.
        """
    @typing.overload
    def reset(self, pos: int) -> rti.connextdds.compliance.RpcMask: 
        """
        Clear the mask bit at the specified position.
        """
    @typing.overload
    def set(self) -> rti.connextdds.compliance.RpcMask: 
        """
        Set all bits in the mask.
        """
    @typing.overload
    def set(self, pos: int, value: bool = True) -> rti.connextdds.compliance.RpcMask: 
        """
        Set the mask bit at the specified position to the provided value (default: true).
        """
    def test(self, pos: int) -> bool: 
        """
        Test whether the mask bit at position "pos" is set.
        """
    def test_all(self) -> bool: 
        """
        Test if all bits are set.
        """
    def test_any(self) -> bool: 
        """
        Test if any bits are set.
        """
    def test_none(self) -> bool: 
        """
        Test if none of the bits are set.
        """
    @builtins.property
    def count(self) -> int:
        """
        Returns the number of bits set in the mask.

        :type: int
        """
    @builtins.property
    def size(self) -> int:
        """
        Returns the number of bits in the mask type.

        :type: int
        """
    DEFAULT_MASK: rti.connextdds.compliance.RpcMask
    USE_STANDARD_RELATED_SAMPLE_PID_BIT: rti.connextdds.compliance.RpcMask
    VENDOR: rti.connextdds.compliance.RpcMask
    __hash__: NoneType
    pass
def get_rpc_mask() -> rti.connextdds.compliance.RpcMask:
    """
    Gets the RPC compliance mask value for the application.
    """
def load_compliance_mask() -> None:
    """
    Load the compliance masks from the environment variables.
    """
def set_rpc_mask(mask: rti.connextdds.compliance.RpcMask) -> None:
    """
    Sets the level of compliance of the application with the Rpc specification.
    """
