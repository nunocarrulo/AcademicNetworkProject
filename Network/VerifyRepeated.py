#!/usr/bin/python

import argparse
import sys
import os

def initGlobalVariables():
	#Global structures and variables
    global repeatedLines, totalRepeatedLines, noDupLines, totalFileLines
    global debug
    debug = False
    repeatedLines = noDupLines = ""
    totalRepeatedLines = totalFileLines = 0

'''
def parseArgs():
    global filename, debug, method
    parser = argparse.ArgumentParser()
    parser.set_defaults(debug=False)
    parser.add_argument('-f', dest="filename", action='store', required='True',
                        help="full path to FILE containing the address objects. Example: /home/nuno/Documents/lol.txt")
    parser.add_argument('-d', dest="debug", action="store_true",
                        help="Debug mode")

    args = parser.parse_args()
    debug = args.debug
    filename = args.filename
'''

def processFile(path):
    global repeatedLines, totalRepeatedLines, noDupLines, totalFileLines

    # Check if file exists
    if not os.path.isfile(path):
        print('The file does not exist.')
        sys.exit()
    #f = open(path, 'r')  # open file

    with open(path) as f:
        seen = set()
        for line in f:

            if line.startswith('#'):  # comment, do not process
                continue

            totalFileLines +=1

            line_lower = line.lower().strip()
            if line_lower in seen:
                totalRepeatedLines+=1
                repeatedLines+="%s" %(line)
                #print(line)
            else:
                seen.add(line_lower)

        #if debug:
        #   print('Lines to be written:\n' + repeatedLines)

    #join all not duplicated strings

    for str in seen:
        noDupLines +=(str+"\n")

    if debug:
        print("Size of set = %d" % (len(seen)))
        print("Duplicated Lines:\n%s" %(noDupLines))


    if totalFileLines == (len(seen) + totalRepeatedLines):
        print("Check passed ! Total lines = dupLines + noDupLines")
    # Create output fileS
    dupsFilename = '/home/nuno/Documents/Sonicwall/O365/repeatedLines.output'
    dupsFile = open(dupsFilename, "w")  # create duplicates file
    dupsFile.write(repeatedLines)
    dupsFile.close()

    noDupsFilename = '/home/nuno/Documents/Sonicwall/O365/OutputNoDups.output'
    noDupsFile = open(noDupsFilename, "w")  # create no duplicates file
    noDupsFile.write(noDupLines)
    noDupsFile.close()

    print("Files '%s' and '%s' successfully written!\nNumber of Repeated Lines: %d\n" % (dupsFilename, noDupsFilename, totalRepeatedLines))


# print outFilename +' successfully written!'


# Init global variables
initGlobalVariables()

# Read arguments
#parseArgs()
filename = "/home/nuno/Documents/Sonicwall/O365/O365FullURLs_original.txt"
# Read and store file contents
processFile(filename)