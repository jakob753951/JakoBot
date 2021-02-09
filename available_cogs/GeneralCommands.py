import asyncio
import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands.converter import TextChannelConverter
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
	async def say(self, ctx, *args):
		try:
			to_convert = args[0]
			cvt = TextChannelConverter()
			channel = await cvt.convert(ctx, to_convert)
			message = ' '.join(args[1:])
			await ctx.message.add_reaction(self.cfg.servers[ctx.guild.id].react_confirm)
		except Exception as e:
			channel = ctx.channel
			message = ' '.join(args)
			await ctx.message.delete()

		message = message.replace('\\n', '\n')

		await channel.send(embed=Embed(description=message, color=0xff8000), files=ctx.message.attachments)

	@commands.command(name='SayNoEmbed', aliases=['NoEmbedSay'])
	async def say_no_embed(self, ctx, *args):
		try:
			to_convert = args[0]
			cvt = TextChannelConverter()
			channel = await cvt.convert(ctx, to_convert)
			message = ' '.join(args[1:])
			await ctx.message.add_reaction(self.cfg.servers[ctx.guild.id].react_confirm)
		except Exception as e:
			channel = ctx.channel
			message = ' '.join(args)
			await ctx.message.delete()

		message = message.replace('\\n', '\n')

		await channel.send(message, files=ctx.message.attachments)


def setup(bot):
	bot.add_cog(GeneralCommands(bot))