import discord
from discord.ext import commands
from Configuration import Configuration, load_config

get_cfg = lambda: {'general': [], 'server': ['confirm_reaction']}

class GeneralCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')

	@commands.command(name='areyouonline')
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

	@commands.command(name='say')
	async def say(self, ctx, channel: discord.TextChannel, *, message):
		await channel.send(message, files=ctx.message.attachments)
		await ctx.message.add_reaction(self.cfg.servers[ctx.guild.id].confirm_reaction)


def setup(bot):
	bot.add_cog(GeneralCommands(bot))