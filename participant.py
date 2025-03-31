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
    code_hash: str
    stakes: dict

    def __init__(self):
        self.stakes = {}
        self.total_stake = nt.Tokens(0)

    def add_stake(self, address: nt.Address, stake: nt.Tokens):
        if address in self.stakes.keys():
            self.total_stake += stake
            self.stakes[address] += stake
        else:
            self.total_stake = stake
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
            if participant.address in participants.keys():
                (participants[participant.address]).add_stake(depool.address, participant.total_stake)
            else:
                participant_info = ParticipantInfo()
                participant_info.add_stake(depool.address, participant.total_stake)
                participant_info.code_hash = await get_codehash(transport, participant.address)
                participants[participant.address] = participant_info
    
    to_write = []
    for key, value in participants.items():
        to_write.append([
            key, 
            value.total_stake, 
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