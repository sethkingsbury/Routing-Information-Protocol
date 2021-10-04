import sys
from socket import *
from select import *
from time import *
from timer import *
from configuration import *
from routing_table import *
from pickle import *
from copy import *
'''Router module contians main functionality with sending and receiving
and binding sockets. Also includeds creating 
the packet and packet checks.
Created by Ashley Freeman and Seth Kingsbury
26/04/2021'''

IP = '127.0.0.1'

########################### ROUTING ###########################

def bind_sockets(ports):
    """Takes a list of port numbers and returns of list of
    UDP sockets bound to these ports"""
    result = []
    for port in ports:
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind(('localhost', port))
        result.append(s)
    return result

def recvSockets(router, input_sockets):
    '''binds the sockets to the input ports and recieves the packet'''
    outputs = []
        
    read, write, excep = select(input_sockets, outputs, input_sockets, 3)
        
    for s in read:
        try:
            data, (_, send_port) = s.recvfrom(1024)
            message = loads(data)
            return message
        except:
            pass
            
def sendSockets(router, table, send_socket, message_type):
    '''sends the given table to each output port'''
    
    for output_port in router['output-ports']:
        port = output_port[0]
        packet = create_packet(split_horizon(table, output_port[2]), router, message_type)
        message = dumps(packet)
        try:
            send_socket.sendto(bytes(message),(IP,port))
        except:
            pass

def create_packet(data, router, message_type):
    """returns a packet to be sent by the router"""
    packet = {
        "version": 2,
        "router": router["router-id"],
        "message-type": message_type,
        "data" : data
    }
    return packet
    
def packet_checks(packet):
    '''Checks the given packet to make sure fixed values are correct'''
    
    packet_correct = True
    table = packet['data']
    
    if packet["version"] != 2:
        packet_correct = False
        print("Packet version number inccorrect")
        
    elif packet["router"] < 1 or packet["router"] > 7:
        packet_correct = False
        print("Packet router number inccorrect")
        
    elif packet["message-type"] < 0 or packet['message-type'] > 1:
        packet_correct = False
        print("Packet message type inccorrect")
        
    #checking table values
    for route in table:
        if route['metric'] > 16 or route['metric'] < 1:
            packet_correct = False
            print("Route metric inccorrect")
            
        elif route['next-hop'] < 1 or route['next-hop'] > 7:
            packet_correct = False
            print("Next hop inccorrect")
            
        elif route['dest'] < 1 or route['dest'] > 7:
            packet_correct = False
            print("Route destination inccorrect")
            
        elif route['timeout'] < 0 or route['timeout'] > 30 :
            packet_correct = False
            print("Route timout inccorrect")
            
        elif route['garbage'] < 0 or route['garbage'] > 30:
            packet_correct = False
            print("Route garbage inccorrect")
            
        elif route['flag'] < 0 or route['flag'] > 1:
            packet_correct = False
            print("Route flag inccorrect")
        
    return packet_correct

          
########################### PROGRAM EXECUTION ###########################

def main():
    #parse router config and create and print inital routing table
    router = parse_config(sys.argv[1])
    table = init_routing_table(router)
    print_routing_table(table, router["router-id"])

    #set the timers
    timeout = timeout_timer()
    trig_timer = triggered_timer()

    #bind sockets
    sockets = bind_sockets(router['input-ports'])
    sendSockets(router, table, sockets[0], 0)

    indirect_invalid_routes = []

    while True:
        if (time.time() > timeout):
            # Send the timed update message
            sendSockets(router, table, sockets[0], 0)
            direct_invalid_routes = update_timeout(table)
            update_garbage(table)
            print_routing_table(table, router["router-id"])
            #send initial triggered update if required 
            if direct_invalid_routes:
                print("INITIAL TRIGGERED UPDATE")
                sendSockets(router, direct_invalid_routes, sockets[0], 1)
                direct_invalid_routes = []
            timeout = timeout_timer()

        data = recvSockets(router, sockets)
        if data:
            correct_packet = packet_checks(data)
            
        if data and correct_packet:
            reset_timeout(table, data["router"])
            indirect_invalid_routes = update_routing_table(table, data, router, indirect_invalid_routes)
            if time.time() > trig_timer:
                if indirect_invalid_routes:
                    print("SECONDARY TRIGGERED UPDATE")
                    sendSockets(router, indirect_invalid_routes, sockets[0], 1)
                    indirect_invalid_routes = []
            
main()
