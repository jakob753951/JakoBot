import discord
from discord import Embed
from discord.ext import commands
from Configuration import *
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

print('Loading config...')
cfg = load_config('Config.json')

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
slash = SlashCommand(bot, override_type=True, sync_commands=True, sync_on_cog_reload=True)

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

@slash.slash(
	name='load',
	description='loads the specified extension',
	options=[
		create_option(
			name='extension',
			description='The extension to load.',
			option_type=3,
			required=True
		)
	])
async def load(ctx: SlashContext, extension: str):
	if not is_owner(ctx):
		await ctx.send(embed=Embed(title="You're not permitted to use this command"))
		return

	try:
		bot.load_extension(f'{cogs_dir}.{extension}')
		embed = Embed(
			title=f'Extension {extension} loaded',
			color=0x00ff00
		)
	except Exception as e:
		embed = Embed(
			title='An error occurrred while loading:',
			description=repr(e),
			color=0xff0000
		)
	await ctx.send(embed=embed)

@slash.slash(
	name='unload',
	description='unloads the specified extension',
	options=[
		create_option(
			name='extension',
			description='The extension to unload.',
			option_type=3,
			required=True
		)
	])
async def unload(ctx: SlashContext, extension: str):
	if not is_owner(ctx):
		await ctx.send(embed=Embed(title="You're not permitted to use this command"))
		return

	try:
		bot.unload_extension(f'{cogs_dir}.{extension}')
		embed = Embed(
			title=f'Extension {extension} unloaded',
			color=0x00ff00
		)
	except Exception as e:
		embed = Embed(
			title='An error occurrred while unloading:',
			description=repr(e),
			color=0xff0000
		)

	await ctx.send(embed=embed)

@slash.slash(
	name='reload',
	description='reloads the specified extension',
	options=[
		create_option(
			name='extension',
			description='The extension to reload.',
			option_type=3,
			required=True
		)
	])
async def reload(ctx: SlashContext, extension: str):
	if not is_owner(ctx):
		await ctx.send(embed=Embed(title="You're not permitted to use this command"))
		return

	try:
		bot.reload_extension(f'{cogs_dir}.{extension}')
		embed = Embed(
			title=f'Extension {extension} reloaded',
			color=0x00ff00
		)
	except Exception as e:
		embed = Embed(
			title='An error occurrred while reloading:',
			description=repr(e),
			color=0xff0000
		)

	await ctx.send(embed=embed)

@slash.slash(name='list-extensions', description='lists the loaded extensions')
async def list_extensions(ctx: SlashContext):
	if not is_owner(ctx):
		await ctx.send(embed=Embed(title="You're not permitted to use this command"))
		return

	await ctx.send(embed=Embed(
		title='Loaded extensions:',
		description='\n'.join(extension.split('.')[-1] for extension in bot.extensions)
	))


print('Starting bot...')
bot.run(cfg.token)
