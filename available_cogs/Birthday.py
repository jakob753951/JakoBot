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
		self.cfg = load_config('Config.json')

	@is_staff()
	@commands.guild_only()
	@commands.command(name='Birthday', aliases=['birthday', 'birthdaypresent', 'birthdaygift'])
	async def birthday(self, ctx, member: discord.Member):
		guild_cfg = self.cfg.servers[ctx.guild.id]

		amount = 500

		desc=f"Here's your birthday present. We hope you like it!\nIt's **{amount}** {pluralise(guild_cfg, amount)}!!!"
		embed = discord.Embed(color=0x00ff00, description=desc, timestamp=datetime.utcnow())
		embed.set_footer(text='Happy birthday')

		await gather(
			manager.addToMemberBalance(ctx.guild.id, member.id, amount),
			transaction_log(self.bot, guild_cfg, member, amount, title=f"User got a birthday present."),
			member.send(embed=embed)
		)


def setup(bot):
	bot.add_cog(Birthday(bot))