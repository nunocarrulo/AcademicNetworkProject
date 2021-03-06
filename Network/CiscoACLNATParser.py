#!/usr/bin/env python3
from __future__ import print_function
import os, sys
from termcolor import colored, cprint


def findNameByIP(ip):
    global dnsData
    if debug:
        print ("DNS Data: %s" %(dnsData))

    for line in dnsData:
        line = line.strip()

        if not line:    #if line empty
            continue

        #Parse information
        line = line.split("\t")
        listIP = line[0].strip()
        listName = line[1].strip()

        if debug:
            print("@findNameByIP : IP-> %s IP on List %s Name %s" % (ip, listIP, listName))

        if ip in listIP:
            print ("Found IP %s with name %s!" %(ip,listName))
            return listName
    print("IP %s was NOT found!" % (ip))

def dstIPProcess(srcIP, parsedLine, srcOpt, dstOpt):
    global numObjs, toWrite

    # SRC ANY
    if srcOpt == "any":
        if dstOpt == "host":
            dstIP = parsedLine[3].lower().strip()
        elif dstOpt == "network":
            dstIP = parsedLine[2].strip()
            dstIPMask = parsedLine[3].strip()
        else:
            print("Source IP is %s - Destination IP is ANY. Moving to next line" % (srcIP))
            return None
    # SRC HOST
    elif srcOpt == "host":
        if dstOpt == "host":
            dstIP = parsedLine[4].lower().strip()
        elif dstOpt == "network":
            dstIP = parsedLine[3].strip()
            dstIPMask = parsedLine[4].strip()
        else:
            print("Source IP is %s - Destination IP is ANY. Moving to next line" % (srcIP))
            return None
    #SRC NETWORK
    else:
        if dstOpt == "host":
            dstIP = parsedLine[4].lower().strip()
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
        name = "WAN_" + name  # adding zone to the name

        if dstOpt == "host":
            toWrite += "address-object ipv4 %s host %s zone WAN\n" % (name, dstIP)
        elif dstOpt == "network":
            toWrite += "address-object ipv4 %s network %s %s zone WAN\n" % (name, dstIP, dstIPMask)
        else:
            print("dstIP is ANY")
        numObjs += 1

    else:
        print("IP %s already added!" %(dstIP))

def commentIsIP(namePrefix):
    # Check if comment is IP
    digCount = pntCount = 0
    for c in namePrefix:
        if c.isdigit():
            digCount += 1
        elif c == ".":
            pntCount += 1

    # if comment is IP no name will be assigned
    return ((digCount > 8) & (pntCount > 2))

def checkNRegName2Long(name):
    global longNameObjCount
    # Names longer than 32 characters
    if len(name) > 32:
        longNameObjCount += 1
        longNameObjList.append((numLines, name))
        print("NAME TOO LONG. Size: %d" % (len(name)))

#Variable initialization
global dnsData, toWrite, numObjs, longNameObjList
IPOC_DNS = False
option = 3          #  0-> ACL 1-> NAT 2 -> Siglicusr 3->IPs to addr-obj CFS
numObjs = numLines = debug = emptyLines = commentLines = longNameObjCount = 0
longNameObjList = []
parsedLines = ""
toWrite = ""


if IPOC_DNS:
    #Reading DNS File to string for Sonicwall
    print("Reading DNS file to string.")
    dnsFilename = "Docs/IPO_MyDNS.txt"
    #dnsFile = open(dnsFilename,'r')
    with open(dnsFilename,'r') as dnsFile:
        dnsData = dnsFile.readlines()
    addedObjects = []


# Choice of operation to perform
if option == 0:
    srcFilename = 'IPOACL-toObjs.txt'
    parsedFilename = "IPOACL-toObjs_Parsed.txt"
elif option == 2:
    srcFilename = 'Docs/siglicusr'
    parsedFilename = 'Docs/siglicusr_Parsed.txt'
elif option == 3:
    addrObjNames = []
    #srcFilename = 'Docs/IPOCParseAllowedIPs/squid_ppl_mal_comportado'
    #parsedFilename = 'Docs/IPOCParseAllowedIPs/squid_ppl_mal_comportado_Parsed.txt'
    #addrGroupName = "LAN_pplMalComportado[G]"
    #srcFilename = 'Docs/IPOCParseAllowedIPs/squid_ip_allow'
    #parsedFilename = 'Docs/IPOCParseAllowedIPs/squid_ip_allow_Parsed.txt'
    #addrGroupName = "LAN_IPAllow[G]"
    srcFilename = 'Docs/IPOCParseAllowedIPs/squid_vip'
    parsedFilename = 'Docs/IPOCParseAllowedIPs/squid_vip_Parsed.txt'
    addrGroupName = "LAN_VIP[G]"

srcFile = open(srcFilename, 'r')    #open file to read information


