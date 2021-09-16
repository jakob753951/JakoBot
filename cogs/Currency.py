from asyncio import gather, sleep
from CustomExceptions import InsufficientFundsException
import discord
from discord.ext import commands
from Configuration import load_config
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
		self.cfg = load_config()

	@is_admin()
	@commands.command(name='AddCurrency')
	async def add_currency(self, ctx, member: discord.Member, amount: int, *, reason: str = None):
		await gather(
			manager.addToMemberBalance(member.id, amount),
			transaction_log(self.bot, member, amount, title=f'{ctx.author.name} added currency to this user:'),
			ctx.message.add_reaction(self.cfg.react_confirm)
		)

	@is_admin()
	@commands.command(name='RemoveCurrency')
	async def remove_currency(self, ctx, member: discord.Member, amount: int, *, reason: str = None):
		await gather(
			manager.addToMemberBalance(member.id, amount * -1),
			transaction_log(self.bot, member, amount * -1, title=f'{ctx.author.name} removed currency from this user:'),
			ctx.message.add_reaction(self.cfg.react_confirm)
		)

	@is_admin()
	@commands.command(name='ClearCurrency')
	async def clear_currency(self, ctx, member: discord.Member):
		chan_rx = await self.bot.fetch_channel(self.cfg.chan_transaction_history)
		await gather(
			manager.setMemberBalance(member.id, 0),
			chan_rx.send(f'Cleared the balance of {member.mention}'),
			ctx.message.add_reaction(self.cfg.react_confirm)
		)

	@is_top_admin()
	@commands.command(name='ResetCurrency')
	async def reset_currency(self, ctx):
		chan_rx = await self.bot.fetch_channel(self.cfg.chan_transaction_history)
		embed = Embed(title='Currency Reset!', description=f'{ctx.author.mention} just reset the entire currency.')
		await gather(
			manager.removeAllData(),
			chan_rx.send(embed=embed),
			ctx.send(embed=embed),
			ctx.message.add_reaction(self.cfg.react_confirm)
		)

	@commands.command(name='Give', aliases=['Send', 'Share'])
	async def give(self, ctx, member: discord.Member, amount: int):
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
			sender_new_balance = await manager.transferBetweenMembers(ctx.author.id, member.id, amount)
			embed = Embed(description='Funds have been sent.', color=0x00ff00)
			embed.add_field(name='New balance:', value=f'{sender_new_balance} {pluralise(sender_new_balance)}')
			await gather(
				ctx.send(embed=embed),
				transaction_log(self.bot, member, amount, ctx.author, 'Send command')
			)
		except InsufficientFundsException as e:
			await ctx.send(embed=Embed(title='Insufficient funds', description=f"You don't have enough money to send. You're missing {e.missing_funds}"))
			return

	@commands.command(name='Balance', aliases=['Bal', '$'])
	async def balance(self, ctx, member: discord.Member = None):
		if not member:
			member = ctx.author

		current_balance = await manager.getMemberBalance(member.id)

		balance_text = f"{member.mention}'s current balance is {current_balance} {pluralise(current_balance)}"
		embed = Embed(color=0x1111ff, description=balance_text)
		await ctx.send(embed=embed)

	@commands.command(name='Leaderboard', aliases=['LB', 'Scoreboard'])
	async def leaderboard(self, ctx, limit_or_phone: str = None, maybe_limit: int = 10):
		if limit_or_phone and limit_or_phone.lower() == 'phone':
			await self.phone_leaderboard(ctx, limit=maybe_limit)
			return
		
		if limit_or_phone and limit_or_phone.isdigit:
			limit = int(limit_or_phone)
		else:
			limit = maybe_limit
		
		if limit > 16:
			limit = 16
		Member = namedtuple('Member', ['rank', 'user', 'balance'])
		members = await manager.getTopRichest(limit)
		leaderboard = [Member(rank+1, ctx.guild.get_member(mem_info[0]), mem_info[1]) for rank, mem_info in enumerate(members)]

		embed = Embed(title='Leaderboard', color=0x0000ff)
		for mem1, mem2 in zip_longest(leaderboard[::2], leaderboard[1::2]):
			if not mem2:
				mem2 = Member(None, None, None)
			embed.add_field(name=rank_string(mem1.rank), value=rank_string(mem2.rank) if mem2.rank else '\u200b', inline=True)
			embed.add_field(name=mem1.user.display_name if mem1.user else '[UNKNOWN USER]', value=mem2.user.display_name if mem2.user else '[UNKNOWN USER]', inline=True)
			embed.add_field(name=f'{mem1.balance} {pluralise(mem1.balance)}', value=f'{mem2.balance} {pluralise(mem2.balance)}' if mem2.balance else '\u200b', inline=True)

		await ctx.send(embed=embed)

	async def phone_leaderboard(self, ctx, limit):
		if limit > 16:
			limit = 16

		Member = namedtuple('Member', ['rank', 'user', 'balance'])
		members = await manager.getTopRichest(limit)
		leaderboard = [Member(rank+1, ctx.guild.get_member(member_info[0]), member_info[1]) for rank, member_info in enumerate(members)]

		lb_line_format = '{place} - {user_name}: {balance}'

		lines = []
		for member in leaderboard:
			line = lb_line_format.format_map({
				'place': member.rank,
				'user_name': member.user.display_name,
				'balance': f'{member.balance} {pluralise(member.balance)}'
			})

			# Bold every other line
			if member.rank % 2 != 0:
				line = f'**{line}**'

			lines.append(line)

		embed = Embed(title='Leaderboard', color=0x0000ff, description='\n'.join(lines))
		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Currency(bot))