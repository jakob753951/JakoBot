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

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.id != 250667785368109056:
			return

		idea_strings = ['i have an idea', 'i have got an idea', 'i gots an idea', 'i has an idea', 'i got an idea', 'ive got an idea', "i've got an idea"]
		if any(s in message.content.lower() for s in idea_strings):
			await gather(
				play_file(message.author.voice.channel, 'https://ladegaardmoeller.dk/audio/OhNo.mp3', .5),
				message.channel.send('https://tenor.com/view/idea-light-bulb-lightbulb-gif-5187169')
			)

	@commands.command(name='Play', aliases=['P'])
	async def play(self, ctx, url: str, volume: float = .5):
		await gather(
			play_file(ctx.author.voice.channel, url, volume),
			ctx.message.add_reaction(self.cfg.servers[ctx.guild.id].react_confirm)
		)


def setup(bot):
	bot.add_cog(PlayFile(bot))