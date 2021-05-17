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

async def play_file(channel: discord.VoiceChannel, source_uri: str, volume: float):
	if not (source_uri.startswith('https://') or source_uri.startswith('http://')):
		source_uri = f'/mnt/volume_fra1_01/Music/{source_uri}.mp3'
	voice = channel.guild.voice_client
	if not voice:
		voice = await channel.connect()
	audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source_uri), volume)
	voice.play(audio, after=after)
	await stop_event.wait()
	stop_event.clear()
	await voice.disconnect()

class PlayFile(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cfg = load_config()
		self.player_volume = .1

	@commands.command(name='Play', aliases=['P'])
	async def play(self, ctx, *, source: str):
		await gather(
			play_file(ctx.author.voice.channel, source, self.player_volume),
			ctx.message.add_reaction(self.cfg.react_confirm)
		)

	@commands.command(name='Volume', aliases=['Vol'])
	async def volume(self, ctx, new_volume: int):
		self.player_volume = new_volume/100

	@commands.command(name='Stop', aliases=['DC'])
	async def stop(self, ctx):
		await ctx.guild.voice_client.disconnect()


def setup(bot):
	bot.add_cog(PlayFile(bot))