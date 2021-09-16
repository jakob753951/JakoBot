from discord.ext import commands
from Configuration import load_config

def is_top_admin():
	async def predicate(ctx):
		cfg = load_config()
		return ctx.author.id in cfg.top_admins
	return commands.check(predicate)

def is_admin():
	async def predicate(ctx):
		cfg = load_config()
		admin_role = ctx.guild.get_role(cfg.role_admin)
		return admin_role in ctx.author.roles
	return commands.check(predicate)

def is_staff():
	async def predicate(ctx):
		cfg = load_config()
		staff_role = ctx.guild.get_role(cfg.role_staff)
		admin_role = ctx.guild.get_role(cfg.role_admin)
		return staff_role in ctx.author.roles or admin_role in ctx.author.roles
	return commands.check(predicate)

def can_verify():
	def predicate(ctx):
		cfg = load_config()
		for allowed in cfg.roles_can_verify:
			if ctx.guild.get_role(allowed) in ctx.author.roles:
				return True
		return False
	return commands.check(predicate)