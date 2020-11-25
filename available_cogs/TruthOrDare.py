import discord
from discord.ext import commands, tasks
from Configuration import *
import json
import random

get_cfg = lambda: {'general': [], 'server': ['chan_truth_or_dare']}

class TruthOrDare(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')
		with open('data/TruthOrDare.json', 'r', encoding="utf8") as question_file:
			self.questions = json.loads(question_file.read())

	@commands.command(name='truth or dare', aliases=['tord', 'truthordare'])
	async def truth_or_dare(self, ctx, *, category = 'sfw'):
		# check for incorrect channel
		if ctx.channel.id != self.cfg.servers[ctx.guild.id].chan_truth_or_dare:
			return

		# check for incorrect category
		if category not in self.questions:
			await ctx.send(f"'{category}' is not a valid category. The valid categories are: '{', '.join(self.questions.keys())}'")
			return

		# send random question in selected category
		await ctx.send(random.choice(self.questions[category]))

def setup(bot):
	bot.add_cog(TruthOrDare(bot))