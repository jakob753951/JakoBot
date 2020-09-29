import discord
from discord.ext import commands
from Configuration import Configuration, load_config
from datetime import datetime
import jsons
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Warning:
	time: datetime
	reason: str = '[no reason given]'
	strikes: int = 1


class WarningSystem(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')
		self.guilds = self.load_warnings()
		jsons.suppress_warnings()

	@commands.command(name='warn')
	async def warn(self, ctx, user: discord.User, *, reason = '[no reason given]', strikes = 1):
		await user.send(f"You have been warned in {ctx.guild.name} for the following reason:\n{reason}")
		member_log = await self.bot.fetch_channel(self.cfg.servers[ctx.guild.id].chan_member_log)
		await member_log.send(f"{user.name} (id: {user.id}) was warned for '{reason}'")

		await ctx.message.add_reaction(self.cfg.confirmation_reaction)

		self.add_warning(ctx.guild.id, user.id, reason, strikes)
	
	@commands.command(name='userwarnings', aliases=['userwarns'])
	async def user_warnings(self, ctx, user: discord.User):
		embed = discord.Embed(color=0x0000ff, description=f'**User {user.mention} has the following warnings:**', timestamp=datetime.utcnow())
		embed.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.avatar_url)
		embed.set_footer(text=f'User ID: {user.id}')

		for warning in self.warnings[str(ctx.guild)][str(user.id)]:
			embed.add_field(name=warning.strftime('Y-%m-%d %H:%M'), value=f'reason: "{warning.reason}" - {warning.strikes} Strikes', inline=True)

		ctx.send(embed=embed)
	
	def add_warning(self, guild_id, user_id, reason, strikes):
		self.guilds[str(guild_id)][str(user_id)].append(Warning(time=datetime.now(), reason=reason, strikes=strikes))
		self.save_warnings()

	def load_warnings(self):
		with open('Warning/warnings.json', 'r', encoding="utf8") as warning_file:
			return defaultdict(lambda: defaultdict(list),
			{
				guild_id: defaultdict(list,
				{
					id:[
						Warning(warning['time'], warning['reason'], warning['strikes'])
						for warning
						in warning_list
					]
					for id, warning_list
					in warnings.items()
				})
				for guild_id, warnings
				in jsons.loads(warning_file.read()).items()
			})
	
	def save_warnings(self):
		with open('Warning/warnings.json', 'w', encoding="utf8") as warning_file:
			warning_file.write(jsons.dumps(self.guilds))

def setup(bot):
	bot.add_cog(WarningSystem(bot))