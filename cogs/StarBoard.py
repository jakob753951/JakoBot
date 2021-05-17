import asyncio
from datetime import datetime
import discord
from discord.ext import commands
from Configuration import load_config
import json
from discord import Embed

requirements = {'general': [], 'server': ['chan_starboard_whitelist', 'chan_starboard_dest']}

def load_stars() -> dict:
	with open('data/Stars.json', 'r', encoding='utf8') as stars_file:
		return json.loads(stars_file.read())

def save_stars(stars: dict) -> None:
	with open('data/Stars.json', 'w', encoding='utf8') as stars_file:
		stars_file.write(json.dumps(stars, indent=4))

def is_channel_whitelisted(channel: discord.abc.GuildChannel) -> bool:
	cfg = load_config('Config.json')
	whitelist = cfg.chan_starboard_whitelist
	try:
		return channel.id in whitelist or channel.category.id in whitelist
	except AttributeError:
		return False


class StarBoard(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')
		self.stars = load_stars()

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		try:
			self.stars = self.bounties[reaction.message.id]
		except KeyError:
			return


def setup(bot):
	bot.add_cog(StarBoard(bot))