from datetime import timedelta
import os
import discord
from discord.ext import commands
from Configuration import *
import CurrencyManager as manager
from CurrencyUtils import *
from CustomChecks import *
from asyncio import gather
import json
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

requirements = {
	'general': [],
	'server': [
		'react_confirm',
		'chan_transaction_history',
		'currency_name_singular',
		'currency_name_plural',
		'role_staff',
		'rewards_sheet_id'
	]
}

fmt = "%Y-%m-%dT%H:%M:%S"

def get_cooldown(guild_id, user_id, reward_id):
	with open('data/RewardCooldowns.json') as cooldowns_file:
		cooldowns = json.loads(cooldowns_file.read())

	try:
		time_string = cooldowns[str(guild_id)][str(user_id)][str(reward_id)]
		return datetime.strptime(time_string, fmt)
	except Exception:
		return datetime.min

def set_cooldown(guild_id, user_id, reward_id):
	with open('data/RewardCooldowns.json') as cooldowns_file:
		cooldowns = json.loads(cooldowns_file.read())
	if str(guild_id) not in cooldowns:
		cooldowns[str(guild_id)] = {}
	if str(user_id) not in cooldowns[str(guild_id)]:
		cooldowns[str(guild_id)][str(user_id)] = {}
	cooldowns[str(guild_id)][str(user_id)][str(reward_id)] = datetime.strftime(datetime.utcnow(), fmt)
	with open('data/RewardCooldowns.json', 'w') as cooldowns_file:
		cooldowns_file.write(json.dumps(cooldowns, indent=4))

def get_rewards(guild_id):
	with open('data/Rewards.json') as rewards_file:
		return json.loads(rewards_file.read())

def get_reward(guild_id, reward_id):
	rewards = get_rewards(guild_id)
	if not str(guild_id) in rewards:
		raise ValueError('Rewards have not been registered for this server.')
	reward_list = [reward for reward in rewards[str(guild_id)] if reward['id'] == reward_id]
	if len(reward_list) != 1:
		raise ValueError('Invalid reward id. Please try again with a correct one.')

	return reward_list[0]

def generate_service():
	scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']

	creds = None
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', scopes)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	return build('sheets', 'v4', credentials=creds)

def load_rewards(guild_id) -> list:
	cfg = load_config('Config.json')
	service = generate_service()
	range_name = 'Rewards!A2:F'

	sheet = service.spreadsheets()
	result = sheet.values().get(spreadsheetId=cfg.servers[guild_id].rewards_sheet_id, range=range_name).execute()
	values = result.get('values', [])

	rewards = []

	for row in values:
		reward_id, name, description, amount, cooldown_in_hours, active = row
		if active.lower() == 'yes':
			rewards.append({
				'id': reward_id,
				'name': name,
				'description': description,
				'amount': int(amount),
				'cooldown_in_hours': int(cooldown_in_hours)
			})

	with open('data/Rewards.json', 'w') as rewards_file:
		rewards_file.write(json.dumps(rewards))

class Rewards(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')

	@commands.guild_only()
	@commands.check_any(is_admin(), is_staff())
	@commands.command(name='Reward', aliases=['Award'])
	async def reward(self, ctx, member: discord.Member, *reward_ids):
		if ctx.author == member:
			return

		for reward_id in reward_ids:
			try:
				reward = get_reward(ctx.guild.id, reward_id.lower())
			except ValueError as e:
				await ctx.send(repr(e))
				return

			last_reward_time = get_cooldown(ctx.guild.id, member.id, reward_id.lower())

			available_time = last_reward_time + timedelta(hours=reward['cooldown_in_hours'])

			cur_time = datetime.utcnow()
			if not available_time < cur_time:
				title = f"Reward {reward['name']} not yet available."
				embed = discord.Embed(color=0xff0000, title=title, timestamp=available_time)
				embed.set_footer(text='Next reward will be available: ')
				await ctx.send(embed=embed)
				return

			amount = reward['amount']

			set_cooldown(ctx.guild.id, member.id, reward_id.lower())

			desc=f"{member.mention} was rewarded {amount} {pluralise(ctx.guild.id, amount)} for task number {reward_id.upper()}: {reward['name']}"
			embed = discord.Embed(color=0x00ff00, description=desc, timestamp=datetime.utcnow())
			await gather(
				manager.addToMemberBalance(ctx.guild.id, member.id, amount),
				transaction_log(self.bot, ctx.guild.id, member, amount, title=f"User was rewarded by {ctx.author.name} for task {reward_id.upper()}: {reward['name']}"),
				ctx.send(embed=embed)
			)

	@commands.guild_only()
	@is_admin()
	@commands.command(name='PostRewards', aliases=['PostTasks'])
	async def post_rewards(self, ctx, channel: discord.TextChannel = None):
		if not channel:
			channel = ctx.channel

		async with channel.typing():
			try:
				load_rewards(ctx.guild.id)
			except Exception:
				print('Error in load_rewards in post_rewards in Rewards.py.\nUsing cached version.')

			rewards = get_rewards(ctx.guild.id)

			embed = discord.Embed(color=0x00ff00, title='Task list:', timestamp=datetime.utcnow())
			embed.set_footer(text='Last updated at:')

			for reward in rewards:
				nl = '\n'
				title = f"{reward['id'].upper()}) {reward['name']}"
				desc = f"{reward['description']}{nl}{reward['amount']} {pluralise(ctx.guild.id, reward['amount'])}"
				embed.add_field(name=title, value=desc, inline=False)

			await gather(
				ctx.message.delete(),
				channel.send(embed=embed)
			)


def setup(bot):
	bot.add_cog(Rewards(bot))