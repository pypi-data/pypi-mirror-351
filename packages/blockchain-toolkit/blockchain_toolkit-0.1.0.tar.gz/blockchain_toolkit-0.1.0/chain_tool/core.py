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
        args: dict,
        is_transaction: bool = False,
        aes_key: bytes = None,
        encrypt_fields: list[str] = None,
        decrypt_return: bool = False
    ):
        """
        Вызывает функцию контракта.

        :param func_name: Имя функции
        :param args: Параметры функции (dict)
        :param is_transaction: True — если транзакция, False — вызов метода
        :param aes_key: Ключ для шифрования/расшифровки
        :param encrypt_fields: Поля, которые нужно зашифровать перед отправкой
        :param decrypt_return: Расшифровать ли возвращаемые данные
        :return: Ответ от контракта
        """

        if not hasattr(self.contract.functions, func_name):
            raise AttributeError(f"Функция '{func_name}' не существует в контракте.")

        # Шифруем указанные поля
        if encrypt_fields and aes_key:
            for field in encrypt_fields:
                if field in args:
                    args[field] = self.encrypt_data(aes_key, args[field])

        func = getattr(self.contract.functions, func_name)

        if is_transaction:
            tx_hash = func(**args).transact()
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt
        else:
            result = func(**args).call()
            if decrypt_return and aes_key and isinstance(result, str) and result.startswith('g'):
                return self.decrypt_data(aes_key, result)
            return result