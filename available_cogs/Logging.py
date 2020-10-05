import discord
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands
from Configuration import Configuration, load_config
from datetime import datetime, timedelta

get_cfg = lambda: {'general': [], 'server': ['webhook_url']}

class Logging(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')

	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		if not after.guild or after.author.bot:
			return
		
		webhook = Webhook.from_url(self.cfg.servers[after.guild.id].webhook_url, adapter=RequestsWebhookAdapter())

		embed = discord.Embed(color=0x0000ff, description=f'**Message edited in {after.channel.mention}**', timestamp=datetime.utcnow())
		embed.set_author(name=f'{after.author.name}#{after.author.discriminator}', icon_url=after.author.avatar_url)
		embed.add_field(name='Before', value=f'{before.content}', inline=False)
		embed.add_field(name='After', value=f'{after.content}', inline=False)
		embed.set_footer(text=f'User ID: {after.id}')
		webhook.send(embed=embed)

	@commands.Cog.listener()
	async def on_message_delete(self, message):
		if not message.guild or message.author.bot:
			return
		
		webhook = Webhook.from_url(self.cfg.servers[message.guild.id].webhook_url, adapter=RequestsWebhookAdapter())

		desc = f'**Message sent by {message.author.mention} deleted in {message.channel.mention}**\n{message.content}'
		embed = discord.Embed(color=0xff0000, description=desc, timestamp=datetime.utcnow())
		embed.set_author(name=f'{message.author.name}#{message.author.discriminator}', icon_url=message.author.avatar_url)
		embed.set_footer(text=f'Author: {message.author.id} | Message ID: {message.id}')
		webhook.send(embed=embed)


def setup(bot):
	bot.add_cog(Logging(bot))