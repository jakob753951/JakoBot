from CustomExceptions import InsufficientFundsException, NegativeBalanceException
from asyncio import gather, sleep
from discord import Embed
from discord.ext import commands
from Configuration import load_config
from CurrencyUtils import *
import CurrencyManager as currency

requirements = {'general': [], 'server': ['react_confirm']}

async def handle_insufficient_funds(ctx, exception: InsufficientFundsException = None, delete: bool = False):
	sent_msg = await ctx.send(embed=Embed(title='Insufficient Funds.', color=0xff0000))
	if delete:
		await sleep(5)
		await sent_msg.delete()

class SimpleColorRoles(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config()
	
	
	@commands.command(name='PurchaseColor', aliases=['BuyColor'])
	async def purchase_default_color(self, ctx):
		await self.purchase_color(ctx, premium=False)

	@commands.command(name='PurchasePremiumColor', aliases=['BuyPremiumColor'])
	async def purchase_premium_color(self, ctx):
		await self.purchase_color(ctx, premium=True)
	

	async def purchase_color(self, ctx, premium: bool):
		default_color_price = self.cfg.price_default_color
		premium_color_price = self.cfg.price_premium_color

		role_price = premium_color_price if premium else default_color_price

		try:
			new_balance = await currency.addToMemberBalance(ctx.author.id, -role_price)
		except NegativeBalanceException as e:
			await handle_insufficient_funds(ctx, exception=e, delete=True)
			return
		
		default_color_role = self.cfg.role_default_color
		premium_color_role = self.cfg.role_premium_color

		purchased_role_id = premium_color_role if premium else default_color_role

		role = ctx.guild.get_role(purchased_role_id)

		await gather(
			ctx.author.add_roles(role, reason='Purchased role'),
			transaction_log(self.bot, ctx.author, -role_price, title='User bought a Color role.'),
			ctx.channel.send(embed=Embed(
				title='Congrats!',
				description=f'New balance: {new_balance} {pluralise(new_balance)}',
				color=0x00ff00
			))
		)

def setup(bot):
	bot.add_cog(SimpleColorRoles(bot))