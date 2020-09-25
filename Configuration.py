import json
from ServerCfg import ServerCfg

class Configuration:
	def __init__(self, token = '', prefix = '.', description = '', name = '', chan_forward_dm = '', minutes_between_saves = '', minutes_between_checks = '', chan_confessions = '', servers = {}):
		self.token = token
		self.prefix = prefix
		self.description = description
		self.name = name
		self.chan_forward_dm = chan_forward_dm
		self.minutes_between_saves = minutes_between_saves
		self.minutes_between_checks = minutes_between_checks
		self.chan_confessions = chan_confessions
		self.servers = {}
		for key, value in servers.items():
			fields = ['role_lurker', 'days_inactivity_before_role', 'chan_truth_or_dare', 'webhook_url']
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
		jsonfile['minutes_between_saves'],
		jsonfile['minutes_between_checks'],
		jsonfile['chan_confessions'],
		jsonfile['servers']
	)

	conf = Configuration(*args)
	return conf
