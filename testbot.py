#!/usr/bin/python

from __future__ import print_function

import sys
from pytox import Tox, ToxAV

from time import sleep
from random import randint

SERVER = [
	"127.0.0.1",
	33445,
	"F404ABAA1C99A9D37D61AB54898F56793E1DEF8BD46B1038B9D822E8460FAB67"
]

FRIENDS = []


class ToxOptions():
	def __init__(self):
		self.ipv6_enabled = False
		self.udp_enabled = True
		self.local_discovery_enabled = True
		self.proxy_type = 0 # 1=http, 2=socks
		self.proxy_host = ""
		self.proxy_port = 0
		self.start_port = 0
		self.end_port = 0
		self.tcp_port = 0
		self.savedata_type = 0 # 1=toxsave, 2=secretkey
		self.savedata_data = b""
		self.savedata_length = 0


class Bot(Tox):
	group_joined = False

	def __init__(self, opts=None):
		if opts is not None:
			super(Bot, self).__init__(opts)

		self.self_set_name("OfflineBot")
		print("ID: %s" % self.self_get_address())
		self.connect()

	def connect(self):
		print("connecting...")
		self.bootstrap(SERVER[0], SERVER[1], SERVER[2])
		self.conference_new()


	def loop(self):
		checked = False
		iterations = 0

		while True:
			status = self.self_get_connection_status()

			if not checked and status:
				print("connected to DHT")
				checked = True
				for i in range(len(FRIENDS)):
					if i <= 0:
						continue
					print("adding friend %s" % FRIENDS[i])
					try:
						self.friend_add(FRIENDS[i], "Hi")
					except:
						pass

			if checked and not status:
				print("disconnected from DHT")
				self.connect()
				checked = False

			iterations += 1
			if iterations >= 4:
				iterations = 0
				self.random_group_action()

			friend_list = self.self_get_friend_list()
			for friend in friend_list:
				self.conference_invite(friend, 0)

			self.iterate()
			sleep(0.01)

	def on_friend_request(self, pk, message):
		print("friend request from %s: %s" % (pk, message))
		self.friend_add_norequest(pk)
		print("accepted")

	def on_conference_invite(self, friendId, type, cookie):
		self.conference_join(friendId, cookie)
		print("accepted group invite from %d" % friendId)
		self.group_joined = True

	def random_group_action(self):
		rand = randint(0,2)

		if rand == 0:
			if self.group_joined:
				self.conference_delete(0)
			else:
				self.random_group_action()
		elif rand == 1:
			self.self_set_name("testbot")
		elif rand == 2:
			self.self_set_name("")

opts = None
opts = ToxOptions()
opts.udp_enabled = True

if len(sys.argv) > 1:
	FRIENDS = sys.argv

t = Bot(opts)
t.loop()

