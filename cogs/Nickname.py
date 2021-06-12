from discord.ext import commands
from discord import Embed

requirements = {'general': [], 'server': []}

class Nickname(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		if after.id != 442752995323805718:
			return

		nick_to_set = 'Cody'

		if after.nick != nick_to_set:
			await after.edit(reason='Piss off mate', nick=nick_to_set)
			await after.send(embed=Embed(title='Piss off mate'))


def setup(bot):
	bot.add_cog(Nickname(bot))