import discord
from discord.ext import commands, tasks
from Configuration import *
import json
from datetime import datetime, timedelta

class Inactivity(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')
		try:
			with open('Inactivity/activity.json', 'r') as data_file:
				self.activity = json.loads(data_file.read())
		except:
			self.activity = {}

		self.write_to_file.start()
		self.assign_role.start()

	@commands.Cog.listener()
	async def on_message(self, message):
		server_cfg = self.cfg.servers[message.guild.id]
		role = message.guild.get_role(server_cfg.role_lurker)
		if role in message.author.roles:
			return

		self.activity[message.author.id] = message.created_at.isoformat()

	@tasks.loop(minutes=self.cfg.minutes_between_saves)
	async def write_to_file(self):
		with open('Inactivity/activity.json', 'w') as out_file:
			out_file.write(json.dumps(self.activity))

	@tasks.loop(minutes=self.cfg.minutes_between_checks)
	async def assign_role(self):
		for server_id in self.cfg.servers:
			server_cfg = self.cfg.servers[server_id]

			for user_id, timestamp in self.activity.items():
				guild = await self.bot.fetch_guild(server_id)
				user = await guild.fetch_member(user_id)
				role = guild.get_role(server_cfg.role_lurker)
				if role in user.roles:
					continue

				must_be_after = datetime.utcnow() - timedelta(server_cfg.days_inactivity_before_role)
				actual = datetime.fromisoformat(timestamp)
				if actual < must_be_after:
					await user.add_roles(role)


def setup(bot):
	bot.add_cog(Inactivity(bot))