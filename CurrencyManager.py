import json
from CustomExceptions import *

def load_data():
    with open('data/Balances.json') as data_file:
        read_json = json.loads(data_file.read())

    return { int(key): int(value) for key, value in read_json.items() }

def save_data(data):
    with open('data/Balances.json', 'w') as data_file:
        data_file.write(json.dumps(data, indent=4))

async def getMemberBalance(member_id) -> int:
    data = load_data()
    if member_id not in data:
        return await setMemberBalance(member_id, 0)
    return data[member_id]

async def setMemberBalance(member_id: int, new_balance: int) -> int:
    if new_balance < 0:
        raise NegativeBalanceException('Balance would go negative.', abs(new_balance))
    data = load_data() or {}
    data[member_id] = new_balance
    save_data(data)
    return new_balance

async def removeMemberData(member_id: int):
    data = load_data()
    del data[member_id]
    save_data(data)

async def removeAllData():
    data = {}
    save_data(data)

async def getAllMembersBalances() -> list[tuple[int, int]]:
    return [(member_id, balance) for member_id, balance in  load_data().items()]

async def getTopRichest(limit: int = 10) -> list[tuple[int, int]]:
    member_dict = await getAllMembersBalances()
    all_members_sorted = sorted(member_dict, key=lambda elem: elem[1], reverse=True)
    return all_members_sorted[:limit]

async def addToMemberBalance(member_id: int, amount: int, set_to_zero_if_result_negative: bool = False) -> int:
    old_balance = await getMemberBalance(member_id)
    new_balance = old_balance + amount
    try:
        await setMemberBalance(member_id, new_balance)
    except NegativeBalanceException as e:
        if set_to_zero_if_result_negative:
            await setMemberBalance(member_id, 0)
        else:
            raise NegativeBalanceException(f'Member balance would go negative. user only has {old_balance}', e.missing_funds)

    return new_balance

async def transferBetweenMembers(sender_id: int, receiver_id: int, amount: int) -> int:
    try:
        sender_new_balance = await addToMemberBalance(sender_id, amount * -1)
    except NegativeBalanceException as e:
        raise InsufficientFundsException(f'Insufficient funds. Sender is missing {e.missing_funds}', e.missing_funds)
    await addToMemberBalance(receiver_id, amount)
    return sender_new_balance
