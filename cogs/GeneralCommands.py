import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands.converter import TextChannelConverter
from Configuration import load_config
from asyncio import gather

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
	return (channel, message)

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
		channel, message = await parse_args(ctx, args, self.cfg.servers[ctx.guild.id].react_confirm)
		await channel.send(embed=Embed(description=message, color=0xff8000), files=ctx.message.attachments)

	@commands.command(name='SayNoEmbed', aliases=['NoEmbedSay'])
	async def say_no_embed(self, ctx, *args):
		channel, message = await parse_args(ctx, args, self.cfg.servers[ctx.guild.id].react_confirm)
		await channel.send(message, files=ctx.message.attachments)
	
	@commands.command(name='SendDM', aliases=['DMMember', 'DMUser'])
	async def send_dm(self, ctx, recipient: discord.User, *, message):
		await gather(
			recipient.send(message),
			ctx.message.add_reaction(self.cfg.react_confirm)
		)


def setup(bot):
	bot.add_cog(GeneralCommands(bot))