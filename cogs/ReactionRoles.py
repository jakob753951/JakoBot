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

	@is_admin()
	@commands.command(name='PostReactionRoles')
	async def post_embed(self, ctx, json_str = None):
		if json_str == None:
			with open('data/Embed.json') as embed_file:
				json_str = embed_file.read()

		embed_dict = json.loads(json_str)
		embed = discord.Embed.from_dict(embed_dict)
		await ctx.send(embed=embed)
		await ctx.message.delete()
	
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