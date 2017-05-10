#!/usr/bin/python

#re => regular expression
import re
import sys
import urllib
import urllib.parse
import base64
import excel

#read file from stdin
with open(sys.argv[1], 'r') as f:
    read_data = f.readline()
f.close()

#build ruleset filename
excelfilename = "firewallPolicy.xlsx"
if sys.argv.__len__() >= 3:
    excelfilename = sys.argv[2]


#remove the two "&" present at the bottom of configuration string
read_data = read_data.replace("&","")
#decode base64 original base64 encoded config file
decoded_data = base64.b64decode(read_data)
#File is encoded in latin-1 (ISO-8859-2)
#'&' is the separator for each config entry
decoded_data = decoded_data.decode('latin-1').split("&")

#RULES
rules=[]
ruleID=""
ruleSrcNet=""
ruleSrcZone=""
ruleDestNet=""
ruleDestZone=""
ruleDestService=""
ruleComment=""
ruleAction=""
ruleStatus=""

prevSrcZone=""
prevDestZone=""

#ADDRESS GROUPS
addrGroups={}
groupID=""
groupObject=""

#ADDRESS OBJECTS
addrObjects={}
addrName=""
addrIP=""
addrSubnet=""
addrZone=""
addrType=""
addrID=""

#SERVICE GROUPS
serviceGroups={}
sgroupID=""
sgroupObject=""

#SERVICE OBJECTS
serviceObjects={}
serviceID=""
serviceName=""
serviceStartPort=""
serviceEndPort=""
serviceProtocol=""
serviceType=""


#read each configuration list item as line
for line in decoded_data:
    #trim leading and trailing characters for each item
    line = line.strip()
#POLICY RULES
    if re.match('^policy', line):
        #policyField - Action; ZONE; source network/host; destination network/host; destination service; Comment; Enable/disable
        #PolicyID - Id of policy
        #policyValue - Value of the Policy field
        policyField, policyID, policyValue = re.search('^policy(.*)_(\d+)=(.*)', line).groups()
        #verify if FIELD is Source Zone
        if re.match('^policySrcZone', line):
            ruleSrcZone = urllib.parse.unquote(policyValue)
        #verify if FIELD is Destination Zone
        elif re.match('^policyDstZone', line):
            ruleDestZone = urllib.parse.unquote(policyValue)
        #verify if FIELD is Source Network
        elif re.match('^policySrcNet', line):
            if policyValue:
                ruleSrcNet = policyValue
            else:
                ruleSrcNet = "Any"
        #verify if FIELD is Destination Network
        elif re.match('^policyDstNet', line):
            if policyValue:
                ruleDestNet = policyValue
            else:
                ruleDestNet = "Any"
        #verify if FIELD is Destination Service
        elif re.match('^policyDstSvc', line):
            if policyValue:
                ruleDestService = policyValue
            else:
                ruleDestService = "Any"
        #verify if FIELD is Policy Comment
        elif re.match('^policyComment', line):
            if not policyValue:
                ruleComment = "No Comment!"
            else:
                ruleComment = policyValue
        #verify if FIELD is Policy Action
        #Values:
        #Allow - 2
        #Discard - 1
        #Deny - Other
        elif re.match('^policyAction', line):
            if policyValue == "2":
                ruleAction = "Allow"
            elif policyValue == "1":
                ruleAction = "Discard"
            else:
                ruleAction = "Deny"
        #verify if FIELD is Policy Enable
        #Enabled - 1
        #Disabled - other
        elif re.match('^policyEnabled', line):
            if policyValue == "1":
                ruleStatus = "Enabled"
            else:
                ruleStatus = "Disabled"
        if ruleSrcZone and ruleDestZone and ruleSrcNet and ruleDestNet and ruleDestService and ruleAction and ruleStatus and ruleComment:
            # Sonicwall is goofy and has some enabled rules set to 0 when its an auto-added rule
            if re.match('^Auto', ruleComment) and ruleStatus == "Disabled":
                ruleStatus = "Enabled"

            #create rule (matrix)
            rule={
                "ruleID": policyID,
                "ruleSrcZone": ruleSrcZone,
                "ruleDestZone": ruleDestZone,
                "ruleSrcNet": urllib.parse.unquote(ruleSrcNet),
                "ruleDestNet": urllib.parse.unquote(ruleDestNet),
                "ruleDestService": urllib.parse.unquote(ruleDestService),
                "ruleAction": ruleAction,
                "ruleStatus": ruleStatus,
                "ruleComment": urllib.parse.unquote(ruleComment)
            }
            #Add rule to rule list
            rules.append(rule)
            #reset all rule fields
            ruleSrcZone=""
            ruleDestZone=""
            ruleSrcNet=""
            ruleDestNet=""
            ruleDestService=""
            ruleAction=""
            ruleComment=""
            ruleStatus=""

