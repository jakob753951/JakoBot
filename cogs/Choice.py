from discord.ext import commands
import random

requirements = {'general': [], 'server': []}

class Choice(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='Choice')
	async def choice(self, ctx, *args):
		await ctx.send(random.choice(args))


def setup(bot):
	bot.add_cog(Choice(bot))