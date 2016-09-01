#!/usr/bin/env python3
from __future__ import print_function

from netmiko import ConnectHandler
from DataStructures import *
#from DataStructures import Device,Interface,Vlan,ChannelGroup
import argparse, os, sys, time, socket
from termcolor import colored
import signal
# import thread

# Global structures and variables
global user, pwd, hosts, dellIdx, hpIdx, dell, hp, myIP, tftpIP, useTFTP, date
global runConfigFile, ifstatusFile, versionFile, systemIDFile, vlanFile
global debug, retInfo
global devices

def initGlobalVariables():

    # Global structures and variables
    global user, pwd, hosts, dellIdx, hpIdx, dell, hp, myIP, tftpIP, useTFTP, date
    global runConfigFile, ifstatusFile, versionFile, systemIDFile, vlanFile
    global debug, retInfo
    global devices
    devices = hosts = []
    tftpIP = None
    useTFTP = False
    hp = dell = [{}]
    user = 'nunoadmin'
    pwd = '12345lol'
    hosts = [('192.168.0.13','dell')]
    #hosts=[('192.168.1.19', 'dell'), ('192.168.1.32', 'dell'), ('192.168.1.36', 'hp')]
    dellIdx = 1
    hpIdx = 1
    date = (time.strftime("%d%m%y"))    ## dd/mm/yyyy format

# Obtain my IP address
# myIP=getMyIP()

def getMyIP():
    if os.name != "nt":
        import fcntl
        import struct
        def get_interface_ip(ifname):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,
                                                struct.pack('256s', ifname[:15]))[20:24])

    def get_lan_ip():
        ip = socket.gethostbyname(socket.gethostname())
        if ip.startswith("127.") and os.name != "nt":
            interfaces = [
                "eth0", "eth1", "eth2", "wlan0",
                "wlan1", "wifi0", "ath0", "ath1", "ppp0", ]
            for ifname in interfaces:
                try:
                    ip = get_interface_ip(ifname)
                    break
                except IOError:
                    pass
        return ip

    return get_lan_ip()

def parseArgs():
    global useTFTP, tftpIP, debug, retInfo
    parser = argparse.ArgumentParser()
    parser.set_defaults(debug=False)
    # parser.add_option("-f", "--file", action="store", type="string", help="path to FILE containing the equipment IP addresses")
    # parser.add_argument("-f", "--file", action="store_true", help="path to FILE containing the equipment IP addresses")
    #parser.add_argument('-f', dest="filename", action='store', required='True',
    #                    help="path to FILE containing the equipment IP addresses. Example: /home/nuno/Documents/lol.txt")
    parser.add_argument('-t', dest="tftp_IP", action="store",
                        help="IP address of TFTP server")
    parser.add_argument('-i', dest="retInfo", action="store_true",
                        help="Retrieve switch details")
    parser.add_argument('-d', dest="debug", action="store_true",
                        help="Debug mode")


    args = parser.parse_args()
    debug = args.debug
    tftpIP = args.tftp_IP
    retInfo = args.retInfo

    # if TFTP IP exists and valid use it for config transfer
    if tftpIP != None:
        if not validate_IPv4(tftpIP):
            print (colored('TFTP IP address is not valid.','red'))
            sys.exit()
        useTFTP = True
    # else save it locally
    else:
        useTFTP = False

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

def createConfigDir():
    # Create directory to store the configs
    global currDir
    currDir = os.path.dirname(os.path.abspath(__file__))  # obtain path of directory where script is being run
    if debug:
        print(currDir)

    # os.getcwd() # path of working directory
    global newDir
    newDir = currDir + '/Configs/'
    if not os.path.exists(newDir):
        print("Directory 'Configs' was created with success on path " + currDir)
        os.makedirs(newDir)
    else:
        print("Directory 'Configs' already exists on directory " + currDir + "/.\nThe obtained configs will be stored on that folder")
        # sys.exit()

def parseMAC(mac):
    newMAC = ''
    mac = mac.replace('.', '')

    for i in range(0, len(mac)):
        if (i % 2 == 0) & (i != 0):
            newMAC += ':' + mac[i]
        else:
            newMAC += mac[i]
    return newMAC

