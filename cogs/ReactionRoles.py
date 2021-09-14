from discord.ext import commands
import discord
from discord import Embed
import json
from discord_slash.model import SlashCommandPermissionType
from CustomChecks import *
from attrdict import AttrMap, AttrDict
from discord_slash import cog_ext
from discord_slash.context import SlashContext
from discord_slash.utils.manage_commands import create_permission
import yaml

def parse_json_object(d: dict):
	return AttrDict({int(k) if str(k).isdigit() else k: v for k, v in d.items()})

def parse_yaml_object(d: dict):
	return [dict_2_map(category) for category in d]

def map_2_dict(m: AttrMap) -> dict:
	return {k: map_2_dict(v) if isinstance(v, AttrMap) else v for k, v in m.items()}

def dict_2_map(d: dict) -> AttrMap:
	return AttrMap({k: dict_2_map(v) if isinstance(v, dict) else v for k, v in d.items()})

def load_data() -> AttrMap:
	with open('data/ReactionRoles.json', encoding='utf-8') as in_file:
		data = json.load(in_file, object_hook=parse_json_object)
	return data

def save_data(data):
	if isinstance(data, AttrMap):
		data = map_2_dict(data)
	with open('data/ReactionRoles.json', 'w', encoding='utf-8') as in_file:
		json.dump(data, in_file, indent=4)

def parse_role(ctx, query_string) -> discord.Role:
	# Check if query_string is an id
	if query_string in (role.id for role in ctx.guild.roles):
		return next(role for role in ctx.guild.roles if role.id == query_string)

	# Check if query_string matches a role name exactly
	if query_string in (role.name for role in ctx.guild.roles):
		return next(role for role in ctx.guild.roles if role.name == query_string)

	# Check if query_string matches a role name case-insensitive
	if query_string.lower() in (role.name.lower() for role in ctx.guild.roles):
		return next(role for role in ctx.guild.roles if role.name.lower() == query_string.lower())
	
	raise KeyError(f'"{query_string}" could not be found as a role in the server')

def load_all_reaction_roles():
    file_name = 'data/AllReactionRoles.yaml'
    with open(file_name) as config_file:
        data = yaml.safe_load(config_file)
    return parse_yaml_object(data)
	# with open('data/AllReactionRoles.json', encoding='utf-8') as in_file:
	# 	return json.load(in_file, object_hook=parse_json_obj)

def get_n_letter_emojis(n):
	for i in range(n):
		i += 0b01100000 # ascii offset for lowercase letters
		i += 1
		letter = chr(i)
		yield f'regional_indicator_{letter}'

def get_n_number_emojis(n):
	number_names = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'keycap_ten']
	for number in number_names:
		yield number

def generate_emojis(role_names: list):
	if len(role_names) <= 10:
		emojis = get_n_number_emojis(len(role_names))
	else:
		emojis = get_n_letter_emojis(len(role_names))

	return {role_names[index]: f':{emoji}:' for index, emoji in enumerate(emojis)}

def emoji_from_name(name: str):
	with open('data/DiscordEmojis.json', encoding='utf-8') as in_file:
		categories: list = json.load(in_file)

	for category in categories.values():
		for emoji in category:
			if name.strip(':') in emoji['names']:
				return emoji['surrogates']
	return name

class ReactionRoles(commands.Cog):
	def __init__(self, bot):
		self.bot: commands.Bot = bot
		self.cfg = load_config()

	@is_admin()
	@commands.command(name='PostAllRoles')
	async def post_all_roles(self, ctx: SlashContext):
		all_roles = load_all_reaction_roles()
		data = load_data()
		
		for category in all_roles:
			if not category.custom_emojis:
				category['roles'] = generate_emojis(category.roles)

			description = '\n\n'.join(f"{emoji} - {role_name}" for role_name, emoji in category['roles'].items())

			sent_msg = await ctx.channel.send(embed=Embed(
				title=category.title,
				description=description,
				color=category.color
			))
			
			roles_dict = {}
			for role_str, emoji_name in category['roles'].items():
				emoji = emoji_from_name(emoji_name.strip(':'))
				await sent_msg.add_reaction(emoji)

				role = parse_role(ctx, role_str)
				roles_dict[emoji] = role.id if role else None

			data[sent_msg.id] = {
				'roles': roles_dict,
				'unique': category['unique']
			}
		
		save_data(data)
	
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

		msg_data: AttrMap = msgs[payload.message_id]

		emoji = payload.emoji.name
		if emoji not in msg_data.roles:
			return
		role_id = msg_data.roles[emoji]

		guild: discord.Guild = self.bot.get_guild(payload.guild_id)
		role: discord.Role = guild.get_role(role_id)
		member: discord.Member = guild.get_member(payload.user_id)

		if payload.event_type == 'REACTION_ADD':
			action = member.add_roles
			if msg_data.unique:
				roles_to_remove = [guild.get_role(r) for r in msg_data.roles.values() if r != role_id]
				await member.remove_roles(*roles_to_remove, reason='Unique Reaction Role')
		else:
			action = member.remove_roles

		await action(role, reason='Reaction Role')


def setup(bot):
	bot.add_cog(ReactionRoles(bot))