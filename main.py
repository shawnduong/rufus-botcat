#!/usr/bin/env python3

import discord
import json

from discord.ext import tasks
from threading import Thread

from lib.db import *
from lib.scrape import *
from settings import *

helpDialogue  = "Hi, I'm Rufus Botcat. I monitor classes and alert you when seats open up. Here's how to use me:\n"
helpDialogue += "- `$rufus help` - Display this message.\n"
helpDialogue += "- `$rufus list` - List all CRNs you're watching.\n"
helpDialogue += "- `$rufus watch <CRN>` - Start watching a specific CRN.\n"
helpDialogue += "- `$rufus unwatch <CRN>` - Stop watching a specific CRN.\n"

URLs = json.loads(open("URLs.json").read())

class Client(discord.Client):

	async def on_ready(self):
		print(f":: Logged in as {self.user.name}")
		print(f":: -> User ID: {self.user.id}")
		self.poll.start()

	async def on_message(self, message):
		"""
		Primary handler for all commands. The prefix is "$rufus" to get the
		bot's attention.
		"""

		tokens = message.content.split()

		# Command prefix is "$rufus."
		if tokens[0] != "$rufus":
			return

		# $rufus help
		if len(tokens) == 2 and tokens[1] == "help":
			try:
				await message.reply(helpDialogue, mention_author=True)
			except:
				await message.reply("Something went wrong! Please report this to skat#4502. [err 0]",
					mention_author=True)

		# $rufus list
		elif len(tokens) == 2 and tokens[1] == "list":

			try:

				entries = session.query(Watcher).filter_by(userID=message.author.id)

				msg  = "You're currently watching the following CRNs:\n"
				msg += "- " + "\n- ".join([str(entry.CRN) for entry in entries])
				await message.reply(msg, mention_author=True)

			except:
				await message.reply("Something went wrong! Please report this to skat#4502. [err 1]",
					mention_author=True)

		# $rufus watch <CRN>
		elif len(tokens) == 3 and tokens[1] == "watch":

			try:

				# CRNs are all 5 numerical digits.
				tokens[2] = int(tokens[2])
				assert tokens[2] <= 99999 and tokens[2] >= 10000, "Out of bounds CRN."

				# Add the user to the DB.
				watcher = Watcher(message.author.id, tokens[2])
				session.add(watcher)
				session.commit()

				await message.reply(f"I'll give you an @ when course CRN {tokens[2]} opens up!",
					mention_author=True)

			except:
				await message.reply("Something went wrong! Please report this to skat#4502. [err 2]",
					mention_author=True)

		# $rufus unwatch <CRN>
		elif len(tokens) == 3 and tokens[1] == "unwatch":

			try:

				# CRNs are all 5 numerical digits.
				tokens[2] = int(tokens[2])
				assert tokens[2] <= 99999 and tokens[2] >= 10000, "Out of bounds CRN."

				# Check if the entry exists in the DB. If it does, then remove it.
				entry = session.query(Watcher).filter_by(userID=message.author.id, CRN=tokens[2]).first()

				if not entry:
					await message.reply(f"You weren't watching {tokens[2]} in the first place.",
						mention_author=True)
				else:
					session.delete(entry)
					session.commit()
					await message.reply(f"I won't alert you for {tokens[2]} anymore.",
						mention_author=True)

			except:
				await message.reply("Something went wrong! Please report this to skat#4502. [err 3]",
					mention_author=True)

		else:
			await message.reply("Confused? Try running `$rufus help`.", mention_author=True)

	@tasks.loop(seconds=10)
	async def poll(self):
		"""
		Check for open seats in CRNs and notify watching users.
		"""

		print(":: Scraping and alerting...", end=" ")

		# Scrape all CRNs being watched.

		threads = []
		outputs = {}

		for CRN in session.query(Watcher.CRN).distinct():
			CRN = CRN[0]
			if str(CRN) in URLs.keys():
				threads.append(Thread(target=scrape, args=(CRN, URLs[str(CRN)], outputs)))

		for thread in threads: thread.start()
		for thread in threads: thread.join()

		# Ping all users that were watching CRNs.

		channel = self.get_channel(CHANNEL)

		for k in outputs.keys():

			if outputs[k] > 0:

				msg = ""
				watchers = session.query(Watcher).filter_by(CRN=k).distinct()

				for watcher in watchers:
					msg += f"<@{watcher.userID}> "

				msg += f"\n**CRN {k} has {outputs[k]} open seat(s)!**"
				await channel.send(msg)

		print("Done.")

client = Client()
client.run(TOKEN)
