"""Hash de contraseñas, tokens de sesión, CSRF y límite de intentos.

Solo se usa la biblioteca estándar: scrypt para contraseñas, sha256 para los
tokens de sesión y secrets para generarlos. El token en claro únicamente vive en
la cookie del navegador; en la base de datos se guarda su hash.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import threading
import time
from collections import defaultdict

SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 32


def hash_password(password: str) -> str:
    """Devuelve `scrypt$N$r$p$salt$hash` con sal aleatoria."""
    salt = os.urandom(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=SCRYPT_DKLEN,
    )
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Verifica una contraseña sin filtrar tiempos por comparación directa."""
    try:
        scheme, n, r, p, salt_hex, digest_hex = stored.split("$")
        if scheme != "scrypt":
            return False
        digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=bytes.fromhex(salt_hex),
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(bytes.fromhex(digest_hex)),
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError, IndexError):
        return False


def new_token() -> str:
    """Token opaco para la cookie de sesión."""
    return secrets.token_urlsafe(32)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def new_csrf_token() -> str:
    return secrets.token_urlsafe(24)


def csrf_matches(expected: str, supplied: str | None) -> bool:
    if not expected or not supplied:
        return False
    return hmac.compare_digest(expected, supplied)


class LoginLimiter:
    """Límite en memoria: 5 fallos por clave cada 15 minutos.

    Suficiente para una instalación de un solo proceso. En producción con varios
    workers habría que moverlo a la base de datos o a Redis.
    """

    def __init__(self, max_attempts: int = 5, window_seconds: int = 900) -> None:
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def _clean(self, key: str, now: float) -> list[float]:
        cutoff = now - self.window_seconds
        values = [stamp for stamp in self._attempts[key] if stamp > cutoff]
        self._attempts[key] = values
        return values

    def is_blocked(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            return len(self._clean(key, now)) >= self.max_attempts

    def register_failure(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            self._clean(key, now).append(now)

    def reset(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)

    def retry_after(self, key: str) -> int:
        now = time.monotonic()
        with self._lock:
            values = self._clean(key, now)
            if len(values) < self.max_attempts:
                return 0
            return max(1, int(self.window_seconds - (now - values[0])))


login_limiter = LoginLimiter()
