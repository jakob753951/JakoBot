import discord
from discord.ext import commands
import asyncio

stop_event = asyncio.Event()

def after(error):
	if error:
		print(error)

	loop = asyncio.get_event_loop()
	loop.call_soon_threadsafe(lambda: stop_event.set())

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

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.id != 250667785368109056:
			return

		if 'i have an idea' in message.content.lower():
			await play_file(message.author.voice.channel, 'https://ladegaardmoeller.dk/main/audio/OhNo.mp3', 1)


