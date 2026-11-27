
import os
import json
import base64

from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

load_dotenv()

ENCRYPTION_PREFIX = "enc:v1:"
AAD = b"nexus-quartz:v1"


def get_encryption_key():
    key_value = os.getenv("AES_ENCRYPTION_KEY")

    if not key_value:
        raise ValueError("AES_ENCRYPTION_KEY is missing from .env")

    try:
        key = base64.b64decode(key_value, validate=True)
    except Exception as exc:
        raise ValueError("AES encryption key is not valid Base64") from exc

    if len(key) != 32:
        raise ValueError("AES-256 requires a 32-byte key")

    return key


def encrypt_text(value):
    if value is None:
        return None

    value = str(value)

    if value.startswith(ENCRYPTION_PREFIX):
        return value

    aes = AESGCM(get_encryption_key())
    nonce = os.urandom(12)

    encrypted = aes.encrypt(
        nonce,
        value.encode("utf-8"),
        AAD
    )

    payload = base64.b64encode(nonce + encrypted).decode("utf-8")

    return ENCRYPTION_PREFIX + payload


def decrypt_text(value):
    if value is None:
        return None

    if not isinstance(value, str):
        return value

    if not value.startswith(ENCRYPTION_PREFIX):
        return value

    payload = base64.b64decode(
        value[len(ENCRYPTION_PREFIX):],
        validate=True
    )

    nonce = payload[:12]
    encrypted = payload[12:]

    aes = AESGCM(get_encryption_key())

    decrypted = aes.decrypt(nonce, encrypted, AAD)

    return decrypted.decode("utf-8")


def encrypt_json(value):
    if value is None:
        return None

    return encrypt_text(json.dumps(value))


def decrypt_json(value):
    if value is None:
        return None

    if isinstance(value, (dict, list)):
        return value

    decrypted = decrypt_text(value)

    try:
        return json.loads(decrypted)
    except (TypeError, json.JSONDecodeError):
        return decrypted
