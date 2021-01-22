import asyncio
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
		'currency_name_singular',
		'currency_name_plural',
		'timely_cooldown_hours',
		'timely_amount'
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
		self.cfg = load_config('config.json')

	@commands.guild_only()
	@commands.command(name='Timely', aliases=['timely', 'daily', 'hourly'])
	async def timely(self, ctx):
		guild_cfg = self.cfg.servers[ctx.guild.id]

		last_reward_time = get_cooldown(ctx.guild.id, ctx.author.id)

		available_time = last_reward_time + timedelta(hours=guild_cfg.timely_cooldown_hours)

		cur_time = datetime.utcnow()
		if not available_time < cur_time:
			title = f"Timely isn't available yet."
			embed = discord.Embed(color=0xff0000, title=title, timestamp=available_time)
			embed.set_footer(text='Next timely will be available: ')
			responses: list = await asyncio.gather(
				ctx.send(embed=embed),
				ctx.message.delete()
			)
			await asyncio.sleep(5)
			await responses[0].delete()
			return

		amount = guild_cfg.timely_amount

		set_cooldown(ctx.guild.id, ctx.author.id)
		desc=f"{ctx.author.mention} You've claimed your {amount} {pluralise(guild_cfg, amount)}."
		embed = discord.Embed(color=0x00ff00, description=desc, timestamp=datetime.utcnow() + timedelta(hours=guild_cfg.timely_cooldown_hours))
		embed.set_footer(text='You can claim again:')
		todo = [
			manager.addToMemberBalance(ctx.guild.id, ctx.author.id, amount),
			ctx.message.delete(),
			transaction_log(self.bot, guild_cfg, ctx.author, amount, title=f"User claimed their timely."),
			ctx.send(embed=embed)
		]

		await asyncio.gather(*todo)


def setup(bot):
	bot.add_cog(Timely(bot))