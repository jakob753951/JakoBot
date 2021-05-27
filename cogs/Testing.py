from discord.ext import commands
import discord
import json
from CustomChecks import *

requirements = {'general': [], 'server': []}

class Testing(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@is_admin()
	@commands.command(name='Embed')
	async def embed(self, ctx, *, json_str = None):
		if json_str == None:
			with open('data/Embed.json') as embed_file:
				json_str = embed_file.read()

		embed_dict = json.loads(json_str)
		embed = discord.Embed.from_dict(embed_dict)
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@is_admin()
	@commands.command(name='purge')
	async def purge(self, ctx, limit: int = 100):
		await ctx.channel.purge(limit=limit)

	@is_admin()
	@commands.command(name='RemoveRoles')
	async def remove_roles(self, ctx):
		for role in ctx.guild.roles:
			v = input(f'Delete role "{role.name}"? [hit enter for yes, type something for no]')
			if not v:
				await role.delete()


def setup(bot):
	bot.add_cog(Testing(bot))