# test_kml_generator.py

from kml_generator import export_navpoints_to_kml, export_path_to_kml

class DummyNavPoint:
    def __init__(self, name, lat, lon):
        self.name = name
        self.latitude = lat
        self.longitude = lon

def test_navpoints_export():
    points = [
        DummyNavPoint("A", 41.4, 2.1),
        DummyNavPoint("B", 41.5, 2.2),
    ]
    export_navpoints_to_kml(points, "test_navpoints.kml")
    print("✔ test_navpoints.kml generado.")

def test_path_export():
    path = [
        DummyNavPoint("A", 41.4, 2.1),
        DummyNavPoint("B", 41.5, 2.2),
    ]
    export_path_to_kml(path, "test_path.kml")
    print("✔ test_path.kml generado.")

if __name__ == "__main__":
    test_navpoints_export()
    test_path_export()