#ADDRESS GROUPS
    #Address Objects
    if re.match('^addro_', line):
        # check line for  Address Object that is part of a group (addro_atomToGrp)
        if re.match('^addro_atomToGrp_', line):
            #get groupID and groupObjectName
            groupID, groupObject = re.search('^addro_atomToGrp_(\d+)=(.*)', line).groups()
            groupObject = urllib.parse.unquote(groupObject)
            nextPattern="^addro_grpToGrp_"+groupID
            #Group ID pattern match
            nextGroupPattern=nextPattern+'=(.*)'
        #verify if line is a group definition (example: addro_grpToGrp_<ID>)
        elif re.match(nextPattern, line):
            groupName = re.search(nextGroupPattern, line).group(1)
            groupName = urllib.parse.unquote(groupName)
            #Check if group exists in addrGroups(dictionary) and creates a new group or appends to existing addrGroup
            if groupName not in addrGroups:
                addrGroups[groupName] = []
                addrGroups[groupName].append(groupObject)
            else:
                addrGroups[groupName].append(groupObject)

#ADDRESS OBJECTS
    #verify if line is an Address Object (addrObj)
    if re.match('^addrObj', line):
        #verify if line is objectId
        if re.match('^addrObjId_', line):
            #Get address ID and Address Name
            addrID, addrName = re.search('^addrObjId_(.*)=(.*)', line).groups()
            addrName = urllib.parse.unquote(addrName)
        #gets addrType ID of object matched before
        elif re.match(str("^addrObjType_"+addrID), line):
            addrType = re.search(str("^addrObjType_"+addrID+"=(.*)"), line).group(1)
        #gets Object Zone of object matched before
        elif re.match(str("^addrObjZone_"+addrID), line):
            addrZone = re.search(str("^addrObjZone_"+addrID+"=(.*)"), line).group(1)
            if addrZone == "":
                addrZone = "None"
        #gets ObjectIP of object matched before
        elif re.match(str("^addrObjIp1_"+addrID), line):
            addrIP = re.search(str("^addrObjIp1_"+addrID+"=(.*)"), line).group(1)
        #gets ObjectSubnet of object matched before
        elif re.match(str("^addrObjIp2_"+addrID), line):
            addrSubnet = re.search(str("^addrObjIp2_"+addrID+"=(.*)"), line).group(1)
        #checks if all object components are present
        if addrID and addrName and addrType and addrZone and addrIP and addrSubnet:
            #creates addrObject (dictinary)
            addrObjects[addrName] = {
                "addrZone": addrZone,
                "addrIP": addrIP,
                "addrSubnet": addrSubnet,
                "addrType": addrType
            }
            #reset all object fields
            addrID=""
            addrName=""
            addrType=""
            addrIP=""
            addrZone=""
            addrSubnet=""

#SERVICE GROUPS
    #verify if line is a service Group (so_)
    if re.match('^so_', line):
        #check line for  Service Object that is part of a group (so_atomToGRp)
        if re.match('^so_atomToGrp_', line):
            #get service Group ID and service group name
            sgroupID, sgroupObject = re.search('^so_atomToGrp_(\d+)=(.*)', line).groups()
            sgroupObject = urllib.parse.unquote(sgroupObject)
            nextsPattern="^so_grpToGrp_"+sgroupID
            # group ID pattern match
            nextsGroupPattern=nextsPattern+'=(.*)'
        #verify if line is a service group definition (example: so_grpToGrp_<ID>)
        elif re.match(nextsPattern, line):
            sgroupName = re.search(nextsGroupPattern, line).group(1)
            sgroupName = urllib.parse.unquote(sgroupName)
            #Check if service group exists in serviceGroups(dictionary) and creates a new group or appends to existing serviceGroups
            if sgroupName not in serviceGroups:
                serviceGroups[sgroupName] = []
                serviceGroups[sgroupName].append(sgroupObject)
            else:
                serviceGroups[sgroupName].append(sgroupObject)

