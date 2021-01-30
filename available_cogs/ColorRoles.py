import discord
from discord.ext import commands
from Configuration import load_config
import json

requirements = {'general': [], 'server': ['react_confirm']}

def load_guild_roles(guild_id):
	with open('data/ColorRoles.json') as color_files:
		return json.load(color_files.read())[str(guild_id)]

class ColorRoles(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')

	def get_preset_embed(self, guild_id):
		guild_data = load_guild_roles(guild_id)
		for preset in guild_data['preset']:
			role_id = preset['role_id']
			role_price = preset['price']



def setup(bot):
	bot.add_cog(ColorRoles(bot))