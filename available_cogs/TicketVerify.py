import discord
from discord.ext import commands
from Configuration import load_config
import asyncio

requirements = {'general': [], 'server': ['cate_verify', 'role_staff', 'roles_can_verify', 'role_unverified', 'role_verified', 'cate_verify_storage']}

class TicketVerify(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')
		self.verification_channels = {}

	@commands.command(name='verify')
	async def verify(self, ctx):
		server_cfg = self.cfg.servers[ctx.message.guild.id]

		verifying = ctx.author

		role_verified = server_cfg.role_verified

		if role_verified in verifying.roles:
			await self.send_delete_after_delay(ctx, 'You are already verified.', 5)
			return

		if ctx.author.id in self.verification_channels.values():
			await self.send_delete_after_delay(ctx, 'You are already being verified.', 5)
			return


		category = ctx.guild.get_channel(server_cfg.cate_verify)
		role_staff = ctx.guild.get_role(server_cfg.role_staff)

		chan_name = f'{verifying.name}'
		overwrites = {
			ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
			role_staff: discord.PermissionOverwrite(read_messages=True),
			verifying: discord.PermissionOverwrite(read_messages=True)
		}

		created_channel = await category.create_text_channel(chan_name, overwrites=overwrites)

		self.verification_channels[created_channel.id] = verifying.id

	@commands.command(name='confirmverify')
	async def confirmverify(self, ctx):
		server_cfg = self.cfg.servers[ctx.message.guild.id]

		if ctx.channel.id not in self.verification_channels:
			await self.send_delete_after_delay(ctx, 'This is not a verification channel.', 5)
			return

		if not self.can_member_verify(ctx.author, server_cfg.roles_can_verify):
			await self.send_delete_after_delay(ctx, 'You do not have permission to verify.', 5)
			return

		category = await self.bot.fetch_channel(server_cfg.cate_verify_storage)
		member_id = self.verification_channels[ctx.channel.id]
		member = ctx.message.guild.get_member(member_id)

		chan_name = f'{ctx.channel.name}'
		storage_channel = await category.create_text_channel(chan_name)
		async with storage_channel.typing():
			async for message in ctx.channel.history(oldest_first=True):
				files = []
				for i, attachment in enumerate(message.attachments):
					extension = attachment.filename.split('.')[-1]
					file_name = f'data/attachments/{message.id}_{i}.{extension}'
					await attachment.save(file_name)
					files.append(discord.File(file_name))

				title = message.author.mention
				desc = message.content
				embed = discord.Embed(color=0xff0000, title=title, description=desc, timestamp=message.created_at)
				embed.set_author(name=f'{message.author.name}#{message.author.discriminator}', icon_url=message.author.avatar_url)
				embed.set_footer(text=f'Member ID: {message.author.id}')

				await storage_channel.send(embed=embed, files=files)


		role_verified = ctx.guild.get_role(server_cfg.role_verified)
		role_unverified = ctx.guild.get_role(server_cfg.role_unverified)

		await member.remove_roles(role_unverified)
		await member.add_roles(role_verified)

		await ctx.channel.delete()

	def can_member_verify(self, member, verifying_roles):
		for role in member.roles:
			if role.id in verifying_roles:
				return True
		return False

	async def send_delete_after_delay(self, chan: discord.abc.Messageable, message, delay):
		msg = await chan.send(message)
		await asyncio.sleep(delay)
		await msg.delete()


def setup(bot):
	bot.add_cog(TicketVerify(bot))