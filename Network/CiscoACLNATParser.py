#!/usr/bin/env python3
from __future__ import print_function
import os, sys

def findNameByIP(ip):
    global dnsData
    for line in dnsData:
        if ip in line.split(" ")[0].strip():
            name = line.split(" ")[1].strip()
            print ("Found IP %s with name %s!" %(ip,name))
            return name
    print("IP %s was NOT found!" % (ip))

def dstIPProcess(srcIP, parsedLine, srcOpt, dstOpt):
    global numObjs, toWrite

    # SRC ANY
    if srcOpt == "any":
        if dstOpt == "host":
            dstIP = parsedLine[2].lower()
        elif dstOpt == "network":
            dstIP = parsedLine[2].strip()
            dstIPMask = parsedLine[3].strip()
        else:
            print("Source IP is %s - Destination IP is ANY. Moving to next line" % (srcIP))
            return None
    # SRC HOST
    elif srcOpt == "host":
        if dstOpt == "host":
            dstIP = parsedLine[4].lower()
        elif dstOpt == "network":
            dstIP = parsedLine[3].strip()
            dstIPMask = parsedLine[4].strip()
        else:
            print("Source IP is %s - Destination IP is ANY. Moving to next line" % (srcIP))
            return None
    #SRC NETWORK
    else:
        if dstOpt == "host":
            dstIP = parsedLine[4].lower()
        elif dstOpt == "network":
            dstIP = parsedLine[3].strip()
            dstIPMask = parsedLine[4].strip()
        else:
            print("Source IP is %s - Destination IP is ANY. Moving to next line" % (srcIP))
            return None

    if dstIP not in addedObjects:
        # add the new object to the list
        addedObjects.append(dstIP)
        # Finding Name
        name = findNameByIP(dstIP)
        if (name == None):  # if a name was not found, use the IP on address-object name
            name = dstIP
        if dstOpt == "host":
            toWrite += "address-object ipv4 %s host %s zone WAN" % (name, dstIP)
        elif dstOpt == "network":
            toWrite += "address-object ipv4 %s network %s %s zone WAN" % (name, dstIP, dstIPMask)

        numObjs += 1

#Variable initialization
global dnsData, toWrite, numObjs
sonicwall = True
option = 1
numObjs = numLines = debug = 0
parsedLines = ""
toWrite = ""


#Reading DNS File to string for Sonicwall
print("Reading DNS file to string.")
dnsFilename = "IPO_MyDNS"
with open(dnsFilename,'r') as dnsFile:
    dnsData = dnsFile.read()

srcFilename = 'IPO-AddrObjs.txt'
parsedFilename = "IPO-AddrObjs_Parsed.txt"
srcFile = open(srcFilename, 'r')


