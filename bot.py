from pytox import Tox
import threading
from time import sleep
from random import randint
from globalvars import *


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


class BotThread (threading.Thread):
	def __init__(self, thread_id, num_iterations, external_tox_id):
		threading.Thread.__init__(self)
		self.thread_id = thread_id
		self.external_friend = external_tox_id
		self.num_iterations = num_iterations

	def run(self):
		opts = ToxOptions()
		bot = TestBot(self.thread_id, self.num_iterations, self.external_friend, opts)
		bot.loop()


class TestBot(Tox):
	def __init__(self, bot_id, num_iterations, external_tox_id, opts=None):
		if opts is not None:
			super(TestBot, self).__init__(opts)

		self.bot_id = bot_id
		self.external_friend = external_tox_id
		self.num_iterations = num_iterations

		self.self_set_name(str("testbot%d" % bot_id))
		tox_id = self.self_get_address()
		bot_public_keys.append(tox_id)
		print("ID: %s" % tox_id)

		self.connect()

	def connect(self):
		print("%d connecting..." % self.bot_id)
		self.bootstrap(SERVER[0], SERVER[1], SERVER[2])

	def loop(self):
		checked = False
		iterations = 0

		while True:
			status = self.self_get_connection_status()

			if not checked and status:
				print("%d connected to DHT" % self.bot_id)
				checked = True
				self.conference_new()

				external_friend = self.external_friend
				if external_friend and external_friend != "":
					try:
						print("%d adding external ID %s" % (self.bot_id, external_friend))
						self.friend_add(external_friend, "hi")
					except:
						pass

				for friend in bot_public_keys:
					if friend == self.self_get_address():
						continue

					print("%d adding friend %s" % (self.bot_id, friend))
					try:
						self.friend_add(friend, "hi")
					except:
						pass

			if status:
				friends = self.self_get_friend_list()
				for friend in friends:
					if self.friend_get_connection_status(friend):
						try:
							self.conference_invite(friend, 0)
						except:
							pass

			if checked and not status:
				print("%d disconnected from DHT" % self.bot_id)
				self.connect()
				checked = False

			iterations += 1
			if iterations >= self.num_iterations:
				iterations = 0
				self.random_group_action()

			self.iterate()
			sleep(0.01)

	def on_friend_request(self, pk, message):
		self.friend_add_norequest(pk)
		print("%d accepted friend request from %s" % (self.bot_id, pk))

	def on_conference_invite(self, friendId, type, cookie):
		self.conference_join(friendId, cookie)
		#print("%d accepted group invite from friend %d" % (self.bot_id, friendId))

	def on_friend_connection_status(self, friendId, status):
		if status:
			groups = self.conference_get_chatlist()
			if len(groups) > 0:
				self.conference_invite(friendId, 0)
				print("%d inviting friend %d to a group" % (self.bot_id, friendId))

	def random_group_action(self):
		groups = self.conference_get_chatlist()
		if len(groups) <= 0 and not self.self_get_connection_status():
			return

		rand = randint(0,2)
		if rand == 0:
			for group in groups:
				if group != 0:
					self.conference_delete(group)
			print("%d leaves all groups" % self.bot_id)
		elif rand == 1:
			name = "testbot%d" % randint(0,999)
			self.self_set_name(name)
			print("%d changes name to %s" % (self.bot_id, name))
		elif rand == 2:
			self.self_set_name("")
			print("%d changes name to an empty string" % self.bot_id)
