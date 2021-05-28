from discord.ext import commands
import discord
import json
from CustomChecks import *
from attrdict import AttrMap

requirements = {'general': [], 'server': []}

def parse_json_obj(d: dict):
	return AttrMap({int(k) if k.isnumeric() else k: v for k, v in d.items()})

def map_2_dict(m: AttrMap) -> dict:
	return {k: map_2_dict(v) if isinstance(v, AttrMap) else v for k, v in m.items()}

def load_data() -> AttrMap:
	with open('data/ReactionRoles.json', encoding='utf-8') as in_file:
		data = json.load(in_file, object_hook=parse_json_obj)

	return data

def save_data(data):
	if isinstance(data, AttrMap):
		data = map_2_dict(data)
	with open('data/ReactionRoles.json', 'w', encoding='utf-8') as in_file:
		json.dump(data, in_file, indent=4)

def parse_role(ctx, query_string) -> discord.Role:
	# Check if query_string is an id
	if query_string in (role.id for role in ctx.guild.roles):
		return next(role for role in ctx.guild.roles if role.id == role)

	# Check if query_string matches a role name exactly
	if query_string in (role.name for role in ctx.guild.roles):
		return next(role for role in ctx.guild.roles if role.name == role)

	# Check if query_string matches a role name case-insensitive
	if query_string.lower() in (role.name.lower() for role in ctx.guild.roles):
		return next(role for role in ctx.guild.roles if role.name.lower() == query_string.lower())
	
	raise KeyError

class ReactionRoles(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config()
	
	@is_admin()
	@commands.command(name='AddReaction')
	async def add_reaction(self, ctx, message_id: int, emoji, *, role: str):
		try:
			role = parse_role(ctx, role)
		except KeyError as e:
			await ctx.send('Role not found')
			return

		msgs = load_data()
		if message_id not in msgs:
			msgs[message_id] = AttrMap({
				'roles': {},
				'unique': False 
			})

		msgs[message_id].roles[emoji] = role.id
		save_data(msgs)
		await ctx.message.add_reaction(self.cfg.react_confirm)
	
	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		await self.handle_reaction(payload)
	
	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		await self.handle_reaction(payload)

	async def handle_reaction(self, payload: discord.RawReactionActionEvent):
		msgs = load_data()

		if payload.message_id not in msgs:
			return
		
		msg_data = msgs[payload.message_id]




def setup(bot):
	bot.add_cog(ReactionRoles(bot))