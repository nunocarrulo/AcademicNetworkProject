#!/usr/bin/env python3
from __future__ import print_function
from netmiko import ConnectHandler
import argparse, os, sys, time, traceback, socket
from termcolor import colored

def initGlobalVariables():

    # Global structures and variables
    global user, pwd, hosts, dellIdx, hpIdx, dell, hp, tftpIP, date
    global debug, states

    states = hosts = []

    tftpIP = None
    hp = [{}]
    dell = [{}]
    user = 'linkcomadmin'
    pwd = 'ascoin2004'

    hosts = [
                ('192.168.1.34', 'dell', 'swclouds'),
                ('10.222.4.34',  'dell', 'swgrandmaster'),
                ('192.168.1.37', 'hp',   'swlanr2'),
                ('192.168.1.38', 'dell', 'swcore01'),
                ('192.168.1.39', 'dell', 'swcore02'),
                ('192.168.1.40', 'dell', 'swmasterdmz'),
                ('192.168.1.46', 'dell', 'swpga'),
                ('192.168.1.47', 'dell', 'swp101'),
                ('192.168.1.53', 'dell', 'swp301'),
                ('192.168.1.59', 'dell', 'swp401'),
                ('192.168.1.60', 'dell', 'swp402'),
                ('192.168.1.61', 'dell', 'swp501'),
                ('192.168.1.62', 'dell', 'swp601'),
                ('192.168.1.65', 'dell', 'swp701'),
                ('10.222.4.36',  'dell', 'swiscsi01'),
                ('10.222.4.37', 'dell', 'swiscsi02')
             ]
    dellIdx = 1
    hpIdx = 1
    date = (time.strftime("%m%d%Y"))    ## mm/dd/yyyy format

def parseArgs():
    global tftpIP, debug
    parser = argparse.ArgumentParser()
    parser.set_defaults(debug=False)

    parser.add_argument('-i', dest="tftp_IP", action="store",
                        help="IP address of TFTP server")
    parser.add_argument('-d', dest="debug", action="store_true",
                        help="Debug mode")

    args = parser.parse_args()
    debug = args.debug
    tftpIP = args.tftp_IP

    # if TFTP IP exists and valid use it for config transfer
    if tftpIP != None:
        if not validate_IPv4(tftpIP):
            print (colored('TFTP IP address is not valid.','red'))
            sys.exit()
    # else use a static one
    else:
        tftpIP = "192.168.2.38"

    # Check if TFTP is running
    '''sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect((tftpIP, 69))
    sock.close()
    #result = sock.connect_ex((tftpIP,69))
    if result == 0:
           print ("Port is open")
    else:
           print ("Port is not open")
           print ("TFTP Server is not listening on "+tftpIP+" ! Exiting...")
           sys.exit()
    '''

    # Read and store file contents
    #readFile(args.filename)

