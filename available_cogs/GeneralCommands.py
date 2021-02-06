import asyncio
import discord
from discord import Embed
from discord.ext import commands
from Configuration import load_config

requirements = {'general': [], 'server': ['react_confirm']}

class GeneralCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')

	@commands.command(name='AreYouOnline')
	async def are_you_online(self, ctx):
		# Get male and female roles
		male = discord.utils.find(lambda r: r.name == 'Male', ctx.guild.roles)
		female = discord.utils.find(lambda r: r.name == 'Female', ctx.guild.roles)

		#reply according to role
		if male in ctx.author.roles:
			await ctx.send("Yea man.")
		elif female in ctx.author.roles:
			await ctx.send("Yea gurl.")
		else:
			await ctx.send("Yea.")

	@commands.command(name='Say')
	async def say(self, ctx, channel: discord.TextChannel, *, message):
		await asyncio.gather(
			channel.send(embed=Embed(description=message), files=ctx.message.attachments),
			ctx.message.add_reaction(self.cfg.servers[ctx.guild.id].react_confirm)
		)

	@commands.command(name='SayNoEmbed', aliases=['NoEmbedSay'])
	async def say_no_embed(self, ctx, channel: discord.TextChannel, *, message):
		await asyncio.gather(
			channel.send(message, files=ctx.message.attachments),
			ctx.message.add_reaction(self.cfg.servers[ctx.guild.id].react_confirm)
		)


def setup(bot):
	bot.add_cog(GeneralCommands(bot))