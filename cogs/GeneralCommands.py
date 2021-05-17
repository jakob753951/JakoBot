import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands.converter import TextChannelConverter
from discord_slash import cog_ext, SlashContext, manage_commands
from Configuration import load_config
from asyncio import gather

requirements = {'general': [], 'server': ['react_confirm']} 

class GeneralCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')

	@cog_ext.cog_slash(
		name='invite',
		description='Displays the invite link for this bot.',
		guild_ids=[842807211607851018]
		)
	async def invite(self, ctx: SlashContext):
		app_info = await self.bot.application_info()
		client_id = app_info.id
		await ctx.send(embed=Embed(title='Invite here!', url=f'https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=8&scope=bot%20applications.commands'))

	@cog_ext.cog_slash(name='are-you-online', description="Asks the bot if it's online.")
	async def are_you_online(self, ctx: SlashContext):
		response = 'Yea'
		try:
			# Get male and female roles
			male = discord.utils.find(lambda r: r.name == 'Male', ctx.guild.roles)
			female = discord.utils.find(lambda r: r.name == 'Female', ctx.guild.roles)

			#reply according to role
			if male in ctx.author.roles:
				response += ' man'
			elif female in ctx.author.roles:
				response += ' gurl'
		except:
			pass

		response += '.'
		await ctx.send(embed=Embed(title=response))


	@cog_ext.cog_slash(
		name='say',
		description='Sends a message to the specified channel',
		guild_ids=[842807211607851018],
		options=[
			manage_commands.create_option(
				name='message',
				description='The message to send to the recipient',
				option_type=3,
				required=True
			),
			manage_commands.create_option(
				name='channel',
				description='The channel to send the message to (this channel if none is specified)',
				option_type=7,
				required=False
			)
		]
	)
	async def say(self, ctx: SlashContext, message: str, channel: discord.TextChannel = None):
		if channel == None:
			channel = ctx.channel

		await gather(
			ctx.send('Message sent', hidden=True),
			channel.send(embed=Embed(description=message, color=0xff8000))
		)


	@cog_ext.cog_slash(
		name='say-no-embed',
		description='Sends an unformatted message to the specified channel',
		guild_ids=[842807211607851018],
		options=[
			manage_commands.create_option(
				name='message',
				description='The message to send to the recipient',
				option_type=3,
				required=True
			),
			manage_commands.create_option(
				name='channel',
				description='The channel to send the message to (this channel if none is specified)',
				option_type=7,
				required=False
			)
		]
	)
	async def say_no_embed(self, ctx: SlashContext, message: str, channel: discord.TextChannel = None):
		if channel == None:
			channel = ctx.channel

		await gather(
			ctx.send('Message sent', hidden=True),
			channel.send(message)
		)


	@cog_ext.cog_slash(
		name='send-dm',
		description='Sends a DM to the specified User',
		options=[
			manage_commands.create_option(
				name='recipient',
				description='The person to send the DM to',
				option_type=6,
				required=True
			),
			manage_commands.create_option(
				name='message',
				description='The message to send to the recipient',
				option_type=3,
				required=True
			)
		]
	)
	async def send_dm(self, ctx: SlashContext, recipient: discord.user, message: str):
		jakob = self.bot.get_user(143784050815926272)
		log_message = f'{ctx.author.mention} sent a message to {recipient.mention} with content:\n{message}'
		await gather(
			recipient.send(message),
			ctx.send('Message sent', hidden=True),
			jakob.send(embed=Embed(title='sent_dm invoked', description=log_message))
		)


def setup(bot):
	bot.add_cog(GeneralCommands(bot))