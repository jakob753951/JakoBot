from discord.ext import commands
from discord import Embed
import json

requirements = {'general': [], 'server': []}

def load_data():
	with open('data/Swearing.json') as data_file:
		loaded_data = json.loads(data_file.read())
	# Convert dict keys from str to int
	return {int(member_id): member_data for member_id, member_data in loaded_data.items()}

def remove_consecutive_duplicates(dupe_list: list):
	return (element for index, element in enumerate(dupe_list) if index == 0 or element != dupe_list[index-1])

def is_swear(word: str, swear_list: str):
	filtered_word = remove_consecutive_duplicates(word)
	if filtered_word in swear_list or word in swear_list:
		return True
	return False

def swears_in_message(content: str, swears):
	return [word for word in content.split() if is_swear(word, swears)]

class Swearing(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_message(self, message):
		data = load_data()
		if message.author.id not in data:
			return

		dom_user_id, swear_list = data[message.author.id]

		message_swears = swears_in_message(message.content, swear_list)

		if not message_swears:
			return

		user_to_dm = message.guild.get_member(dom_user_id)
		title = 'Swearing detected'
		nl = '\n'
		desc = f"{message.author.mention} sent a swear in {message.channel.mention}: {message.content}{nl}swear(s) detected: [{', '.join(message_swears)}]"
		embed = Embed(title=title, description=desc)
		await user_to_dm.send(embed=embed)


def setup(bot):
	bot.add_cog(Swearing(bot))