if IPOC_DNS:
    # Read each line and parse it to excel
    for line in srcFile.readlines():
        # ACL
        if option == 0:
            parsedLine = ((line.split("permit", 1)[1].strip()).split(" "))
            protocol = parsedLine[0]
            srcIP = parsedLine[1].strip()

            #IF SRC = ANY
            if srcIP.lower() == "any":

                #IF DST = HOST
                if (parsedLine[2].lower() == "host"):
                    print ("SRC = ANY & DST = HOST")
                    dstIPProcess(srcIP, parsedLine, "any","host")

                #IF DST = NETWORK
                elif (parsedLine[2].lower() != "any"):
                    print("SRC = ANY & DST = NETWORK")
                    dstIPProcess(srcIP, parsedLine, "any", "network")

                #IF DST = ANY
                else:
                    print("SRC = ANY & DST = ANY")
                    print("Source IP is \"Any\" - Destination IP is ANY. Moving to next line")

            #If SRC = HOST
            elif srcIP.lower() == "host":
                print("SRC = HOST & DST = HOST")
                srcIP = parsedLine[2].strip()

                if srcIP not in addedObjects:
                    addedObjects.append(srcIP)      # add the new object to the list

                    name = findNameByIP(srcIP)
                    if (name == None):  # if a name was not found, use the IP on address-object name
                        name = srcIP
                    name = "WAN_" + name  # adding zone to the name

                    toWrite += "address-object ipv4 %s host %s zone WAN\n" % (name, srcIP)      #Writing object
                    numObjs += 1    #counting object

                #SRC = HOST & DST = HOST
                if parsedLine[3].lower() == "host":
                    print("SRC = HOST & DST = HOST")
                    dstIPProcess(srcIP, parsedLine, "host","host")

                #SRC = HOST & DST = NETWORK
                elif parsedLine[3].lower() != "any":
                    print("SRC = HOST & DST = NETWORK")
                    dstIPProcess(srcIP, parsedLine, "host","network")

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
                    name = "WAN_"+name  #adding zone to the name

                    toWrite += "address-object ipv4 %s network %s %s zone WAN\n" % (name, srcIP, srcIPMask)  # Writing object
                    numObjs += 1  # counting object

                #DST = HOST
                if parsedLine[3].lower() == "host":
                    print("SRC = NETWORK & DST = HOST")
                    dstIPProcess(srcIP, parsedLine, "network","host")

                #DST = NETWORK
                elif parsedLine[3].lower() != "any":
                    print("SRC = NETWORK & DST = NETWORK")
                    dstIPProcess(srcIP, parsedLine, "network","network")

                else:
                    print("SRC = NETWORK & DST = ANY")
                    print("Source IP is %s - Destination IP is ANY. Moving to next line" % (srcIP))

            numLines += 1
            print(numLines)

            #cprint("ToWrite: \n%s" %(toWrite), 'green',attrs=['bold'])
            #if numLines == 1:
            #    sys.exit()
        # 1 to 1 NAT
        #elif option == 1:

else:
    #initialization for siglicusr
    #namePrefix = "LAN_"
    name = namePrefix = ""
    if option == 2:
        basename = "LAN_SIGLI_"
    elif option == 3:
        basename = "LAN_"
    #switch = False

    # Read each line and parse it to excel
    for line in srcFile.readlines():
        numLines += 1
        line = line.strip()
        if not line:  # if line empty
            emptyLines +=1
            continue

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
        #siglicusr parse
        elif option == 2:
            if line.startswith("#"):
                commentLines+=1
                basename = ""       #clear name if repeated #
                namePrefix = line.split(("#"))[1].strip()
                basename+= "LAN_SIGLI_%s_" %(namePrefix)

            else:
                IP = line.strip()                       #get full IP
                reducedIP = line.split(".",2)[2]        #Parse IP to display last 2 octecs
                name = (basename+reducedIP)
                toWrite += "address-object ipv4 %s host %s zone LAN\n" % (name, IP)
                numObjs+=1
            print("@Line: %s Name: %s" % (numLines, name))

        # IPs to address objects parse
        elif option == 3:

            if line.startswith("#"):
                commentLines += 1
                basename = ""  # clear name if repeated #

                namePrefix = line.split(("#"))[1].strip().replace(" ","")

                if commentIsIP(namePrefix):
                    namePrefix = ""
                    basename="LAN_"
                else:
                    basename += "LAN_%s_" % (namePrefix)
                #print ("@Line: %d\tDigit Number: %d Point Number: %d" %((numLines),digCount, pntCount))

            else:
                IP = line.strip()  # get full IP
                reducedIP = line.split(".", 2)[2]  # Parse IP to display last 2 octecs
                name = (basename + reducedIP)

                checkNRegName2Long(name)    #verify and register if name too long

                addrObjNames.append(name)   #save names in array to create address-group at the end
                toWrite += "address-object ipv4 %s host %s zone LAN\n" % (name, IP)
                numObjs += 1

            print("@Line: %d Name: %s Basename: %s" % (numLines, name, basename))

if debug:
    print ("Parsed Lines: "+parsedLines)
print ("toWrite\n %s" %(toWrite))

#Creation of address group for the file processed
print("-----------------------------------------------------------------------")
print("Creating Address-Group %s obtained from file %s..." %(addrGroupName, srcFilename))
toWrite +="commit\naddress-group ipv4 %s\n"%(addrGroupName)
objCount = 0
for name in addrObjNames:
    #print("Name: %s" %(name))
    objCount +=1
    toWrite+= "address-object ipv4 %s\n" %(name)
print("Address-Group %s created with %d objects!\n" %(addrGroupName, objCount))

#Write output File
dstFile = open(parsedFilename,'w')
dstFile.write(toWrite)
dstFile.close()

print("-----------------------------------------------------------------------")
print ("File %s was successfully written!\nNumber of lines processed: %d\nNumber of objects added: %d\nNumber of empty Lines: %d\nNumber of commented lines: %d\n" \
       % (parsedFilename, numLines,numObjs, emptyLines, commentLines))

print("-----------------------------------------------------------------------")
print("Number of objects too long: %d\nLong Name Object List:" %(longNameObjCount))
for name in longNameObjList:
    print("@Line: %s Name: %s" %(name[0],name[1]))


