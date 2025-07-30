'''
Created on 15 Apr 2025

@author: jacklok
'''
from flask_caching import Cache

AGE_TIME_FIVE_MINUTE    = 60*5
AGE_TIME_QUATER_HOUR    = AGE_TIME_FIVE_MINUTE * 3
AGE_TIME_HALF_HOUR      = AGE_TIME_QUATER_HOUR * 2
AGE_TIME_ONE_HOUR       = AGE_TIME_HALF_HOUR * 2
AGE_TIME_TWO_HOUR       = AGE_TIME_ONE_HOUR * 2
AGE_TIME_SIX_HOUR       = AGE_TIME_ONE_HOUR * 6
AGE_TIME_ONE_DAY        = AGE_TIME_ONE_HOUR * 24

cache = Cache()

def setCache(cache_key, value, timeout=300):
    cache.set(cache_key, value, timeout=timeout)
    
def getFromCache(cache_key):
    return cache.get(cache_key)

def deleteFromCache(cache_key):
    cache.delete(cache_key)