import asyncio
import random
from datetime import datetime, timedelta
import json
import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError
from Configuration import *
import CurrencyManager as currency

requirements = {'general': [], 'server': ['react_confirm']}

fmt = "%Y-%m-%dT%H:%M:%S"

def pluralise(server_cfg, amount):
	if abs(amount) == 1:
		return server_cfg.currency_name_singular
	else:
		return server_cfg.currency_name_plural


class Drops(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')
		try:
			self.load_data()
		except Exception as e:
			print(f'Error when loading DropChannels.json: {e}')
			self.data = {}
			print('defaulting to "\{\}"')

	def load_data(self):
		with open('data/DropChannels.json') as data_file:
			self.data = json.loads(data_file.read())

	def save_data(self):
		with open('data/DropChannels.json', 'w') as data_file:
			data_file.write(json.dumps(self.data, indent=4))

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return

		self.load_data()

		if not str(message.channel.id) in self.data:
			return

		if message.content.startswith('.'):
			return

		msg_cfg = self.cfg.servers[message.guild.id]

		# Get the data for the channel the message was sent in
		channel_data = self.data[str(message.channel.id)]

		# Check that channel has not had a drop recently
		last_message_time = datetime.strptime(channel_data['last_drop'], fmt)
		available_time = last_message_time + timedelta(minutes=channel_data['minute_difference'])

		cur_time = datetime.utcnow()
		if not available_time < cur_time:
			return

		# Check against chance
		if not random.random() < channel_data['drop_chance']:
			return

		# If we reach this point, we should make a drop

		# Get random drop with biases
		with open('data/Drops.json') as drop_file:
			drops = json.loads(drop_file.read())[str(message.guild.id)]

		chosen_drop = random.choices(population=drops['drops'], weights=drops['probabilities'])[0]

		# Get value
		pick_value = random.randrange(chosen_drop['pick_min_value'], chosen_drop['pick_max_value']+1)
		run_value = random.randrange(chosen_drop['run_min_value'], chosen_drop['run_max_value']+1)


		drop = {
			'name': chosen_drop['name'],
			'pick_value': pick_value,
			'run_value': run_value,
			'pick_message': chosen_drop['pick_message'],
			'run_message': chosen_drop['run_message'],
		}

		desc = chosen_drop['drop_message'].format(
			name=chosen_drop['name'],
			amount=drop['pick_value'],
			abs_amount=abs(drop['pick_value']),
			curr_name=pluralise(msg_cfg, drop['pick_value'])
		)

		embed = discord.Embed(color=0xff0000, title='A drop has appeared!', description=desc, timestamp=datetime.utcnow())
		embed.set_image(url=f"https://ladegaardmoeller.dk/JakoBot/Drops/Images/{chosen_drop['drop_image']}")
		sent_msg = await message.channel.send(embed=embed)

		drop['message_id'] = sent_msg.id

		# Add drop to channel
		self.data[str(message.channel.id)]['active_drops'].append(drop)
		self.data[str(message.channel.id)]['last_drop'] = datetime.strftime(datetime.utcnow(), fmt)

		self.save_data()

	@commands.command(name='AddDrops', aliases=['adddrops', 'enabledrops', 'editdrops', 'changedrops', 'dropsadd', 'dropsenable', 'dropsedit', 'dropschange'])
	async def add_drops(self, ctx, channel: discord.TextChannel = None, chance: float = 0.05, minutes_between = 10):
		if not channel:
			channel = ctx.channel

		self.load_data()

		last_drop = None
		if str(channel.id) in self.data:
			last_drop = self.data[str(channel.id)]['last_drop']

		min_time = datetime.fromtimestamp(0)

		channel_data = {
			'drop_chance': chance,
			'last_drop': last_drop or datetime.strftime(min_time, fmt),
			'minute_difference': int(minutes_between),
			'active_drops': []
		}

		self.data[str(channel.id)] = channel_data

		self.save_data()

		await ctx.message.add_reaction(self.cfg.servers[ctx.guild.id].react_confirm)

	@commands.command(name='RemoveDrops', aliases=['removedrops', 'disabledrops'])
	async def remove_drops(self, ctx, channel: discord.TextChannel = None):
		if not channel:
			channel = ctx.channel

		del self.data[str(channel.id)]
		self.save_data()

	@commands.command(name='Pick', aliases=['pick', 'take'])
	async def pick(self, ctx):
		await self.grab_drop(ctx, 'pick')

	@commands.command(name='Run', aliases=['run', 'ignore'])
	async def run(self, ctx):
		await self.grab_drop(ctx, 'run')

	async def grab_drop(self, ctx, take_kind):
		msg_cfg = self.cfg.servers[ctx.guild.id]
		if str(ctx.channel.id) not in self.data:
			return

		self.load_data()

		if not self.data[str(ctx.channel.id)]['active_drops']:
			sent_msg = await ctx.send('Nothing to be picked!')
			await ctx.message.delete()
			await asyncio.sleep(5)
			await sent_msg.delete()
			return

		drop = self.data[str(ctx.channel.id)]['active_drops'].pop()
		self.save_data()

		amount = drop['pick_value' if take_kind == 'pick' else 'run_value']

		await currency.addToMemberBalance(ctx.guild.id, ctx.author.id, amount)

		try:
			drop_message = await ctx.channel.fetch_message(drop['message_id'])
		except Exception:
			drop_message = None

		await ctx.message.delete()
		if drop_message:
			await drop_message.delete()

		text = drop['pick_message' if take_kind == 'pick' else 'run_message']
		sent_msg = await ctx.send(text.format(user=ctx.author.mention, name=drop['name'], amount=amount, abs_amount=abs(amount), curr_name=pluralise(msg_cfg, amount)))
		await asyncio.sleep(5)
		await sent_msg.delete()

def setup(bot):
	bot.add_cog(Drops(bot))