def validate_IPv4(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True

def composeRunConfigCmd(model, IP, filename):
    #HP
    if model == 'hp':
        cmd = 'copy startup-config tftp ' + tftpIP + ' ' + filename + "\nY"
    #Dell, Cisco
    else:
        cmd = 'copy startup-config tftp://' + tftpIP + '/' + filename + "\nY"
    return cmd

def writeAudit():
    auditFilename = "Audits/Audit_NetworkConfig_" + date
    auditFile = open(auditFilename, 'w')
    auditFile.write("------------------------------------------------------------------------------------\n")
    auditFile.write(audit)
    auditFile.write("------------------------------------------------------------------------------------\n")
    auditFile.write("Equipments processed: %d [Dell: %d HP: %d] in %.1f secs (~%.1f secs/device). \n" % (
        len(hosts), (dellIdx - 1), (hpIdx - 1), duration, duration / nDevices))
    auditFile.close()

def readFile(path):
    # Check if file exists
    if not os.path.isfile(path):
        print('The file does not exist.')
        sys.exit()
    f = open(path, 'r')  # open file

    # Read and parse file
    for line in f.read().strip().split('\n'):
        if line.startswith('#'):  # comment, do not process
            continue
        lol = line.split(';')
        if debug:
            print(lol[0] + ' ' + lol[1])
        hosts.append((lol[0], lol[1]))

    if debug:
        print('Verification:')
        for host in hosts:
            print(host[0] + ' ' + host[1])

def closeConnection(conn):
    # Clean and close connection
    conn.cleanup()
    conn.disconnect()

    print (colored("Connection to " + host[0] + " successfully closed!",'green'))

def obtainConfigs(conn, name, ip, model):
    global date, tftpIP
    localDebug = False
    if debug:
        print (colored("\tObtaining Startup-config to TFTP Server %s",'yellow') % (str(tftpIP)))

    filename = name + '_' + ip + '_' + date + '.cfg'  # parse filename

    if len(filename) > 32:  # purge string if bigger than 32 characters
        filename = name + '_' + date + '.cfg'

    if localDebug:
        print (conn.send_command('show running-config'))

    #Construct command
    cmd = composeRunConfigCmd(model,tftpIP,filename)

    #Send command to switch
    output = conn.send_command(command_string=cmd,max_loops=10)

    if localDebug:
        print ("Command output:"+output)

    print('\tStartup configuration successfully transferred to TFTP Server ' + str(tftpIP) + ' with name \'' + filename + '\' !')

def initDeviceProperties(host):
    global dellIdx, hpIdx, states
    global dell, hp
    appendedDell = appendedHP = timeoutException = False
    localDebug = False
    counter = 0

    # print ('DellIdx= '+str(dellIdx)+' HpIdx= '+str(hpIdx))dell_force10
    while (timeoutException == True & counter < 3):
        if localDebug:
            print ("Counter: %d TimeoutException: %r" %(counter,timeoutException))
        try:
            if counter >= 1:
                print("Retrying connectivity to host %s. Attempt %d" %(counter, host[0]))
            conn = None

            if host[1].lower() == 'dell':
                dell.append({'device_type': 'dell_force10', 'ip': host[0],
                             'username': user, 'password': pwd, 'secret': pwd, 'ssh_strict': False})
                appendedDell = True
                if localDebug:
                    print(colored("Appended Dell!", 'yellow'))
                conn = ConnectHandler(**dell[dellIdx])
                dellIdx += 1

            elif host[1].lower() == 'hp':
                hp.append({'device_type': 'hp_procurve', 'ip': host[0],
                           'username': user, 'password': pwd, 'secret': pwd, 'ssh_strict': False})
                appendedHP = True
                if localDebug:
                    print(colored("Appended HP!", 'yellow'))
                conn = ConnectHandler(**hp[hpIdx])
                hpIdx += 1

            else:
                print( colored("@initDeviceProperties -> Unrecognized equipment brand !",'red'))

            states.append("OK")  # OK
            print( colored ("Host: %s State: OK!",'green') %(host[2]))
            return conn

        except Exception as exception:

            print("Unexpected exception : " + str(sys.exc_info()[0]))
            print(exception)
            traceback.print_exc()
            print("Counter: %d" % (counter))
            # Report state as failed in last try
            if counter == 2:
                states.append("Failed")
                print( colored("Host: %s State: Failed!",'red') % (host[2]))

            #Removed if device was added
            if appendedDell:
                if localDebug:
                    print(colored("Poped Dell!",'yellow'))
                dell.pop()
            elif appendedHP:
                if localDebug:
                    print(colored("Poped HP!", 'yellow'))
                hp.pop()

            if debug:
                print(colored('@initDeviceProperties -> Check your connectivity status please!','red'))
                print(exception.__class__.__name__)

            if str(exception).lower() == 'netmikoauthenticationexception':
                print (colored("Authentication error. Please check if your credentials are valid.",'red'))
                sys.exit()
            else:
                timeoutException = True
                counter += 1
                print ("\t@Else->Timeout Exception: %r\tCounter increased to %d" %(timeoutException, counter))

        appendedDell = appendedHP = False   #reset flags

    for a in dell:
        print('dell')
        print (a)
    for b in hp:
        print('hp')
        print (b)
    print ("HP Index= %d Dell Index= %d" %(hpIdx,dellIdx))

# Global structures and variables
global user, pwd, hosts, dellIdx, hpIdx, dell, hp
global debug, tftpIP, date, states

# Init global variables
initGlobalVariables()

# Read arguments
parseArgs()

# main loop
nDevices = i = 0
audit = tempAudit = ""
before = time.time()

for host in hosts:
    nDevices += 1

    print (colored('----------------------------------------------------------------------------------'))
    print(colored('-> Processing host %d %s (%s)...' % (nDevices, host[0], host[1].upper()),'yellow'))

    # Initialize equipment properties and establish connection
    conn = initDeviceProperties(host)

    devIP = host[0]
    model = host[1]
    name = host[2]

    # Retrieve info for auditing
    tempAudit = "\tHost: %s\t\t\tModel: %s\tIP: %s\tState: %s\n" % (name, model, devIP, states[i])
    if debug:
        print (colored(tempAudit,'yellow'))
    i += 1                  #increase state pointer to next device
    audit+= tempAudit       #append audit from last device

    if conn == None:
        print("Moving to next node.")
        continue

    conn.enable()            # enable switch
    conn.send_command('terminal length 0')

    if debug:
        print(conn.send_command('terminal length 0'))
        #print(conn.send_command('show interface status'))
        #print(conn.send_command('show running-config'))

    print("\tHostname: %s IP: %s Model: %s" % (name, devIP, model))

    # Obtain and store running config
    obtainConfigs(conn, name, devIP, model) #<--PROBLEM

    #Close SSH connection
    closeConnection(conn)
    time.sleep(0.5)

after = time.time()
duration = (after - before)

#Write audit to file
writeAudit()

#Write audit to screen
print("------------------------------------------------------------------------------------")
print (audit)
print("------------------------------------------------------------------------------------")
print("Equipments processed: %d [Dell: %d HP: %d] in %.1f secs (~%.1f secs/device). \n" % (
len(hosts), (dellIdx - 1), (hpIdx - 1), duration, duration / nDevices))


