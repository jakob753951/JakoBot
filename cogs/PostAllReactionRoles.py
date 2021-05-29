from asyncio.tasks import gather
from attrdict import AttrMap
from discord import Embed
from CustomChecks import *
from discord.ext import commands
from Configuration import *

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

def parse_json_obj(d: dict):
	return AttrDict(d)

def parse_role(ctx, query_string):
	# Check if query_string is an id
	if query_string in (role.id for role in ctx.guild.roles):
		return next(role for role in ctx.guild.roles if role.id == query_string)

	# Check if query_string matches a role name exactly
	if query_string in (role.name for role in ctx.guild.roles):
		return next(role for role in ctx.guild.roles if role.name == query_string)

	# Check if query_string matches a role name case-insensitive
	if query_string.lower() in (role.name.lower() for role in ctx.guild.roles):
		return next(role for role in ctx.guild.roles if role.name.lower() == query_string.lower())

def load_all_reaction_roles():
	with open('data/AllReactionRoles.json', encoding='utf-8') as in_file:
		return json.load(in_file, object_hook=parse_json_obj)

def get_n_letter_emojis(n):
	for i in range(n):
		i += 1
		i += 0b01100000
		letter = chr(i)
		yield f'regional_indicator_{letter}'

number_names = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'keycap_ten']

def generate_emojis(role_names: list):
	if len(role_names) <= 10:
		emojis = number_names[:len(role_names)]
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


class PostAllReactionRoles(commands.Cog):
	def __init__(self, bot):
		self.bot: commands.Bot = bot
		self.cfg = load_config()
	
	@is_admin()
	@commands.command(name='PostAllRoles')
	async def post_all_roles(self, ctx):
		all_roles = load_all_reaction_roles()
		data = load_data()
		
		for category in all_roles:

			if not category.custom_emojis:
				category['roles'] = generate_emojis(category.roles)

			description = '\n\n'.join(f"{emoji} - {role_name}" for role_name, emoji in category['roles'].items())

			sent_msg = await ctx.send(embed=Embed(
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


def setup(bot):
	bot.add_cog(PostAllReactionRoles(bot))