import json
from typing import List, Tuple
from CustomExceptions import *

def load_data():
    with open('data/MainData.json') as data_file:
        return json.loads(data_file.read())

def save_data(data):
    with open('data/MainData.json', 'w') as data_file:
        data_file.write(json.dumps(data, indent=4))

async def getMemberBalance(guild_id, member_id) -> int:
    data = load_data()
    if str(member_id) not in data[str(guild_id)]:
        return await setMemberBalance(guild_id, member_id, 0)
    return data[str(guild_id)][str(member_id)]

async def setMemberBalance(guild_id: int, member_id: int, new_balance: int) -> int:
    data = load_data()
    data[str(guild_id)][str(member_id)] = new_balance
    save_data(data)
    return new_balance

async def getAllMembersBalances(guild_id) -> List[Tuple[int, int]]:
    data = load_data()
    users = data[str(guild_id)]
    return [(int(key), value) for key, value in users.items()]

async def getTopRichest(guild_id: int, limit: int = 10) -> List[Tuple[int, int]]:
    member_dict = await getAllMembersBalances(guild_id)
    return sorted(member_dict, key=lambda e: e[1], reverse=True)

async def addToMemberBalance(guild_id: int, member_id: int, amount: int) -> int:
    old_balance = await getMemberBalance(guild_id, member_id)
    new_balance = old_balance + amount
    await setMemberBalance(guild_id, member_id, new_balance)
    return new_balance

async def transferBetweenMembers(guild_id: int, sender_id: int, receiver_id: int, amount: int) -> int:
    sender_balance = await getMemberBalance(guild_id, sender_id)
    if sender_balance - amount < 0:
        missing_funds = 0 - (sender_balance - amount)
        raise InsufficientFundsException(f'Sender is missing {missing_funds} funds', missing_funds)
    sender_new_balance = await addToMemberBalance(guild_id, sender_id, amount * -1)
    await addToMemberBalance(guild_id, receiver_id, amount)
    return sender_new_balance
