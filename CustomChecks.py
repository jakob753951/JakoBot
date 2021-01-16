from Configuration import load_config

def is_admin(ctx):
    cfg = load_config('config.json')
    role = ctx.guild.get_role(cfg.servers[ctx.guild.id].role_admin)
    return role in ctx.author.roles

def can_verify(ctx):
	cfg = load_config('config.json')
	for allowed in cfg.servers[ctx.guild.id].roles_can_verify:
		if ctx.guild.get_role(allowed) in ctx.author.roles:
			return True
	return False