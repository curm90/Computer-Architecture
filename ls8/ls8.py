#!/usr/bin/env python3
import sys
from cpu import *

"""Main."""
cpu = CPU()

cpu.load(sys.argv[1])
cpu.run()
