''' RIP configuration module
 contains functions related to parsing router info from configuration files

Configuration files are in the format

 router-id 1
input-ports 2001, 2002, 2003
outputs 2004-1-2, 2014-5-6, 2015-8-7

router-id: The id of the router 

input-ports: The set of port numbers on which the 
            router will listen for incoming packets
outputs: contact info for neighbouring routers
         first value is input port of neighbouring router
         second value is metric for that peer to peer link
         third value is router-id of the peer router       
Created by Ashley Freeman and Seth Kingsbury'''

import sys
        
def parse_config(filename):
    """takes the config file for a router as input and 
    outputs the parsed values"""
    file = open(filename)
    lines = file.readlines()
    result = {}
    result['router-id'], result['input-ports'] , result['output-ports'] = config_checks(lines)
    return result

def parse_id(line):
    """Parses the router-id from the config file"""
    return int(line.strip().split()[1])
    
def parse_inputs(line):
    """Parses the input ports from the config file"""
    line = line.strip().split()[1:]
    return [int(port.strip(',')) for port in line]
    

def parse_outputs(line):
    """Parses the output data from the config file"""
    line = line.strip().split()[1:]
    outputs = []
    for output in line:
        output = output.strip(',').split('-')
        for num in range(3):
            output[num] = int(output[num])
        if output[0] < 1024 or output[0] > 64000:
            raise RuntimeError
        outputs.append(output)
    return outputs

def config_checks(config):
    """Checks validity of the configuration file"""
    try:
        if len(config) != 3:
            raise RuntimeError
        rid = parse_id(config[0])
        inputs = parse_inputs(config[1])
        outputs = parse_outputs(config[2])

        for i in inputs:
            if i < 1024 or i > 64000:
                raise RuntimeError

        return rid, inputs, outputs

    except:
        print("\nThe Conifguration File provided is of an invalid format!\n")
        print("Configuration file should be of the following format:\n")
        print("\trouter-id 1\n\tinput-ports 2001, 2002, 2003\n\toutputs 2004-1-2, 2014-5-6, 2015-8-7\n")
        print("\trouter-id is an integer representing the id of the router")
        print("\tinput-ports is the set of port numbers on which the router will listen for incoming updates, these should lie between 1024 and 64000")
        print("\toutput-ports is a list of contact information for neighbouring routers e.g 2004-1-2:\n")
        print("\t\t2004 represents the input port of the neighbouring router")
        print("\t\t1 represents the metric value for the link")
        print("\t\t2 represents the id of the neigbouring router.\n")
        sys.exit(1)
