import asyncio
import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import SlashContext
from discord_slash.utils.manage_commands import create_option
from Configuration import load_config
from datetime import datetime
import random
import json

requirements = {'general': ['chan_confessions', 'confession_seed'], 'server': []}

class Confessions(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')
		with open('data/Confessions.json', 'r', encoding='utf8') as confessions_file:
			self.confessions = json.loads(confessions_file.read())

	@cog_ext.cog_slash(
	name='confession',
	description='Posts an anonymous confession',
	guild_ids=[842807211607851018],
	options=[
		create_option(
			name='text',
			description='The confession you want to post',
			option_type=3,
			required=True
		)
	])
	async def confession(self, ctx: SlashContext, text: str):
		random.seed(ctx.author.id + self.cfg.confession_seed)
		user_id = random.randint(1, 10000000) * 15616156345675451 % 0xffffffff
		color = user_id % 0xffffff
		embed = discord.Embed(colour=color, description=text, timestamp=datetime.utcnow())
		chan = await self.bot.fetch_channel(self.cfg.chan_confessions)
		await asyncio.gather(
			chan.send(embed=embed),
			ctx.send('Your confession has been sent', hidden=True)
		)
		user_confessions = self.confessions.get(str(ctx.author.id), [])
		user_confessions.append(text)
		self.confessions[str(ctx.author.id)] = user_confessions
		with open('data/Confessions.json', 'w') as out_file:
			out_file.write(json.dumps(self.confessions, indent=4))


def setup(bot):
	bot.add_cog(Confessions(bot))