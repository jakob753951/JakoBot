import random
from datetime import datetime, timedelta
import json
import discord
from discord.ext import commands
from Configuration import *

requirements = {'general': [], 'server': ['confirm_reaction', 'days_inactivity_before_role']}

class Drops(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')
		try:
			with open('data/Drops.json', 'r') as data_file:
				self.data = json.loads(data_file.read())
		except Exception as e:
			print(f'Error when loading Drops.json: {e}')
			self.data = {}

	@commands.Cog.listener()
	async def on_message(self, message):
		if not str(message.channel.id) in self.data:
			return

		# Get the data for the channel the message was sent in
		channel_data = self.data[str(message.channel.id)]

		# Check that channel has not had a drop recently
		last_message_time = channel_data['last_drop']
		available_time = last_message_time + timedelta(minutes=channel_data['minute_difference'])

		if not available_time < datetime.now():
			return

		# Check against chance
		if not random.random() < float(float(1)/int(channel_data['chance'])):
			return

		# If we reach this point, we should make a drop

		# Get drop type

		# Get value

		# Add drop to channel

	@commands.command(name='AddDrops')
	async def add_drops(self, ctx, channel: discord.TextChannel = None, chance = '100'):
		if not channel:
			channel = ctx.channel

		channel_data = {'drop_chance': int(chance), 'last_drop': "1970-01-01T00:00:00"}

		self.data[str(channel.id)] = channel_data
		await ctx.message.add_reaction(self.cfg.servers[ctx.guild.id].confirm_reaction)


def setup(bot):
	bot.add_cog(Drops(bot))