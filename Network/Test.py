#!/usr/bin/env python

from DataStructures import Device,Interface,Vlan,ChannelGroup

#a = "asdadasd.......123456"
a = "Service Tag: asdada12e1d12"
print a[0:3]
a = 'ab'
b = 'bc'
if (a != 'bc') & (b != 'cb'):
    print ("lol")

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