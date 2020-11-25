import json
from ServerCfg import ServerCfg

class Configuration:
	def __init__(self, token = None, prefix = '.', description = None, name = None, chan_forward_dm = None, owner_id = None, servers = {}):
		self.token = token
		self.prefix = prefix
		self.description = description
		self.name = name
		self.chan_forward_dm = chan_forward_dm
		self.owner_id = owner_id
		self.servers = {}
		for key, value in servers.items():
			fields = ['cate_personal_vc', 'chan_personal_vc', 'chan_message_log', 'chan_member_log', 'role_remind', 'chan_remind', 'confirm_reaction']
			args = [value[field] for field in fields]
			srv = ServerCfg(*args)
			self.servers[int(key)] = srv

def load_config(filename):
	with open(filename) as cfg_file:
		jsonfile = json.loads(cfg_file.read())

	args = (
		jsonfile['token'],
		jsonfile['prefix'],
		jsonfile['description'],
		jsonfile['name'],
		jsonfile['chan_forward_dm'],
		jsonfile['owner_id'],
		jsonfile['servers']
	)

	conf = Configuration(*args)
	return conf
