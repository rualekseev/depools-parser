import asyncio
import csv
import logging
import nekoton as nt
import sys

from src.utils.depools import get_depools
from src.models.depool import Depool
from src.utils.jrpc import get_codehash


filename = "participant.csv"

class ParticipantInfo:
    total_stake: nt.Tokens
    free_stake: nt.Tokens
    lock_stake: nt.Tokens
    vesting_stake: nt.Tokens
    code_hash: str
    stakes: dict

    def __init__(self):
        self.stakes = {}
        self.total_stake = nt.Tokens(0)
        self.free_stake = nt.Tokens(0)
        self.lock_stake = nt.Tokens(0)
        self.vesting_stake = nt.Tokens(0)

    def add_stake(self, address: nt.Address, stake: nt.Tokens):
        self.total_stake += stake

    def add_free_stake(self, address: nt.Address, stake: nt.Tokens):
        self.free_stake += stake
        if address in self.stakes.keys():
            self.stakes[address] += stake
        else:
            self.stakes[address] = stake

    def add_vesting_stake(self, address: nt.Address, stake: nt.Tokens):
        self.vesting_stake += stake
        if address in self.stakes.keys():
            self.stakes[address] += stake
        else:
            self.stakes[address] = stake

    def add_lock_stake(self, address: nt.Address, stake: nt.Tokens):
        self.lock_stake += stake
        if address in self.stakes.keys():
            self.stakes[address] += stake
        else:
            self.stakes[address] = stake


async def main():
    transport = nt.JrpcTransport(endpoint="https://jrpc.everwallet.net")
    await transport.check_connection()

    

    depools = await get_depools(transport)

    participants = {}

    for depool in depools:
        state = await  transport.get_account_state(depool)
        depool = Depool(depool, state)

        for participant in depool.participants():
            participant_info = ParticipantInfo()
            if participant.address in participants.keys():
                participant_info = (participants[participant.address])
            else:
                participant_info.code_hash = await get_codehash(transport, participant.address)
                participants[participant.address] = participant_info            
            participant_info.add_stake(depool.address, participant.total_stake)
            participant_info.add_free_stake(depool.address, participant.even_stake)
            participant_info.add_free_stake(depool.address, participant.odd_stake)
            participant_info.add_vesting_stake(depool.address, participant.even_vesting_stake)
            participant_info.add_vesting_stake(depool.address, participant.odd_vesting_stake)
            participant_info.add_lock_stake(depool.address, participant.even_lock_stake)
            participant_info.add_lock_stake(depool.address, participant.odd_lock_stake)

    
    to_write = []
    for key, value in participants.items():
        to_write.append([
            key, 
            value.total_stake, 
            value.free_stake, 
            value.vesting_stake, 
            value.lock_stake, 
            value.code_hash,
            len(value.stakes),
            value.stakes.keys()])
        

    with open(filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        # writing the fields
        csvwriter.writerow([
            'address',
            'total_stake',
            'free_stake',
            'vesting_stake',
            'lock_stake',
            'code_hash',
            'stake_count',
            'depools'
            ])
        
        # writing the data rows
        csvwriter.writerows(to_write)










logging.basicConfig(filename='depool.log', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logger = logging.getLogger(__name__)

logger.info('Started')
asyncio.run(main())
logger.info('Finished')