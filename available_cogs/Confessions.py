import discord
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands
from Configuration import Configuration, load_config
from datetime import datetime
import random
import json

get_cfg = lambda: {'general': ['chan_confessions'], 'server': ['confirm_reaction']}

class Confessions(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')
		with open('Confessions/data.json', 'r', encoding="utf8") as question_file:
			self.confessions = json.loads(question_file.read())

	@commands.command(name='Confession', aliases=['confession', 'confess'])
	async def confession(self, ctx, *, text):
		if not isinstance(ctx.channel, discord.channel.DMChannel):
			return

		random.seed(ctx.author.id)
		user_id = random.randint(1, 10000000) * 15616156345675451 % 0xffffffff
		color = user_id % 0xffffff
		embed = discord.Embed(colour=color, description=text, timestamp=datetime.utcnow())
		chan = await self.bot.fetch_channel(self.cfg.chan_confessions)
		await chan.send(embed=embed)

		await ctx.send(embed=discord.Embed(colour=discord.Colour.green(), title='Your confession has been sent'))
		existing = self.confessions.get(ctx.author.id, [])
		existing.append(text)
		self.confessions[ctx.author.id] = existing
		with open('Confessions/data.json', 'w') as out_file:
			out_file.write(json.dumps(self.confessions))


def setup(bot):
	bot.add_cog(Confessions(bot))