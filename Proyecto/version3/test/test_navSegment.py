from navSegment import NavSegment


def test_nav_segment():
    print("Testing NavSegment class...")

    # Create a segment
    segment = NavSegment(4954, 5129, 109.631114)

    print(f"Segment from {segment.origin} to {segment.destination}")
    print(f"Distance: {segment.distance} km")

    print("NavSegment tests completed.")


if __name__ == "__main__":
    test_nav_segment()
