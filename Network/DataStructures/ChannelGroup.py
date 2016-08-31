class ChannelGroup:

    def __init__(self, id):
        self.id = id

    def setProperties(self, switchportMode, interfaces, uvlan, tvlans):
        self.mode = switchportMode
        self.interfaces = interfaces
        self.uVlan = uvlan
        self.tVlans = tvlans

    def getMode(self):
        return self.mode

    def getInterfaces(self):
        return self.interfaces

    def getUVlan(self):
        return self.uVlan

    def getTVlans(self):
        return self.tVlans