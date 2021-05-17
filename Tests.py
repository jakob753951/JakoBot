import CurrencyManager as cm
import asyncio
import random

user_1 = 1
user_2 = 2

async def setAndGetDataReturnsSetData():
    value_to_set = random.randint(0, 10000)
    await cm.setMemberBalance(user_1, value_to_set)
    assert await cm.getMemberBalance(user_1) == value_to_set

async def getAllMembersBalances_ReturnsCorrectTypes():
    members = await cm.getAllMembersBalances()
    for member in members:
        assert isinstance(member[0], int)
        assert isinstance(member[1], int)

async def getTopRichest_IsSorted():
    members = await cm.getTopRichest()
    balances = [member[1] for member in members]
    assert balances == sorted(balances, reverse=True)

async def addToMemberBalance_AddsCorrectly():
    amount_to_add = random.randint(0, 10000)
    initial_balance = await cm.getMemberBalance(user_1)
    await cm.addToMemberBalance(user_1, amount_to_add)
    new_balance = await cm.getMemberBalance(user_1)
    assert initial_balance + amount_to_add == new_balance

async def addToMemberBalance_ReturnsNewBalance():
    amount_to_add = random.randint(0, 10000)
    returned_new_balance = await cm.addToMemberBalance(user_1, amount_to_add)
    actual_new_balance = await cm.getMemberBalance(user_1)
    assert returned_new_balance == actual_new_balance

async def transferBetweenMembers_MasterTest():
    amount_to_transfer = random.randint(0, 10000)
    sender_initial_balance = await cm.getMemberBalance(user_1)
    recipient_initial_balance = await cm.getMemberBalance(user_2)

    await cm.transferBetweenMembers(user_1, user_2, amount_to_transfer)

    sender_expected_balance = sender_initial_balance - amount_to_transfer
    recipient_expected_balance = recipient_initial_balance + amount_to_transfer

    sender_actual_balance = await cm.getMemberBalance(user_1)
    recipient_actual_balance = await cm.getMemberBalance(user_2)

    assert sender_expected_balance == sender_actual_balance
    assert recipient_expected_balance == recipient_actual_balance

async def run_tests():
    await setAndGetDataReturnsSetData()
    await getAllMembersBalances_ReturnsCorrectTypes()
    await getTopRichest_IsSorted()
    await addToMemberBalance_AddsCorrectly()
    await addToMemberBalance_ReturnsNewBalance()
    await transferBetweenMembers_MasterTest()
    print('All tests passed!')

if __name__ == '__main__':
    asyncio.run(run_tests())