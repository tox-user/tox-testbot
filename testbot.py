#!/usr/bin/python

from __future__ import print_function
import sys
from bot import *


num_args = len(sys.argv)
for i in range(num_args):
	if i == 0:
		continue

	if sys.argv[i] == "-b" or sys.argv[i] == "--num-bots":
		if i < num_args - 1:
			NUM_BOTS = int(sys.argv[i+1])
			if NUM_BOTS < 1:
				NUM_BOTS = 1

	if sys.argv[i] == "-i" or sys.argv[i] == "--num-iterations":
		if i < num_args - 1:
			NUM_ITERATIONS = int(sys.argv[i+1])
			if NUM_ITERATIONS < 0:
				NUM_ITERATIONS = 0

	if sys.argv[i] == "-h" or sys.argv[i] == "--help":
		print("Runs multiple Tox bots that talk to each other.\n\n\
Options:\n\
  -h, --help            prints this help message\n\
  -b, --num-bots        sets number of bots\n\
  -i, --num-iterations  sets number of loop instances required for bots to do a random conference action")
		exit()

for i in range(0, NUM_BOTS):
	thread = BotThread(i)
	thread.daemon = True
	thread.start()

try:
	while True:
		sleep(100)
except KeyboardInterrupt:
	print("Interrupted by user. Exiting.")
