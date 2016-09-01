class Vlan:

    def __init__(self, id):
        self.id = id
        #self.ipaddress='N/D'

    def setName(self, name):
        self.name = name

    #def setIPaddress(self, ipaddress):
    #    self.ipaddress = ipaddress

    def getName(self):
        return self.name

    def toString(self):
        return (self.id + "\t\t" + self.name)