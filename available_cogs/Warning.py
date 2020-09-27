import discord
from discord.ext import commands
from Configuration import Configuration, load_config
from datetime import datetime
import jsons
from dataclasses import dataclass

@dataclass
class UserWarning:
    time: datetime
    reason: str = '[no reason given]'
    strikes: int = 1


class Warnings(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')
		self.confirmation_reaction = self.cfg.servers[ctx.guild.id].confirm_sent_reaction
		self.guilds = self.load_warnings()

	@commands.command(name='warn')
	async def warn(self, ctx, user: discord.User, *, reason = '[no reason given]'):
		await user.send(f"You have been warned in {ctx.guild.name} for the following reason:\n{reason}")
		member_log = await self.bot.fetch_channel(self.cfg.servers[ctx.guild.id].chan_member_log)
		await member_log.send(f"{user.name} (id: {user.id}) was warned for '{reason}'")

		await ctx.message.add_reaction(self.confirmation_reaction)

		self.add_warning(ctx.guild.id, user.id)
	
	def add_warning(self, guild_id, user_id):
		self.guilds[str(guild_id)][str(user_id)].append(UserWarning(time=datetime.now(), reason='testing purposes', strikes=1))
		self.save_warnings()

	def load_warnings(self):
		with open('Warning/warnings.json', 'r', encoding="utf8") as warning_file:
			return defaultdict(lambda: defaultdict(list),
			{
				guild_id: defaultdict(list,
				{
					id:[
						UserWarning(warning['time'], warning['reason'], warning['strikes'])
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
	bot.add_cog(Warning(bot))