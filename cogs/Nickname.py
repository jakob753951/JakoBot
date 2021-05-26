from discord.ext import commands

requirements = {'general': [], 'server': []}

class Nickname(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		if not after.id == 442752995323805718:
			return

		if after.nick != before.nick:
			after.nick = before.nick


def setup(bot):
	bot.add_cog(Nickname(bot))