def getSystemName(brand):
    if debug:
        print (colored("\t@getSystemName -> Obtaining Name and  Model version...",'yellow'))

    name = ''
    model = ''
    brand = brand.lower()
    if brand == "dell":
        output = conn.send_command('show system')  # sending command

        # parsing command information
        for line in output.split('\n'):
            if "Machine Type:" in line:
                model = (line.split(':'))[1].strip()

            elif "System Name:" in line:
                name = (line.split(':'))[1].strip()
                break

    elif brand == 'hp':
        output = conn.send_command('show system')  # sending command
        # Getting hostname
        for line in output.split('\n'):
            if "System Name" in line:
                name = (line.split(':'))[1].strip()
                if debug:
                    print(name)
                break

        output = conn.send_command('show tech buffers')  # sending command
        # Getting model information
        for line in output.split('\n'):
            if "Name:" in line:
                model = (line.split(':'))[1].strip()
                if debug:
                    print(model)
                break
    else:
        print (colored("Unrecognized system brand @ 'parseSystemOutput'.",'red'))
    return name, model

def parseInterfaceStatus(device):
    counter = i = 0
    vlanNextLine = False

    if debug:
        print (colored("@parseInterfaceStatusParsing Interfaces Information",'yellow'))

    '''
        0 - start
        1 - interfaces
        2 - portchannels
    '''

    for line in ifstatusFile.splitlines():
        i+=1

        # In case vlans exceed more than one line
        if vlanNextLine == True:
            ifaceVlans+=line.strip()
            if line.endswith(','):
                continue
            else:
                vlanNextLine = False
                iface.vlans = ifaceVlans
                device.addInterface(iface)      #add interface
                print ("Interface "+ iface.id + " added to "+ device.name +"successfully!")
                continue

        if counter == 1:    #read interfaces

            # Read Interface Name and instantiate interface
            if (len(line) == 0):
                counter+=1
                print (colored("No more physical interfaces! Moving to port channels.",'cyan'))
                continue

            ifName = line[0:9].strip()
            iface = Interface.Interface(ifName)

            # Read Interface Status
            ifStatus = line[46:51].strip().lower()

            if ifStatus == "up":
                iface.setStatus(1)
            elif ifStatus == "down":
                iface.setStatus(0)
            else:
                print (colored("Misread interface status information. Result: "+ifStatus,'red'))
                print(colored("Line:\n" + line), 'blue')
                iface.setStatus(0)       #consider the interface down

            #Read and add Switchport Mode to device
            ifMode = line[59:62].strip().upper()

            if (ifMode != 'A') & (ifMode != 'G') & (ifMode != 'T'):
                print (colored("Misread switchport mode information. Result: "+ifMode,'red'))
                print (colored("Line:\n"+line),'blue')
            else:
                iface.setMode(ifMode)

            # Read and add Vlans to device
            ifaceVlans = line[62:].strip()
            if ifaceVlans.endswith(','):
                vlanNextLine = True
                continue
            else:
                vlanNextLine = False
                iface.setVlans(ifaceVlans)
                device.addInterface(iface)      #adding interface to device

        elif counter == 2:  #read port channels
            print (colored("Port Channels feature not yet programmed!",'cyan'))
            break
        else:
            if line.startswith('------'):
                counter += 1
            continue

    if debug:
        print (colored("Printing " + device.getName() + " information to 'Check' file. Total: "+str(i)+" interfaces.",'yellow'))
    '''
    print (colored(device.toString()),'cyan')  # print all device details
    # Save to file 'check' all device details
    check = open("check", "w")  # create file
    check.write(device.toString())
    check.close()
    sys.exit()
    '''

def parseSystemDetails(device):
    # Parsing version
    print(colored("\nParsing 'Version' Information (Firmware Version, Serial, MAC)", 'yellow'))

    readFirm = False
    for line in versionFile.splitlines():
        if readFirm == True:
            device.setFirmVersion(line[29:43].strip())
            readFirm = False
        elif "Serial" in line:
            device.setSerial(line.split('.')[-1].strip())
        elif "MAC" in line:
            device.setMac(parseMAC(line[-14:]))
        elif "----" in line:
            readFirm = True

    # Parsing system id
    print(colored("\nParsing 'System id' information (Service Tag)", 'yellow'))

    for line in systemIDFile.splitlines():
        if "Service Tag:" in line:
            device.setServiceTag(line.split("Service Tag:")[1].strip())
            break

    if debug:
        print(colored(
            "Serial: " + device.getSerial() + " ST: " + device.getServiceTag() + " Firmware Version: " + device.getFirmVersion() + " MAC: " + device.getMac(),
            'cyan'))

    # Parsing show vlan file (vlans)
    readVlan = False
    for line in vlanFile.splitlines():
        if line[0] == ' ':  # if no information on that line, move on
            continue
        elif '----' in line:
            readVlan = True
            continue
        elif readVlan:
            # Obtain Vlan info
            vlanID = line[0:4]
            vlanName = line[6:26]

            vlan = Vlan.Vlan(vlanID)  # instantiate vlan object
            vlan.setName(vlanName)  # set vlan name
            device.addVlan(vlan)  # add vlan to device
    '''
    if debug:
        print(colored("Vlan ID\t\tName", 'cyan'))
        for vlan in device.getVlans():
            print(colored(vlan.toString(), 'cyan'))
    '''

