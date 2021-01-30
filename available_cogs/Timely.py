from asyncio import gather, sleep
from datetime import timedelta
import discord
from discord import Embed
from discord.ext import commands
from Configuration import *
import CurrencyManager as manager
from CurrencyUtils import *
from CustomChecks import *

requirements = {
	'general': [],
	'server': [
		'currency_name_singular',
		'currency_name_plural',
		'timely_cooldown_hours',
		'timely_amount',
		'chans_timely'
	]
}

fmt = "%Y-%m-%dT%H:%M:%S"

def get_cooldown(guild_id, user_id):
		with open('data/TimelyCooldowns.json') as cooldowns_file:
			cooldowns = json.loads(cooldowns_file.read())

		try:
			time_string = cooldowns[str(guild_id)][str(user_id)]
			return datetime.strptime(time_string, fmt)
		except:
			return datetime.min

def set_cooldown(guild_id, user_id):
		with open('data/TimelyCooldowns.json') as cooldowns_file:
			cooldowns = json.loads(cooldowns_file.read())
		if str(guild_id) not in cooldowns:
			cooldowns[str(guild_id)] = {}
		cooldowns[str(guild_id)][str(user_id)] = datetime.strftime(datetime.utcnow(), fmt)
		with open('data/TimelyCooldowns.json', 'w') as cooldowns_file:
			cooldowns_file.write(json.dumps(cooldowns, indent=4))

class Timely(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')

	@commands.guild_only()
	@commands.command(name='Timely', aliases=['Daily', 'Hourly'])
	async def timely(self, ctx):
		guild_cfg = self.cfg.servers[ctx.guild.id]

		if len(guild_cfg.chans_timely) != 0 and ctx.channel.id not in guild_cfg.chans_timely:
			chans = [ctx.guild.get_channel(chan_id) for chan_id in guild_cfg.chans_timely]
			desc = f'Arr matey! To {chans[0].mention} you must go to claim your booty... yarr!'

			sent_msg, _ = await gather(
				ctx.send(embed=Embed(title='Incorrect channel', description=desc, color=0xff0000)),
				ctx.message.delete()
			)
			await sleep(5)
			await sent_msg.delete()
			return

		last_reward_time = get_cooldown(ctx.guild.id, ctx.author.id)

		available_time = last_reward_time + timedelta(hours=guild_cfg.timely_cooldown_hours)

		cur_time = datetime.utcnow()
		if not available_time < cur_time:
			title = f"Timely isn't available yet."
			embed = Embed(color=0xff0000, title=title, timestamp=available_time)
			embed.set_footer(text='Next timely will be available: ')
			responses: list = await gather(
				ctx.send(embed=embed),
				ctx.message.delete()
			)
			await sleep(5)
			await responses[0].delete()
			return

		amount = guild_cfg.timely_amount

		set_cooldown(ctx.guild.id, ctx.author.id)
		desc=f"{ctx.author.mention} You've claimed your {amount} {pluralise(guild_cfg, amount)}."
		embed = Embed(color=0x00ff00, description=desc, timestamp=datetime.utcnow() + timedelta(hours=guild_cfg.timely_cooldown_hours))
		embed.set_footer(text='You can claim again:')

		await gather(
			manager.addToMemberBalance(ctx.guild.id, ctx.author.id, amount),
			ctx.message.delete(),
			transaction_log(self.bot, guild_cfg, ctx.author, amount, title=f"User claimed their timely."),
			ctx.send(embed=embed)
		)


def setup(bot):
	bot.add_cog(Timely(bot))