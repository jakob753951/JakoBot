from CustomExceptions import InsufficientFundsException
from asyncio import gather, sleep
import asyncio
import discord
from discord import Embed
from discord.ext import commands
from Configuration import load_config
import json
from CurrencyUtils import *
import CurrencyManager as currency
import re

requirements = {'general': [], 'server': ['react_confirm']}

def get_guild_data(guild_id: int):
	with open('data/ColorRoles.json') as color_roles_file:
		color_roles = json.loads(color_roles_file.read())

	return color_roles[str(guild_id)]

def get_preset_roles(guild_id: int):
	return get_guild_data(guild_id)['preset_roles']

def get_id_by_index(guild_id: int, index: int) -> int:
	preset_roles = get_preset_roles(guild_id)
	return preset_roles[index % len(preset_roles)]

def get_preset_role_by_index(guild: discord.Guild, index: int) -> discord.Role:
	role_id = get_id_by_index(guild.id, index)
	return guild.get_role(role_id)

def get_preset_role_info(guild: discord.Guild, role_index: int) -> dict:
	guild_data = get_guild_data(guild.id)
	role_id = get_id_by_index(guild.id, role_index)
	role = get_preset_role_by_index(guild, role_index)

	return {
		'id': role_id,
		'name': role.name,
		'price': guild_data['preset_cost']
	}

def get_role_embed(guild: discord.Guild, role_index: int) -> Embed:
	guild_data = get_guild_data(guild.id)

	role = get_preset_role_by_index(guild, role_index)


	embed = Embed(
		title=role.name,
		color=role.color,
		description=guild_data['instructions'].format(amount=guild_data['preset_cost'])
	)

	return embed

def get_menu_embed(guild: discord.Guild, page: int) -> Embed:
	preset_roles = get_preset_roles(guild.id)

	numbers = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
	desc = '\n'.join([
		f"{numbers[i]} : {guild.get_role(role_id).name}"
		for i, role_id
		in enumerate(preset_roles[page*10:page*10+10])
	])

	return Embed(title='Preset Color Roles:', description=desc)

def hex_to_int(hex_code):
	return int(hex_code.strip('#'), 16)

def parse_args(args):
	pattern = re.compile(r'#?[0-9a-f]{6}$')
	if pattern.match(args[-1]):
		return ' '.join(args[:-1]), hex_to_int(args[-1])
	return ' '.join(args), None

async def currency_check(guild_id, member_id, minimum_balance):
	member_balance = await currency.getMemberBalance(guild_id, member_id)
	if member_balance < minimum_balance:
		return False
	return True

async def handle_insufficient_funds(ctx, exception: InsufficientFundsException = None):
	await ctx.send(embed=Embed(title='Insufficient Funds.'))

class ConfirmAwaiter(commands.Cog):
	def __init__(self, bot, user, msg_id, positive, negative):
		self.bot = bot
		self.msg_id = msg_id
		self.confirmer = user
		self.positive = positive
		self.negative = negative
		self.on_confirm = asyncio.Event()

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if reaction.message.id != self.msg_id:
			return

		if user != self.confirmer:
			return

		if reaction.emoji not in [self.positive, self.negative]:
			return

		self.did_confirm = reaction.emoji == self.positive

		self.on_confirm.set()

