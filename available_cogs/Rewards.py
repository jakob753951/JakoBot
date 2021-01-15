from CustomExceptions import InsufficientFundsException
import asyncio
import discord
from discord.errors import DiscordException
from discord.ext import commands
from Configuration import *
import CurrencyManager as manager

requirements = {
	'general': [],
	'server': [
		'react_confirm',
		'chan_transaction_history',
		'currency_name_singular',
		'currency_name_plural'
	]
}

def pluralise(server_cfg, amount):
	if abs(amount) == 1:
		return server_cfg.currency_name_singular
	else:
		return server_cfg.currency_name_plural

class Rewards(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')

	@commands.command(name='AddCurrency', aliases=['addcurrency', 'awardcurrency', 'award'])
	async def reward(self, ctx, member: discord.Member, amount: int, *, reason: str = None):
		msg_cfg = self.cfg.servers[ctx.guild.id]
		await manager.addToMemberBalance(ctx.guild.id, member.id, amount)
		await self.transaction_log(ctx.guild.id, f'{ctx.author.mention} added {amount} {pluralise(msg_cfg, amount)} to {member.mention}.{f" reason: " + reason if reason else ""}')
		await ctx.message.add_reaction(msg_cfg.react_confirm)

	async def transaction_log(self, guild_id, message):
		msg_cfg = self.cfg.servers[guild_id]
		chan_rx = await self.bot.fetch_channel(msg_cfg.chan_transaction_history)
		await chan_rx.send(message)


def setup(bot):
	bot.add_cog(Rewards(bot))