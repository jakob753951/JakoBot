import asyncio
import discord
from discord.ext import commands
from Configuration import load_config

requirements = {'general': ['chan_forward_dm'], 'server': ['react_confirm']}

class ForwardDM(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config()

	@commands.Cog.listener()
	async def on_message(self, message):
		if not isinstance(message.channel, discord.channel.DMChannel):
			return
		
		if message.author.id == self.bot.id:
			return

		forward_channel = await self.bot.fetch_channel(self.cfg.chan_forward_dm)
		await forward_channel.send(f'{message.author.name}: "{message.content}"')
		if message.attachments:
			await forward_channel.send(f'with the following attachment{"s" if len(message.attachments) > 1 else ""}:')
			await forward_channel.send('\n'.join([att.url for att in message.attachments]))

	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		# Make sure it's a user editing a message in a DM with the bot
		if after.author.bot or after.guild:
			return

		forward_channel = await self.bot.fetch_channel(self.cfg.chan_forward_dm)
		await forward_channel.send(f'{after.author.name} edited their message: "{before.content}" --> "{after.content}"')


def setup(bot):
	bot.add_cog(ForwardDM(bot))