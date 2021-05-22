from discord.ext import commands
import discord
import json
from CustomChecks import *
from attrdict import AttrDict

requirements = {'general': [], 'server': []}

def load_reaction_roles():
	with open('ReactionRoles.json', encoding='utf-8') as in_file:
		data = json.load(in_file)
	return data

class ReactionRoles(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		await self.handle_reaction(self, payload)
	
	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		await self.handle_reaction(self, payload)

	async def handle_reaction(self, payload: discord.RawReactionActionEvent):
		msgs = load_reaction_roles()

		if payload.message_id not in msgs:
			return
		
		msg_data = AttrDict(msgs[payload.message_id])


def setup(bot):
	bot.add_cog(ReactionRoles(bot))