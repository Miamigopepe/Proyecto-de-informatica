# kml_generator.py

def generate_kml_header():
    return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://www.opengis.net/kml/2.2\">
  <Document>"""

def generate_kml_footer():
    return """  </Document>
</kml>"""

def generate_kml_point(name, lon, lat):
    return f"""
    <Placemark>
      <name>{name}</name>
      <Point>
        <coordinates>{lon},{lat}</coordinates>
      </Point>
    </Placemark>"""

def generate_kml_line(name, coordinates):
    coords_str = "\n        ".join([f"{lon},{lat}" for lon, lat in coordinates])
    return f"""
    <Placemark>
      <name>{name}</name>
      <LineString>
        <coordinates>
        {coords_str}
        </coordinates>
      </LineString>
    </Placemark>"""

def export_navpoints_to_kml(navpoints, filename):
    with open(filename, 'w') as f:
        f.write(generate_kml_header())
        for np in navpoints:
            f.write(generate_kml_point(np.name, np.longitude, np.latitude))
        f.write(generate_kml_footer())

def export_path_to_kml(path_nodes, filename):
    with open(filename, 'w') as f:
        f.write(generate_kml_header())
        coords = [(n.longitude, n.latitude) for n in path_nodes]  # <-- ya es una lista
        f.write(generate_kml_line("Ruta más corta", coords))
        f.write(generate_kml_footer())

