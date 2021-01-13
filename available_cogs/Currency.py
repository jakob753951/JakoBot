from CustomExceptions import InsufficientFundsException
from datetime import datetime
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
		chan_rx = await self.bot.fetch_channel(msg_cfg.chan_transaction_history)
		chan_rx.send(f'Cleared the balance of {member.mention}')
		await ctx.message.add_reaction(msg_cfg.react_confirm)

	@commands.command(name='Give', aliases=['give', 'send', 'share'])
	async def give(self, ctx, member: discord.Member, amount: int):
		msg_cfg = self.cfg.servers[ctx.guild.id]
		if amount < 0:
			sent_msg = await ctx.send("Nice try. You can't send negative money...")
			await sent_msg.delete()
			return
		if amount == 0:
			sent_msg = await ctx.send('You have to send *something*.')
			await sent_msg.delete()
			return

		try:
			sender_new_balance = await manager.transferBetweenMembers(ctx.guild.id, ctx.author.id, member.id, amount)
			await ctx.send(f'Funds have been sent. Your new balance is {sender_new_balance} {pluralise(self.cfg.servers[ctx.guild.id], sender_new_balance)}')
			await self.transaction_log(msg_cfg, member, amount, ctx.author)
		except InsufficientFundsException as e:
			await ctx.send(f"You don't have enough money to send. You're missing {e.missing_funds}")
			return

	@commands.command(name='Balance', aliases=['balance', 'bal', '$'])
	async def balance(self, ctx, member: discord.Member = None):
		if not member:
			member = ctx.author

		current_balance = await manager.getMemberBalance(ctx.guild.id, member.id)

		await ctx.send(f"{member.mention}'s current balance is {current_balance} {pluralise(self.cfg.servers[ctx.guild.id], current_balance)}")

	@commands.command(name='Leaderboard', aliases=['leaderboard', 'lb', 'scoreboard'])
	async def leaderboard(self, ctx, limit: int = 10):
		guild = self.bot.get_guild(ctx.guild.id)
		leaderboard = await manager.getTopRichest(guild.id)

		await ctx.send('\n'.join([f'{guild.get_member(member[0]).display_name}: {member[1]}' for member in leaderboard]))


	async def transaction_log(self, msg_cfg, recipient: discord.Member, amount: int, sender: discord.Member = None):
		chan_rx = await self.bot.fetch_channel(msg_cfg.chan_transaction_history)

		if sender:
			desc = f'{sender.mention} sent {recipient.mention} {amount} {pluralise(msg_cfg, amount)}'
		else:
			desc = f"{recipient.mention} {'got' if amount >= 0 else 'lost'} {amount} {pluralise(msg_cfg, amount)}"

		embed = discord.Embed(color=0x0000ff, title=f'User received money:', description=desc, timestamp=datetime.utcnow())
		embed.set_author(name=f'{recipient.name}#{recipient.discriminator}', icon_url=recipient.avatar_url)
		if sender:
			embed.add_field(name='Sender: ', value=f'{sender.name}#{sender.discriminator}', inline=True)
		embed.add_field(name='Amount: ', value=amount, inline=True)

		await chan_rx.send(embed=embed)


def setup(bot):
	bot.add_cog(Currency(bot))