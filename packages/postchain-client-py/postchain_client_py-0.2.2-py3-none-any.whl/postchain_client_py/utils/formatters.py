from typing import Any, Dict, Union, List, Tuple, TYPE_CHECKING
import binascii
from .gtv import encode_value, gtv_auto

# Import QueryObject only for type checking to avoid circular imports
if TYPE_CHECKING:
    from ..blockchain_client.types import QueryObject

def to_buffer(hex_str: str) -> bytes:
    """Convert hex string to bytes"""
    return binascii.unhexlify(hex_str)

def to_string(buffer: bytes, encoding: str = 'hex') -> str:
    """Convert bytes to string"""
    if encoding == 'hex':
        return binascii.hexlify(buffer).decode('ascii').upper()
    return buffer.decode(encoding)

def to_query_object(name_or_query_object: Union[str, Dict[str, Any], 'QueryObject'], query_arguments: Dict[str, Any] = None) -> bytes:
    """
    Convert a query name/arguments or query object into a GTV-compatible format.
    
    This matches the JavaScript implementation:
    export type QueryObjectGTV = [name: string, args: Arg];
    export function toQueryObjectGTV(
      nameOrObject: string | QueryObject,
      queryArguments?: DictPair,
    ): QueryObjectGTV {
      let name;
      if (typeof nameOrObject === "string") {
        name = nameOrObject;
        return [name, { ...queryArguments }];
      } else {
        const objectCopy = { ...nameOrObject };
        const { type, ...restProps } = objectCopy;
        return [type, restProps];
      }
    }
    
    Args:
        name_or_query_object: Either a string query name, a query object dict, or a QueryObject instance
        query_arguments: Optional dictionary of query arguments
    
    Returns:
        Bytes containing the GTV-encoded query
    """
    if isinstance(name_or_query_object, str):
        # If it's a string, use it as the name and the arguments as the second element
        query_tuple = [name_or_query_object, query_arguments or {}]
    elif hasattr(name_or_query_object, '__class__') and name_or_query_object.__class__.__name__ == 'QueryObject':
        # Check for QueryObject by class name to avoid import issues, but still be type-safe
        if not (hasattr(name_or_query_object, 'name') and hasattr(name_or_query_object, 'args')):
            raise TypeError("QueryObject must have 'name' and 'args' attributes")
        query_tuple = [name_or_query_object.name, name_or_query_object.args]
    elif isinstance(name_or_query_object, dict):
        # If it's a dict, extract the 'name' or 'type' as the query name and the rest as arguments
        query_dict = name_or_query_object.copy()
        
        # Try to get 'name' first, then fall back to 'type' for backward compatibility
        query_name = query_dict.pop('name', None)
        if query_name is None:
            query_name = query_dict.pop('type', None)
            if query_name is None:
                raise ValueError("Query object must have a 'name' or 'type' field")
        
        query_tuple = [query_name, query_dict]
    else:
        # Handle any other object that might have the right structure
        raise TypeError(f"Invalid query object type: {type(name_or_query_object)}. Expected string, dict, or QueryObject instance.")
    
    # Convert to GTV format and encode
    gtv_value = gtv_auto(query_tuple)
    return encode_value(gtv_value)