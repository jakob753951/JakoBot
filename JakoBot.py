from os import listdir
from os.path import isfile, join
import asyncio
from datetime import datetime
import discord
from discord.ext import commands
from Configuration import *
from ServerCfg import *
import GenerateConfig

GenerateConfig.generate_all('fields.json')

cfg = load_config('config.json')

bot = commands.Bot(command_prefix=commands.when_mentioned_or(cfg.prefix), description=cfg.description, pm_help=True)

#load cogs from cogs_dir
cogs_dir = "enabled_cogs"
if __name__ == '__main__':
	#for file (no extension) in cogs_dir
	for file_name in [''.join(f.split('.')[:-1]) for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
		bot.load_extension(f'{cogs_dir}.{file_name}')

@bot.event
async def on_ready():
	print(f'Connected!')
	print(f'Username: {bot.user.name}')
	print(f'ID: {bot.user.id}')

@bot.event
async def on_message(message: discord.Message):
	await bot.process_commands(message)


bot.run(cfg.token)