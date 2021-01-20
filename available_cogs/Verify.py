import discord
from discord.ext import commands
from Configuration import load_config
from CustomChecks import *

requirements = {'general': [], 'server': ['roles_can_verify', 'role_unverified', 'role_verified', 'chan_verify_rx']}

class Verify(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')
		self.recently_verified = set()

	@can_verify()
	@commands.command()
	async def verify(self, ctx, member: discord.Member, *, details = None):
		msg_cfg = self.cfg.servers[ctx.guild.id]

		unverified = ctx.guild.get_role(msg_cfg.role_unverified)
		verified = ctx.guild.get_role(msg_cfg.role_verified)

		if verified in member.roles:
			await ctx.send('Member is already verified!')
			return

		self.recently_verified.add(member.id)

		try:
			await member.remove_roles(unverified, reason="verification")
			await member.add_roles(verified, reason="verification")
		except Exception:
			await ctx.send('Sorry! Something went wrong. Please try again later')
			return

		self.recently_verified.remove(member.id)

		await self.post_welcome_message(member, ctx.author, details)

	@commands.Cog.listener()
	async def on_member_update(self, before: discord.Member, after: discord.Member):
		if after.id in self.recently_verified:
			return

		server = after.guild

		# if we don't have the id in our config, return
		if server.id not in self.cfg.servers:
			return

		msg_cfg = self.cfg.servers[server.id]
		verified = server.get_role(msg_cfg.role_verified)

		# If user already had role, return
		if verified in before.roles:
			return
		# If user doesn't have the role after, return
		if verified not in after.roles:
			return

		unverified = server.get_role(msg_cfg.role_unverified)
		await after.remove_roles(unverified, reason="verification")

		await self.post_welcome_message(after)

	async def post_welcome_message(self, member: discord.Member, verifier: discord.Member = None, details = None):
		#log the verification
		server = member.guild
		msg_cfg = self.cfg.servers[server.id]
		verify_rx = server.get_channel(msg_cfg.chan_verify_rx)

		message = f'{member.mention} ({member.id}) is verified'

		if verifier:
			message += f' by {verifier.mention}'

		if details:
			message += f' with info:\n"{details}"'

		await verify_rx.send(message)
		# welcome = server.get_channel(msg_cfg.chan_verify_welcome)
		# await welcome.send(f'Welcome {member.mention} to the server! Please read the {msg_cfg.chan_rules.mention}, remember to get your {msg_cfg.chan_roles.mention}, and maybe make a profile in {msg_cfg.chan_create_profile.mention}.')


def setup(bot):
	bot.add_cog(Verify(bot))
