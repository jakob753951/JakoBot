import asyncio
import discord
from discord.ext import commands
from Configuration import load_config
from datetime import datetime
import random
import json

requirements = {'general': ['chan_confessions'], 'server': []}

class Confessions(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')
		with open('data/Confessions.json', 'r', encoding="utf8") as confessions_file:
			self.confessions = json.loads(confessions_file.read())

	@commands.dm_only()
	@commands.command(name='Confession', aliases=['Confess'])
	async def confession(self, ctx, *, text):
		random.seed(ctx.author.id)
		user_id = random.randint(1, 10000000) * 15616156345675451 % 0xffffffff
		color = user_id % 0xffffff
		embed = discord.Embed(colour=color, description=text, timestamp=datetime.utcnow())
		chan = await self.bot.fetch_channel(self.cfg.chan_confessions)
		await asyncio.gather(
			chan.send(embed=embed),
			ctx.send(embed=discord.Embed(colour=discord.Colour.green(), title='Your confession has been sent'))
		)
		user_confessions = self.confessions.get(str(ctx.author.id), [])
		user_confessions.append(text)
		self.confessions[str(ctx.author.id)] = user_confessions
		with open('data/Confessions.json', 'w') as out_file:
			out_file.write(json.dumps(self.confessions, indent=4))


def setup(bot):
	bot.add_cog(Confessions(bot))