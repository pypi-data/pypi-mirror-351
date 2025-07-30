import hashlib
from typing import List, Any, Tuple, Union, Dict
from .gtv import GTV, encode_value, gtv_auto, GTVType

# Hash prefix constants
HASH_PREFIX_LEAF = 1
HASH_PREFIX_NODE = 0 
HASH_PREFIX_NODE_ARRAY = 7
HASH_PREFIX_NODE_DICT = 8

def sha256(data: bytes) -> bytes:
    """Calculate SHA256 hash of data"""
    return hashlib.sha256(data).digest()

class CryptoSystem:
    """Simple crypto system for hashing"""
    def digest(self, buffer: bytes) -> bytes:
        return sha256(buffer)

class BinaryTreeElement:
    """Base class for tree elements"""
    pass

class Node(BinaryTreeElement):
    """Represents an internal node in the Merkle tree"""
    def __init__(self, left: BinaryTreeElement, right: BinaryTreeElement):
        self.left = left
        self.right = right

class Leaf(BinaryTreeElement):
    """Represents a leaf node containing a GTV value"""
    def __init__(self, content: GTV):
        self.content = content

class EmptyLeaf(BinaryTreeElement):
    """Represents an empty leaf node"""
    pass

class ContainerNode(Node):
    """Base class for container nodes"""
    def __init__(self, left: BinaryTreeElement, right: BinaryTreeElement, content: Any, size: int):
        super().__init__(left, right)
        self.content = content
        self.size = size

class ArrayHeadNode(ContainerNode):
    """Special node type for array containers"""
    pass

class DictHeadNode(ContainerNode):
    """Special node type for dictionary containers"""
    pass

class BinaryTreeFactory:
    """Factory for creating binary trees from GTV values"""
    
    @staticmethod
    def build_higher_layer(elements: List[BinaryTreeElement]) -> BinaryTreeElement:
        """Build the next layer of the tree from a list of elements"""
        if not elements:
            raise ValueError("Cannot work on empty arrays")
        if len(elements) == 1:
            return elements[0]
            
        result = []
        i = 0
        while i < len(elements) - 1:
            result.append(Node(elements[i], elements[i + 1]))
            i += 2
            
        # Handle odd number of elements    
        if i < len(elements):
            result.append(elements[i])
            
        return BinaryTreeFactory.build_higher_layer(result)

    @staticmethod
    def handle_array_container(items: List[Any]) -> BinaryTreeElement:
        """Build a tree from array items"""
        if not items:
            return ArrayHeadNode(EmptyLeaf(), EmptyLeaf(), [], 0)

        # Build leaves recursively
        leaves = []
        for item in items:
            leaves.append(BinaryTreeFactory.build_tree(item))

        if len(leaves) == 1:
            # Single item case - leaf becomes left, right is empty
            return ArrayHeadNode(leaves[0], EmptyLeaf(), items, len(items))
            
        # Build tree structure for multiple items
        tree_root = BinaryTreeFactory.build_higher_layer(leaves)
        
        # If tree_root is a Node, use its left/right directly
        if isinstance(tree_root, Node):
            return ArrayHeadNode(tree_root.left, tree_root.right, items, len(items))
        # If tree_root is a Leaf, it becomes the left child
        return ArrayHeadNode(tree_root, EmptyLeaf(), items, len(items))

    @staticmethod
    def handle_dict_container(items: List[Tuple[str, GTV]]) -> BinaryTreeElement:
        """Build a tree from dictionary items"""
        if not items:
            return DictHeadNode(EmptyLeaf(), EmptyLeaf(), [], 0)

        # Build leaves recursively
        leaves = []
        for key, value in items:
            leaves.append(Leaf(gtv_auto(key)))
            leaves.append(BinaryTreeFactory.build_tree(value))

        if len(leaves) == 2:  # Single key-value pair
            return DictHeadNode(leaves[0], leaves[1], items, len(items))
            
        # Build tree structure
        tree_root = BinaryTreeFactory.build_higher_layer(leaves)
        
        # If tree_root is a Node, use its left/right directly
        if isinstance(tree_root, Node):
            return DictHeadNode(tree_root.left, tree_root.right, items, len(items))
        # If tree_root is a Leaf, it becomes the left child
        return DictHeadNode(tree_root, EmptyLeaf(), items, len(items))

    @staticmethod 
    def build_tree(value: Union[GTV, Any]) -> BinaryTreeElement:
        """Build tree elements from a GTV value"""
        if not isinstance(value, GTV):
            value = gtv_auto(value)
            
        # Handle container types recursively    
        if value.type == GTVType.ARRAY:
            return BinaryTreeFactory.handle_array_container(value.value)
        elif value.type == GTVType.DICT:
            return BinaryTreeFactory.handle_dict_container(value.value)
        else:
            return Leaf(value)

class MerkleHashCalculator:
    """Calculates Merkle tree hashes with support for nested structures"""
    def __init__(self, crypto_system: CryptoSystem):
        self.crypto_system = crypto_system

    def calculate_node_hash(self, prefix: int, hash_left: bytes, hash_right: bytes) -> bytes:
        """Calculate hash of an internal node"""
        buffer_sum = bytes([prefix]) + hash_left + hash_right
        return self.crypto_system.digest(buffer_sum)

    def calculate_leaf_hash(self, value: GTV) -> bytes:
        """Calculate hash of a leaf node"""
        buffer_sum = bytes([HASH_PREFIX_LEAF]) + encode_value(value)
        return self.crypto_system.digest(buffer_sum)

    def calculate_merkle_hash(self, element: BinaryTreeElement) -> bytes:
        """Calculate Merkle hash recursively for any tree element"""
        if isinstance(element, EmptyLeaf):
            return bytes(32)
        
        if isinstance(element, Leaf):
            return self.calculate_leaf_hash(element.content)

        # Get hash prefix based on node type
        if isinstance(element, ArrayHeadNode):
            prefix = HASH_PREFIX_NODE_ARRAY
        elif isinstance(element, DictHeadNode):
            prefix = HASH_PREFIX_NODE_DICT
        else:
            prefix = HASH_PREFIX_NODE

        return self.calculate_node_hash(
            prefix,
            self.calculate_merkle_hash(element.left),
            self.calculate_merkle_hash(element.right)
        )

def gtv_hash(value: Union[GTV, Any]) -> bytes:
    """Calculate the GTV hash of a value"""
    if not isinstance(value, GTV):
        value = gtv_auto(value)

    calculator = MerkleHashCalculator(CryptoSystem())    
    tree = BinaryTreeFactory.build_tree(value)
        
    return calculator.calculate_merkle_hash(tree)