import nekoton as nt
from typing import List, Tuple, TypedDict
from src.abi.generated.depool import DePoolAbi

class Participant:
    address: nt.Address
    total_stake: nt.Tokens
    even_stake: nt.Tokens
    odd_stake: nt.Tokens
    has_stake: bool
    even_lock_stake: nt.Tokens
    odd_lock_stake: nt.Tokens
    has_lock_stake: bool
    lock_owner: nt.Address
    lock_donor: nt.Address
    even_vesting_stake: nt.Tokens
    odd_vesting_stake: nt.Tokens
    has_vesting_stake: bool
    vesting_owner: nt.Address
    vesting_donor: nt.Address

    def __init__(self, address: nt.Address, stake: nt.Tokens):
        self.address = address
        self.total_stake = stake
        self.even_stake = nt.Tokens(0)
        self.odd_stake = nt.Tokens(0)
        self.has_stake = False
        self.even_lock_stake = nt.Tokens(0)
        self.odd_lock_stake = nt.Tokens(0)
        self.has_lock_stake = False
        self.even_vesting_stake = nt.Tokens(0)
        self.odd_vesting_stake = nt.Tokens(0)
        self.has_vesting_stake = False
        self.vesting_owner = nt.Address('0:0000000000000000000000000000000000000000000000000000000000000000')
        self.lock_owner = nt.Address('0:0000000000000000000000000000000000000000000000000000000000000000')

    def set_lock_donor(self, address: nt.Address):
        self.lock_donor = address

    def set_vesting_donor(self, address: nt.Address):
        self.vesting_donor = address
    
    def add_stake(self, even_stake: nt.Tokens, odd_stake: nt.Tokens):
        if even_stake + odd_stake > nt.Tokens(0):
            self.has_stake = True
        self.even_stake += even_stake
        self.odd_stake += odd_stake

    def add_lock_stake(self, even_stake: nt.Tokens, odd_stake: nt.Tokens, owner: nt.Address):
        if even_stake + odd_stake > nt.Tokens(0):
            self.has_lock_stake = True
        self.even_lock_stake += even_stake
        self.odd_lock_stake += odd_stake
        self.lock_owner = owner

    def add_vesting_stake(self, even_stake: nt.Tokens, odd_stake: nt.Tokens, owner: nt.Address):
        if even_stake + odd_stake > nt.Tokens(0):
            self.has_vesting_stake = True
        self.even_vesting_stake += even_stake
        self.odd_vesting_stake += odd_stake
        self.vesting_owner = owner


