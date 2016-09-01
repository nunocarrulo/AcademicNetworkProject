from termcolor import colored

class Interface:

    def __init__(self, id):
        self.id = id
        self.status = 0
        self.mode = 'A'
        self.vlans = '(1)'
        self.channelGroup = 0   # no channel group
        self.description = ''

    def setProperties(self, switchportMode, status, vlans):
        self.mode = switchportMode
        self.status = status
        self.vlans = vlans
        #self.uVlan = uVlan
        #self.tVlans = tVlans

    def setStatus(self, status):
        self.status = status

    def setVlans(self,vlans):
        self.vlans = vlans

    def setMode(self,mode):
        self.mode = mode

    def setIfaceDescription(self, ifaceDesc):
        self.description = ifaceDesc

    def setChannelGroup(self, cgID):
        self.channelGroup = cgID

    def removeChannelGroup(self):
        self.channelGroup = 0

    '''
    def setUVlan(self, uvlan):
        self.uVlan = uvlan

    def setTVlans(self, tvlans):
        self.tVlans = tvlans
    '''
    '''
        Create getters if necessary
    '''
    def getID(self):
        return self.id

    def getStatus(self):
        return self.status

    def getVlans(self):
        return self.vlans

    def getMode(self, mode):
        return self.mode

    def getIfaceDesc(self):
        return self.description

    def toString(self):
        return (self.id + "\tDescription"+self.description+"\t"+self.mode+"\t"+self.vlans)