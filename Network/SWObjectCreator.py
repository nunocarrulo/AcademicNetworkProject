#!/usr/bin/python

import argparse
import sys
import os
from os.path import basename
from os import path

'''
#Find Computer name by IP
computerFilename = '/home/nuno/Documents/IMI_ISAServer2004/Computers_Parsed.txt'

#Opening files
computerFile = open (computerFilename, 'r')

'''


def initGlobalVariables():
    # Global structures and variables
    global filename, method, debug, cidrDict, index, zone, prefix
    global hostsNumber, networksNumber
    hostsNumber = networksNumber = index = 0
    debug = False
    prefix = "WAN_O365_"
    zone = "WAN"
    cidrDict = {8: "255.0.0.0", 9: "255.128.0.0", 10: "255.192.0.0", 11: "255.224.0.0", 12: "255.240.0.0", 13: "255.248.0.0", 14: "255.252.0.0", 15: "255.254.0.0",
             16 : "255.255.0.0", 17 : "255.255.128.0", 18 : "255.255.192.0", 19 : "255.255.224.0", 20 : "255.255.240.0",21 : "255.255.248.0",
             22 : "255.255.252.0", 23 : "255.255.254.0", 24 : "255.255.255.0", 25 : "255.255.255.128", 26 : "255.255.255.192", 27 : "255.255.255.224",
             28 : "255.255.255.240", 29 : "255.255.255.248", 30 : "255.255.255.252", 31 : "255.255.255.254"}

def parseArgs():
    global filename, debug, method
    parser = argparse.ArgumentParser()
    parser.set_defaults(debug=False)
    # parser.add_option("-f", "--file", action="store", type="string", help="path to FILE containing the equipment IP addresses")
    # parser.add_argument("-f", "--file", action="store_true", help="path to FILE containing the equipment IP addresses")
    parser.add_argument('-f', dest="filename", action='store', required='True',
                        help="full path to FILE containing the address objects. Example: /home/nuno/Documents/lol.txt")
    parser.add_argument('-d', dest="debug", action="store_true",
                        help="Debug mode")

    args = parser.parse_args()
    debug = args.debug
    filename = args.filename

    # if method is missing or is invalid
    if method == None:
        print('Method missing or invalid.')
        sys.exit()


def processFile(path):
    global hostsNumber, networksNumber, rangeNumber, cidrDict, index, prefix
    objects = ''

    # Check if file exists
    if not os.path.isfile(path):
        print('The file does not exist.')
        sys.exit()
    f = open(path, 'r')  # open file

    # Read and parse file
    for line in f.read().strip().split('\n'):
        index+=1        #line being processed fo original file
        netname = hostname = ""   #clear hostname and network obj name

        if line.startswith('#'):  # comment, do not process
            continue

        lol = line.split("/")      #obtain line

        # stripping strings
        for i in range(0, len(lol) - 1):
            lol[i] = lol[i].rstrip(' \t\n\r')

        # striping host and mask
        network = lol[0]
        #if no mask argument consider a host /32
        if len(lol) > 1:
            mask = int(lol[1])
        else:
            mask = 32
        #process host
        if (int(mask) == 32 or mask ==""):
            v6network = network[-20:]       #get last 20 characters in case string too long
            #remove special characters from first
            if v6network[0] == ':':
                v6network = v6network[1:]
            hostname = prefix+v6network
            if debug:
                print("Line %d with value %s is a Host" %(index,lol))
            objects += 'address-object ipv6 ' + hostname + ' host ' + network + ' zone ' + zone + '\n'
            hostsNumber += 1        #increase the counter of hosts

        #process network
        #elif mask in cidrDict:
        elif 1 == 1:
            netname = prefix+line
            if debug:
                print("Line %d with value %s is a Network" % (index, lol))
            if len(network) > 20:
                print("Line %d exceeds 20 characters" %(index))
            objects += 'address-object ipv6 ' + netname + ' network ' + network + ' ' + str(mask) + ' zone ' + zone + '\n'
            networksNumber += 1
        else:
            print("Line %d not a host and mask not in dictionary")
            #sys.exit()

    if (hostsNumber+networksNumber == index):
        print("Check passed. Number of hosts + Number of Networks = Number of lines")
    else:
        temp = index - (hostsNumber+networksNumber)
        print("Check failed by %d. Verify any missing objects" %(temp))

    if debug:
        print('Lines to be written:\n' + objects)

    # Create output file
    outFilename = '/home/nuno/Documents/Sonicwall/O365/parsedObjects.txt'
    outFile = open(outFilename, "w")  # create file output
    outFile.write(objects)
    outFile.close()

    print("File '%s' successfully written!\nHosts: %d\tNetworks: %d Total: %d\n" % (outFilename, hostsNumber, networksNumber,(hostsNumber+networksNumber)))



# Init global variables
initGlobalVariables()

# Read arguments
#parseArgs()

# Read and store file contents
filename = "/home/nuno/Documents/Sonicwall/O365/O365_Full_IPv6.txt"
processFile(filename)
