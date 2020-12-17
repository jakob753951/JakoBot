from os import listdir
from os.path import isfile, join
import asyncio
import discord
from discord.ext import commands
import GenerateConfig

print('Generating configs...')
GenerateConfig.generate_all()

from Configuration import *

cfg = load_config('config.json')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or(cfg.prefix), description=cfg.description, intents=intents, pm_help=True)

#load cogs from cogs_dir
cogs_dir = "enabled_cogs"
if __name__ == '__main__':
	#for every file (no extension) in cogs_dir
	for file_name in [''.join(f.split('.')[:-1]) for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
		bot.load_extension(f'{cogs_dir}.{file_name}')

@bot.event
async def on_ready():
	print(f'Connected!')
	print(f'Username: {bot.user.name}')
	print(f'ID: {bot.user.id}')

is_owner = lambda ctx: ctx.author.id == cfg.owner_id

@bot.command()
@commands.check(is_owner)
async def load(ctx, extension_name: str):
	try:
		bot.load_extension(f'{cogs_dir}.{extension_name}')
		await ctx.send(f'Extension {extension_name} loaded')
	except Exception as e:
		await ctx.send(f'An error occurrred while loading: "{repr(e)}"')

@bot.command()
@commands.check(is_owner)
async def unload(ctx, extension_name: str):
	try:
		bot.unload_extension(f'{cogs_dir}.{extension_name}')
		await ctx.send(f'Extension {extension_name} unloaded')
	except Exception as e:
		await ctx.send(f'An error occurrred while unloading: "{repr(e)}"')

@bot.command()
@commands.check(is_owner)
async def reload(ctx, extension_name: str):
	try:
		bot.reload_extension(f'{cogs_dir}.{extension_name}')
		await ctx.send(f'Extension {extension_name} reloaded')
	except Exception as e:
		await ctx.send(f'An error occurrred while reloading: "{repr(e)}"')

print('Starting bot...')
bot.run(cfg.token)
