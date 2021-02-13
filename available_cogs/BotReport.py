import discord
from discord.errors import InvalidArgument
from discord.ext import commands
from Configuration import load_config

requirements = {'general': [], 'server': ['react_confirm', 'chan_reports', 'react_positive', 'react_negative']}

def get_report_embed(member: discord.Member):
	desc = f'{member.mention} has been reported for being a bot. Should they be banned?'
	return discord.Embed(description=desc)

class ForwardDM(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')
		self.reports = {}

	@commands.command(name='Report', aliases=[])
	async def report(self, ctx, member: discord.Member):
		server_cfg = self.cfg.servers[ctx.guild.id]

		was_report_created = await self.try_create_report(member)
		if not was_report_created:
			await ctx.send('this user has already been reported')
			return

		await ctx.message.add_reaction(server_cfg.react_confirm)

	async def try_create_report(self, reported_member: discord.Member):
		try:
			await self.create_report(reported_member)
			return True
		except Exception as e:
			print(e)
			return False

	async def create_report(self, reported_member: discord.Member):
		if reported_member.id in self.reports.values():
			raise InvalidArgument('report already exists')
		vote_id = await self.send_vote(reported_member)
		self.reports[vote_id] = reported_member.id

	async def send_vote(self, reported_member: discord.Member):
		server_cfg = self.cfg.servers[reported_member.guild.id]

		to_channel = await self.bot.fetch_channel(server_cfg.chan_reports)

		embed = self.get_report_embed(reported_member)

		msg = await to_channel.send(embed=embed)
		# await msg.add_reaction(server_cfg.react_positive)
		# await msg.add_reaction(server_cfg.react_negative)

		return msg.id




def setup(bot):
	bot.add_cog(ForwardDM(bot))