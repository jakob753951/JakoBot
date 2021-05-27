import discord
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands
from Configuration import load_config
from datetime import datetime

requirements = {'general': [], 'server': ['msg_log_webhook_url', 'member_log_webhook_url']}

def get_member_count(guild: discord.Guild):
	return len([member for member in guild.members if not member.bot])

class Logging(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')

	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		if not after.guild or after.author.bot:
			return

		embed = discord.Embed(color=0x0000ff, description=f'**Message edited in {after.channel.mention}**', timestamp=datetime.utcnow())
		embed.set_author(name=f'{after.author.name}#{after.author.discriminator}', icon_url=after.author.avatar_url)
		embed.add_field(name='Before', value=f'{before.content or "[No content]"}', inline=False)
		embed.add_field(name='After', value=f'{after.content or "[No content]"}', inline=False)
		embed.set_footer(text=f'User ID: {after.id}')

		webhook = Webhook.from_url(self.cfg.msg_log_webhook_url, adapter=RequestsWebhookAdapter())
		try:
			webhook.send(embed=embed)
		except Exception as err:
			print(f'err: {err}')
			print(f'before.content: {before.content}')
			print(f'after.content: {after.content}')


	@commands.Cog.listener()
	async def on_raw_message_delete(self, payload):
		webhook = Webhook.from_url(self.cfg.msg_log_webhook_url, adapter=RequestsWebhookAdapter())
		if not payload.cached_message:
			channel = await self.bot.fetch_channel(payload.channel_id)

			desc = f'**Message deleted in {channel.mention}**'
			embed = discord.Embed(color=0xff0000, description=desc, timestamp=datetime.utcnow())
			embed.set_footer(text=f'Message ID: {payload.message_id}')

			webhook.send(embed=embed)
			return

		message = payload.cached_message

		if not message.guild or message.author.bot:
			return

		desc = f'**Message sent by {message.author.mention} deleted in {message.channel.mention}**\n{message.content}'
		embed = discord.Embed(color=0xff0000, description=desc, timestamp=datetime.utcnow())
		embed.set_author(name=f'{message.author.name}#{message.author.discriminator}', icon_url=message.author.avatar_url)
		embed.set_footer(text=f'Author: {message.author.id} | Message ID: {payload.message_id}')

		webhook.send(embed=embed)

	@commands.Cog.listener()
	async def on_member_join(self, member):
		await self.on_member_count_update(member, embed_color=0x00ff00, joined_left='joined')

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		await self.on_member_count_update(member, embed_color=0xff0000, joined_left='left')

	async def on_member_count_update(self, member: discord.Member, embed_color: int, joined_left: str):
		title = f'Has {joined_left} **{member.guild.name}**!'
		desc = f'New member count: {get_member_count(member.guild)}'
		embed = discord.Embed(color=embed_color, title=title, description=desc, timestamp=datetime.utcnow())
		embed.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
		embed.set_footer(text=f'Member ID: {member.id}')

		webhook = Webhook.from_url(self.cfg.member_log_webhook_url, adapter=RequestsWebhookAdapter())
		webhook.send(embed=embed)


def setup(bot):
	bot.add_cog(Logging(bot))