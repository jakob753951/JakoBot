from CustomExceptions import InsufficientFundsException
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

class Currency(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')

	@commands.command(name='AddCurrency', aliases=['addcurrency', 'awardcurrency', 'award'])
	async def add_currency(self, ctx, member: discord.Member, amount: int, *, reason: str = None):
		msg_cfg = self.cfg.servers[ctx.guild.id]
		await manager.addToMemberBalance(ctx.guild.id, member.id, amount)
		await self.transaction_log(ctx.guild.id, f'{ctx.author.mention} added {amount} {pluralise(msg_cfg, amount)} to {member.mention}.{f" reason: " + reason if reason else ""}')
		await ctx.message.add_reaction(msg_cfg.react_confirm)

	@commands.command(name='RemoveCurrency', aliases=['removecurrency'])
	async def remove_currency(self, ctx, member: discord.Member, amount: int, *, reason: str = None):
		msg_cfg = self.cfg.servers[ctx.guild.id]
		await manager.addToMemberBalance(ctx.guild.id, member.id, amount * -1)
		await self.transaction_log(ctx.guild.id, f'{ctx.author.mention} removed {amount} {pluralise(msg_cfg, amount)} from {member.mention}.{" reason: " + reason if reason else ""}')
		await ctx.message.add_reaction(msg_cfg.react_confirm)

	@commands.command(name='ClearCurrency', aliases=['clearcurrency'])
	async def clear_currency(self, ctx, member: discord.Member):
		msg_cfg = self.cfg.servers[ctx.guild.id]
		await manager.setMemberBalance(ctx.guild.id, member.id, 0)
		await self.transaction_log(ctx.guild.id, f"{ctx.author.mention} cleared {member.mention}'s balance.")
		await ctx.message.add_reaction(msg_cfg.react_confirm)

	@commands.command(name='Give', aliases=['give', 'send'])
	async def give(self, ctx, member: discord.Member, amount: int):
		msg_cfg = self.cfg.servers[ctx.guild.id]
		try:
			sender_new_balance = await manager.transferBetweenMembers(ctx.guild.id, ctx.author.id, member.id, amount)
			await ctx.send(f'Funds have been sent. Your new balance is {sender_new_balance} {pluralise(self.cfg.servers[ctx.guild.id], sender_new_balance)}')
		except InsufficientFundsException as e:
			await ctx.send(f"You don't have enough money to send. You're missing {e.missing_funds}")
			return

	@commands.command(name='Balance', aliases=['balance', 'bal', '$'])
	async def balance(self, ctx, member: discord.Member = None):
		if not member:
			member = ctx.author

		current_balance = await manager.getMemberBalance(ctx.guild.id, member.id)

		await ctx.send(f"{member.mention}'s current balance is {current_balance} {pluralise(self.cfg.servers[ctx.guild.id], current_balance)}")

	async def transaction_log(self, guild_id, message):
		msg_cfg = self.cfg.servers[guild_id]
		chan_rx = await self.bot.fetch_channel(msg_cfg.chan_transaction_history)
		await chan_rx.send(message)


def setup(bot):
	bot.add_cog(Currency(bot))