def parseSwitchDetails(device):

    # Files ifstatusFile, versionFile, systemIDFile

    # Parsing interface status
    parseInterfaceStatus(device)

    # Parsing version and ST
    parseSystemDetails(device)

    # Parsing Show run config (interface description)
    #print(colored("Parsing running config, namely IF description", 'yellow'))
    descDepth = False
    i = 0
    print ("Run Config File: "+runConfigFile)
    for line in runConfigFile.splitlines():
        print (str(i))
        if descDepth:
            #no description, move on
            if "exit" in line:
                descDepth = False
                continue
            elif "description" in line:
                print("Found description")
                ifaceObj = device.ifaces.getIface(ifaceID)
                print ("ALALALA: "+line.split("description")[1].strip())
                ifaceObj.setIfaceDescription(line.split("description")[1].strip())
                if debug:
                    print (colored("Interface "+ifaceID+" was found!",'green'))
                descDepth = False
        elif (("Interface " in line) & (not descDepth)):
            print ("Found Interface")
            # Verify if interface is on device list
            ifaceID = line.split("Interface")[1].strip()
            if device.ifaceOnList(ifaceID):
                descDepth = True    #Read description
    sys.exit()
    print ("\tID\tDescription\t\tMode\tVlans")
    for x in device.getIfaces():
       print (x.toString())

def obtainSwitchDetails(conn, device):
    global runConfigFile, ifstatusFile, versionFile, systemIDFile, vlanFile

    if debug:
        print (colored("@obtainSwitchDetails -> Obtaining Switch Details",'yellow'))

    #conn.disable_paging()
    conn.send_command(' terminal length 0')
    time.sleep(1)
    runConfigFile = conn.send_command('    show running-config ')
    time.sleep(1)
    ifstatusFile = conn.send_command(' show interface status ')

    versionFile = conn.send_command(' show version ')

    systemIDFile = conn.send_command(' show system id ')

    vlanFile = conn.send_command(' show vlan ')

    configFile = open('sh run', "w")  # create file
    configFile.write(runConfigFile)
    configFile.close()

    if debug:
        print("-----------------------------------------------------------------------------------------")
        print("Printing 'show running-config'\n")
        print(runConfigFile)
        print("-----------------------------------------------------------------------------------------")
        print ("Printing 'show interface status'\n")
        print (ifstatusFile)
        print("-----------------------------------------------------------------------------------------")
        print("Printing 'show version'")
        print(versionFile)
        print("-----------------------------------------------------------------------------------------")
        print("Printing 'system id'")
        print(systemIDFile)
        print("-----------------------------------------------------------------------------------------")
        print("Printing 'show vlan'")
        print(vlanFile)

    if debug:
        print (colored("@obtainSwitchDetails -> Switch information retrieved with success!",'green'))
    sys.exit()

def closeConnection(conn):
    # Clean and close connection
    conn.cleanup()
    conn.disconnect()

    print (colored("Connection to " + host[0] + " successfully closed!",'green'))

