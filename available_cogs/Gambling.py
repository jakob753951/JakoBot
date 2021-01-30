from asyncio import gather, sleep
from discord import Embed
from discord.ext import commands
from Configuration import *
import CurrencyManager as currency
from CustomChecks import *
from CurrencyUtils import *
import random


requirements = {
	'general': [],
	'server': [
		'chan_transaction_history',
		'currency_name_singular',
		'currency_name_plural'
	]
}

class Gambling(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')

	@commands.command(name='BetFlip', aliases=['BF'])
	async def bet_flip(self, ctx, amount, guess: str):
		msg_cfg = self.cfg.servers[ctx.guild.id]

		bet = await parse_amount(ctx.guild.id, ctx.author.id, amount)
		if bet < 2:
			await ctx.send(embed=Embed(title='Bet too low.'))
			return
		heads_stings = ['h', 'head', 'heads']
		tails_stings = ['t', 'tail', 'tails']
		if guess.lower() in heads_stings:
			int_guess = 1
		elif guess.lower() in tails_stings:
			int_guess = 0
		else:
			await ctx.send(embed=Embed(title='Invalid Guess! >:['))
			return

		if await currency.getMemberBalance(ctx.guild.id, ctx.author.id) < bet:
			await ctx.send(embed=Embed(title="You don't have enough money to do that"))

		result = random.getrandbits(1)
		success = result == int_guess

		if success:
			winnings = int(bet * 0.95)
			desc = f'{ctx.author.mention} You guessed it! You won {bet + winnings} {pluralise(msg_cfg, winnings)}'
		else:
			winnings = bet * -1
			desc = f'{ctx.author.mention} Better luck next time'

		embed = Embed(description=desc)
		image_url = f"https://ladegaardmoeller.dk/JakoBot/Gambling/Images/{'Heads' if result else 'Tails'}.png"
		embed.set_image(url=image_url)
		gather(
			ctx.send(embed=embed),
			currency.addToMemberBalance(ctx.guild.id, ctx.author.id, winnings),
			transaction_log(self.bot, msg_cfg, ctx.author, winnings, title=f"{ctx.author.name} {'won' if success else 'lost'} a BetFlip")
		)



def setup(bot):
	bot.add_cog(Gambling(bot))