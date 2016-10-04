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
	#Global structures and variables
	global filename, method, debug
	global hostsNumber, networksNumber, rangeNumber, fqdnNumber, servicesNumber
	global serviceProtocols
	hostsNumber = networksNumber = rangeNumber = fqdnNumber = servicesNumber = 0
	serviceProtocols = ['6over4', 'ah', 'eigrp', 'esp', 'gre', 'icmp', 'icmpv6', 'igmp', 'l2tp', 'ospf', 'pim']

def parseArgs():
	global filename, debug, method
	parser = argparse.ArgumentParser()
	parser.set_defaults(debug=False)
	#parser.add_option("-f", "--file", action="store", type="string", help="path to FILE containing the equipment IP addresses")
	#parser.add_argument("-f", "--file", action="store_true", help="path to FILE containing the equipment IP addresses")
	parser.add_argument('-f', dest="filename",action='store', required='True',
		help="full path to FILE containing the address objects. Example: /home/nuno/Documents/lol.txt")
	parser.add_argument('-m', dest="method", action="store", 
		help="Method to be used: hosts, network, range, fqdn or service")
	parser.add_argument('-d', dest="debug", action="store_true", 
		help="Debug mode")
	
	args = parser.parse_args()
	debug = args.debug
	method = args.method
	filename = args.filename

	# if method is missing or is invalid
	if method == None:
		print ('Method missing or invalid.')
		sys.exit()


def processFile(path):
	global hostsNumber, networksNumber, rangeNumber, fqdnNumber,servicesNumber
	objects=''
	fqdn=''
	#Check if file exists
	if not os.path.isfile(path):
		print ('The file does not exist.')
		sys.exit()
	f = open(path, 'r')			#open file

	#Read and parse file
	for line in f.read().strip().split('\n'):
		
		if line.startswith('#'):	#comment, do not process
			continue
		lol = line.split()

		#stripping strings
		for i in range(0,len(lol)-1):
			lol[i] = lol[i].rstrip(' \t\n\r')
		
		# Method decision
		if method.lower() == 'hosts':
			objects+='address-object ipv4 ' + lol[0] + ' host ' + lol[1] + ' zone ' + lol[2] +'\n'
			hostsNumber+=1
		elif method.lower() == 'fqdn':
			fqdn = lol[0].split('_')[1]
			if debug:
				print 'FQDN: '+fqdn
			objects+='address-object fqdn ' + lol[0] + ' domain ' + fqdn + ' zone ' + lol[1] + '\n'
			fqdnNumber+=1
		elif method.lower() == 'network':
			aux = lol[1].split('/')
			network = aux[0]
			mask = '/'+aux[1]
			if debug:
				print 'Network: '+network+' Mask: '+mask

			objects+='address-object ipv4 ' + lol[0] + ' network ' + network + ' ' + mask + ' zone ' + lol[2] + '\n'
			networksNumber+=1
		elif method.lower() == 'range':
			netRange = lol[1].split('-')
			initAddr = netRange[0]
			aux = (netRange[0].rsplit('.',1))[0]
			endAddr = aux + '.' +netRange[1]
			if debug:
				print ('initAddr= '+ initAddr + ' endAddr= ' + endAddr)
			objects+='address-object ipv4 ' + lol[0] + ' range ' + initAddr + ' ' + endAddr + ' zone ' + lol[2] + '\n'
			rangeNumber+=1
		elif method.lower() == 'service':

			if lol[1].lower() in serviceProtocols:	#protocol type == service protocols does not require port definitio
				objects+=('service-object %s %s\n' % (lol[0], lol[1] ) )
			else:	#for custom, tcp or udp ports must be specified
				objects+=('service-object %s %s %s %s\n' % (lol[0], lol[1], lol[2], lol[3] ) )
			servicesNumber+=1
		else:
			print 'WTF went wrong ?'
			sys.exit()

		if debug:
			print('Lines to be written:\n'+objects)

	# Create output file		
	outFilename = method + '.output'		
	outFile = open(outFilename, "w")		#create file output
	outFile.write(objects)
	outFile.close()

	print("File '%s' successfully written!\nHosts: %d\tFQDN: %d\tNetworks: %d\tRanges: %d\t Services: %d\n" % (outFilename, hostsNumber, fqdnNumber, networksNumber, rangeNumber, servicesNumber) )
	#print outFilename +' successfully written!'
	

#Init global variables
initGlobalVariables()

#Read arguments
parseArgs()

#Read and store file contents
processFile(filename)
