import logging
import typing
from abc import ABC, abstractmethod

from pytoniq import LiteBalancer, BalancerError
from pytoniq_core import Address

from db_manager import db_manager, DbManager
from exceptions import CreateClientError, GetTransactionsError, CloseClientError
from model import TransactionRecord


class BcClient(ABC):
    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def get_new_transactions(self, address: typing.Union[Address, str], count: int,
                                   from_lt: int = None, from_hash: typing.Optional[bytes] = None,
                                   to_lt: int = 0, **kwargs) -> typing.List[TransactionRecord]:
        pass


class TonClient(LiteBalancer, BcClient):
    db_manager: DbManager = db_manager

    async def start(self):
        try:
            await self.start_up()
        except (BalancerError, Exception) as err:
            logging.exception('Error in starting up the client')
            raise CreateClientError from err

    async def close(self):
        try:
            await self.close_all()
        except (BalancerError, Exception) as err:
            logging.exception('Error in closing the client')
            raise CloseClientError from err

    async def get_new_transactions(self, address: typing.Union[Address, str], count: int,
                                   from_lt: int = None, from_hash: typing.Optional[bytes] = None,
                                   to_lt: int = 0, **kwargs) -> typing.List[TransactionRecord]:
        try:
            print(f"get_all_transactions")
            raw_transactions = await self.get_transactions(address, count, from_lt, from_hash,
                                                           to_lt, **kwargs)

            print(f"RAW TRANSACTIONS: {raw_transactions}")
            result = [TransactionRecord.from_transaction(raw_transaction)
                      for raw_transaction in raw_transactions]
        except (BalancerError, Exception) as err:
            logging.exception('Error in getting transactions')
            raise GetTransactionsError from err
        else:
            return result


try:
    client = TonClient.from_testnet_config(trust_level=0)  # client = TonClient.from_mainnet_config(trust_level=0)
except (BalancerError, Exception) as e:
    logging.exception('Error in creating the client')
    raise CreateClientError from e
