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
		'currency_name_plural'
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
		if not str(reward_id) in rewards[str(guild_id)]:
			raise ValueError('Invalid reward id. Please try again with a correct one.')

		return rewards[str(guild_id)][str(reward_id)]

	@commands.guild_only()
	@commands.command(name='Reward', aliases=['reward', 'award'])
	async def reward(self, ctx, member: discord.Member, reward_id: int):
		msg_cfg = self.cfg.servers[ctx.guild.id]
		try:
			reward = self.get_reward(ctx.guild.id, reward_id)
		except ValueError as e:
			await ctx.send(repr(e))
			return

		last_reward_time = self.get_cooldown(ctx.guild.id, member.id, reward_id)

		available_time = last_reward_time + timedelta(hours=reward['cooldown_in_hours'])

		cur_time = datetime.utcnow()
		if not available_time < cur_time:
			desc = f'Reward not yet available.'
			embed = discord.Embed(color=0x0000ff, description=desc, timestamp=available_time)
			embed.set_footer(text='Next reward will be available: ')
			await ctx.send(embed=embed)
			return

		amount = reward['amount']

		self.set_cooldown(ctx.guild.id, member.id, reward_id)
		await manager.addToMemberBalance(ctx.guild.id, member.id, amount)

		await transaction_log(self.bot, msg_cfg, member, amount, title=f"User was rewarded by {ctx.author.name} for task number {reward_id}: {reward['name']}")
		await ctx.message.add_reaction(msg_cfg.react_confirm)


def setup(bot):
	bot.add_cog(Rewards(bot))