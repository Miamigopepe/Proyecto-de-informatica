from navAirport import NavAirport
from navPoint import NavPoint


def test_nav_airport():
    print("Testing NavAirport class...")

    # Create an airport
    airport = NavAirport("LEBL")

    # Create some navigation points
    sid_point = NavPoint(6063, "IZA.D", 38.8711546833, 1.37242975)
    star_point = NavPoint(6062, "IZA.A", 38.8772804833, 1.36930455)

    # Add SIDs and STARs
    airport.addSid(sid_point)
    airport.addSTARs(star_point)

    print(f"Airport: {airport.name}")
    print(f"SIDs: {[p.name for p in airport.SIDs]}")
    print(f"STARs: {[p.name for p in airport.STARs]}")

    print("NavAirport tests completed.")


if __name__ == "__main__":
    test_nav_airport()
