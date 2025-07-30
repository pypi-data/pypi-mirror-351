#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2025 <> All Rights Reserved
# https://github.com/hailiang-wang/python-env3
#
# File: /c/Users/Administrator/courses/LLMs/ollama-get-started/langchain/env.py
# Author: Hai Liang Wang
# Date: 2025-05-28:13:08:18
#
#===============================================================================

"""
Support env file format
* all values are injected as string.

```
# COMMENT
FOO=BAR
```

NOT SUPPORT
```
FOO=BAR # COMMENT
```
"""
__copyright__ = "Copyright (c) 2020 . All Rights Reserved"
__author__ = "Hai Liang Wang"
__date__ = "2025-05-28:13:08:18"

import os, sys
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

if sys.version_info[0] < 3:
    raise RuntimeError("Must be using Python 3")
else:
    unicode = str

# ENV object, https://blog.csdn.net/ad72182009/article/details/116117744
ENVIRON = os.environ.copy()


def print_env(env_obj):
    '''
    Print env key values
    '''
    print(env_obj)
    for x in env_obj.keys():
        print("%s=%s" % (x, env_obj[x]))

def parse_env(dotenv_file):
    '''
    Parse env file, inject values into ENV
    '''
    print("[env.py] parse_env: %s" % dotenv_file)

    with open(dotenv_file, mode="r", encoding="utf-8") as fin:
        lines = fin.readlines()
        for x in lines:
            y = x.strip()
            if y.startswith("#") or y.startswith("//") or y.startswith("="): continue
            if not "=" in y: continue
            spls = y.split('=', 1)
            if len(spls) == 2:
                ENVIRON[spls[0]] = spls[1]
            else:
                print("[env.py] skip invalid format: %s" % y)
        
        return ENVIRON

def read_env(dotenv_file = None):
    '''
    Read ENV
    1) first, try to read env from argv
    2) second, try to read env from cwd dir
    3) third, try to read env from ~/.env
    '''
    if not dotenv_file:
        default_env = os.path.join(os.getcwd(), ".env")
        print("[env.py] Read default env", default_env)
        if not os.path.exists(default_env):
            print("[env.py] WARN cwd env not present %s" % default_env)
        else:
            return parse_env(default_env)

        from pathlib import Path
        HOME_DIRECTORY = Path.home()
        default_env2 = os.path.join(HOME_DIRECTORY, ".env")

        if not os.path.exists(default_env2):
            print("[env.py] .env file default path not present at %s and %s"% (default_env, default_env2))
        else:
            return parse_env(default_env2)
        
        return ENVIRON
    else:
        if not os.path.exists(dotenv_file):
            raise BaseException("[env.py] .env file path not present with argv: " + dotenv_file)
        return parse_env(dotenv_file)
    

def load_env(dotenv_file = None):
    '''
    First read env, then inject ENV into os.environ
    '''
    ENV = read_env(dotenv_file=dotenv_file)
    for k in ENV.keys():
        os.environ[k] = ENV.get(k)

    return ENV