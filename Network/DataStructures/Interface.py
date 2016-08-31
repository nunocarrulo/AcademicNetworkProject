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

    def getIfaceDesc(self):
        return self.description

    def toString(self):
        print(self.id + "\t"+self.mode+"\t"+self.vlans)