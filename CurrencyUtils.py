from datetime import datetime
import discord
import CurrencyManager as currency

def pluralise(guild_cfg, amount: int):
	if abs(amount) == 1:
		return guild_cfg.currency_name_singular
	else:
		return guild_cfg.currency_name_plural

async def transaction_log(bot, guild_cfg, recipient: discord.Member, amount: int, sender: discord.Member = None, title: str = 'User received money:'):
	chan_rx = await bot.fetch_channel(guild_cfg.chan_transaction_history)

	if sender:
		desc = f'{sender.mention} sent {recipient.mention} {amount} {pluralise(guild_cfg, amount)}'
	else:
		desc = f"{recipient.mention} {'got' if amount >= 0 else 'lost'} {amount} {pluralise(guild_cfg, amount)}"

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