from discord.ext import commands
from Configuration import load_config

def is_admin():
	async def predicate(ctx):
		cfg = load_config('config.json')
		role = ctx.guild.get_role(cfg.servers[ctx.guild.id].role_admin)
		return role in ctx.author.roles
	return commands.check(predicate)

def is_staff():
	async def predicate(ctx):
		cfg = load_config('config.json')
		role = ctx.guild.get_role(cfg.servers[ctx.guild.id].role_staff)
		return role in ctx.author.roles
	return commands.check(predicate)

def can_verify():
	def predicate(ctx):
		cfg = load_config('config.json')
		for allowed in cfg.servers[ctx.guild.id].roles_can_verify:
			if ctx.guild.get_role(allowed) in ctx.author.roles:
				return True
		return False
	return commands.check(predicate)