import base64
import binascii
import hashlib
import secrets

from database import db
from database.models import Account


def hash_password(password_str: str, salt_byte: bytes) -> bytes:
    dk = hashlib.pbkdf2_hmac("sha256", password_str.encode("utf-8"), salt_byte, 10000)
    return binascii.hexlify(dk)


class AccountService:
    """
    Service class for managing user accounts.
    """

    @staticmethod
    async def create_account(
        email: str,
        password: str,
        name: str,
        language: str = "en-US",
        timezone: str = "UTC",
        interface_theme: str = "default",
        last_login_ip: str = "From UI",
    ) -> Account:
        """
        Create a new user account.

        :param email: The email address of the user.
        :param password: The password for the user account.
        :param name: The name of the user. If not provided, it will be derived from the email.
        :param language: The preferred language of the user. Default is 'en-US'.
        :param timezone: The preferred timezone of the user. Default is 'UTC'.
        """

        account = Account()
        account.email = email
        account.name = name
        salt = secrets.token_bytes(16)
        base64_salt = base64.b64encode(salt).decode()

        # encrypt password with salt
        password_hashed = hash_password(password, salt)
        base64_password_hashed = base64.b64encode(password_hashed).decode()

        account.password = base64_password_hashed
        account.password_salt = base64_salt

        account.interface_language = language
        account.interface_theme = interface_theme

        account.last_login_ip = last_login_ip
        # Set timezone based on language
        account.timezone = timezone
        async with db.session() as session:
            session.add(account)
            await session.commit()
        return account
