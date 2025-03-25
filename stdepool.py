import asyncio
import csv
import logging
import nekoton as nt
import sys

from src.utils.depools import get_stdepools
from src.models.stdepool import StDepool
from src.utils.helper import from_wei


filename = "stdepools.csv"

async def main():
    transport = nt.JrpcTransport(endpoint="https://jrpc.everwallet.net")
    await transport.check_connection()

    stdepools = await get_stdepools(transport)

    depool_info = []

    for depool in stdepools:
        state = await  transport.get_account_state(depool)
        model = StDepool(depool, state)
        model.fill_round()
        depool_info.append([
            depool, 
            model.native_balance(), 
            model.total_staked(), 
            model.even_total_staked(), 
            model.odd_total_staked(), 
            len(model.participants()), 
            model.is_rustcup_depool(),
            model.has_lock_stakes(),
            model.has_vesting_stakes(),
            model.round0.election_time,
            model.round0.state,
            model.round0.stake,
            model.round1.election_time,
            model.round1.state,
            model.round1.stake,
            model.round2.election_time,
            model.round2.state,
            model.round2.stake,
            model.round3.election_time,
            model.round3.state,
            model.round3.stake,
              ])
        

    with open(filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        # writing the fields
        csvwriter.writerow([
            'address',
            'balance',
            'total_stake',
            'even total stake',
            'odd_total_stake',
            'participan_count',
            'rust cup',
            'has lock',
            'has vestings',
            'round0_election',
            'round0_state',
            'round0_stake',
            'round1_election',
            'round1_state',
            'round1_stake',
            'round2_election',
            'round2_state',
            'round2_stake',
            'round3_election',
            'round3_state',
            'round3_stake'
            ])
        # writing the data rows
        csvwriter.writerows(depool_info)










logging.basicConfig(filename='depool.log', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logger = logging.getLogger(__name__)

logger.info('Started')
asyncio.run(main())
logger.info('Finished')


