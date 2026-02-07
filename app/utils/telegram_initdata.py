from __future__ import annotations
import hashlib
import hmac
from urllib.parse import parse_qsl
from typing import Dict


def _secret_key(bot_token: str) -> bytes:
    return hashlib.sha256(bot_token.encode()).digest()


def verify_init_data(init_data: str, bot_token: str) -> Dict[str, str]:
    """
    Telegram WebApp initData verification.
    Returns parsed dict if valid, else raises ValueError.
    """
    data = dict(parse_qsl(init_data, keep_blank_values=True))
    if "hash" not in data:
        raise ValueError("hash missing")

    recv_hash = data.pop("hash")
    pairs = []
    for k in sorted(data.keys()):
        pairs.append(f"{k}={data[k]}")
    check_string = "\n".join(pairs)

    secret = _secret_key(bot_token)
    calc_hash = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calc_hash, recv_hash):
        raise ValueError("invalid initData hash")

    return data
