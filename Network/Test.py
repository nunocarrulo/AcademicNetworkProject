#!/usr/bin/env python3

import sys
from DataStructures import Device,Interface

oldFilename = "IPOACL-toObjs_Old.txt"
with open(oldFilename,'r') as oldFile:
    oldData = oldFile.readlines()

newFilename = "IPOACL-toObjs_Parsed.txt"
with open(newFilename,'r') as newFile:
    newData = newFile.readlines()

counter = 0
toWrite =""
for line in newData:
    if line not in oldData:
        toWrite+=line.strip()+"\n"
        counter+=1

comparisonFilename = "missingAddrObjs"
dstFile = open(comparisonFilename,'w')
dstFile.write(toWrite)
dstFile.close()

print ("Found %d new address objects!" %(counter))


'''
a = "description asdadasd.......123456"
print (a.split("description")[1].strip())
sys.exit()
iface = Interface.Interface(10)
iface2 = Interface.Interface(20)
dev = Device.Device('lol.aitec.pt','192.168.1.1')



dev.addInterface(iface)
dev.addInterface(iface2)

print len(dev.getIfaces())
for lol in dev.getIfaces():
    print (lol.toString())


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