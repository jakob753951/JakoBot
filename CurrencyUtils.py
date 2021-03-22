from datetime import datetime
import discord
import CurrencyManager as currency
from Configuration import load_config

def get_guild_cfg(guild_id):
	cfg = load_config('Config.json')
	return cfg.servers[guild_id]

def pluralise(guild_id, amount: int):
	guild_cfg = get_guild_cfg(guild_id)
	if abs(amount) == 1:
		return guild_cfg.currency_name_singular
	else:
		return guild_cfg.currency_name_plural

async def transaction_log(bot, guild_id, recipient: discord.Member, amount: int, sender: discord.Member = None, title: str = 'User received money:'):
	guild_cfg = get_guild_cfg(guild_id)
	chan_rx = await bot.fetch_channel(guild_cfg.chan_transaction_history)

	if sender:
		desc = f'{sender.mention} sent {recipient.mention} {abs(amount)} {pluralise(guild_id, amount)}'
	else:
		desc = f"{recipient.mention} {'got' if amount >= 0 else 'lost'} {abs(amount)} {pluralise(guild_id, amount)}"

	embed = discord.Embed(color=0x0000ff, title=title, description=desc, timestamp=datetime.utcnow())
	embed.set_author(name=f'{recipient.name}#{recipient.discriminator}', icon_url=recipient.avatar_url)
	if sender:
		embed.add_field(name='Sender: ', value=f'{sender.name}#{sender.discriminator}', inline=True)
	embed.add_field(name='Amount: ', value=amount, inline=True)

	await chan_rx.send(embed=embed)

async def parse_amount(guild_id: int, member_id: int, amount: str, max_amount: int = None):
	if amount.lower() == 'all':
		return await currency.getMemberBalance(guild_id, member_id)
	if amount.lower() == 'half':
		return (await currency.getMemberBalance(guild_id, member_id)) // 2
	if amount.lower() == 'max' and max_amount:
		return max_amount
	try:
		return int(amount)
	except:
		raise ValueError