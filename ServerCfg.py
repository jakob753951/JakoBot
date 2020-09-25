class ServerCfg:
	def __init__(self, role_lurker, days_inactivity_before_role, chan_truth_or_dare, webhook_url):
		self.role_lurker = role_lurker
		self.days_inactivity_before_role = days_inactivity_before_role
		self.chan_truth_or_dare = chan_truth_or_dare
		self.webhook_url = webhook_url
