from cryptography.fernet import Fernet
import base64
from web3 import Web3


class BlockchainToolkit:
    def __init__(self, w3: Web3, contract_address: str, abi: dict):
        """
        :param w3: Экземпляр web3.Web3
        :param contract_address: Адрес смарт-контракта
        :param abi: ABI смарт-контракта в виде словаря
        """
        self.w3 = w3
        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)

    @staticmethod
    def generate_aes_key():
        return Fernet.generate_key()

    @staticmethod
    def encrypt_data(key: bytes, data: str) -> str:
        """Шифрует данные AES"""
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")

    @staticmethod
    def decrypt_data(key: bytes, encrypted_data: str) -> str:
        """Расшифровывает данные AES"""
        fernet = Fernet(key)
        decrypted = fernet.decrypt(base64.b64decode(encrypted_data))
        return decrypted.decode("utf-8")

    def call_contract_function(
        self,
        func_name: str,
        args: tuple,
        is_transaction: bool = False,
    ):
        """
        Вызывает функцию контракта.

        :param func_name: Имя функции
        :param args: Параметры функции (dict)
        :param is_transaction: True — если транзакция, False — вызов метода
        :return: Ответ от контракта
        """

        if not hasattr(self.contract.functions, func_name):
            raise AttributeError(f"Функция '{func_name}' не существует в контракте.")

        func = getattr(self.contract.functions, func_name)

        if is_transaction:
            tx_hash = func(*args).transact({
                'from': self.w3.eth.default_account
            })
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt
        else:
            result = func(*args).call()
            return result