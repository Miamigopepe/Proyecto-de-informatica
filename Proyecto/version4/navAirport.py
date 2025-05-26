class NavAirport:
    def __init__(self, name):
        self.name = name
        self.SIDs = []
        self.STARs = []
        self.coordinates = None

    def addSid(self, SIDs):
        self.SIDs.append(SIDs)

    def addSTARs(self, STARs):
        self.STARs.append(STARs)

def __str__(self):
    return f"Airport {self.name} - SIDs: {len(self.SIDs)}, STARs: {len(self.STARs)}"