import discord
from discord import Embed
from discord.ext import commands
from Configuration import *
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

print('Loading config...')
cfg = load_config()

intents = discord.Intents.default()
intents.members = True

print('making bot...')
bot = commands.Bot(
	command_prefix=commands.when_mentioned_or(cfg.prefix),
	description=cfg.description,
	intents=intents,
	case_insensitive=True,
	pm_help=True
)
slash = SlashCommand(
	bot,
	override_type=True,
	sync_commands=True,
	sync_on_cog_reload=True
)

print('loading cogs...')
cogs_dir = 'cogs'
for cog_name in cfg.launch_cogs:
	bot.load_extension(f'{cogs_dir}.{cog_name}')

@bot.event
async def on_ready():
	print(f'Connected!')
	print(f'Username: {bot.user.name}')
	print(f'ID: {bot.user.id}')

is_owner = lambda ctx: ctx.author.id == cfg.owner_id

@bot.command(name='Load', aliases=['Enable'])
@commands.check(is_owner)
async def load(ctx, extension_name: str):
	try:
		bot.load_extension(f'{cogs_dir}.{extension_name}')
		log_message = f'Extension {extension_name} loaded'
		print(log_message)
		embed = Embed(
			title=log_message,
			color=0x00ff00
		)
	except Exception as e:
		log_message = 'An error occurrred while loading:'
		print(log_message)
		embed = Embed(
			title=log_message,
			description=repr(e),
			color=0xff0000
		)
	await ctx.send(embed=embed)

@bot.command(name='Unload', aliases=['Disable'])
@commands.check(is_owner)
async def unload(ctx, extension_name: str):
	try:
		bot.unload_extension(f'{cogs_dir}.{extension_name}')
		log_message = f'Extension {extension_name} unloaded'
		print(log_message)
		embed = Embed(
			title=log_message,
			color=0x00ff00
		)
	except Exception as e:
		log_message = 'An error occurrred while loading:'
		print(log_message)
		embed = Embed(
			title=log_message,
			description=repr(e),
			color=0xff0000
		)
	await ctx.send(embed=embed)

@bot.command(name='Reload', aliases=['Restart'])
@commands.check(is_owner)
async def reload(ctx, extension_name: str):
	try:
		bot.reload_extension(f'{cogs_dir}.{extension_name}')
		log_message = f'Extension {extension_name} reloaded'
		print(log_message)
		embed = Embed(
			title=log_message,
			color=0x00ff00
		)
	except Exception as e:
		log_message = 'An error occurrred while loading:'
		print(log_message)
		embed = Embed(
			title=log_message,
			description=repr(e),
			color=0xff0000
		)
	await ctx.send(embed=embed)

@bot.command(name='ListExtensions', aliases=['ListCogs'])
@commands.check(is_owner)
async def list_extensions(ctx):
	await ctx.send(embed=Embed(
		title='Loaded extensions:',
		description='\n'.join(extension.split('.')[-1] for extension in bot.extensions)
	))


print('Starting bot...')
bot.run(cfg.token)
