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
from google.oauth2 import service_account

requirements = {
	'general': [],
	'server': [
		'react_confirm',
		'chan_transaction_history',
		'currency_name_singular',
		'currency_name_plural',
		'role_admin',
		'rewards_sheet_id'
	]
}

fmt = "%Y-%m-%dT%H:%M:%S"

def get_cooldown(user_id, reward_id):
	with open('data/RewardCooldowns.json') as cooldowns_file:
		cooldowns = json.loads(cooldowns_file.read())

	try:
		time_string = cooldowns[str(user_id)][str(reward_id)]
		return datetime.strptime(time_string, fmt)
	except Exception:
		return datetime.min

def set_cooldown(user_id, reward_id):
	with open('data/RewardCooldowns.json') as cooldowns_file:
		cooldowns = json.loads(cooldowns_file.read())
	if str(user_id) not in cooldowns:
		cooldowns[str(user_id)] = {}
	cooldowns[str(user_id)][str(reward_id)] = datetime.strftime(datetime.utcnow(), fmt)
	with open('data/RewardCooldowns.json', 'w') as cooldowns_file:
		cooldowns_file.write(json.dumps(cooldowns, indent=4))

def get_rewards():
	with open('data/Rewards.json') as rewards_file:
		return json.loads(rewards_file.read())

def get_reward(reward_id):
	for category_name, rewards in get_rewards().items():
		matching_rewards = [reward for reward in rewards if reward['id'] == reward_id]
		if len(matching_rewards) == 1:
			return category_name, matching_rewards[0]

	raise ValueError('Invalid reward id. Please try again with a correct one.')
	

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
			creds = service_account.Credentials.from_service_account_file(
        		'service_account.json', scopes=scopes)
			# flow = InstalledAppFlow.from_client_secrets_file(
			# 	'credentials.json', scopes)
			# creds = flow.run_local_server()
		# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	return build('sheets', 'v4', credentials=creds)

def load_rewards() -> list:
	cfg = load_config()
	service = generate_service()
	sheet_names = cfg.rewards_sheet_names
	categories = {}
	for sheet_name in sheet_names:
		range_name = f'{sheet_name}!A2:F'

		sheet = service.spreadsheets()
		result = sheet.values().get(spreadsheetId=cfg.rewards_sheet_id, range=range_name).execute()
		rows = result.get('values', [])

		rewards = [
			{
				'id': reward_id,
				'name': name,
				'description': description,
				'amount': int(amount),
				'cooldown_in_hours': int(cooldown_in_hours)
			}
			for reward_id, name, description, amount, cooldown_in_hours, active in rows
			if active.lower().strip() == 'yes'
		]
		categories[sheet_name] = rewards

	with open('data/Rewards.json', 'w') as rewards_file:
		rewards_file.write(json.dumps(categories))

class Rewards(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config()

	@commands.guild_only()
	@commands.check_any(is_admin(), is_staff())
	@commands.command(name='Reward', aliases=['Award'])
	async def reward(self, ctx, member: discord.Member, *reward_ids):
		if ctx.author == member:
			return

		for reward_id in reward_ids:
			try:
				category_name, reward = get_reward(reward_id.lower())
			except ValueError as e:
				await ctx.send(repr(e))
				continue

			last_reward_time = get_cooldown(member.id, reward_id.lower())

			available_time = last_reward_time + timedelta(hours=reward['cooldown_in_hours'])

			cur_time = datetime.utcnow()
			if not available_time < cur_time:
				title = f"Reward {reward['name']} not yet available."
				embed = discord.Embed(color=0xff0000, title=title, timestamp=available_time)
				embed.set_footer(text='Next reward will be available: ')
				await ctx.send(embed=embed)
				continue

			amount = reward['amount']

			set_cooldown(member.id, reward_id.lower())

			title=f'Task completed from the {category_name} list!'
			desc=f"{member.mention} was rewarded {amount} {pluralise(amount)} for task number {reward_id.upper()}: {reward['name']}"
			embed = discord.Embed(color=0x00ff00, description=desc, timestamp=datetime.utcnow())
			await gather(
				manager.addToMemberBalance(member.id, amount),
				transaction_log(self.bot, member, amount, title=f"User was rewarded by {ctx.author.name} for task {reward_id.upper()}: {reward['name']}"),
				ctx.send(embed=embed)
			)

	@commands.guild_only()
	@is_staff()
	@commands.command(name='PostRewards', aliases=['PostTasks'])
	async def post_rewards(self, ctx, channel: discord.TextChannel = None):
		if not channel:
			channel = ctx.channel

		async with channel.typing():
			try:
				load_rewards()
			except Exception as e:
				print('Error in load_rewards in post_rewards in Rewards.py.\nUsing cached version.')
				await channel.send(repr(e))
			categories = get_rewards()
			for sheet_name, category in categories.items():
				embed = discord.Embed(color=0x00ff00, title=f'{sheet_name}:', timestamp=datetime.utcnow())
				embed.set_footer(text='Last updated at:')

				for reward in category:
					name = f"{reward['id'].upper()}) {reward['name']}"
					value = f"{reward['description']}\n{reward['amount']} {pluralise(reward['amount'])}"
					embed.add_field(name=name, value=value, inline=False)

				await channel.send(embed=embed)
			await ctx.message.delete()


def setup(bot):
	bot.add_cog(Rewards(bot))