class ColorRoles(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')
		self.menus = {}
		self.examine_messages = {}
		self.confirms = {}

	async def display_menu(self, guild: discord.Guild, channel: discord.abc.Messageable, page: int):
		preset_roles = get_preset_roles(guild.id)
		numbers = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
		sent_msg = await channel.send(embed=get_menu_embed(guild, page))
		self.menus[sent_msg.id] = 0
		emojis = ['◀', '▶', *numbers]
		await gather(*(sent_msg.add_reaction(emoji) for emoji in emojis[:len(preset_roles)+2]))

	async def display_examine(self, guild: discord.Guild, channel: discord.abc.Messageable, role_index: int):
		embed = get_role_embed(guild, role_index)

		sent_msg = await channel.send(embed=embed)

		self.examine_messages[sent_msg.id] = 0

		await gather((sent_msg.add_reaction(emoji) for emoji in ['◀', '💰', '▶']))

	@commands.command(name='Shop', aliases=['Store', 'ColorRoles'])
	async def shop(self, ctx, page = 0):
		await self.display_menu(ctx.guild, ctx.channel, page)

	@commands.command(name='CustomRole', aliases=['CustomColor'])
	async def custom_role(self, ctx, *args):
		role_name, role_color = parse_args(args)
		role_price = 10000 if role_color else 2000
		role = await ctx.guild.create_role(name=role_name)

		if not await currency_check(ctx.guild.id, ctx.author.id, role_price):
			await handle_insufficient_funds(ctx)
			return

		if role_color:
			await role.edit(color=role_color)
			embed = Embed(title='Do you want this to be your **Visible** color?')
			if await self.get_confirmation(ctx.channel, ctx.author, embed):
				await self.give_role_priority(role)

		embed = Embed(
			title=f'Are you sure you want to buy a role with the name {role_name} for {role_price} {pluralise(ctx.guild.id, role_price)}?'
		)
		if not await self.get_confirmation(ctx.channel, ctx.author, embed):
			await role.delete()
			return

		try:
			await currency.addToMemberBalance(ctx.guild.id, ctx.author.id, -role_price)
		except InsufficientFundsException as e:
			await handle_insufficient_funds(ctx, e)
			return

		await gather(
			ctx.author.add_roles(role),
			ctx.send(embed=Embed(title=f'Congrats on your new role.\nYou have been charged {role_price}.'))
		)

	async def get_confirmation(self, channel: discord.abc.Messageable, user: discord.User, message: Embed, positive: str = '👍', negative: str = '👎'):
		sent_msg = await channel.send(embed=message)
		await gather(
			sent_msg.add_reaction(positive),
			sent_msg.add_reaction(negative)
		)

		cog = ConfirmAwaiter(
			self.bot,
			user,
			sent_msg.id,
			positive=positive,
			negative=negative
		)

		self.bot.add_cog(cog)
		await cog.on_confirm.wait()
		did_confirm = cog.did_confirm
		self.bot.remove_cog(cog)
		await sent_msg.delete()
		return did_confirm

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		await self.on_reaction(reaction, user)

	@commands.Cog.listener()
	async def on_reaction_remove(self, reaction, user):
		await self.on_reaction(reaction, user)

	async def on_reaction(self, reaction, user):
		if user.bot:
			return

		message = reaction.message
		channel = message.channel
		guild = message.guild

		if message.id in self.menus:
			page = self.menus[message.id]
			if reaction.emoji in ['◀', '▶']:
				if reaction.emoji == '◀':
					page -= 1
				if reaction.emoji == '▶':
					page += 1

				page = page % ((len(get_preset_roles(guild.id)) // 10) + 1)

				self.menus[message.id] = page
				await message.edit(embed=get_menu_embed(guild, page))
				return

			numbers = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']

			selection = numbers.index(reaction.emoji)
			index = 10*page+selection

			await message.edit(embed=get_role_embed(guild, index))
			await message.clear_reactions()
			await gather(*(message.add_reaction(emoji) for emoji in ['◀', '💰', '▶']))
			del self.menus[message.id]
			self.examine_messages[message.id] = index

		if message.id in self.examine_messages:
			page = self.examine_messages[message.id]
			if reaction.emoji == '💰':
				role_data = get_preset_role_info(guild, page)
				if await currency.getMemberBalance(guild.id, user.id) < role_data['price']:
					sent_msg = await channel.send(embed=Embed(description=f"{user.mention} you do not have enough money to buy that.", color=0xff0000))
					await sleep(5)
					await sent_msg.delete()
					return

				embed = Embed(
					title='Confirmation',
					description=f"{user.mention} are you sure you want to buy {role_data['name']} for **{role_data['price']}** {pluralise(user.guild.id, role_data['price'])}?"
				)

				did_confirm = await self.get_confirmation(message.channel, message.author, embed)
				if not did_confirm:
					return

				new_balance = await currency.addToMemberBalance(guild.id, user.id, -role_data['price'])

				role = guild.get_role(role_data['id'])
				roles = [guild.get_role(id) for id in get_preset_roles(guild.id) if id != role_data['id']]

				await user.remove_roles(*roles, reason='Purchased new role')
				await user.add_roles(role, reason='Purchased role')
				await transaction_log(self.bot, user.guild.id, user, -role_data['price'], title='User bought a Color role.')
				await message.channel.send(embed=Embed(
					title='Congrats!',
					description=f'New balance: {new_balance} {pluralise(user.guild.id, new_balance)}'
				))
				return

			if reaction.emoji == '◀':
				page -= 1
			if reaction.emoji == '▶':
				page += 1
			self.examine_messages[message.id] = page

			await message.edit(embed=get_role_embed(guild, page))


def setup(bot):
	bot.add_cog(ColorRoles(bot))