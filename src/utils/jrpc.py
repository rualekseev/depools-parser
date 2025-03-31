import nekoton as nt


async def get_codehash(transport: nt.JrpcTransport, address: nt.Address) -> str:
    account = await transport.get_account_state(address)
    if account.status == nt.AccountStatus.NotExists:
        return ""

    if account.status == nt.AccountStatus.Uninit:
        return ""

    if account.status == nt.AccountStatus.Frozen:
        return ""

    return account.state_init.code_hash.hex()