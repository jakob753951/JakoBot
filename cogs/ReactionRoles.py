from discord.ext import commands
import discord
import json
from CustomChecks import *
from attrdict import AttrDict

requirements = {'general': [], 'server': []}

def load_data():
	with open('ReactionRoles.json', encoding='utf-8') as in_file:
		data = json.load(in_file)
	return data

def save_data(data):
	with open('ReactionRoles.json', 'w', encoding='utf-8') as in_file:
		json.dump(data, in_file)

def parse_role(ctx, role) -> discord.Role:
	# Check if role is an id
	if role in (role.id for role in ctx.guild.roles):
		return next(role for role in ctx.guild.roles if role.id == role)

	# Check if role matches a role name exactly
	if role in (role.name for role in ctx.guild.roles):
		return next(role for role in ctx.guild.roles if role.name == role)

	# Check if role matches a role name case-insensitive
	if role.lower() in (role.name.lower() for role in ctx.guild.roles):
		return next(role.lower() for role in ctx.guild.roles if role.name.lower() == role.lower())
	
	raise KeyError

class ReactionRoles(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@is_admin()
	@commands.command(name='PostEmbed')
	async def post_embed(self, ctx, json_str = None):
		if json_str == None:
			with open('data/Embed.json') as embed_file:
				json_str = embed_file.read()

		embed_dict = json.loads(json_str)
		embed = discord.Embed.from_dict(embed_dict)
		await ctx.send(embed=embed)
		await ctx.message.delete()
	
	@is_admin()
	@commands.command(name='AddReaction')
	async def add_reaction(self, ctx, emoji, *, role: str):
		try:
			role = parse_role(ctx, role)
		except KeyError:
			await ctx.send('Role not found')
			return

		[ctx.message.id] = {'role_id': role.id, 'unique': False}
	
	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		await self.handle_reaction(self, payload)
	
	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		await self.handle_reaction(self, payload)

	async def handle_reaction(self, payload: discord.RawReactionActionEvent):
		msgs = load_data()

		if payload.message_id not in msgs:
			return
		
		msg_data = AttrDict(msgs[payload.message_id])


def setup(bot):
	bot.add_cog(ReactionRoles(bot))