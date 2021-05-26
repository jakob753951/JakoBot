from datetime import datetime
import discord
import CurrencyManager as currency
from Configuration import load_config

def pluralise(amount: int):
	cfg = load_config('Config.json')
	if abs(amount) == 1:
		return cfg.currency_name_singular
	else:
		return cfg.currency_name_plural

async def transaction_log(bot, recipient: discord.User, amount: int, sender: discord.user = None, title: str = 'User received money:'):
	cfg = load_config('Config.json')
	log_channel = await bot.fetch_channel(cfg.chan_transaction_history)

	if sender:
		desc = f'{sender.mention} sent {recipient.mention} {abs(amount)} {pluralise(amount)}'
	else:
		desc = f"{recipient.mention} {'got' if amount >= 0 else 'lost'} {abs(amount)} {pluralise(amount)}"

	embed = discord.Embed(color=0x0000ff, title=title, description=desc, timestamp=datetime.utcnow())
	embed.set_author(name=f'{recipient.name}#{recipient.discriminator}', icon_url=recipient.avatar_url)
	if sender:
		embed.add_field(name='Sender: ', value=f'{sender.name}#{sender.discriminator}', inline=True)
	embed.add_field(name='Amount: ', value=amount, inline=True)

	await log_channel.send(embed=embed)

async def parse_amount(member_id: int, amount: str, max_amount: int = None):
	if amount.lower() == 'all':
		return await currency.getMemberBalance(member_id)
	if amount.lower() == 'half':
		return (await currency.getMemberBalance(member_id)) // 2
	if amount.lower() == 'max' and max_amount:
		return max_amount
	try:
		return int(amount)
	except:
		raise ValueError