import asyncio
import csv
import logging
import nekoton as nt
import sys

from src.utils.depools import get_depools
from src.models.depool import Depool


filename = "depools.csv"

async def main():
    transport = nt.JrpcTransport(endpoint="https://jrpc.everwallet.net")
    await transport.check_connection()

    depools = await get_depools(transport)
    depool_info = []

    for depool in depools:
        state = await  transport.get_account_state(depool)
        model = Depool(depool, state)
        model.fill_round()
        depool_info.append([
            depool, 
            model.native_balance(), 
            model.total_staked(), 
            model.even_total_staked(), 
            model.odd_total_staked(), 
            len(model.participants()), 
            model.has_lock_stakes(),
            model.has_vesting_stakes(),
            model.contains_rustcup_lock_donor(),
            model.rustcup_lock_stake(),
            model.contains_rustcup_vesting_donor(),
            model.rustcup_vesting_stake(),
            model.contains_extra_stake_lock_donor(),
            model.extra_stake_lock_stake(),
            model.contains_extra_stake_vesting_donor(),
            model.extra_stake_vesting_stake(),
            model.contains_mludi_lock_donor(),
            model.mludi_lock_stake(),
            model.contains_mludi_vesting_donor(),
            model.mludi_vesting_stake(),
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
            model.round3.stake])


    with open(filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        # writing the fields
        csvwriter.writerow([
            'address',
            'native balance',
            'total_stake',
            'even total stake',
            'odd_total_stake',
            'participan_count',
            'has locks',
            'has vestings',
            'has rustcup lock',
            'total rustcup lock stake',
            'has rustcup vesting',
            'total rustcup vesting stake',
            'has extra stake lock',
            'total extra lock stake',
            'has extra stake vesting',
            'total extra vesting stake',
            'has M.Ludi lock',
            'total M.Ludi lock stake',
            'has M.Ludi vesting',
            'total M.Ludi vesting stake',
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
            'round3_stake'])
        # writing the data rows
        csvwriter.writerows(depool_info)










logging.basicConfig(filename='depool.log', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logger = logging.getLogger(__name__)

logger.info('Started')
asyncio.run(main())
logger.info('Finished')


