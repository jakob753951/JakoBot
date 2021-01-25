import asyncio
import discord
from discord.ext import commands

requirements = {'general': [], 'server': []}

class Confessions(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.guild_only()
	@commands.command(name='Bulk Add Roles', aliases=['addroles', 'bulkaddroles'])
	async def bulk_add_roles(self, ctx, *, role_names):
		await asyncio.gather(
			ctx.send(embed=discord.Embed(colour=discord.Colour.green(), title='Roles have been created')),
			*(ctx.guild.create_role(name=role_name, reason='Bulk Add', permissions=ctx.guild.default_role.permissions) for role_name in role_names.split(','))
		)


def setup(bot):
	bot.add_cog(Confessions(bot))