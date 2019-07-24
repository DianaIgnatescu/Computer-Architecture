#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

if len(sys.argv) is not 2:
    print("Missing second argument. Try typing python ls8.py example/mult.ls8")
    sys.exit(1)

cpu = CPU()

cpu.load(sys.argv[1])
cpu.run()
