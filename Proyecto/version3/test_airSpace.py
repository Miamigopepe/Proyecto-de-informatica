import airSpace


def test_airspace_loading():
    airspace = airSpace.AirSpace()
    airspace.load_airspace_data("data/Cat_nav.txt", "data/Cat_seg.txt", "data/Cat_aer.txt")

    # Verificar que se cargaron datos
    assert len(airspace.NavPoints) > 0
    assert len(airspace.NavSegments) > 0
    assert len(airspace.NavAirports) > 0

    # Probar funcionalidades
    neighbors = airspace.get_neighbors(6063)  # IZA.D
    assert len(neighbors) > 0

    print("All tests passed!")


if __name__ == "__main__":
    test_airspace_loading()