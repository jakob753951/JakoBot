from asyncio import gather, sleep

from discord_slash import cog_ext
from discord_slash.context import SlashContext
from discord_slash.utils.manage_commands import create_option
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
	'general': [
		'react_confirm',
		'chan_transaction_history',
		'currency_name_singular',
		'currency_name_plural'
	],
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

	@cog_ext.cog_slash(
	name='add-currency',
	description="Add currency to a user",
	guild_ids=[842807211607851018],
	options=[
		create_option(
			name='user',
			description='The person to add currency to',
			option_type=6,
			required=True
		),
		create_option(
			name='amount',
			description='How much currency to add',
			option_type=4,
			required=True
		)
	])
	async def add_currency(self, ctx: SlashContext, member: discord.user, amount: int):
		await gather(
			manager.addToMemberBalance(member.id, amount),
			transaction_log(self.bot, member, amount, title=f'{ctx.author.name} added currency to this user:'),
			ctx.send(embed=Embed(title='Currency added'))
		)


	@cog_ext.cog_slash(
	name='remove-currency',
	description="Remove currency from a user",
	guild_ids=[842807211607851018],
	options=[
		create_option(
			name='user',
			description='The person to remove currency from',
			option_type=6,
			required=True
		),
		create_option(
			name='amount',
			description='How much currency to remove',
			option_type=4,
			required=True
		)
	])
	async def remove_currency(self, ctx: SlashContext, user: discord.User, amount: int):
		await gather(
			manager.addToMemberBalance(user.id, amount * -1),
			transaction_log(self.bot, user, amount * -1, title=f'{ctx.author.name} removed currency from this user:'),
			ctx.send(embed=Embed(title='Currency removed'))
		)


	@cog_ext.cog_slash(
	name='clear-currency',
	description="Remove user from the currency system",
	guild_ids=[842807211607851018],
	options=[
		create_option(
			name='user',
			description='The user to be removed',
			option_type=6,
			required=True
		)
	])
	async def clear_currency(self, ctx: SlashContext, user: discord.User):
		transaction_history = await self.bot.fetch_channel(self.cfg.chan_transaction_history)
		await gather(
			manager.setMemberBalance(user.id, 0),
			transaction_history.send(f'Cleared the balance of {user.mention}'),
			ctx.send(embed=Embed(title='Currency cleared'))
		)


	@cog_ext.cog_slash(
	name='send',
	description="Send money to a specified user",
	guild_ids=[842807211607851018],
	options=[
		create_option(
			name='user',
			description='The person to send money to',
			option_type=6,
			required=True
		),
		create_option(
			name='amount',
			description='How much money to send',
			option_type=4,
			required=True
		)
	])
	async def give(self, ctx: SlashContext, user: discord.user, amount: int):
		if amount < 1:
			if amount == 0:
				err_text = 'You have to send ***something***.'
			else:
				err_text = "Nice try. You can't send negative money..."

			await ctx.send(err_text, hidden=True)
			return

		try:
			sender_new_balance = await manager.transferBetweenMembers(ctx.author.id, user.id, amount)
			embed = Embed(description='Funds have been sent.', color=0x00ff00)
			embed.add_field(name='New balance:', value=f'{sender_new_balance} {pluralise(sender_new_balance)}')
			await gather(
				ctx.send(embed=embed),
				transaction_log(self.bot, user, amount, ctx.author, 'Send command')
			)
		except InsufficientFundsException as e:
			await ctx.send(f"You don't have enough money to send. You're missing {e.missing_funds}", hidden=True)


	@cog_ext.cog_slash(
	name='balance',
	description="Shows a user's balance",
	guild_ids=[842807211607851018],
	options=[
		create_option(
			name='user',
			description="The person's balance to display",
			option_type=6,
			required=True
		)
	])
	async def balance(self, ctx: SlashContext, user: discord.user = None):
		if not user:
			user = ctx.author

		current_balance = await manager.getMemberBalance(user.id)

		balance_text = f"{user.mention}'s current balance is {current_balance} {pluralise(current_balance)}"
		embed = Embed(color=0x1111ff, description=balance_text)
		await ctx.send(embed=embed)


	@cog_ext.cog_slash(
	name='leaderboard',
	description='Displays the top richest people',
	guild_ids=[842807211607851018],
	options=[
		create_option(
			name='limit',
			description='How many entries to display',
			option_type=4,
			required=False
		)
	])
	async def leaderboard(self, ctx: SlashContext, limit: int = 10):
		limit = min(limit, 16)
		Member = namedtuple('Member', ['rank', 'user', 'balance'])
		members = await manager.getTopRichest(limit)

		leaderboard = []
		for rank, mem_info in enumerate(members):
			try:
				mem = ctx.guild.get_member(mem_info[0])
			except:
				mem = None

			leaderboard.append(Member(rank+1, mem, mem_info[1]))

		embed = Embed(title='Leaderboard', color=0x0000ff)
		for mem1, mem2 in zip_longest(leaderboard[::2], leaderboard[1::2]):
			if not mem2:
				mem2 = Member(None, None, '\u200b')
			embed.add_field(name=rank_string(mem1.rank), value=rank_string(mem2.rank) if mem2.user else '\u200b', inline=True)
			embed.add_field(name=mem1.user.display_name if mem1.user else '\u200b', value=mem2.user.display_name if mem2.user else '\u200b', inline=True)
			embed.add_field(name=f'{mem1.balance} {pluralise(mem1.balance)}', value=f'{mem2.balance} {pluralise(mem2.balance)}' if mem2.user else '\u200b', inline=True)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Currency(bot))