class Depool: 
    address: nt.Address
    state: nt.AccountState

    rustcup_donor: nt.Address
    extra_stake_donor: nt.Address
    mludi_donor: nt.Address

    def __init__(self, address: nt.Address, state: nt.AccountState):
        self.address = address
        self.state = state
        self.rustcup_donor = nt.Address('0:eabd38806e244f941f0611aef85d8ab06dd9289cb2495153e9561153c08dc4d5')
        self.extra_stake_donor = nt.Address('0:3de70f9212154344a3158768b3fed731fc865ca15948b0d6d0d34daf4c6a7a0a')
        self.mludi_donor = nt.Address('0:e17ac4e77f46626579c7c4fefe35286117384c5ccfc8745c9780cdf056c378bf')

    def native_balance(self) -> nt.Tokens:
        return self.state.balance
    
    def total_staked(self) -> nt.Tokens:
        participants = self.participants()
        balance = nt.Tokens(0)
        for participant in participants:
            balance += participant.total_stake
        
        return balance
    
    def even_total_staked(self) -> nt.Tokens:
        participants = self.participants()
        balance = nt.Tokens(0)
        for participant in participants:
            balance += participant.even_stake + participant.even_lock_stake + participant.even_vesting_stake 
        
        return balance
    
    def odd_total_staked(self) -> nt.Tokens:
        participants = self.participants()
        balance = nt.Tokens(0)
        for participant in participants:
            balance += participant.odd_stake + participant.odd_lock_stake + participant.odd_vesting_stake 
        
        return balance
    
    def participants(self) ->  List[Participant]:
        addresses = DePoolAbi.get_participants().with_args({}).call(self.state).output['participants']
        
        result = []
        for address in addresses:
            result.append(self.participant_info(address))
        return result

    def participant_info(self, address: nt.Address) ->  Participant:
        stake = nt.Tokens.from_nano(DePoolAbi.get_participant_info().with_args({"addr":address}).call(self.state).output['total'])
        participant = Participant(address, stake)

        stakes = DePoolAbi.get_participant_info().with_args({"addr":address}).call(self.state).output['stakes']
        lock_stakes = DePoolAbi.get_participant_info().with_args({"addr":address}).call(self.state).output['locks']
        vesting_stakes = DePoolAbi.get_participant_info().with_args({"addr":address}).call(self.state).output['vestings']

        for stake in stakes:
            if stake[0]%2 == 0:
                participant.add_stake(nt.Tokens.from_nano(stake[1]), nt.Tokens(0))
            else:
                participant.add_stake(nt.Tokens(0), nt.Tokens.from_nano(stake[1]))
                

        for stake in lock_stakes:
            if stake[0]%2 == 0:
                participant.add_lock_stake(nt.Tokens.from_nano(stake[1]['remainingAmount']), nt.Tokens(0), stake[1]['owner'])
            else:
                participant.add_lock_stake(nt.Tokens(0), nt.Tokens.from_nano(stake[1]['remainingAmount']), stake[1]['owner'])

        for stake in vesting_stakes:
            if stake[0]%2 == 0:
                participant.add_vesting_stake(nt.Tokens.from_nano(stake[1]['remainingAmount']), nt.Tokens(0), stake[1]['owner'])
            else:
                participant.add_vesting_stake(nt.Tokens(0), nt.Tokens.from_nano(stake[1]['remainingAmount']), stake[1]['owner'])

        participant.set_lock_donor(DePoolAbi.get_participant_info().with_args({"addr":address}).call(self.state).output['lockDonor'])
        participant.set_vesting_donor(DePoolAbi.get_participant_info().with_args({"addr":address}).call(self.state).output['vestingDonor'])

        return participant

    def has_lock_stakes(self) -> bool:
        participants = self.participants()
        for participant in participants:
            if participant.has_lock_stake:
                return True
        return False
    
    def has_vesting_stakes(self) -> bool:
        participants = self.participants()
        for participant in participants:
            if participant.has_vesting_stake:
                return True
        return False

    def contains_rustcup_lock_donor(self) -> bool:
        return self.contains_lock_donor(self.rustcup_donor)

    def rustcup_lock_stake(self) -> nt.Tokens:
        return self.lock_stake_by_donor(self.rustcup_donor)  

    def contains_rustcup_vesting_donor(self) -> bool:
        return self.contains_vesting_donor(self.rustcup_donor)

    def rustcup_vesting_stake(self) -> nt.Tokens:
        return self.vesting_stake_by_donor(self.rustcup_donor) 

    def contains_extra_stake_lock_donor(self) -> bool:
        return self.contains_lock_donor(self.extra_stake_donor)

    def extra_stake_lock_stake(self) -> nt.Tokens:
        return self.lock_stake_by_donor(self.extra_stake_donor)  

    def contains_extra_stake_vesting_donor(self) -> bool:
        return self.contains_vesting_donor(self.extra_stake_donor)

    def extra_stake_vesting_stake(self) -> nt.Tokens:
        return self.vesting_stake_by_donor(self.extra_stake_donor)
    
    def contains_mludi_lock_donor(self) -> bool:
        return self.contains_lock_donor(self.mludi_donor)

    def mludi_lock_stake(self) -> nt.Tokens:
        return self.lock_stake_by_donor(self.mludi_donor)  

    def contains_mludi_vesting_donor(self) -> bool:
        return self.contains_vesting_donor(self.mludi_donor)

    def mludi_vesting_stake(self) -> nt.Tokens:
        return self.vesting_stake_by_donor(self.mludi_donor) 

    def contains_lock_donor(self, donor: nt.Address) -> bool:
        participants = self.participants()
        for participant in participants:
            if participant.lock_donor == donor and participant.lock_owner == donor:
                return True
        return False        

    def lock_stake_by_donor(self, donor: nt.Address) -> nt.Tokens:
        stake = nt.Tokens(0)
        participants = self.participants()
        for participant in participants:
            if participant.lock_donor == donor and participant.lock_owner == donor:
                stake += participant.even_lock_stake
                stake += participant.odd_lock_stake        
        return stake 

    def contains_vesting_donor(self, donor: nt.Address) -> bool:
        participants = self.participants()
        for participant in participants:
            if participant.vesting_donor == donor and participant.vesting_owner == donor:
                return True
        return False 

    def vesting_stake_by_donor(self, donor: nt.Address) -> nt.Tokens:
        stake = nt.Tokens(0)
        participants = self.participants()
        for participant in participants:
            if participant.vesting_donor == donor and participant.vesting_owner == donor:
                stake += participant.even_vesting_stake
                stake += participant.odd_vesting_stake        
        return stake
    
    async def reload_state(self, transport: nt.Transport):
        await transport.check_connection()
        self.state = await transport.get_account_state(self.address)
    