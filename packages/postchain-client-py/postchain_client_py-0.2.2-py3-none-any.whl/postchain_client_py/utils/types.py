from typing import Any, Union, Optional


class BigInt:
    """
    A wrapper class for Python integers to be explicitly serialized as gtv_bigint.
    
    This allows users to specify when they want to use a BigInt type, 
    even for values that would fit in a regular int range.
    
    Usage:
        from postchain_client_py.utils import BigInt
        
        # Create a BigInt
        big_value = BigInt(12345)
        
        # Use in operation
        client.create_operation("my_op", [big_value])
    """
    
    def __init__(self, value: Union[int, str, "BigInt"]):
        """
        Initialize with an integer value or string representation of an integer.
        
        Args:
            value: Integer value or string representation of an integer
        """
        if isinstance(value, BigInt):
            self.value = value.value
        elif isinstance(value, str):
            try:
                self.value = int(value)
            except ValueError:
                raise ValueError(f"Invalid string for BigInt: {value}")
        elif isinstance(value, int):
            self.value = value
        else:
            raise TypeError(f"BigInt requires int or str, got {type(value).__name__}")
    
    def __repr__(self) -> str:
        return f"BigInt({self.value})"
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __int__(self) -> int:
        return self.value
    
    # Basic comparison operators
    def __eq__(self, other) -> bool:
        if isinstance(other, BigInt):
            return self.value == other.value
        elif isinstance(other, (int, str)):
            return self.value == BigInt(other).value
        return False
    
    def __lt__(self, other) -> bool:
        if isinstance(other, BigInt):
            return self.value < other.value
        return self.value < int(other)
    
    def __gt__(self, other) -> bool:
        if isinstance(other, BigInt):
            return self.value > other.value
        return self.value > int(other)
    
    # Basic arithmetic operations
    def __add__(self, other):
        if isinstance(other, BigInt):
            return BigInt(self.value + other.value)
        return BigInt(self.value + int(other))
    
    def __sub__(self, other):
        if isinstance(other, BigInt):
            return BigInt(self.value - other.value)
        return BigInt(self.value - int(other))
    
    def __mul__(self, other):
        if isinstance(other, BigInt):
            return BigInt(self.value * other.value)
        return BigInt(self.value * int(other))
    
    def __truediv__(self, other):
        if isinstance(other, BigInt):
            return BigInt(self.value // other.value)
        return BigInt(self.value // int(other))
    
    # Hash function for use in dictionaries, etc.
    def __hash__(self) -> int:
        return hash(self.value) 