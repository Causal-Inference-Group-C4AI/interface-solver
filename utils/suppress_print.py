import os
import sys


def blockPrint():
    sys.stdout = open(os.devnull, 'w')


def enablePrint():
    sys.stdout = sys.__stdout__


def suppress_print(func):
    def wrapper(*args, **kwargs):
        blockPrint()
        try:
            result = func(*args, **kwargs)
        finally:
            enablePrint()
        return result
    return wrapper
