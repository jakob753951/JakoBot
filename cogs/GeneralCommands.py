import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands.converter import TextChannelConverter
from Configuration import load_config
from asyncio import gather
from CustomChecks import *

requirements = {'general': [], 'server': ['react_confirm']}

async def parse_args(ctx, args, react_confirm):
	try:
		channel = await TextChannelConverter().convert(ctx, args[0])
		await ctx.message.add_reaction(react_confirm)
		start_index = 2
	except Exception:
		channel = ctx.channel
		start_index = 1
		await ctx.message.delete()

	message = ' '.join(ctx.message.content.split(' ')[start_index:])
	message = message.replace('\\n', '\n')
	return (channel, message)

class GeneralCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config()

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
		
	@is_admin()
	@commands.command(name='ban')
	async def ban(self, ctx: commands.Context, user: discord.User, reason: str = None):
		guild = ctx.guild
		await guild.ban(user, reason=reason)
		await ctx.send(embed=Embed(description=f'User {user.name} was banned.', color=0xff0000))
		
	@is_admin()
	@commands.command(name='kick')
	async def kick(self, ctx: commands.Context, user: discord.User, reason: str = None):
		guild = ctx.guild
		await guild.kick(user, reason=reason)
		await ctx.send(embed=Embed(description=f'User {user.name} was kicked.', color=0xff0000))

	@is_admin()
	@commands.command(name='Say')
	async def say(self, ctx, *args):
		channel, message = await parse_args(ctx, args, self.cfg.react_confirm)
		await channel.send(embed=Embed(description=message, color=0xff8000), files=ctx.message.attachments)

	@is_admin()
	@commands.command(name='SayNoEmbed', aliases=['NoEmbedSay'])
	async def say_no_embed(self, ctx, *args):
		channel, message = await parse_args(ctx, args, self.cfg.react_confirm)
		await channel.send(message, files=ctx.message.attachments)
	
	@is_admin()
	@commands.command(name='SendDM', aliases=['DMMember', 'DMUser'])
	async def send_dm(self, ctx, recipient: discord.User, *, message):
		await gather(
			recipient.send(message.replace('\\n', '\n')),
			ctx.message.add_reaction(self.cfg.react_confirm)
		)


def setup(bot):
	bot.add_cog(GeneralCommands(bot))