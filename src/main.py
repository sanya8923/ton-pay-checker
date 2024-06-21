import asyncio
import logging
from quart import Quart, jsonify, Response, request

from src import config_reader
from src.db_manager import db_manager
from src.exceptions import TransactionManagerError, TonClientError, MongoError
from model import Order
from tr_manager import tr_manager

app = Quart(__name__)
logging.basicConfig(level=logging.DEBUG,
                    filename='../logs.log',
                    filemode='w',
                    format='%(asctime)s - %(message)s')


@app.before_serving
async def startup():
    loop = asyncio.get_event_loop()
    loop.create_task(main())


@app.route('/transactions', methods=['GET'])
async def on_get_transactions() -> Response:
    try:
        data = await request.get_data()
        invoice_id = data.decode()

        order = await db_manager.get_one(col_name='orders',
                                         fltr={'invoice_id': invoice_id})
        if order:
            order = Order.deserialize(order)
            return jsonify(order.to_dict())
        else:
            return jsonify([])

    except (MongoError, TonClientError, TransactionManagerError, Exception) as e:
        logging.exception('Error in on_get_transactions')


@app.route('/create_order', methods=['POST'])
async def on_create_order() -> Response:
    try:
        invoice = Order.deserialize(await request.get_json())
        orders_in_db_list = await db_manager.get_many('orders',
                                                      {'value': invoice.value,
                                                          'status': 'new'})
        new_order = Order(invoice_id=invoice.invoice_id,
                          value=invoice.value)
        if not orders_in_db_list:
            new_order.value_id = invoice.value
        else:
            orders_in_db = [Order.deserialize(order) for order in orders_in_db_list]
            sorted_orders_in_db = sorted(orders_in_db,
                                         key=lambda order: order.value_id,
                                         reverse=True)

            new_order.value_id = sorted_orders_in_db[0].value_id + 1
        await db_manager.add_one('orders', new_order.serialize())
        return jsonify(new_order.to_dict())
    except (MongoError, TonClientError, TransactionManagerError, Exception):
        logging.exception('Error in on_create_order')


async def main():
    while True:
        await tr_manager.check_transactions_in_bc()
        await asyncio.sleep(60)


if __name__ == '__main__':
    app.run(port=config_reader.config.app_port.get_secret_value())
