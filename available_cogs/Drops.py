import asyncio
import random
from datetime import datetime, timedelta
import json
import discord
from discord.ext import commands
from Configuration import *

requirements = {'general': [], 'server': ['react_confirm']}

fmt = "%Y-%m-%dT%H:%M:%S"

class Drops(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')
		try:
			with open('data/DropChannels.json') as data_file:
				self.data = json.loads(data_file.read())
		except Exception as e:
			print(f'Error when loading DropChannels.json: {e}')
			self.data = {}
			print('defaulting to "\{\}"')

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return

		if not str(message.channel.id) in self.data:
			return

		if message.content.startswith('.'):
			return

		# Get the data for the channel the message was sent in
		channel_data = self.data[str(message.channel.id)]

		# Check that channel has not had a drop recently
		last_message_time = datetime.strptime(channel_data['last_drop'], "%Y-%m-%dT%H:%M:%S")
		available_time = last_message_time + timedelta(minutes=channel_data['minute_difference'])

		cur_time = datetime.now()
		if not available_time < cur_time:
			return

		# Check against chance
		if not random.random() < channel_data['drop_chance']:
			return

		# If we reach this point, we should make a drop

		# Get random drop with biases
		with open('data/Drops.json') as drop_file:
			drops = json.loads(drop_file.read())

		chosen_drop = random.choices(population=drops['drops'], weights=drops['probabilities'])[0]

		# Get value
		amount = random.randrange(chosen_drop['min_value'], chosen_drop['max_value']+1)


		drop = {'name': chosen_drop['name'], 'amount': amount, 'pick_message': chosen_drop['pick_message']}


		with open('data/Currency.json') as money_file:
			currency = json.loads(money_file.read())

		sent_message = await message.channel.send(chosen_drop['drop_message'].format(name=drop['name'], amount=drop['amount'], curr_name=currency[str(message.guild.id)]['currency_name']))
		drop['message_id'] = sent_message.id

		# Add drop to channel
		self.data[str(message.channel.id)]['active_drops'].append(drop)
		self.data[str(message.channel.id)]['last_drop'] = datetime.strftime(datetime.utcnow(), fmt)

		with open('data/DropChannels.json', 'w') as data_file:
			data_file.write(json.dumps(self.data, indent=4))

	@commands.command(name='AddDrops', aliases=['adddrops'])
	async def add_drops(self, ctx, channel: discord.TextChannel = None, chance = '0.01', minutes_between = 10):
		if not channel:
			channel = ctx.channel

		if str(channel.id) in self.data:
			msg = await ctx.send('Channel already gets drops. remove them before trying to add them again.')
			await asyncio.sleep(5)
			await msg.delete()
			return


		min_time = datetime.fromtimestamp(0)

		channel_data = {
			'drop_chance': float(chance),
			'last_drop': datetime.strftime(min_time, fmt),
			'minute_difference': int(minutes_between),
			'active_drops': []
			}

		self.data[str(channel.id)] = channel_data

		with open('data/DropChannels.json', 'w') as data_file:
			data_file.write(json.dumps(self.data, indent=4))

		await ctx.message.add_reaction(self.cfg.servers[ctx.guild.id].react_confirm)

	@commands.command(name='Pick', aliases=['pick'])
	async def pick(self, ctx):
		if str(ctx.channel.id) not in self.data:
			return

		if not self.data[str(ctx.channel.id)]['active_drops']:
			sent_msg = await ctx.send('Nothing to be picked!')
			await asyncio.sleep(5)
			await sent_msg.delete()
			await ctx.message.delete()
			return

		drop = self.data[str(ctx.channel.id)]['active_drops'].pop()

		with open('data/Currency.json') as money_file:
			currency = json.loads(money_file.read())
		currency[str(ctx.guild.id)]['users'][str(ctx.author.id)]['balance'] += drop['amount']

		drop_message = await ctx.channel.fetch_message(drop['message_id'])

		await ctx.message.delete()
		await drop_message.delete()
		await ctx.send(drop['pick_message'].format(name=drop['name'], amount=drop['amount'], curr_name=currency[str(ctx.guild.id)]['currency_name']))


def setup(bot):
	bot.add_cog(Drops(bot))