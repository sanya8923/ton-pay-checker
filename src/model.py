import datetime
from enum import Enum

from pydantic import BaseModel
from pytoniq_core import Transaction


class Model(BaseModel):
    """
    A base class that provides serialization and deserialization methods for models.
    """
    def serialize(self) -> dict:
        """
        Serializes the model instance.

        Returns
        -------
        dict
            The serialized model instance.
        """
        return self.model_dump()

    @classmethod
    def deserialize(cls, serialized_data: dict) -> 'Model':
        """
        Deserializes data into a model instance.

        Parameters
        ----------
        serialized_data : dict
            The serialized data.

        Returns
        -------
        Model
            The deserialized model instance.
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

    Attributes
    ----------
    lt : int
        The logical time of the transaction.
    timestamp : str
        The timestamp of the transaction.
    value : int
        The value of the transaction.
    from_address : str
        The source address of the transaction.
    """
    lt: int = -1
    timestamp: str = ''
    value: int
    from_address: str | None = None

    class Config:
        use_enum_values = True

    @classmethod
    def from_transaction(cls, transaction: Transaction) -> 'TransactionRecord':
        """
        Creates a TransactionRecord instance from a Transaction instance.

        Parameters
        ----------
        transaction : Transaction
            The transaction instance.

        Returns
        -------
        TransactionRecord
            The created TransactionRecord instance.
        """
        return cls(
            lt=transaction.lt,
            timestamp=str(transaction.now),  # Assuming 'now' is the creation date in Unix timestamp
            value=transaction.in_msg.info.value_coins,  # Assuming 'value_coins' is the value
            from_address=transaction.in_msg.info.src.to_str())  # Assuming 'src' is the source address

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the instance.

        Returns
        -------
        dict
            The dictionary representation of the instance.
        """
        return {
            'lt': self.lt,
            'timestamp': self.timestamp,
            'value': self.value,
            'from_address': self.from_address
        }


class Order(Model):
    """
    Represents an order with attributes like invoice id, value, value id, and status.

    Attributes
    ----------
    invoice_id : int
        The invoice id of the order.
    value : int
        The value of the order.
    value_id : int
        The value id of the order.
    status : str
        The status of the order.
    """
    invoice_id: int
    value: int
    value_id: int = 0
    status: str = OrderStatus.NEW.value

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the instance.

        Returns
        -------
        dict
            The dictionary representation of the instance.
        """
        return {
            'invoice_id': self.invoice_id,
            'value': self.value,
            'value_id': self.value_id,
            'status': self.status
        }

