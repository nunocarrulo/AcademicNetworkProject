#!/usr/bin/env python
import sys
from DataStructures import Device,Interface,Vlan,ChannelGroup

#a = "asdadasd.......123456"
a = "Service Tag: asdada12e1d12"
mac = "F8B1.5659.7A51"
newMAC = ''

mac = mac.replace('.','')
print len(mac)

for i in range(0,len(mac)):
    if (i % 2 == 0) & (i != 0):
        newMAC += ':' + mac[i]
    else:
        newMAC+=mac[i]

print newMAC
#c = a.split("Service Tag:")
#print c[1]
#b = a.split('.')

#print b[-1]

'''
devices = []
ifaces = []
#lol = Device()
lol = Device.Device('swtest','192.168.0.12')
print lol.getName()
devices.append(lol)

for a in devices:
    print a.getName()

iface = Interface.Interface(20)
print iface.id
#print lol.getName()
'''