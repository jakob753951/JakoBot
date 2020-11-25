from discord.ext import commands
from Configuration import *

get_cfg = lambda: {'general': [], 'server': ['cate_personal_vc', 'chan_personal_vc']}

class PersonalVC(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')
		self.user_vc = {}

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		# Left channel was a personal VC
		if before.channel and before.channel.id in self.user_vc:
			# And it is now empty
			if not before.channel.members:

				# Delete the text-channel and the role
				for chan in self.user_vc[before.channel.id]:
					await chan.delete()
				# Delete the vc
				await before.channel.delete()

				# Remove from dict
				self.user_vc.pop(before.channel.id)

		# User disconnects
		if not after.channel:
			return

		# User entered an irrelevant channel, so we don't care
		if after.channel != await self.bot.fetch_channel(self.cfg.servers[member.guild.id].chan_personal_vc):
			return

		# If we reach this point, the user has connected to the 'Create personal VC' channel
		# So we create the channels for them and move them to the VC
		await self.create_channels()

	async def create_channels(self, member):
		# Shorthand for later use
		server = member.guild
		username = member.display_name

		# Create role and add it to the user
		role = await server.create_role(name=username)
		await member.add_roles(role)

		# Get cate_personal_vc for the server
		cat = await self.bot.fetch_channel(self.cfg.servers[member.guild.id].cate_personal_vc)

		channel_name = f"{username}'s channel"
		vc = await cat.create_voice_channel(channel_name)
		await member.move_to(vc)

		tc = await cat.create_text_channel(channel_name)

		# Add the vc as a key to user_vc, while setting the value to a tuple with tc and role
		self.user_vc[vc.id] = (tc, role)


def setup(bot):
	bot.add_cog(PersonalVC(bot))
