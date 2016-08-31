class Device:

    def __init__(self, name, ipaddress):
        self.name = name
        self.ipaddress = ipaddress
        self.ifaces = []
        self.vlans = []

    '''
        Setters
    '''

    def setDeviceProperties(self, model, firmVersion, serviceTag, serial, mac):
        self.model = model
        self.firmVersion = firmVersion
        self.serviceTag = serviceTag
        self.serial = serial
        self.mac = mac

    def setInterfaces(self, ifs):
        self.ifaces = ifs

    def setVlans(self, vlans):
        self.vlans = vlans

    def setModel(self, model):
        self.model = model

    def setFirmVersion(self, firmVersion):
        self.firmVersion = firmVersion

    def setServiceTag(self, st):
        self.serviceTag = st

    def setSerial(self, serial):
        self.serial = serial

    def setMac(self, mac):
        self.mac = mac

    '''
        Getters
    '''

    def getName(self):
        return self.name

    def getVlans(self):
        return self.vlans

    '''
        Operations
    '''
    def ifaceOnList(self, ifaceID):
        for iface in self.ifaces:
            if iface.id == ifaceID:
                return True
        return False

    def getIface(self, ifaceID):
        for iface in self.ifaces:
            if iface.id == ifaceID:
                return iface
        print ("@device.getIface -> Interface " + iface.id + " was not found!")

    def addVlan(self, vlan):
        self.vlans.append(vlan)
        # order vlan list again
        print "Vlan " + vlan.id + "added with success !"

    def removeVlan(self, vlan):
        self.vlans.remove(vlan)
        # order vlan list again
        print "Vlan " + vlan.id + "removed with success !"

    def addPortChannel(self, channelGroup):
        self.channelGroups.append(channelGroup)
        # Order channel group for id
        print "Channel Group " + channelGroup.id + "added with success !"


    def addInterface(self, iface):
        self.ifaces.append(iface)
        # order interface list again
        print "Interface " + iface.name + "added with success !"

    def removeInterface(self, iface):
        self.IFs.remove(iface)
        print "Interface " + iface.name + "removed with success !"

    def removePortChannel(self, channelGroup):
        self.channelGroups.remove(channelGroup)
        print "Channel Group " + channelGroup.id + "removed with success !"

    def toString(self):
        print ("Device: "+ self.name + " IP Address: "+ self.ipaddress + " Model: "+ self.model + "\nMAC Address "+ self.mac + "Service Tag: "+self.serviceTag + \
               " Serial Number: " + self.serial + " Firmware Version: " + self.firmVersion )
        print("\n\tVlan:\tName\tIP Address\n")
        print("-----------------------------------------------------------------------")
        for vlan in self.vlans:
            print("\t" + vlan.toString())
        print("\n\tID\tMode\t\tVlans\t\n")
        print("-----------------------------------------------------------------------------------------------------")
        for iface in self.ifaces:
            print("\t" + iface.toString())