#SERVICE OOBJECTS
    #verify if line is a service Object (svcObj)
    if re.match('^svcObj', line):
        #verify if line is service object ID
        if re.match('^svcObjId_', line):
            #extracts service ID and service name
            serviceID, serviceName = re.search('^svcObjId_(.*)=(.*)', line).groups()
            serviceName = urllib.parse.unquote(serviceName)
        #verify if line is service type of service object ID matched before
        elif re.match(str("^svcObjType_"+serviceID), line):
            serviceType = re.search(str("^svcObjType_"+serviceID+"=(.*)"), line).group(1)
        #verify if line is service protocol of service object ID matched before
        elif re.match(str("^svcObjIpType_"+serviceID), line):
            serviceProtocol = re.search(str("^svcObjIpType_"+serviceID+"=(.*)"), line).group(1)
        #verify if line is start port of service object ID matched before
        elif re.match(str("^svcObjPort1_"+serviceID), line):
            serviceStartPort = re.search(str("^svcObjPort1_"+serviceID+"=(.*)"), line).group(1)
        #verify if line is end port of service object ID matched before
        elif re.match(str("^svcObjPort2_"+serviceID), line):
            serviceEndPort = re.search(str("^svcObjPort2_"+serviceID+"=(.*)"), line).group(1)
        #checks if all object components are present
        if serviceID and serviceName and serviceProtocol and serviceStartPort and serviceEndPort:
            #create service Object
            #service is group
            if serviceType == "2":
                serviceProtocol = "NA"
                serviceType = "Group"
                serviceEndPort = "NA"
                serviceStartPort = "NA"
            #service is object
            elif serviceType == "1":
                serviceType = "Object"
            if serviceProtocol == "17":
                serviceProtocol = "UDP"
            elif serviceProtocol == "6":
                serviceProtocol = "TCP"
            elif serviceProtocol == "57":
                serviceProtocol = "GRE"
            elif serviceProtocol == "50":
                serviceProtocol = "ESP"
            elif serviceProtocol == "2":
                serviceProtocol = "IGMP"
            elif serviceProtocol == "1":
                serviceProtocol = "ICMP"
            elif serviceProtocol == "41":
                serviceProtocol = "6over4"
            elif serviceProtocol == "58":
                serviceProtocol = "ICMPv6"
            elif serviceProtocol == "51":
                serviceProtocol = "AH"
            #populates service details
            serviceObjects[serviceName] = {
                "serviceStartPort": serviceStartPort,
                "serviceEndPort": serviceEndPort,
                "serviceProtocol": serviceProtocol,
                "serviceType": serviceType
            }
            #reset service objects field
            serviceID=""
            serviceName=""
            serviceStartPort=""
            serviceEndPort=""
'''
print ("==========================================================")
print ("================== Firewall Rules ========================")
print ("==========================================================")
print ("")
print ("RuleID,Source Zone,Dest Zone,Source Net,Dest Net, Dest Service, Action, Status, Comment")
for x in rules:
    if x["ruleSrcZone"] != prevSrcZone or x["ruleDestZone"] != prevDestZone:
        print ('\n\nSource Zone: %s, Dest Zone: %s' % (x["ruleSrcZone"], x["ruleDestZone"]))
    print ('%s,%s,%s,%s,%s,%s,%s,%s' % (x["ruleSrcZone"], x["ruleDestZone"], x["ruleSrcNet"], x["ruleDestNet"], x["ruleDestService"], x["ruleAction"], x["ruleStatus"], x["ruleComment"]))
    prevSrcZone=x["ruleSrcZone"]
    prevDestZone=x["ruleDestZone"]

print ("")
print ("==========================================================")
print ("================== Address Objects =======================")
print ("==========================================================")
print ("")
print ("Address Name,Zone,IP,Subnet")
oAddrObjects = collections.OrderedDict(sorted(addrObjects.items()))
#for addr,addrFields in oAddrObjects.iteritems():
for addr,addrFields in oAddrObjects.items():
    #checks if address Object is not a Group (Group addrType==8)
    if addrFields["addrType"] == '1':
        print ('%s,%s,%s,%s' % (addr, addrFields["addrZone"], addrFields["addrIP"], addrFields["addrSubnet"]))

print ("")
print ("==========================================================")
print ("================== Address Groups ========================")
print ("==========================================================")
print ("")
#for group,groupObjects in addrGroups.iteritems():
for group,groupObjects in addrGroups.items():
    print (group)
    for groupObj in groupObjects:
        print ("\t%s" % groupObj)
    print ("")

print ("")
print ("==========================================================")
print ("================== Service Objects =======================")
print ("==========================================================")
print ("")
print ("Service Name, Start Port, EndPort, Protocol, ObjectType")
oServiceObjects = collections.OrderedDict(sorted(serviceObjects.items()))
#for service,serviceFields in oServiceObjects.iteritems():
for service,serviceFields in oServiceObjects.items():
    print ('%s,%s-%s,%s,%s' % (service, serviceFields["serviceStartPort"], serviceFields["serviceEndPort"], serviceFields["serviceProtocol"], serviceFields["serviceType"]))

print ("")
print ("==========================================================")
print ("================== Service Groups ========================")
print ("==========================================================")
print ("")
#for serviceGroup,serviceGroupObjects in serviceGroups.iteritems():
for serviceGroup,serviceGroupObjects in serviceGroups.items():
    print (serviceGroup)
    for serviceObj in serviceGroupObjects:
        #print serviceObj
        print ("\t%s" % serviceObj)
    print ("")
'''
excelhHandler = excel.excelHelper(rules, addrObjects, addrGroups, serviceObjects, serviceGroups)
excelhHandler.createWorkbook()
excelhHandler.writeData(excelfilename)