addedObjects = []
if sonicwall:
    # Read each line and parse it to excel
    for line in srcFile.readlines():
        # ACL
        if option == 0:
            parsedLine = ((line.split("extended", 1)[1].strip()).split(" "))
            protocol = parsedLine[0]
            srcIP = parsedLine[1].strip()

            #IF SRC = ANY
            if srcIP.lower() == "any":

                #IF DST = HOST
                if (parsedLine[2].lower() == "host"):
                    dstIPProcess(srcIP, parsedLine, "any","host")
                    '''
                    dstIP = parsedLine[3].strip()

                    #Check if destination IP exists
                    if dstIP not in addedObjects:
                        addedObjects.append(dstIP)
                    else:   #proceed to next object
                        continue

                    name = findNameByIP(dstIP)
                    if (name == None): #if a name was not found, use the IP on address-object name
                        name = dstIP

                    dstIP = parsedLine[2].strip()
                    toWrite += "address-object ipv4 %s host %s zone WAN\n" % (name,dstIP)
                    numObjs += 1
                    '''
                #IF DST = NETWORK
                elif (parsedLine[2].lower() != "any"):
                    dstIPProcess(srcIP, parsedLine, "any", "network")
                    '''
                    print("Source IP is \"Any\" - Destination IP is a network")
                    dstIP = parsedLine[2].strip()
                    dstIPMask = parsedLine[3].strip()
                    toWrite += "address-object ipv4 %s network %s %s zone WAN\n" % (name,dstIP, dstIPMask)
                    numObjs+=1
                    '''
                #IF DST = ANY
                else:
                    print("Source IP is \"Any\" - Destination IP is ANY. Moving to next line")

            #If SRC = HOST
            elif srcIP.lower() == "host":
                srcIP = parsedLine[2].strip()

                if srcIP not in addedObjects:
                    addedObjects.append(srcIP)      # add the new object to the list

                    name = findNameByIP(srcIP)
                    if (name == None):  # if a name was not found, use the IP on address-object name
                        name = srcIP

                    toWrite += "address-object ipv4 %s host %s zone LAN\n" % (name, srcIP)      #Writing object
                    numObjs += 1    #counting object

                    #SRC = HOST & DST = HOST
                    if parsedLine[3].lower() == "host":
                        dstIPProcess(srcIP, parsedLine, "host","host")
                        '''
                        dstIP = parsedLine[4].lower()
                        if dstIP not in addedObjects:

                            # add the new object to the list
                            addedObjects.append(dstIP)

                            #Finding Name
                            name = findNameByIP(dstIP)
                            if (name == None):  # if a name was not found, use the IP on address-object name
                                name = dstIP

                            toWrite += "address-object ipv4 %s host %s zone WAN" % (name, dstIP)
                            numObjs += 1
                            '''
                    #SRC = HOST & DST = NETWORK
                    elif parsedLine[3].lower() != "any":
                        dstIPProcess(srcIP, parsedLine, "host","network")
                        '''
                        dstIP = parsedLine[3].strip()
                        dstIPMask = parsedLine[4].strip()

                        if dstIP not in addedObjects:
                            # add the new object to the list
                            addedObjects.append(dstIP)
                            # Finding Name
                            name = findNameByIP(dstIP)
                            if (name == None):  # if a name was not found, use the IP on address-object name
                                name = dstIP
                            toWrite += "address-object ipv4 %s network %s %s zone WAN" % (name, dstIP, dstIPMask)
                            numObjs += 1
                        '''
                    # SRC = HOST & DST = ANY
                    else:
                        print("Source IP is %s - Destination IP is ANY. Moving to next line" %(srcIP))

            # SRC = NETWORK
            else:
                srcIP = parsedLine[1].strip()
                srcIPMask = parsedLine[2].strip()

                if srcIP not in addedObjects:
                    addedObjects.append(srcIP)  # add the new object to the list

                    name = findNameByIP(srcIP)
                    if (name == None):  # if a name was not found, use the IP on address-object name
                        name = srcIP

                    toWrite += "address-object ipv4 %s network %s zone LAN\n" % (name, srcIP, srcIPMask)  # Writing object
                    numObjs += 1  # counting object

                    #DST = HOST
                    if parsedLine[3].lower() == "host":
                        dstIPProcess(srcIP, parsedLine, "network","host")
                        '''
                        dstIP = parsedLine[4].lower()
                        if dstIP not in addedObjects:

                            # add the new object to the list
                            addedObjects.append(dstIP)

                            # Finding Name
                            name = findNameByIP(dstIP)
                            if (name == None):  # if a name was not found, use the IP on address-object name
                                name = dstIP

                            toWrite += "address-object ipv4 %s host %s zone WAN" % (name, dstIP)
                            numObjs += 1
                        '''
                    #DST = NETWORK
                    elif parsedLine[3].lower() != "any":
                        dstIPProcess(srcIP, parsedLine, "network","network")
                        '''
                        dstIP = parsedLine[3].strip()
                        dstIPMask = parsedLine[4].strip()

                        if dstIP not in addedObjects:
                            # add the new object to the list
                            addedObjects.append(dstIP)
                            # Finding Name
                            name = findNameByIP(dstIP)
                            if (name == None):  # if a name was not found, use the IP on address-object name
                                name = dstIP
                            toWrite += "address-object ipv4 %s network %s %s zone WAN" % (name, dstIP, dstIPMask)
                            numObjs += 1
                        '''
                    else:
                        print("Source IP is %s - Destination IP is ANY. Moving to next line" % (srcIP))

            numLines += 1
        # 1 to 1 NAT
        #elif option == 1:
else:
    # Read each line and parse it to excel
    for line in srcFile.readlines():
        # ACL
        if option == 0:
            parsedLines += (((line.split("extended",1)[1].strip()).replace(" ","\t")) + "\n")
            numObjs +=1

        # 1 to 1 NAT
        elif option == 1:
            lineArray = line.strip().split(" ")
            #obtain IF info
            srcIF = lineArray[1].replace("(","").replace(")","").split(",")[0]
            dstIF = lineArray[1].replace("(","").replace(")","").split(",")[1]

            #Obtain IPs info
            realIP = lineArray[3]
            mappedIP = lineArray[2]
            realIPMask = lineArray[5]
            parsedLines += srcIF+"\t"+dstIF+"\t"+realIP+"\t"+realIPMask+"\t"+mappedIP+"\n"

            numObjs += 1

if debug:
    print ("Parsed Lines: "+parsedLines)

#Write output File
dstFile = open(parsedFilename,'w')
dstFile.write(toWrite)
dstFile.close()
#parsedAclFile = open(parsedFilename, 'w')
#parsedAclFile.write(parsedLines)
#parsedACLFile.close()

print ("File %s was successfully written!\nNumber of lines processed: %d\nNumber of objects added: %d" % (parsedFilename, numLines,numObjs))


