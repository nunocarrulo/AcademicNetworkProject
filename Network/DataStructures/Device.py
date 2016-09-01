from termcolor import colored

class Device:

    def __init__(self, name, ipaddress):
        self.name = name
        self.ipaddress = ipaddress
        self.ifaces = []
        self.vlans = []
        self.mac = ''
        self.serviceTag = ''
        self.firmVersion = ''
        self.serial = ''
        self.model = ''
        self.debug = False

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

    def setDebug(self, debug):
        self.debug = debug

    '''
        Getters
    '''

    def getVlans(self):
        return self.vlans

    def getModel(self):
        return self.model

    def getFirmVersion(self):
        return self.firmVersion

    def getServiceTag(self):
        return self.serviceTag

    def getSerial(self):
        return self.serial

    def getMac(self):
        return self.mac

    def getName(self):
        return self.name

    def getIfaces(self):
        return self.ifaces


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
        if self.debug:
            print ("@device.getIface -> Interface " + iface.id + " was not found!")

    def addVlan(self, vlan):
        self.vlans.append(vlan)
        # order vlan list again
        if self.debug:
            print ("Vlan " + vlan.id + "added with success !")

    def removeVlan(self, vlan):
        self.vlans.remove(vlan)
        # order vlan list again
        if self.debug:
            print ("Vlan " + vlan.id + "removed with success !")

    def addPortChannel(self, channelGroup):
        self.channelGroups.append(channelGroup)
        # Order channel group for id
        if self.debug:
            print (colored("Channel Group " + channelGroup.id + "added with success !",'green'))


    def addInterface(self, iface):
        self.ifaces.append(iface)
        # order interface list again
        if self.debug:
            print (colored("Interface " + str(iface.id) + " added to "+ self.name +" with success !",'green'))

    def removeInterface(self, iface):
        self.IFs.remove(iface)
        if self.debug:
            print (colored("Interface " + iface.name + "removed with success !",'green'))

    def removePortChannel(self, channelGroup):
        self.channelGroups.remove(channelGroup)
        if self.debug:
            print (colored("Channel Group " + channelGroup.id + "removed with success !",'green'))

    def toString(self):
        output = ''
        output+=("Device: "+ self.name + " IP Address: "+ self.ipaddress + " Model: "+ self.model + "\nMAC Address "+ self.mac + "Service Tag: "+self.serviceTag + \
               " Serial Number: " + self.serial + " Firmware Version: " + self.firmVersion+"\n" )
        output+=("\tVlan:\tName\tIP Address\n-----------------------------------------------------------------------\n")

        for vlan in self.vlans:
            output+= ("\t" + vlan.toString())
        output+= ("\nID\t\tMode\t\tVlans\t\n-----------------------------------------------------------------------------------------------------\n")

        for iface in self.ifaces:
           output+= (iface.toString()+"\n")
        return output

