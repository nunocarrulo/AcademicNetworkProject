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
    global filename, method, debug, index, zone, prefix, httpCount
    index = httpCount = 0
    debug = False
    prefix = "WAN_O365_"
    zone = "WAN"

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
    global index, prefix, httpCount
    objects = ''
    shortFQDN = ''
    zone = "WAN"
    prefix = zone+"_O365_"

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

        line = line.strip()

        #if line contains http it will be excluded
        if "http" in line:
            httpCount+=1
            print("Line %d contains http. Value: %s" % (index,line))
            continue


        name = prefix + line

        if len(name) > 32:
            shortFQDN = line[-23:]
            name = prefix + shortFQDN

        objects += 'address-object fqdn ' + name + ' domain ' + line + ' zone ' + zone + '\n'

    if debug:
        print('Lines to be written:\n' + objects)

    # Create output file
    outFilename = '/home/nuno/Documents/Sonicwall/O365/parsedFQDNObjects.txt'
    outFile = open(outFilename, "w")  # create file output
    outFile.write(objects)
    outFile.close()

    print("File '%s' successfully written!\nTotal Lines: %d \nHTTPs: %d FQDN: %d\n" % (outFilename, index, httpCount, (index-httpCount)))



# Init global variables
initGlobalVariables()

# Read arguments
#parseArgs()

# Read and store file contents
filename = "/home/nuno/Documents/Sonicwall/O365/O365_Full_URLsNODups.txt"
processFile(filename)
