'''RIP timer module
contains functions related to setting timers'''

import time, random

TIMEOUT_TIMER = 5
GARBAGE_TIMER = 30
OFFSET = random.randint(0, 2)

def timeout_timer():
    """Timeout to determine if route becomes invalid"""
    return time.time() + TIMEOUT_TIMER + OFFSET


def garbageCollectionTimer():
    """Garbage collection timer for route deletion process"""
    return time.time() + GARBAGE_TIMER

def triggered_timer():
    """Timer to wait for all route changes after sending a triggered update"""
    return time.time() + random.randint(1, 5)