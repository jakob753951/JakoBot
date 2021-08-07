import asyncio
import discord
from discord.ext import commands
from Configuration import load_config
from datetime import datetime
import random
import json

requirements = {'general': ['chan_valentine', 'valentine_seed'], 'server': []}

class Valentine(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config()
		with open('data/Valentine.json', 'r', encoding="utf8") as valentines_file:
			self.valentines = json.loads(valentines_file.read())

	@commands.dm_only()
	@commands.command(name='Valentine', aliases=['Valentines'])
	async def valentine(self, ctx, *, text):
		random.seed(ctx.author.id + self.cfg.valentine_seed)
		user_id = random.randint(1, 10000000) * 15616156345675451 % 0xffffffff
		color = user_id % 0xffffff
		embed = discord.Embed(colour=color, description=text, timestamp=datetime.utcnow())
		chan = await self.bot.fetch_channel(self.cfg.chan_valentine)
		await asyncio.gather(
			chan.send(embed=embed),
			ctx.send(embed=discord.Embed(colour=discord.Colour.green(), title='Your valentine has been sent'))
		)
		user_valentines = self.valentines.get(str(ctx.author.id), [])
		user_valentines.append(text)
		self.valentines[str(ctx.author.id)] = user_valentines
		with open('data/Valentine.json', 'w') as out_file:
			out_file.write(json.dumps(self.valentines, indent=4))


def setup(bot):
	bot.add_cog(Valentine(bot))