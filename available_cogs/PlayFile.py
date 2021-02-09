from Configuration import load_config
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

async def play_file(channel: discord.VoiceChannel, source_uri: str, volume: float = .5):
	voice = channel.guild.voice_client
	if not voice:
		voice = await channel.connect()
	audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source_uri), volume)
	voice.play(audio, after=after)
	await stop_event.wait()
	await voice.disconnect()

class PlayFile(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config()

	@commands.command(name='Play', aliases=['P'])
	async def play(self, ctx, source: str, volume: float = .5):
		await gather(
			play_file(ctx.author.voice.channel, source, volume),
			ctx.message.add_reaction(self.cfg.servers[ctx.guild.id].react_confirm)
		)

	@commands.command(name='Stop', aliases=['DC'])
	async def stop(self, ctx):
		await ctx.guild.voice_client.disconnect()


def setup(bot):
	bot.add_cog(PlayFile(bot))