from discord.ext import commands
from Configuration import load_config
import json
import random

requirements = {'general': [], 'server': ['chan_truth_or_dare']}

class TruthOrDare(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')
		with open('data/TruthOrDare.json', 'r', encoding="utf8") as prompt_file:
			self.questions = json.loads(prompt_file.read())

	@commands.command(name='TruthOrDare', aliases=['TorD', 'ToD'])
	async def truth_or_dare(self, ctx, *, category = 'sfw'):
		# check for incorrect channel
		if ctx.channel.id != self.cfg.chan_truth_or_dare:
			return

		# check for incorrect category
		if category not in self.questions:
			await ctx.send(f"'{category}' is not a valid category. The valid categories are: '{', '.join(self.questions.keys())}'")
			return

		# send random question in selected category
		await ctx.send(random.choice(self.questions[category]))


def setup(bot):
	bot.add_cog(TruthOrDare(bot))