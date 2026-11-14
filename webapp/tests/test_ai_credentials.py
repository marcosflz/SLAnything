"""Credenciales de IA por usuario y suscripción personal (ADR-024)."""

from __future__ import annotations

import pytest

from webapp import config
from webapp.authoring import credentials, settings, store
from webapp.db import connect
from webapp.generation import pipeline

from conftest import admin_login, login_and_csrf, self_learner_login, teacher_login


@pytest.fixture
def ai_env(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "AUTHORING_DIR", tmp_path / "authoring")
    monkeypatch.setattr(config, "USER_PROVIDERS", True)
    monkeypatch.setattr(config, "SUBSCRIPTION_PROVIDER", True)
    monkeypatch.setattr(config, "LLM_FAKE", True)
    store.ensure_dir()
    yield


def _user_id(email: str) -> int:
    conn = connect()
    try:
        return int(conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()["id"])
    finally:
        conn.close()


def _put(client, token, **body):
    return client.put("/api/v1/account/ai", json=body, headers={"X-CSRF-Token": token})


def test_own_api_key_is_encrypted_and_never_returned(client, ai_env):
    token = self_learner_login(client)
    saved = _put(client, token, provider="anthropic", model="claude-sonnet-5-5", secret="sk-ant-secreto-9876")
    assert saved.status_code == 200, saved.text
    body = saved.json()
    assert body["active"] is True and body["key_hint"] == "••••9876"
    assert "sk-ant-secreto" not in saved.text
    assert "sk-ant-secreto" not in client.get("/api/v1/account/ai").text

    conn = connect()
    try:
        row = conn.execute("SELECT secret_enc FROM user_ai_settings").fetchone()
    finally:
        conn.close()
    assert "secreto" not in row["secret_enc"]

    uid = _user_id(config.SELF_LEARNER_EMAIL)
    resolved = credentials.resolve(uid)
    assert resolved["source"] == "user" and resolved["api_key"] == "sk-ant-secreto-9876"
    studio = client.get("/api/v1/authoring").json()
    assert studio["ai"]["source"] == "user"
    assert "api_key" not in studio["ai"]

    assert client.post("/api/v1/account/ai/test", headers={"X-CSRF-Token": token}).json()["ok"] is True
    assert client.delete("/api/v1/account/ai", headers={"X-CSRF-Token": token}).json()["configured"] is False
    assert credentials.resolve(uid)["source"] == "platform"


def test_students_cannot_configure_or_use_ai(client, ai_env):
    token = login_and_csrf(client)  # alumno de la academia demo
    assert client.get("/api/v1/account/ai").status_code == 403
    assert _put(client, token, provider="anthropic", model="m", secret="k").status_code == 403
    assert client.get("/api/v1/authoring").status_code == 403


def test_subscription_is_personal_and_needs_explicit_consent(client, ai_env):
    token = teacher_login(client)
    refused = _put(client, token, provider="claude-code", secret="sk-ant-oat01-token")
    assert refused.status_code == 400
    accepted = _put(client, token, provider="claude-code", secret="sk-ant-oat01-token", accept_personal=True)
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["accepted_personal_at"]

    teacher = _user_id(config.TEACHER_EMAIL)
    learner = _user_id(config.SELF_LEARNER_EMAIL)
    assert credentials.resolve(teacher)["provider"] == "claude-code"
    assert credentials.resolve(teacher)["user_id"] == teacher
    # Nadie más hereda la suscripción del profesor.
    assert credentials.resolve(learner)["source"] == "platform"

    # La instancia puede desactivar la suscripción: se vuelve al proveedor de plataforma.
    config.SUBSCRIPTION_PROVIDER = False
    try:
        assert credentials.resolve(teacher)["source"] == "platform"
        ids = {item["id"] for item in client.get("/api/v1/account/ai").json()["providers"]}
        assert "claude-code" not in ids
    finally:
        config.SUBSCRIPTION_PROVIDER = True


def test_users_cannot_pick_self_hosted_endpoints(client, ai_env):
    token = self_learner_login(client)
    for provider in ("custom", "ollama", "lmstudio"):
        assert _put(client, token, provider=provider, model="qwen3").status_code == 400


def test_platform_provider_cannot_be_a_subscription(client, ai_env):
    token = admin_login(client)
    response = client.put(
        "/api/v1/authoring/settings",
        json={"provider": "claude-code", "model": "sonnet", "api_key": "tok"},
        headers={"X-CSRF-Token": token},
    )
    assert response.status_code == 400
    assert settings.load_settings()["provider"] != "claude-code"


def test_regenerating_someone_elses_job_uses_the_requesters_credentials(client, ai_env):
    token = teacher_login(client)
    _put(client, token, provider="claude-code", secret="tok-profe", accept_personal=True)
    teacher = _user_id(config.TEACHER_EMAIL)
    admin = _user_id(config.ADMIN_EMAIL)
    store.create_job(
        job_id="job-ajeno", owner_id=teacher, title="Unidad", source_names=[],
        provider="claude-code", model="", languages=["es"],
    )
    assert pipeline._settings("job-ajeno")["api_key"] == "tok-profe"
    # Otra persona (p. ej. la administración) regenera: nunca con la suscripción del autor.
    other = pipeline._settings("job-ajeno", actor_id=admin)
    assert other["source"] == "platform"
    assert other.get("api_key") != "tok-profe"


def test_rotating_the_secret_makes_stored_credentials_unusable(client, ai_env, monkeypatch):
    token = self_learner_login(client)
    _put(client, token, provider="openrouter", model="anthropic/claude-sonnet-5.5", secret="sk-or-123456")
    uid = _user_id(config.SELF_LEARNER_EMAIL)
    monkeypatch.setattr(config, "SECRET_KEY", "otro-secreto")
    assert credentials.resolve(uid)["source"] == "platform"
    assert "warning" in credentials.public(uid)
