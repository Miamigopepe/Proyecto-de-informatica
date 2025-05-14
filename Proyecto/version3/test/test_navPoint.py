from navPoint import NavPoint


def test_nav_point():
    print("Testing NavPoint class...")

    # Create two navigation points
    point1 = NavPoint(1, "GIR", 41.9313888889, 2.7716666667)
    point2 = NavPoint(2, "GODOX", 39.3725, 1.4108333333)

    # Test distance calculation
    distance = point1.longitude - point2.longitude
    print(f"Distance between {point1.name} and {point2.name}: {distance:.2f} km")

    # Test adding neighbors
    result = point1.add_neighbor(point2)
    print(f"Added neighbor: {result}")  # Should be True
    result = point1.add_neighbor(point2)
    print(f"Added same neighbor again: {result}")  # Should be False

    print("NavPoint tests completed.")


if __name__ == "__main__":
    test_nav_point()
