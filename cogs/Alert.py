import discord
from discord import Embed
from discord.ext import commands
from Configuration import load_config
from asyncio import gather

requirements = {'general': [], 'server': ['react_confirm']}

class Alert(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config('Config.json')
	
	@commands.command(name='Alert', aliases=['Alarm'])
	async def alert(self, ctx, *, message: str = 'The alert has been sounded.'):
		recipient_id = self.cfg.owner_id
		recipient: discord.User = self.bot.get_user(recipient_id)

		await gather(
			recipient.send(embed=Embed(
				title=f'{ctx.author.name} sent the following alert:',
				description=message,
				url=f'https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}',
				color=0xff0000
			)),
			ctx.send(embed=Embed(
				title='Alert sent!',
				description='Thanks for the heads up.\nThe botmaster has been alerted of the problem.\nPlease be patient while we resolve the issue',
				color=0x00ff00
			))
		)


def setup(bot):
	bot.add_cog(Alert(bot))