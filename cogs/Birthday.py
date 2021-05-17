from asyncio import gather
import discord
from discord import Embed
from discord.ext import commands
from discord_slash.utils.manage_commands import create_option
from Configuration import *
import CurrencyManager as manager
from CurrencyUtils import *
from CustomChecks import *
from discord_slash import cog_ext, SlashContext

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

	@cog_ext.cog_slash(
	name='birthday',
	description='Gives the user a birthday gift',
	guild_ids=[842807211607851018],
	options=[
		create_option(
			name='user',
			description='The person to give the gift to',
			option_type=6,
			required=True
		)
	])
	async def birthday(self, ctx: SlashContext, member: discord.user):
		if not is_staff(ctx):
			await ctx.send(embed=Embed(title="You're not permitted to use this command"))
			return

		amount = self.cfg.birthday_amount

		desc=f"Here's your birthday present. We hope you like it!\nIt's **{amount}** {pluralise(amount)}!!!"
		embed = Embed(color=0x00ff00, description=desc, timestamp=datetime.utcnow())
		embed.set_footer(text='Happy birthday')

		await gather(
			manager.addToMemberBalance(member.id, amount),
			transaction_log(self.bot, member, amount, title=f'User got a birthday present.'),
			member.send(embed=embed)
		)


def setup(bot):
	bot.add_cog(Birthday(bot))