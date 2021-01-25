from os import listdir
from os.path import isfile, join
import discord
from discord.ext import commands
import GenerateConfig

print('Generating configs...')
GenerateConfig.generate_all()

from Configuration import *

print('Loading config...')
cfg = load_config('Config.json')

intents = discord.Intents.default()
intents.members = True

print('making bot...')
bot = commands.Bot(command_prefix=commands.when_mentioned_or(cfg.prefix), description=cfg.description, intents=intents, pm_help=True)

print('loading cogs...')
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
		embed = discord.Embed(color=0x00ff00, title=f'Extension {extension_name} loaded')
	except Exception as e:
		embed = discord.Embed(color=0xff0000, title='An error occurrred while loading:', description=repr(e))
	await ctx.send(embed=embed)

@bot.command()
@commands.check(is_owner)
async def unload(ctx, extension_name: str):
	try:
		bot.unload_extension(f'{cogs_dir}.{extension_name}')
		embed = discord.Embed(color=0x00ff00, title=f'Extension {extension_name} unloaded')
	except Exception as e:
		embed = discord.Embed(color=0xff0000, title='An error occurrred while unloading:', description=repr(e))
	await ctx.send(embed=embed)

@bot.command()
@commands.check(is_owner)
async def reload(ctx, extension_name: str):
	try:
		bot.reload_extension(f'{cogs_dir}.{extension_name}')
		embed = discord.Embed(color=0x00ff00, title=f'Extension {extension_name} reloaded')
	except Exception as e:
		embed = discord.Embed(color=0xff0000, title='An error occurrred while reloading:', description=repr(e))
	await ctx.send(embed=embed)


print('Starting bot...')
bot.run(cfg.token)
