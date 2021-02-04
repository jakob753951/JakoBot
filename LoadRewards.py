import os
import json
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def get_rewards(service, sheet_id) -> list:
	range_name = 'Rewards!A2:F'

	sheet = service.spreadsheets()
	result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
	values = result.get('values', [])

	rewards = []

	for row in values:
		id, name, description, amount, cooldown_in_hours, active = row
		if active.lower() == 'yes':
			rewards.append({
				'id': id,
				'name': name,
				'description': description,
				'amount': int(amount),
				'cooldown_in_hours': int(cooldown_in_hours)
			})

	return rewards

scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']

creds = None
if os.path.exists('token.pickle'):
	with open('token.pickle', 'rb') as token:
		creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
	if creds and creds.expired and creds.refresh_token:
		creds.refresh(Request())
	else:
		flow = InstalledAppFlow.from_client_secrets_file(
			'credentials.json', scopes)
		creds = flow.run_local_server(port=0)
	# Save the credentials for the next run
	with open('token.pickle', 'wb') as token:
		pickle.dump(creds, token)

service = build('sheets', 'v4', credentials=creds)

keys = {
	669731845260443678: '1_RxsVYTEwYXSvyWQVnvKVwOePX3-ZfclkN8HaU48jRc'
}

rewards = {guild_id: get_rewards(service, sheet_id) for guild_id, sheet_id in keys.items()}

with open('data/Rewards.json', 'w') as rewards_file:
	rewards_file.write(json.dumps(rewards, indent=4))