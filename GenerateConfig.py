from os import listdir
from os.path import isfile, join
import importlib

def generate_all():
	cogs_dir = "enabled_cogs"
	general = ['token', 'prefix', 'description', 'name', 'owner_id']
	server = []
	try:
		for file in [''.join(f.split('.')[:-1]) for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
			requirements = importlib.import_module(f'{cogs_dir}.{file}').requirements
			general.extend(requirements['general'])
			server.extend(requirements['server'])
	except Exception as e:
		print(f'something went wrong: {e}\nRegenerate Configs? [y/n]')
		resp = input()
		if resp != 'y':
			return
		generate_server_cfg(server)
		generate_general_cfg(general, server)
		generate_all()
		return

	general = list(set(general))
	server = list(set(server))

	generate_general_cfg(general, server)
	generate_server_cfg(server)


def generate_general_cfg(general, server):
	with open('Configuration.py', 'w') as cfg_file:
		cfg_file.write(f"""\
import json
from ServerCfg import ServerCfg

class Configuration:
\tdef __init__(self, """)
		cfg_file.write(', '.join([*[f"""{field} = {"'.'" if field == 'prefix' else None}""" for field in general], "servers = {}"]))
		cfg_file.write('):\n')

		for field in general:
			cfg_file.write(f'\t\tself.{field} = {field}\n')

		cfg_file.write('\t\tself.servers = {}\n')

		cfg_file.write(f"""\t\tfor key, value in servers.items():
			fields = [{", ".join(["'" + f + "'" for f in server])}]
			args = [value[field] for field in fields]
			srv = ServerCfg(*args)
			self.servers[int(key)] = srv
""")

		sep = ',\n\t\t'
		cfg_file.write(f"""
def load_config(filename):
	with open(filename, encoding='utf8') as cfg_file:
		jsonfile = json.loads(cfg_file.read())

	args = [
		{sep.join([*[f"jsonfile['{field}']" for field in general], "jsonfile['servers']"])}
	]

	conf = Configuration(*args)
	return conf
""")

def generate_server_cfg(server):
	sep = '\n\t\t'
	with open('ServerCfg.py', 'w') as cfg_file:
		cfg_file.write(f"""\
class ServerCfg:
	def __init__(self{''.join([', ' + prop for prop in server])}):
		{sep.join([f"self.{prop} = {prop}" for prop in server]) if server else 'pass'}
""")