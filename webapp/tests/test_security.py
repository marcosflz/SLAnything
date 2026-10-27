"""Pruebas unitarias de las primitivas de seguridad."""

from __future__ import annotations

from webapp.security import (
    LoginLimiter,
    csrf_matches,
    hash_password,
    new_token,
    token_hash,
    verify_password,
)


def test_password_hash_uses_random_salt_and_verifies():
    password = "clave-segura-123"
    first = hash_password(password)
    second = hash_password(password)

    assert first != second  # sal aleatoria
    assert first.startswith("scrypt$")
    assert password not in first
    assert verify_password(password, first)
    assert not verify_password("otra-clave", first)
    assert not verify_password(password, "formato-inválido")


def test_session_tokens_are_opaque_and_hashed():
    token = new_token()

    assert len(token) >= 40
    assert token != new_token()
    assert token_hash(token) != token
    assert len(token_hash(token)) == 64
    assert token_hash(token) == token_hash(token)


def test_csrf_comparison_rejects_missing_or_wrong_values():
    assert csrf_matches("token-de-sesion", "token-de-sesion")
    assert not csrf_matches("token-de-sesion", None)
    assert not csrf_matches("token-de-sesion", "")
    assert not csrf_matches("", "token-de-sesion")
    assert not csrf_matches("token-de-sesion", "otro-token")


def test_login_limiter_blocks_and_resets():
    limiter = LoginLimiter(max_attempts=2, window_seconds=60)

    assert not limiter.is_blocked("alumno@example.com")
    limiter.register_failure("alumno@example.com")
    assert not limiter.is_blocked("alumno@example.com")
    limiter.register_failure("alumno@example.com")

    assert limiter.is_blocked("alumno@example.com")
    assert limiter.retry_after("alumno@example.com") >= 1

    limiter.reset("alumno@example.com")
    assert not limiter.is_blocked("alumno@example.com")
    assert limiter.retry_after("alumno@example.com") == 0
