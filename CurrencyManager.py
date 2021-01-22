import json
from typing import List, Tuple
from CustomExceptions import *

def load_data():
    with open('data/Balances.json') as data_file:
        return json.loads(data_file.read())

def save_data(data):
    with open('data/Balances.json', 'w') as data_file:
        data_file.write(json.dumps(data, indent=4))

async def getMemberBalance(guild_id, member_id) -> int:
    data = load_data()
    if str(member_id) not in data[str(guild_id)]:
        return await setMemberBalance(guild_id, member_id, 0)
    return data[str(guild_id)][str(member_id)]

async def setMemberBalance(guild_id: int, member_id: int, new_balance: int) -> int:
    if new_balance < 0:
        raise NegativeBalanceException('Balance would go negative.', abs(new_balance))
    data = load_data()
    if not str(guild_id) in data:
        data[str(guild_id)] = {}
    data[str(guild_id)][str(member_id)] = new_balance
    save_data(data)
    return new_balance

async def getAllMembersBalances(guild_id) -> List[Tuple[int, int]]:
    data = load_data()
    users = data[str(guild_id)]
    return [(int(key), value) for key, value in users.items()]

async def getTopRichest(guild_id: int, limit: int = 10) -> List[Tuple[int, int]]:
    member_dict = await getAllMembersBalances(guild_id)
    all_members_sorted = sorted(member_dict, key=lambda e: e[1], reverse=True)[:10]
    return all_members_sorted[:limit]

async def addToMemberBalance(guild_id: int, member_id: int, amount: int, set_to_zero_if_result_negative: bool = False) -> int:
    old_balance = await getMemberBalance(guild_id, member_id)
    new_balance = old_balance + amount
    try:
        await setMemberBalance(guild_id, member_id, new_balance)
    except NegativeBalanceException as e:
        if set_to_zero_if_result_negative:
            await setMemberBalance(guild_id, member_id, 0)
        raise NegativeBalanceException(f'Member balance would go negative. user only has {old_balance}', e.missing_funds)

    return new_balance

async def transferBetweenMembers(guild_id: int, sender_id: int, receiver_id: int, amount: int) -> int:
    try:
        sender_new_balance = await addToMemberBalance(guild_id, sender_id, amount * -1)
    except NegativeBalanceException as e:
        raise InsufficientFundsException(f'Insufficient funds. Sender is missing {e.missing_funds}', e.missing_funds)
    await addToMemberBalance(guild_id, receiver_id, amount)
    return sender_new_balance
