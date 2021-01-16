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
		self.load_cooldowns()

	def load_cooldowns(self):
		with open('data/RewardCooldowns.json') as cooldowns_file:
			self.cooldowns = json.loads(cooldowns_file.read())

	def save_cooldowns(self):
		with open('data/RewardCooldowns.json', 'w') as cooldowns_file:
			cooldowns_file.write(json.dumps(self.cooldowns))

	def load_rewards(self):
		with open('data/Rewards.json') as rewards_file:
			self.rewards = json.loads(rewards_file.read())

	@commands.guild_only()
	@commands.command(name='AddCurrency', aliases=['addcurrency'])
	async def reward(self, ctx, member: discord.Member, reward_id: int):
		msg_cfg = self.cfg.servers[ctx.guild.id]

		self.load_cooldowns()
		self.load_rewards()

		time_string = self.cooldowns[ctx.guild.id][ctx.author.id][reward_id]
		reward = self.rewards[ctx.guild.id][reward_id]

		last_reward_time = datetime.strptime(time_string, fmt)
		available_time = last_reward_time + timedelta(hours=reward['cooldown_in_hours'])

		cur_time = datetime.utcnow()
		if not available_time < cur_time:
			desc = f'Reward not yet available. Will be available'
			embed = discord.Embed(color=0x0000ff, description=desc, timestamp=available_time)
			embed.set_footer(text='Next reward will be available at: ')
			ctx.send(embed=embed)
			return

		amount = reward['amount']

		await manager.addToMemberBalance(ctx.guild.id, member.id, amount)
		await transaction_log(self.bot, msg_cfg, ctx.author, amount, title=f'User was rewarded for task number {reward_id}: {reward.name}')
		await ctx.message.add_reaction(msg_cfg.react_confirm)


def setup(bot):
	bot.add_cog(Rewards(bot))