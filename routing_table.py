'''RIP routing table module
contains functions related to creating and updating routing tables

Routing tables a represented as a list of dictionaries in the below format

     routing_table = [
        "metric: _",
        "next-hop": _,
        "dest": _,
        "timeout": _,
        "garbage": _,
        "flag": _
         ]
'''

from copy import *
from time import *
from timer import *

def reset_timeout(table, id):
    for route in table:
        if route["next-hop"] == id and route['metric'] != 16:
            route["timeout"] = 30


def init_routing_table(router):
    """Function to initialise the routing table when a router is launched
       using information from the routers configuration"""
    routing_table = []
    routes = router["output-ports"]
    for route in routes:
        route = {
            "metric": int(route[1]),
            "next-hop": int(route[2]),
            "dest": int(route[2]),
            "timeout": 30,
            "garbage": 30,
            "flag": 0
        }
        routing_table.append(route)
    return routing_table

        
def print_routing_table(table ,id):
    """Function that print the routing table in a more readable format"""
    if table:
        print("Router: " + str(id))
        print("-- Destination -- Metric -- Next Hop -- Timeout -- Garbage -- Flag -- ")
        for route in sorted(table,key = lambda i: i['dest']):
            print("        " + str(route["dest"]) + "            " + str(route["metric"]) + "          " + str(route["next-hop"]) + "          "  + str(route["timeout"]) + "        "  + str(route["garbage"]) + "         "  + str(route["flag"]))
        print("-" * 65)
        print('\n')
    else:
        print("-------------------------------------------")
        print("--------------EMPTY TABLE------------------")
        print("-------------------------------------------")


def update_timeout(table):
    """ Function updates the timeout value for every route inthe routing table
        If a route becomes invalid the metric is set to 16 and it is added to the list of
        invalid routes to be returned and sent in the triggered update.
     """
    invalid_routes = []

    for route in table:
        #Update timeout if route is still valid
        if route["timeout"] > 0:
            route["timeout"] = route["timeout"] - 5
        
        #mark route as invalid if timeout expires
        if route["timeout"] == 0 and route["flag"] == 0:
            route["metric"] = 16
            route["timeout"] = 0
            route["flag"] = 1
            invalid_routes.append(route)
    return invalid_routes


def update_routing_table(table, data, router, invalid_routes):

    #config router and route variables
    router_id = router["router-id"]
    recv_id = data["router"]
    recv_table = data["data"]

    # Check packet to see if message is triggered or timed
    if data["message-type"] == 1:
        invalid_routes = update_invalid_routes(table, recv_table, recv_id)

    else:
        recv_table = remove_invalid_routes(recv_table)
        direct_metric = update_direct_route(table, recv_table, router_id, recv_id)
        update_indirect_route(table, recv_table, router_id, recv_id, direct_metric)   

    return invalid_routes


def update_invalid_routes(table, invalid_routes, recv_id):
    """updates the routes in the table according to the invalid routes"""

    result = []
    
    for invalid_route in invalid_routes:
        for route in table:
            if route["dest"] == invalid_route["dest"] and recv_id == route["next-hop"]:
                print("ROUTE INVALIDATED")
                route["metric"] = 16
                route["timeout"] = 0
                route["flag"] = 1
                result.append(route)

    return result

def update_garbage(table):
    """Updates garbage timeout value and/or removes garbage routes if required"""
    garbage = []

    for route in table:
        if route["metric"] == 16:
            if route["garbage"] > 0:
                route["garbage"] = route["garbage"] - 5
            else:
                garbage.append(route)

    for route in garbage:
        table.remove(route)
    
    

def remove_invalid_routes(routes):
    """removes invalid routes from the data for updating better paths"""
    for route in routes:
        if route["metric"] == 16:
            routes.remove(route)
    return routes
  
def update_direct_route(table, routes, router_id, recv_id):
    """updates any direct routes to the sending router if required"""
    direct_metric = 16

    #Check if direct route exists in table and update metric is required
    for new_route in routes:
        path_updated = False
        for route in table:
            if route["dest"] == recv_id and new_route["dest"] == router_id:
                if new_route["metric"] < route["metric"] and new_route["dest"] == new_route["next-hop"]:
                    print("DIRECT ROUTE UPDATED")
                    route["next-hop"] = recv_id
                    route["metric"] = new_route["metric"]
                    route["timeout"] = 30
                    route["garbage"] = 30
                    route["flag"] = 0
                path_updated = True
                direct_metric = route["metric"]

        #add direct route to table if required
        if path_updated is False:
                if new_route["metric"] < 16 and new_route["dest"] == router_id:
                    print("DIRECT ROUTE ADDED")
                    new_route["dest"] = recv_id
                    new_route["next-hop"] = recv_id
                    new_route["timeout"] = 30
                    new_route["garbage"] = 30
                    new_route["flag"] = 0
                    table.append(new_route)
                    direct_metric = new_route["metric"]
                    path_updated = True

    return direct_metric

def update_indirect_route(table, routes, router_id, recv_id, direct_metric):
    """updates any indirect routes through the sending router to other routers if required"""

    # update existing route if metric smaller
    for new_route in routes:
        path_updated = False
        for route in table:
            if route["dest"] == new_route["dest"]:
                if route["metric"] > new_route["metric"] + direct_metric:
                    print("INDIRECT ROUTE UPDATED")
                    route["metric"] = new_route["metric"] + direct_metric
                    route["next-hop"] = recv_id
                    route["timeout"] = 30
                    route["garbage"] = 30
                    route["flag"] = 0
                path_updated = True
        
        # route dest not found so add to table if metric valid
        if path_updated is False:
            if new_route["metric"] + direct_metric < 16 and new_route["dest"] != router_id:
                print("INDIRECT ROUTE ADDED")
                new_route["metric"] = new_route["metric"] + direct_metric
                new_route["next-hop"] = recv_id
                new_route["timeout"] = 30
                new_route["garbage"] = 30
                new_route["flag"] = 0
                table.append(new_route)
                path_updated = True

    return table
                    
def split_horizon(table, dest):
    """Takes the current routing table and the id of the router 
    and if the id of the router is a next hop in the current table 
    set the metric to 16"""
    
    result = deepcopy(table)
    
    for route in result:
        if dest == route["next-hop"] and dest != route["dest"]:
            route["metric"] = 16
    
    return result      