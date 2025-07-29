#!/usr/bin/env python
# coding: utf-8

s = """

global __result__
def main():
    __result__ = {'x': 1}

main()
"""

gs = {'__result__': {}}
exec(s, gs)
print(gs['__result__'])



