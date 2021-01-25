from discord.ext import commands
from Configuration import load_config
import asyncio

requirements = {'general': [], 'server': ['react_confirm', 'chan_remind', 'role_remind']}

class Remind(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('config.json')
		self.is_waiting = False

	@commands.Cog.listener()
	async def on_message(self, message):
		if self.is_waiting:
			return

		if message.content.lower() != '!d bump':
			return

		guild = message.guild
		server_cfg = self.cfg.servers[guild.id]

		if message.channel.id != server_cfg.chan_remind:
			return

		await message.add_reaction(server_cfg.react_confirm)

		self.is_waiting = True
		await asyncio.sleep(2 * 60 * 60)
		self.is_waiting = False

		role = guild.get_role(server_cfg.role_remind)
		await message.channel.send(f'{role.mention} Time to bump!\n`!d bump`')


def setup(bot):
	bot.add_cog(Remind(bot))