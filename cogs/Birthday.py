from asyncio import gather
import discord
from discord.ext import commands
from Configuration import *
import CurrencyManager as manager
from CurrencyUtils import *
from CustomChecks import *

requirements = {
	'general': [],
	'server': [
		'currency_name_singular',
		'currency_name_plural'
	]
}

class Birthday(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config()

	@is_staff()
	@commands.guild_only()
	@commands.command(name='Birthday', aliases=['BirthdayPresent', 'BirthdayGift'])
	async def birthday(self, ctx, member: discord.Member):
		amount = 500

		desc=f"Here's your birthday present. We hope you like it!\nIt's **{amount}** {pluralise(amount)}!!!"
		embed = discord.Embed(color=0x00ff00, description=desc, timestamp=datetime.utcnow())
		embed.set_footer(text='Happy birthday')

		await gather(
			manager.addToMemberBalance(member.id, amount),
			transaction_log(self.bot, member, amount, title=f"User got a birthday present."),
			member.send(embed=embed)
		)


def setup(bot):
	bot.add_cog(Birthday(bot))