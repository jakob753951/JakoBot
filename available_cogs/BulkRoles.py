import discord
from discord.ext import commands

get_cfg = lambda: {'general': [], 'server': []}

class Confessions(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='Bulk Add Roles', aliases=['addroles', 'bulkaddroles'])
	async def bulk_add_roles(self, ctx, *role_names):
		# Check if DM
		if isinstance(ctx.channel, discord.channel.DMChannel):
			await ctx.send('This command cannot be used in DMs')
			return

		perms = ctx.guild.roles[0].permissions

		# Add roles
		for role_name in role_names:
			await ctx.guild.create_role(name=role_name, reason='Bulk Add', permissions=perms)

		# Send feedback
		await ctx.send(embed=discord.Embed(colour=discord.Colour.green(), title='Roles have been created'))


def setup(bot):
	bot.add_cog(Confessions(bot))