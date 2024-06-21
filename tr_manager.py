import logging

import config_reader
from db_manager import db_manager
from model import TransactionRecord, OrderStatus, Order
from exceptions import StoreNewTransactionsError, TonClientError, \
    TransactionManagerError, MongoError, CheckTransactionsError, GetOldLatestTransactionError
from ton_client import client, BcClient
from pydantic import ValidationError


class TransactionManager:
    def __init__(self, cl, db_man):
        self.client: BcClient = cl
        self.db_manager = db_man

    latest_transaction: TransactionRecord | None = None

    async def check_transactions_in_bc(self) -> list:
        try:
            print('check_transactions_in_bc')
            await client.start()
            if last_transaction := await self.get_old_latest_transaction():
                new_transactions = await client.get_new_transactions(
                                         address=config_reader.config.pay_address.get_secret_value(),
                                         count=16,
                                         to_lt=last_transaction.lt)
            else:
                new_transactions = await client.get_new_transactions(
                                         address=config_reader.config.pay_address.get_secret_value(),
                                         count=16)
            await client.close()
            print(f'new transactions: {new_transactions}')
            orders = await self.db_manager.get_many(col_name='orders',
                                                    fltr={'status': OrderStatus.NEW.value})
            if orders:
                orders = [Order.deserialize(order) for order in orders]
                confirmed_orders = [order for order in orders
                                    if order.value_id in [transaction.value for transaction in new_transactions]]
                print(f'confirmed: {confirmed_orders}')
                for conf_order in confirmed_orders:
                    conf_order.status = OrderStatus.CONFIRMED.value
                    await self.db_manager.replace_one(col_name='orders',
                                                      fltr={'invoice_id': conf_order.invoice_id,
                                                            'status': OrderStatus.NEW.value,
                                                            'value_id': conf_order.value_id},
                                                      replacement=conf_order.serialize())
            await self.store_new_transactions(new_transactions)
        except (MongoError,
                TonClientError,
                TransactionManagerError,
                Exception) as e:
            logging.exception('Error in on_get_transactions')
            raise CheckTransactionsError from e

    async def get_old_latest_transaction(self) -> TransactionRecord | None:
        try:
            transactions_in_db = await self.db_manager.get_many(col_name='transactions', fltr={})
            if not transactions_in_db:
                return None
            transactions = [TransactionRecord.deserialize(transactions_in_db) for transactions_in_db in transactions_in_db]
            sorted_transactions_in_db = sorted(transactions, key=lambda tr: tr.timestamp, reverse=True)
            self.latest_transaction = sorted_transactions_in_db[0]
            return self.latest_transaction
        except (MongoError,
                ValidationError,
                Exception) as e:
            raise GetOldLatestTransactionError from e

    async def store_new_transactions(self, new_transactions: list[TransactionRecord]):
        try:
            if len(new_transactions) == 0:
                logging.debug('No new transactions to store')
                return

            await self.db_manager.add_many(col_name='transactions',
                                           data=[tr.serialize() for tr in new_transactions])
            logging.debug(f'Stored new transactions: {new_transactions}')
        except (MongoError,
                Exception) as e:
            logging.exception('Error in storing new transactions')
            raise StoreNewTransactionsError from e


tr_manager = TransactionManager(client, db_manager)