def obtainConfigs(conn, name, ip):
    global date, tftpIP, runConfigFile
    print (colored("\tObtaining Startup-config...",'yellow'))

    if debug:
        print(colored("\t\tTFTP: " + str(useTFTP) + " TFTP Server: " + str(tftpIP),'yellow'))

    #If no TFTP then just read and store running config
    if not useTFTP:
        '''
        conn.disable_paging()
        runConfigFile = conn.send_command(' show run')  # obtain running config
        filename = newDir + name + '_' + ip + '_' + date + '.cfg'  # parse filename
        configFile = open(filename, "w")  # create file

        if debug:
            print (colored("\tWriting running config...",'yellow'))

        configFile.write(runConfigFile)
        configFile.close()
        sys.exit()
        '''
    else:
        if debug:
            print("\tUsing TFTP Server")
        # print("\tVerifying TFTP Connectivity")
        # command = ' ping '+tftpIP
        # output = conn.send_command(command)
        filename = name + '_' + ip + '_' + date + '.cfg'  # parse filename

        if len(filename) > 32:  # purge string if bigger than 32 charaters
            filename = name + '_' + date + '.cfg'
        output = conn.send_command(' copy startup-config tftp://' + tftpIP + '/' + filename)
        # if (debug):
        # print (output)
        output = conn.send_command('y')
        if (debug):
            print(output)

        print('\tStartup configuration successfully transferred to TFTP Server ' + str(
            tftpIP) + ' with name \'' + filename + '\' !')

def initDeviceProperties(host):
    global dellIdx
    global hpIdx
    timeoutException = False
    counter = 0
    # print ('DellIdx= '+str(dellIdx)+' HpIdx= '+str(hpIdx))dell_force10
    while (timeoutException == True & counter < 3):
        try:
            if counter >= 1:
                print("Retrying connectivity to host %s. Attempt %d" %(counter, host[0]))

            if host[1].lower() == 'dell':
                # dell.append({'device_type': 'cisco_ios', 'ip': host[0],
                #	'username': user, 'password': pwd, 'secret':pwd, 'ssh_strict':False})
                dell.append({'device_type': 'dell_force10', 'ip': host[0],
                             'username': user, 'password': pwd, 'secret': pwd, 'ssh_strict': False})
                conn = ConnectHandler(**dell[dellIdx])
                dellIdx += 1
                return conn

            elif host[1].lower() == 'hp':
                hp.append({'device_type': 'hp_procurve', 'ip': host[0],
                           'username': user, 'password': pwd, 'secret': pwd, 'ssh_strict': False})
                conn = ConnectHandler(**hp[hpIdx])
                hpIdx += 1
                return conn

            else:
                print( colored("@initDeviceProperties -> Unrecognized equipment brand !",'red'))
                return None
        except Exception as exception:
            # print ("Unexpected exception : "+str(sys.exc_info()[0]))
            if debug:
                print(colored('@initDeviceProperties -> Check your connectivity status please!','red'))
                print(exception.__class__.__name__)

            if str(exception).lower() == 'netmikoauthenticationexception':
                print (colored("Authentication error. Please check if your credentials are valid.",'red'))
                sys.exit()
            else:
                print ("Timeout Exception")
                timeoutException = True
                counter += 1

# Init global variables
initGlobalVariables()

# Read arguments
parseArgs()

# Create directory where the configs will be stored, if tftp is not to be used
if not useTFTP:
    createConfigDir()

# main loop
nDevices = 0
before = time.time()

for host in hosts:
    nDevices += 1
    print (colored('----------------------------------------------------------------------------------'))
    print(colored('-> Processing host %d %s (%s)...' % (nDevices, host[0], host[1].upper()),'yellow'))

    # Initialize equipment properties and establish connection
    conn = initDeviceProperties(host)
    if conn == None:
        print("Moving to next node.")
        continue

    conn.enable()  # enable switch

    # Obtain model and name
    (name, model) = getSystemName(host[1])  # parse command information

    print("\tHostname: %s IP: %s Model: %s" % (name, host[0], model))

    # Instantiate device and set some details
    device = Device.Device(name, host[0])
    device.setDebug(False)                  #setting debug mode in Device.py
    device.setModel(model)                  #set model
    devices.append(device)                  #append device to array

    # Obtain and store running config
    obtainConfigs(conn, name, host[0])

    #Obtain and parse other information (IFStatus, version, system id)
    if retInfo:
        obtainSwitchDetails(conn, device)

    #Close SSH connection
    closeConnection(conn)

    #Parse and push data to data structure
    if retInfo:
        parseSwitchDetails(device)


after = time.time()
duration = (after - before)

print("Equipments processed: %d [Dell: %d HP: %d] in %.1f secs (~%.1f secs/device). \n" % (
len(hosts), (dellIdx - 1), (hpIdx - 1), duration, duration / nDevices))


