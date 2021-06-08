from discord.ext import commands
from Configuration import load_config
import json
import random
import discord
from discord import Embed
from asyncio import sleep

requirements = {'general': [], 'server': ['chan_truth_or_dare']}

class TruthOrDare(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')
		with open('data/TruthOrDare.json', encoding="utf8") as prompt_file:
			self.questions = json.load(prompt_file)

	@commands.command(name='TruthOrDare', aliases=['TorD', 'ToD'])
	async def truth_or_dare(self, ctx, *, category = 'sfw'):
		# check for incorrect channel
		if ctx.channel.id != self.cfg.chan_truth_or_dare:
			return

		if self.cfg.truth_or_dare_no_two_in_a_row:
			if self.last_user and self.last_user == ctx.author:
				sent_msg = await ctx.send(embed=Embed(title="Can't ask twice in a row"))
				await sleep(5)
				await sent_msg.delete()
				return

		# check for incorrect category
		if category not in self.questions:
			await ctx.send(f"'{category}' is not a valid category. The valid categories are: '{', '.join(self.questions.keys())}'")
			return

		# send random question in selected category
		await ctx.send(random.choice(self.questions[category]))
		self.last_user = ctx.author


def setup(bot):
	bot.add_cog(TruthOrDare(bot))