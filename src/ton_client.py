import logging
import typing
from abc import ABC, abstractmethod

from pytoniq import LiteBalancer, BalancerError
from pytoniq_core import Address

from src.db_manager import db_manager, DbManager
from src.exceptions import CreateClientError, GetTransactionsError, CloseClientError
from src.model import TransactionRecord


class BcClient(ABC):
    """
        An abstract base class that defines the interface for blockchain clients.

        ...

        Methods
        -------
        start():
            Starts the client.
        close():
            Closes the client.
        get_new_transactions(address: typing.Union[Address, str], count: int, from_lt: int = None, from_hash: typing.Optional[bytes] = None, to_lt: int = 0, **kwargs):
            Retrieves new transactions from the blockchain.
    """
    @abstractmethod
    async def start(self):
        """
            Starts the client.

            Raises
            ------
            NotImplementedError
                If the method is not implemented.
        """
        pass

    @abstractmethod
    async def close(self):
        """
            Closes the client.

            Raises
            ------
            NotImplementedError
                If the method is not implemented.
        """
        pass

    @abstractmethod
    async def get_new_transactions(self, address: typing.Union[Address, str], count: int,
                                   from_lt: int = None, from_hash: typing.Optional[bytes] = None,
                                   to_lt: int = 0, **kwargs) -> typing.List[TransactionRecord]:
        """
            Retrieves new transactions from the blockchain.

            Parameters
            ----------
            address : typing.Union[Address, str]
                The address to retrieve transactions from.
            count : int
                The number of transactions to retrieve.
            from_lt : int, optional
                The logical time to retrieve transactions from.
            from_hash : typing.Optional[bytes], optional
                The hash to retrieve transactions from.
            to_lt : int, optional
                The logical time to retrieve transactions to.

            Returns
            -------
            typing.List[TransactionRecord]
                A list of new transactions.

            Raises
            ------
            NotImplementedError
                If the method is not implemented.
        """
        pass


class TonClient(LiteBalancer, BcClient):
    """
        A class used to interact with the blockchain.

        ...

        Attributes
        ----------
        db_manager : DbManager
            a manager to interact with the database

        Methods
        -------
        start():
            Starts the client.
        close():
            Closes the client.
        get_new_transactions(address: typing.Union[Address, str], count: int, from_lt: int = None, from_hash: typing.Optional[bytes] = None, to_lt: int = 0, **kwargs):
            Retrieves new transactions from the blockchain.
    """
    db_manager: DbManager = db_manager

    async def start(self):
        """
        Starts the client.

        Raises
        ------
        CreateClientError
            If an error occurs while starting the client.
        """
        try:
            await self.start_up()
        except (BalancerError, Exception) as err:
            logging.exception('Error in starting up the client')
            raise CreateClientError from err

    async def close(self):
        """
        Closes the client.

        Raises
        ------
        CloseClientError
            If an error occurs while closing the client.
        """
        try:
            await self.close_all()
        except (BalancerError, Exception) as err:
            logging.exception('Error in closing the client')
            raise CloseClientError from err

    async def get_new_transactions(self, address: typing.Union[Address, str], count: int,
                                   from_lt: int = None, from_hash: typing.Optional[bytes] = None,
                                   to_lt: int = 0, **kwargs) -> typing.List[TransactionRecord]:
        """
        Retrieves new transactions from the blockchain.

        Parameters
        ----------
        address : typing.Union[Address, str]
            The address to retrieve transactions from.
        count : int
            The number of transactions to retrieve.
        from_lt : int, optional
            The logical time to retrieve transactions from.
        from_hash : typing.Optional[bytes], optional
            The hash to retrieve transactions from.
        to_lt : int, optional
            The logical time to retrieve transactions to.

        Returns
        -------
        typing.List[TransactionRecord]
            A list of new transactions.

        Raises
        ------
        GetTransactionsError
            If an error occurs while retrieving new transactions.
        """
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
