from path import Path
from node import Node


def test_path_operations():
    print("=== Testing Path Operations ===")

    # Create test nodes
    nodeA = Node("A", 0, 0)
    nodeB = Node("B", 3, 4)
    nodeC = Node("C", 6, 8)

    # Test empty path
    path = Path()
    print("\nEmpty path:")
    print(f"Path: {path}")
    print(f"Contains A: {path.contains_node(nodeA)}")
    print(f"Cost to A: {path.cost_to_node(nodeA)}")

    # Test path with one node
    path.add_node(nodeA)
    print("\nPath with one node:")
    print(f"Path: {path}")
    print(f"Contains A: {path.contains_node(nodeA)}")
    print(f"Cost to A: {path.cost_to_node(nodeA)}")
    print(f"Contains B: {path.contains_node(nodeB)}")

    # Test path with multiple nodes
    path.add_node(nodeB)
    path.add_node(nodeC)
    print("\nPath with multiple nodes:")
    print(f"Path: {path}")
    print(f"Contains B: {path.contains_node(nodeB)}")
    print(f"Cost to B: {path.cost_to_node(nodeB)}")
    print(f"Cost to C: {path.cost_to_node(nodeC)}")

    # Test path copying
    path_copy = path.copy()
    print("\nCopied path:")
    print(f"Original: {path}")
    print(f"Copy: {path_copy}")
    print(f"Equal: {path.nodes == path_copy.nodes and path.cost == path_copy.cost}")

    # Test non-existent node
    nodeD = Node("D", 10, 10)
    print("\nTesting with non-existent node:")
    print(f"Contains D: {path.contains_node(nodeD)}")
    print(f"Cost to D: {path.cost_to_node(nodeD)}")


if __name__ == "__main__":
    test_path_operations()