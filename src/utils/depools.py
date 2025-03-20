import nekoton as nt
from typing import List

depool_codehash = bytes.fromhex("14e20e304f53e6da152eb95fffc993dbd28245a775d847eed043f7c78a503885")
stdepool_codehash = bytes.fromhex("533adf8a5680849177b9f213f61c48dfd8d730597078670d2367a5eef77251fe")


async def get_stdepools(transport: nt.JrpcTransport) -> List[nt.Address]:
    return await get_contracts_by_codehash(transport, stdepool_codehash)

async def get_depools(transport: nt.JrpcTransport) -> List[nt.Address]:
    return await get_contracts_by_codehash(transport, depool_codehash)

async def get_contracts_by_codehash(transport: nt.JrpcTransport, code_hash: str) -> List:
    addresses = []
    addresses = await transport.get_accounts_by_code_hash(
        code_hash=code_hash,
        continuation=None,
        limit=100)

    if len(addresses) < 100:
        return addresses

    last = addresses[-1]
    while(True):
        next_addresses = await transport.get_accounts_by_code_hash(
        code_hash=code_hash,
        continuation=last,
        limit=100)

        if len(next_addresses) == 0:
            break;

        addresses.extend(next_addresses)
        last = next_addresses[-1]
    
    return addresses