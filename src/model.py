import datetime
from enum import Enum

from pydantic import BaseModel
from pytoniq_core import Transaction


class Model(BaseModel):
    
    def serialize(self):
        """
        Serialize the model instance.
        """
        return self.model_dump()

    @classmethod
    def deserialize(cls, serialized_data: dict) -> 'Model':
        """
        Deserialize data into a model instance.
        """
        return cls(**serialized_data)


class OrderStatus(Enum):
    """
    Enumeration for transaction statuses.
    """
    NEW = 'new'
    CONFIRMED = 'confirm'
    CANCELED = 'aborted'


class TransactionRecord(Model):
    """
    Represents a transaction with attributes like creation date, status, etc.
    """
    lt: int = -1
    timestamp: str = ''
    value: int
    from_address: str | None = None

    class Config:
        use_enum_values = True

    @classmethod
    def from_transaction(cls, transaction: Transaction) -> 'TransactionRecord':
        return cls(
            lt=transaction.lt,
            timestamp=str(transaction.now),  # Assuming 'now' is the creation date in Unix timestamp
            value=transaction.in_msg.info.value_coins,  # Assuming 'value_coins' is the value
            from_address=transaction.in_msg.info.src.to_str())  # Assuming 'src' is the source address

    def to_dict(self):
        return {
            'lt': self.lt,
            'timestamp': self.timestamp,
            'value': self.value,
            'from_address': self.from_address
        }


class Order(Model):
    invoice_id: int
    value: int
    value_id: int = 0
    status: str = OrderStatus.NEW.value

    def to_dict(self):
        return {
            'invoice_id': self.invoice_id,
            'value': self.value,
            'value_id': self.value_id,
            'status': self.status
        }

