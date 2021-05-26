import asyncio
from discord.ext import commands
from Configuration import load_config

requirements = {'general': [], 'server': ['cate_personal_vc', 'chan_personal_vc']}

class PersonalVC(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')
		self.user_vc = {}

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		# Left channel was a personal VC
		if before.channel and before.channel.id in self.user_vc:
			# And it is now empty
			if not after.channel.members:
				# Delete channels
				await asyncio.gather(
					*[chan.delete() for chan in self.user_vc[after.channel.id]],
					await after.channel.delete()
				)

				# Remove from dict
				self.user_vc.pop(after.channel.id)

		# User disconnects
		if not after.channel:
			return

		# User entered an irrelevant channel, so we don't care
		if after.channel != await self.bot.fetch_channel(self.cfg.servers[member.guild.id].chan_personal_vc):
			return

		# If we reach this point, the user has connected to the 'Create personal VC' channel
		# So we create the channels for them and move them to the VC
		await self.create_channels(member)

	async def create_channels(self, member):
		# Shorthand for later use
		server = member.guild
		username = member.display_name
		channel_name = f"{username}'s channel"

		# Get cate_personal_vc for the server
		cat = await self.bot.fetch_channel(self.cfg.servers[member.guild.id].cate_personal_vc)

		tc, vc, role = await asyncio.gather(
			cat.create_text_channel(channel_name),
			cat.create_voice_channel(channel_name),
			server.create_role(name=username)
		)

		await asyncio.gather(
			member.add_roles(role),
			member.move_to(vc)
		)

		# Add the vc as a key to user_vc, while setting the value to a tuple with tc and role
		self.user_vc[vc.id] = (tc, role)


def setup(bot):
	bot.add_cog(PersonalVC(bot))
