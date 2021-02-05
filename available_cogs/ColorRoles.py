from asyncio import gather, sleep
import discord
from discord import Embed
from discord.ext import commands
from Configuration import load_config
import json
from CurrencyUtils import *
import CurrencyManager as currency

requirements = {'general': [], 'server': ['react_confirm']}

def get_preset_roles(guild_id):
	with open('data/ColorRoles.json') as color_roles_file:
		color_roles = json.loads(color_roles_file.read())

	guild_data = color_roles[str(guild_id)]

	return guild_data['preset_roles']

def get_preset_role_info(guild: discord.Guild, role_index: int) -> dict:
	with open('data/ColorRoles.json') as color_roles_file:
		color_roles = json.loads(color_roles_file.read())

	guild_data = color_roles[str(guild.id)]

	preset_roles = guild_data['preset_roles']

	role_id = preset_roles[role_index % len(preset_roles)]

	role = guild.get_role(role_id)

	return {
		'id': role_id,
		'name': role.name,
		'price': guild_data['preset_cost']
	}

def get_role_menu(guild: discord.Guild, role_index: int) -> Embed:
	with open('data/ColorRoles.json') as color_roles_file:
		color_roles = json.loads(color_roles_file.read())

	guild_data = color_roles[str(guild.id)]

	preset_roles = guild_data['preset_roles']

	role_id = preset_roles[role_index % len(preset_roles)]
	role = guild.get_role(role_id)

	embed = Embed(
		title=role.name,
		color=role.color,
		description=guild_data['instructions'].format(amount=guild_data['preset_cost'])
	)

	return embed

class ColorRoles(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')
		self.menus = {}
		self.examine_messages = {}
		self.confirms = {}

	async def display_menu(self, guild: discord.Guild, channel: discord.abc.Messageable, page: int):
		preset_roles = get_preset_roles(guild.id)

		numbers = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
		desc = '\n'.join([
			f"**{numbers[i]} : {guild.get_role(role_id).name}**"
			for i, role_id
			in enumerate(preset_roles[page*10:page*10+10])
		])

		sent_msg = await channel.send(embed=Embed(description=desc))
		self.menus[sent_msg.id] = 0
		emojis = ['◀', '▶', *numbers]
		await gather(*(sent_msg.add_reaction(emoji) for emoji in emojis[:len(preset_roles)+2]))

	async def display_examine(self, guild: discord.Guild, channel: discord.abc.Messageable, role_index: int):
		embed = get_role_menu(guild, role_index)

		sent_msg = await channel.send(embed=embed)

		self.examine_messages[sent_msg.id] = 0

		await gather((sent_msg.add_reaction(emoji) for emoji in ['◀', '💰', '▶']))

	@commands.command(name='Shop', aliases=['Store', 'ColorRoles'])
	async def shop(self, ctx, page = 0):
		await self.display_menu(ctx.guild, ctx.channel, page)

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
		msg_cfg = self.cfg.servers[guild.id]

		if message.id in self.menus:
			page = self.menus[message.id]
			if reaction.emoji in ['◀', '▶']:
				if reaction.emoji == '◀':
					page -= 1
				if reaction.emoji == '▶':
					page += 1

				page = page % ((len(get_preset_roles(guild.id)) // 10) + 1)

				self.examine_messages[message.id] = page
				await message.edit(embed=get_role_menu(guild, page))
				return

			numbers = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']

			selection = numbers.index(reaction.emoji)
			index = 10*page+selection

			await message.edit(embed=get_role_menu(guild, index))
			await message.clear_reactions()
			await gather(*(message.add_reaction(emoji) for emoji in ['◀', '💰', '▶']))
			del self.menus[message.id]
			self.examine_messages[message.id] = index

		if message.id in self.examine_messages:
			page = self.examine_messages[message.id]
			if reaction.emoji == '💰':
				role = get_preset_role_info(guild, page)
				if await currency.getMemberBalance(guild.id, user.id) < role['price']:
					sent_msg = await channel.send(embed=Embed(description=f"{user.mention} you do not have enough money to buy that.", color=0xff0000))
					await sleep(5)
					await sent_msg.delete()
					return
				await message.edit(embed=Embed(
					title='Confirmation',
					description=f"{user.mention} are you sure you want to buy {role['name']} for **{role['price']}** {pluralise(msg_cfg, role['price'])}?"
				))
				await message.clear_reactions()
				await gather(
					message.add_reaction('✅'),
					message.add_reaction('❎')
				)
				del self.examine_messages[message.id]
				self.confirms[message.id] = (user.id, role)
				return

			if reaction.emoji == '◀':
				page -= 1
			if reaction.emoji == '▶':
				page += 1
			self.examine_messages[message.id] = page

			await message.edit(embed=get_role_menu(guild, page))


		if message.id in self.confirms:
			confirm_data = self.confirms[message.id]
			if user.id != confirm_data[0]:
				return

			if reaction.emoji == '❎':
				await message.delete()

			if reaction.emoji == '✅':
				role_data = confirm_data[1]
				new_balance = await currency.addToMemberBalance(guild.id, user.id, -role_data['price'])

				role = guild.get_role(role_data['id'])
				roles = [guild.get_role(id) for id in get_preset_roles(guild.id)]
				roles.remove(role)

				await user.remove_roles(*roles, reason='Purchased new role')
				await user.add_roles(role, reason='Purchased role')
				await transaction_log(self.bot, msg_cfg, user, -role_data['price'], title='User bought a Color role.')
				await message.channel.send(embed=Embed(
					title='Congrats!',
					description=f'New balance: {new_balance} {pluralise(msg_cfg, new_balance)}'
				))
				await message.delete()


def setup(bot):
	bot.add_cog(ColorRoles(bot))