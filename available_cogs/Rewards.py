from datetime import timedelta
import discord
from discord.ext import commands
from Configuration import *
import CurrencyManager as manager
from CurrencyUtils import *
from CustomChecks import *

requirements = {
	'general': [],
	'server': [
		'react_confirm',
		'chan_transaction_history',
		'currency_name_singular',
		'currency_name_plural',
		'role_staff'
	]
}

fmt = "%Y-%m-%dT%H:%M:%S"

class Rewards(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')

	def get_cooldown(self, guild_id, user_id, reward_id):
		with open('data/RewardCooldowns.json') as cooldowns_file:
			cooldowns = json.loads(cooldowns_file.read())

		try:
			time_string = cooldowns[str(guild_id)][str(user_id)][str(reward_id)]
			return datetime.strptime(time_string, fmt)
		except:
			return datetime.min

	def set_cooldown(self, guild_id, user_id, reward_id):
		with open('data/RewardCooldowns.json') as cooldowns_file:
			cooldowns = json.loads(cooldowns_file.read())
		if str(guild_id) not in cooldowns:
			cooldowns[str(guild_id)] = {}
		if str(user_id) not in cooldowns[str(guild_id)]:
			cooldowns[str(guild_id)][str(user_id)] = {}
		cooldowns[str(guild_id)][str(user_id)][str(reward_id)] = datetime.strftime(datetime.utcnow(), fmt)
		with open('data/RewardCooldowns.json', 'w') as cooldowns_file:
			cooldowns_file.write(json.dumps(cooldowns, indent=4))

	def get_reward(self, guild_id, reward_id):
		with open('data/Rewards.json') as rewards_file:
			rewards = json.loads(rewards_file.read())

		if not str(guild_id) in rewards:
			raise ValueError('Rewards have not been registered for this server.')
		reward_list = [reward for reward in rewards[str(guild_id)] if reward['id'] == reward_id]
		if len(reward_list) != 1:
			raise ValueError('Invalid reward id. Please try again with a correct one.')

		return reward_list[0]

	@commands.guild_only()
	@commands.check_any(is_admin(), is_staff())
	@commands.command(name='Reward', aliases=['reward', 'award'])
	async def reward(self, ctx, member: discord.Member, reward_id: str):
		if ctx.author == member:
			return

		guild_cfg = self.cfg.servers[ctx.guild.id]
		try:
			reward = self.get_reward(ctx.guild.id, reward_id.lower())
		except ValueError as e:
			await ctx.send(repr(e))
			return

		last_reward_time = self.get_cooldown(ctx.guild.id, member.id, reward_id.lower())

		available_time = last_reward_time + timedelta(hours=reward['cooldown_in_hours'])

		cur_time = datetime.utcnow()
		if not available_time < cur_time:
			title = f'Reward not yet available.'
			embed = discord.Embed(color=0xff0000, title=title, timestamp=available_time)
			embed.set_footer(text='Next reward will be available: ')
			await ctx.send(embed=embed)
			return

		amount = reward['amount']

		self.set_cooldown(ctx.guild.id, member.id, reward_id.lower())
		await manager.addToMemberBalance(ctx.guild.id, member.id, amount)

		await transaction_log(self.bot, guild_cfg, member, amount, title=f"User was rewarded by {ctx.author.name} for task {reward_id.upper()}: {reward['name']}")
		desc=f"{member.mention} was rewarded for task number {reward_id.upper()}: {reward['name']}"
		embed = discord.Embed(color=0x00ff00, description=desc, timestamp=datetime.utcnow())
		await ctx.send(embed=embed)

	@commands.guild_only()
	@is_admin()
	@commands.command(name='PostRewards', aliases=['postrewards', 'posttasks'])
	async def post_rewards(self, ctx, channel: discord.TextChannel = None):
		guild_cfg = self.cfg.servers[ctx.guild.id]
		if not channel:
			channel = ctx.channel

		with open('data/Rewards.json') as rewards_file:
			rewards = json.loads(rewards_file.read())
		embed = discord.Embed(color=0x00ff00, title='Task list:', timestamp=datetime.utcnow())
		embed.set_footer(text='Last updated at:')
		for reward in rewards[str(ctx.guild.id)]:
			nl = '\n'
			title = f"{reward['id'].upper()}) {reward['name']}"
			desc = f"{reward['description']}{nl}{reward['amount']} {pluralise(guild_cfg, reward['amount'])}"
			embed.add_field(name=title, value=desc, inline=False)

		await channel.send(embed=embed)


def setup(bot):
	bot.add_cog(Rewards(bot))