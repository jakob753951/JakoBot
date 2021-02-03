from asyncio import gather, sleep
from CustomExceptions import InsufficientFundsException
import discord
from discord.ext import commands
from Configuration import *
import CurrencyManager as manager
from CustomChecks import *
from CurrencyUtils import *
from itertools import zip_longest
from collections import namedtuple
from discord import Embed


requirements = {
	'general': [],
	'server': [
		'react_confirm',
		'chan_transaction_history',
		'currency_name_singular',
		'currency_name_plural'
	]
}

def rank_string(rank: int):
	if rank % 10 == 1 and rank % 100 != 11:
		place_string = 'st:'
	elif rank % 10 == 2 and rank % 100 != 12:
		place_string = 'nd:'
	elif rank % 10 == 3 and rank % 100 != 13:
		place_string = 'rd:'
	else:
		place_string = 'th:'

	return str(rank) + place_string

class Currency(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')

	@is_admin()
	@commands.command(name='AddCurrency')
	async def add_currency(self, ctx, member: discord.Member, amount: int, *, reason: str = None):
		msg_cfg = self.cfg.servers[ctx.guild.id]
		await gather(
			manager.addToMemberBalance(ctx.guild.id, member.id, amount),
			transaction_log(self.bot, msg_cfg, member, amount, title=f'{ctx.author.name} added currency to this user:'),
			ctx.message.add_reaction(msg_cfg.react_confirm)
		)

	@is_admin()
	@commands.command(name='RemoveCurrency')
	async def remove_currency(self, ctx, member: discord.Member, amount: int, *, reason: str = None):
		msg_cfg = self.cfg.servers[ctx.guild.id]
		await gather(
			manager.addToMemberBalance(ctx.guild.id, member.id, amount * -1),
			transaction_log(self.bot, msg_cfg, member, amount * -1, title=f'{ctx.author.name} removed currency from this user:'),
			ctx.message.add_reaction(msg_cfg.react_confirm)
		)

	@is_admin()
	@commands.command(name='ClearCurrency')
	async def clear_currency(self, ctx, member: discord.Member):
		msg_cfg = self.cfg.servers[ctx.guild.id]
		chan_rx = await self.bot.fetch_channel(msg_cfg.chan_transaction_history)
		await gather(
			manager.setMemberBalance(ctx.guild.id, member.id, 0),
			chan_rx.send(f'Cleared the balance of {member.mention}'),
			ctx.message.add_reaction(msg_cfg.react_confirm)
		)

	@commands.command(name='Give', aliases=['Send', 'Share'])
	async def give(self, ctx, member: discord.Member, amount: int):
		msg_cfg = self.cfg.servers[ctx.guild.id]
		if amount < 1:
			if amount == 0:
				embed = Embed(title='Try again, bud', color=0xff0000, description='You have to send ***something***.')
			else:
				embed = Embed(title='Boo hoo.', color=0xff0000, description="Nice try. You can't send negative money...")

			sent_msg, _ = await gather(
				ctx.send(embed=embed),
				sleep(5)
			)
			await gather(
				sent_msg.delete(),
				ctx.message.delete()
			)
			return

		try:
			sender_new_balance = await manager.transferBetweenMembers(ctx.guild.id, ctx.author.id, member.id, amount)
			embed = Embed(description=f'Funds have been sent.', color=0x00ff00)
			embed.add_field(name='New balance:', value=f'{sender_new_balance} {pluralise(self.cfg.servers[ctx.guild.id], sender_new_balance)}')
			await gather(
				ctx.send(embed=embed),
				transaction_log(self.bot, msg_cfg, member, amount, ctx.author, 'Send command')
			)
		except InsufficientFundsException as e:
			await ctx.send(embed=Embed(description=f"You don't have enough money to send. You're missing {e.missing_funds}"))
			return

	@commands.command(name='Balance', aliases=['Bal', '$'])
	async def balance(self, ctx, member: discord.Member = None):
		if not member:
			member = ctx.author

		current_balance = await manager.getMemberBalance(ctx.guild.id, member.id)

		balance_text = f"{member.mention}'s current balance is {current_balance} {pluralise(self.cfg.servers[ctx.guild.id], current_balance)}"
		embed = Embed(color=0x1111ff, description=balance_text)
		await ctx.send(embed=embed)

	@commands.command(name='Leaderboard', aliases=['LB', 'Scoreboard'])
	async def leaderboard(self, ctx, limit: int = 10):
		if limit > 16:
			limit = 16
		msg_cfg = self.cfg.servers[ctx.guild.id]
		Member = namedtuple('Member', ['rank', 'user', 'balance'])
		members = await manager.getTopRichest(ctx.guild.id, limit)
		leaderboard = [Member(rank+1, ctx.guild.get_member(mem_info[0]), mem_info[1]) for rank, mem_info in enumerate(members)]

		embed = Embed(title='Leaderboard')
		for mem1, mem2 in zip_longest(leaderboard[::2], leaderboard[1::2]):
			if not mem2:
				mem2 = Member(None, None, '\u200b')
			embed.add_field(name=rank_string(mem1.rank), value=rank_string(mem2.rank) if mem2.user else '\u200b', inline=True)
			embed.add_field(name=mem1.user.display_name, value=mem2.user.display_name if mem2.user else '\u200b', inline=True)
			embed.add_field(name=f'{mem1.balance} {pluralise(msg_cfg, mem1.balance)}', value=f'{mem2.balance} {pluralise(msg_cfg, mem2.balance)}' if mem2.user else '\u200b', inline=True)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Currency(bot))