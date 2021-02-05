from discord.ext import commands
import discord
import json

requirements = {'general': [], 'server': []}

class GeneralCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='embed')
	async def embed(self, ctx, *, embed):
		with open('data/Embed.json') as embed_file:
			embed_dict = json.loads(embed_file.read)
		embed = discord.Embed.from_dict(embed_dict)
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command(name='purge')
	async def purge(self, ctx, limit: int = 100):
		await ctx.channel.purge(limit=limit)


def setup(bot):
	bot.add_cog(GeneralCommands(bot))