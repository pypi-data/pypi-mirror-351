#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: shadowshell
"""

import sys
import time
from shadowshell.logging import LoggerFactory

logger = LoggerFactory().get_logger()

def performance_monitor(class_name=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = None
            try:
                result = func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                if (class_name is not None):
                    logger.info(f"[PERFORMANCE_MONITOR][{class_name}.{func.__name__}] has ran, time elapsed:{elapsed:.6f}s.")
                else:
                    logger.info(f"[PERFORMANCE_MONITOR][{func.__name__}] has ran, time elapsed:{elapsed:.6f}s.")
                return result
        return wrapper
    return decorator

def function_monitor(class_name=None, callback=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = None
            try:
                result = func(*args, **kwargs)    
            except Exception as e:
                logger.error(e)
                raise
            except:
                logger.error(sys.exc_info()[0])
                raise
            finally:
                elapsed = time.perf_counter() - start
                # log
                if (class_name is not None):
                    logger.info(f"[FUNCTION_MONITOR][{class_name}.{func.__name__}] has ran, time elapsed:{elapsed:.6f}s.")            
                else:
                    logger.info(f"[FUNCTION_MONITOR][{func.__name__}] has ran, time elapsed:{elapsed:.6f}s.")
                
                 # callback
                if callback is not None:
                    try:
                        callback(args, kwargs, result, f"{elapsed:.6f}")
                    finally:
                        logger.error(sys.exc_info()[0])  
                        
                return result
        return wrapper
    return decorator
