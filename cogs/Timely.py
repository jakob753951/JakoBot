from asyncio import gather, sleep
from datetime import timedelta
from discord import Embed
from discord.ext import commands
from Configuration import *
import CurrencyManager as manager
from CurrencyUtils import *
from CustomChecks import *
from discord_slash import cog_ext, SlashContext

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

def get_cooldown(user_id):
	with open('data/TimelyCooldowns.json') as cooldowns_file:
		cooldowns = json.loads(cooldowns_file.read())

	try:
		time_string = cooldowns[str(user_id)]
		return datetime.strptime(time_string, fmt)
	except Exception:
		return datetime.min

def set_cooldown(user_id):
	with open('data/TimelyCooldowns.json') as cooldowns_file:
		cooldowns = json.loads(cooldowns_file.read())

	cooldowns[str(user_id)] = datetime.strftime(datetime.utcnow(), fmt)
	with open('data/TimelyCooldowns.json', 'w') as cooldowns_file:
		cooldowns_file.write(json.dumps(cooldowns, indent=4))

class Timely(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')
	
	@cog_ext.cog_slash(
		name='timely',
		description='Claim your timely reward.',
		guild_ids=[669731845260443678]
	)
	async def timely_slash(self, ctx: SlashContext):
		await self.timely(ctx)

	@commands.guild_only()
	@commands.command(name='Timely', aliases=['Daily', 'Hourly'])
	async def timely_cmd(self, ctx: commands.Context):
		await self.timely(ctx)

	async def timely(self, ctx):
		if len(self.cfg.chans_timely) != 0 and ctx.channel.id not in self.cfg.chans_timely:
			chans = [ctx.guild.get_channel(chan_id) for chan_id in self.cfg.chans_timely]
			desc = f'Arr matey! To {chans[0].mention} you must go to claim your booty... yarr!'

			if isinstance(ctx, commands.Context):
				sent_msg, _ = await gather(
					ctx.send(embed=Embed(title='Incorrect channel', description=desc, color=0xff0000)),
					ctx.message.delete(),
					sleep(5)
				)
				await sent_msg.delete()
			else:
				await ctx.send(embed=Embed(title='Incorrect channel', description=desc, color=0xff0000), hidden=True)
			return

		last_reward_time = get_cooldown(ctx.author.id)

		available_time = last_reward_time + timedelta(hours=self.cfg.timely_cooldown_hours)

		cur_time = datetime.utcnow()
		if not available_time < cur_time:
			desc = f"**{ctx.author.mention} Timely isn't available yet.**"
			embed = Embed(color=0xff0000, description=desc, timestamp=available_time)
			embed.set_footer(text='Next timely will be available: ')
			
			if isinstance(ctx, commands.Context):
				sent_msg, _ = await gather(
					ctx.send(embed=embed),
					ctx.message.delete(),
					sleep(5)
				)
				await sent_msg.delete()
			else:
				await ctx.send(embed=embed, hidden=True)
			return

		amount = self.cfg.timely_amount

		set_cooldown(ctx.author.id)
		desc=f"{ctx.author.mention} You've claimed your {amount} {pluralise(amount)}."
		embed = Embed(color=0x00ff00, description=desc, timestamp=datetime.utcnow() + timedelta(hours=self.cfg.timely_cooldown_hours))
		embed.set_footer(text='You can claim again:')

		await gather(
			manager.addToMemberBalance(ctx.author.id, amount),
			transaction_log(self.bot, ctx.author, amount, title=f"User claimed their timely."),
			ctx.send(embed=embed)
		)


def setup(bot):
	bot.add_cog(Timely(bot))