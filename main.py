import asyncio
import csv
import logging
import nekoton as nt
import sys

from src.utils.depools import get_stdepools, get_depools
from src.models.depool import Depool
from src.utils.helper import from_wei


filename = "data.csv"

async def main():
    transport = nt.JrpcTransport(endpoint="https://jrpc.everwallet.net")
    await transport.check_connection()

    depools = await get_depools(transport)
    #stdepools = await get_stdepools(transport)

    depool_info = []

    for depool in depools:
        state = await  transport.get_account_state(depool)
        model = Depool(depool, state)
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
            'has vestings'])
        # writing the data rows
        csvwriter.writerows(depool_info)










logging.basicConfig(filename='depool.log', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logger = logging.getLogger(__name__)

logger.info('Started')
asyncio.run(main())
logger.info('Finished')


