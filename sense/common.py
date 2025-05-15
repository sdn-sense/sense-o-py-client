#!/usr/bin/env python3
"""Common functions for SENSE-0 API Client"""
import os
import inspect
import time
import json
from yaml import safe_load as yload

def functionwrapper(func):
    """Function wrapper to print start/runtime/end"""
    def wrapper(*args, **kwargs):
        if isDebugSet():
            print(f"[WRAPPER][{time.time()}] Enter {func.__qualname__}, {func.__code__.co_filename}")
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = end_time - start_time
            print(f"[WRAPPER][{time.time()}] Function {func.__qualname__} {args} {kwargs} Took {total_time:.4f} seconds")
            print(f"[WRAPPER][{time.time()}] Leave {func.__qualname__}")
        else:
            result = func(*args, **kwargs)
        return result

    return wrapper

def classwrapper(cls):
    """Class wrapper to print all functions start/runtime/end"""
    for name, method in cls.__dict__.items():
        if callable(method) and name != "__init__":
            if inspect.isfunction(method):
                if inspect.signature(method).parameters.get('self'):
                    setattr(cls, name, functionwrapper(method))
            elif inspect.ismethod(method):
                if inspect.signature(method).parameters:
                    firstParam = next(iter(inspect.signature(method).parameters))
                    if firstParam == 'self':
                        setattr(cls, name, functionwrapper(method))
    return cls

def loadJSON(path):
    """Load JSON file"""
    ret = None
    with open(path, 'r', encoding="utf-8") as fd:
        ret = json.load(fd)
    return ret

def isDebugSet():
    """Check if debug is set"""
    if os.environ.get('SENSE_FULL_DEBUG'):
        return True
    return False

def loadYamlFile(fname):
    """Load Yaml file"""
    try:
        with open(fname, 'r', encoding='utf-8') as fd:
            return yload(fd.read())
    except Exception as e:
        print(f"Error loading yaml file: {fname}. Error: {e}")
    return {}

def getConfig(configFile='/etc/sense-o-auth.yaml'):
    """Get SENSE Auth config file"""
    if os.getenv('SENSE_AUTH_OVERRIDE'):
        configFile = os.getenv('SENSE_AUTH_OVERRIDE')
        if not os.path.isfile(configFile):
            raise Exception(f"SENSE_AUTH_OVERRIDE env flag set, but file not found: {configFile}")
    elif not os.path.isfile(configFile):
        configFile = os.getenv('HOME') + '/.sense-o-auth.yaml'
        if not os.path.isfile(configFile):
            raise Exception(f"Config file not found: {configFile}")
    return loadYamlFile(configFile)

def getHTTPTimeout():
    """Get HTTP Timeout from env or default to 300 seconds"""
    return int(os.environ.get('SENSE_TIMEOUT', 300))

def getHTTPRetries():
    """Get HTTP Retries from env or default to 1"""
    return int(os.environ.get('SENSE_RETRIES', 1))
