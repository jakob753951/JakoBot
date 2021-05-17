from discord.ext import commands
from Configuration import load_config
import asyncio

requirements = {'general': [], 'server': ['react_confirm', 'chan_remind', 'role_remind']}

class Remind(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')
		self.is_waiting = False

	@commands.Cog.listener()
	async def on_message(self, message):
		if self.is_waiting:
			return

		if message.content.lower() != '!d bump':
			return

		guild = message.guild

		if message.channel.id != self.cfg.chan_remind:
			return

		await message.add_reaction(self.cfg.react_confirm)

		self.is_waiting = True
		await asyncio.sleep(2 * 60 * 60)
		self.is_waiting = False

		role = guild.get_role(self.cfg.role_remind)
		await message.channel.send(f'{role.mention} Time to bump!\n`!d bump`')


def setup(bot):
	bot.add_cog(Remind(bot))