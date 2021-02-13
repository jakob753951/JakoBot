import asyncio
import discord
from discord.ext import commands
from Configuration import load_config
from datetime import datetime
import json
from collections import defaultdict
from dataclasses import dataclass

requirements = {'general': [], 'server': ['react_confirm', 'chan_member_log']}

def load_warnings():
	with open('data/Warning.json', 'r', encoding="utf8") as warning_file:
		return defaultdict(lambda: defaultdict(list),
		{
			guild_id: defaultdict(list,
			{
				id:
				[
					Warning(warning['time'], warning['reason'], warning['strikes'])
					for warning
					in warning_list
				]
				for id, warning_list
				in warnings.items()
			})
			for guild_id, warnings
			in json.loads(warning_file.read()).items()
		})

def save_warnings(guilds):
	with open('data/Warning.json', 'w', encoding="utf8") as warning_file:
		warning_file.write(json.dumps(guilds, indent=4))

@dataclass
class UserWarning:
    time: datetime
    reason: str = '[no reason given]'
    strikes: int = 1

class Warning(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')
		self.guilds = self.load_warnings()

	@commands.command(name='Warn')
	async def warn(self, ctx, user: discord.User, *, reason = '[no reason given]', strikes = 1):
		member_log = await self.bot.fetch_channel(self.cfg.servers[ctx.guild.id].chan_member_log)
		await asyncio.gather(
			user.send(f"You have been warned in {ctx.guild.name} for the following reason:\n{reason}"),
			member_log.send(f"{user.name} (id: {user.id}) was warned for '{reason}'"),
			ctx.message.add_reaction(self.cfg.servers[ctx.guild.id].react_confirm)
		)

		self.add_warning(ctx.guild.id, user.id, reason, strikes)

	@commands.command(name='UserWarnings', aliases=['UserWarns'])
	async def user_warnings(self, ctx, user: discord.User):
		embed = discord.Embed(color=0x0000ff, description=f'**User {user.mention} has the following warnings:**', timestamp=datetime.utcnow())
		embed.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.avatar_url)
		embed.set_footer(text=f'User ID: {user.id}')

		for warning in self.warnings[str(ctx.guild)][str(user.id)]:
			embed.add_field(name=warning.strftime('Y-%m-%d %H:%M'), value=f'reason: "{warning.reason}" - {warning.strikes} Strikes', inline=True)

		ctx.send(embed=embed)

	def add_warning(self, guild_id, user_id, reason, strikes):
		self.guilds[str(guild_id)][str(user_id)].append(UserWarning(time=datetime.now(), reason=reason, strikes=strikes))
		save_warnings(self.guilds)


def setup(bot):
	bot.add_cog(Warning(bot))