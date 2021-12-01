#!/usr/bin/env python3

import discord
from discord.ext import tasks

from lib.db import *
from settings import *

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
			await message.reply(f"There'll be a help menu here one day.", mention_author=True)

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
				await message.reply("Something went wrong! Please report this to skat#4502. [err 1]",
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
				await message.reply("Something went wrong! Please report this to skat#4502. [err 2]",
					mention_author=True)

		else:
			await message.reply("Confused? Try running `$rufus help`.", mention_author=True)

	@tasks.loop(seconds=10)
	async def poll(self):
		"""
		Check for open seats in CRNs and notify watching users.
		"""

		channel = self.get_channel(CHANNEL)
		#await channel.send("AAAAAAAAAAHHHHHHH")

client = Client()
client.run(TOKEN)
