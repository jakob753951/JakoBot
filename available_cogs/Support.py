import discord
from discord.ext import commands
from Configuration import *

class Support(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')
		with open('Support/tickets.json', 'r', encoding="utf8") as ticket_file:
			self.tickets = json.loads(ticket_file.read())

	@commands.Cog.listener()
	async def on_message(self, message):
		# Make sure it's a user sending a message in a DM to the bot
		if message.author.bot or message.guild:
			return

		forward_channel = await self.get_forward_channel()
		await forward_channel.send(f'{message.author.name}: "{message.content}"')
		if message.attachments:
			await forward_channel.send(f'with the following attachment{"s" if len(message.attachments) > 1 else ""}:')
			await forward_channel.send('\n'.join([att.url for att in message.attachments]))

	async def get_forward_channel(self):
		return await self.bot.fetch_channel(self.cfg.chan_forward_dm)


def setup(bot):
	bot.add_cog(Support(bot))