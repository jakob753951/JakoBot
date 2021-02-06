import discord
from discord.ext import commands
import asyncio
from asyncio import gather

requirements = {'general': [], 'server': ['react_confirm']}

stop_event = asyncio.Event()

def after(error):
	if error:
		print(error)
	stop_event.set()

async def play_file(channel, filename, volume = 1):
	voice = channel.guild.voice_client
	if not voice:
		voice = await channel.connect()
	audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename), volume)
	voice.play(audio, after=after)
	await stop_event.wait()
	await voice.disconnect()

class PlayFile(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='Play', aliases=['P'])
	async def play(self, ctx, url: str, volume: float = .5):
		await gather(
			play_file(ctx.author.voice.channel, url, volume),
			ctx.message.add_reaction(self.cfg.servers[ctx.guild.id].react_confirm)
		)


def setup(bot):
	bot.add_cog(PlayFile(bot))