from configuration import *
from routing_table import *


"""
routing_table = [
        "metric: _",
        "next-hop": _,
        "dest": _,
        "timeout": _,
        "garbage": _,
        "flag": _
         ]
"""

def test_initial_expired_route():
    table = [
        {'metric': 1, 'next-hop': 2, 'dest': 2, 'timeout': 0, "garbage" : 30, 'flag': 0}
    ]

    invalid_routes = update_timeout(table)

    assert invalid_routes == [
        {'metric': 16, 'next-hop': 2, 'dest': 2, 'timeout': 0, "garbage" : 30, 'flag': 1}
    ]

    assert table == [
        {'metric': 16, 'next-hop': 2, 'dest': 2, 'timeout': 0, "garbage" : 30, 'flag': 1}
    ]


def test_update_timeout_not_expired():
    table = [
        {'metric': 1, 'next-hop': 2, 'dest': 2, 'timeout': 20, 'flag': 0}
    ]

    invalid_routes = update_timeout(table)

    assert invalid_routes == []

    assert table == [
        {'metric': 1, 'next-hop': 2, 'dest': 2, 'timeout': 15, 'flag': 0}
    ]

def test_config():
    router = parse_config("test-1")
    table = init_routing_table(router)

    assert table == [
        {'metric': 1, 'next-hop': 2, 'dest': 2, 'timeout': 30, 'garbage': 30, 'flag': 0},
        {'metric': 5, 'next-hop': 6, 'dest': 6, 'timeout': 30, 'garbage': 30, 'flag': 0},
        {'metric': 8, 'next-hop': 7, 'dest': 7, 'timeout': 30, 'garbage': 30, 'flag': 0}
    ]


def main():

    #CONFIGURATION TEST
    test_config()


    # UPDATE TESTS
    test_initial_expired_route()
    test_update_timeout_not_expired()
    print("Tests successful")
main()