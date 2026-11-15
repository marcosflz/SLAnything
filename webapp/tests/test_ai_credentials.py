"""Credenciales de IA: varios proveedores, modelos visibles, academia y suscripciones (ADR-024, ADR-025)."""

from __future__ import annotations

import json
import time

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
    return client.put("/api/v1/account/ai/providers", json=body, headers={"X-CSRF-Token": token})


def _provider(data, provider_id):
    return next(p for p in data["providers"] if p["id"] == provider_id)


def _models(*ids):
    return [{"id": i, "label": i.upper()} for i in ids]


def test_own_api_key_is_encrypted_and_never_returned(client, ai_env):
    token = self_learner_login(client)
    saved = _put(client, token, provider="anthropic", secret="sk-ant-secreto-9876", models=_models("claude-sonnet-5-5"))
    assert saved.status_code == 200, saved.text
    view = _provider(saved.json(), "anthropic")["config"]
    assert view["ready"] is True and view["key_hint"] == "••••9876"
    assert "sk-ant-secreto" not in saved.text
    assert "sk-ant-secreto" not in client.get("/api/v1/account/ai").text

    conn = connect()
    try:
        row = conn.execute("SELECT secret_enc FROM ai_providers WHERE provider = 'anthropic'").fetchone()
    finally:
        conn.close()
    assert "secreto" not in row["secret_enc"]

    uid = _user_id(config.SELF_LEARNER_EMAIL)
    resolved = credentials.resolve(uid)
    assert resolved["source"] == "user" and resolved["api_key"] == "sk-ant-secreto-9876"
    studio = client.get("/api/v1/authoring").json()
    assert studio["ai"]["source"] == "user" and "api_key" not in studio["ai"]

    assert client.post("/api/v1/account/ai/providers/anthropic/test", headers={"X-CSRF-Token": token}).json()["ok"] is True
    deleted = client.delete("/api/v1/account/ai/providers/anthropic", headers={"X-CSRF-Token": token})
    assert _provider(deleted.json(), "anthropic")["config"] is None
    assert credentials.resolve(uid)["source"] == "platform"


def test_several_providers_with_visible_models_and_a_default(client, ai_env):
    token = self_learner_login(client)
    uid = _user_id(config.SELF_LEARNER_EMAIL)
    assert _put(client, token, provider="openrouter", secret="sk-or-111111", models=_models("a/one", "b/two")).status_code == 200
    assert _put(client, token, provider="deepseek", secret="sk-ds-222222", models=_models("deepseek-chat")).status_code == 200

    # El primero que queda listo pasa a ser el predeterminado.
    assert credentials.user_default(uid) == {"source": "user", "provider": "openrouter", "model": "a/one"}
    groups = client.get("/api/v1/ai/models").json()
    mine = [(g["provider"], [m["id"] for m in g["models"]]) for g in groups["groups"] if g["source"] == "user"]
    assert mine == [("openrouter", ["a/one", "b/two"]), ("deepseek", ["deepseek-chat"])]

    choice = {"source": "user", "provider": "deepseek", "model": "deepseek-chat"}
    assert client.put("/api/v1/account/ai/default", json=choice, headers={"X-CSRF-Token": token}).status_code == 200
    assert credentials.resolve(uid)["provider"] == "deepseek"
    # Un modelo no activo no puede ser el predeterminado ni elegirse.
    bad = {**choice, "model": "otro"}
    assert client.put("/api/v1/account/ai/default", json=bad, headers={"X-CSRF-Token": token}).status_code == 400
    assert credentials.resolve(uid, choice=bad)["provider"] == "deepseek"  # cae al predeterminado

    # Elegir explícitamente otro proveedor activo.
    picked = credentials.resolve(uid, choice={"source": "user", "provider": "openrouter", "model": "b/two"})
    assert picked["provider"] == "openrouter" and picked["model"] == "b/two" and picked["api_key"] == "sk-or-111111"

    # Desactivar un proveedor lo saca del selector sin borrar su clave.
    _put(client, token, provider="openrouter", enabled=False)
    providers_now = {g["provider"] for g in client.get("/api/v1/ai/models").json()["groups"] if g["source"] == "user"}
    assert providers_now == {"deepseek"}
    assert _provider(client.get("/api/v1/account/ai").json(), "openrouter")["config"]["key_configured"] is True


def test_students_cannot_configure_or_use_ai(client, ai_env):
    token = login_and_csrf(client)  # alumno de la academia demo
    assert client.get("/api/v1/account/ai").status_code == 403
    assert _put(client, token, provider="anthropic", secret="k").status_code == 403
    assert client.get("/api/v1/ai/models").status_code == 403
    assert client.get("/api/v1/authoring").status_code == 403


def test_subscription_is_personal_and_needs_explicit_consent(client, ai_env):
    token = teacher_login(client)
    refused = _put(client, token, provider="claude-code", secret="sk-ant-oat01-token")
    assert refused.status_code == 400
    accepted = _put(client, token, provider="claude-code", secret="sk-ant-oat01-token", accept_personal=True)
    assert accepted.status_code == 200, accepted.text
    assert _provider(accepted.json(), "claude-code")["config"]["accepted_personal_at"]

    teacher = _user_id(config.TEACHER_EMAIL)
    learner = _user_id(config.SELF_LEARNER_EMAIL)
    resolved = credentials.resolve(teacher)
    assert resolved["provider"] == "claude-code" and resolved["user_id"] == teacher
    # Nadie más hereda la suscripción del profesor.
    assert credentials.resolve(learner)["source"] == "platform"

    # La instancia puede desactivar la suscripción: se vuelve al proveedor de plataforma.
    config.SUBSCRIPTION_PROVIDER = False
    try:
        assert credentials.resolve(teacher)["source"] == "platform"
        ids = {item["id"] for item in client.get("/api/v1/account/ai").json()["providers"]}
        assert "claude-code" not in ids and "chatgpt" not in ids
    finally:
        config.SUBSCRIPTION_PROVIDER = True


def test_users_cannot_pick_self_hosted_endpoints(client, ai_env):
    token = self_learner_login(client)
    for provider in ("custom", "ollama", "lmstudio"):
        assert _put(client, token, provider=provider, models=_models("qwen3")).status_code == 400


def test_chatgpt_is_linked_by_signing_in_not_by_pasting_a_key(client, ai_env):
    token = self_learner_login(client)
    response = _put(client, token, provider="chatgpt", secret="sk-anything", accept_personal=True)
    assert response.status_code == 400


def test_platform_provider_cannot_be_a_subscription(client, ai_env):
    token = admin_login(client)
    for provider in ("claude-code", "chatgpt"):
        response = client.put(
            "/api/v1/authoring/settings",
            json={"provider": provider, "model": "sonnet", "api_key": "tok"},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == 400
    assert settings.load_settings()["provider"] not in ("claude-code", "chatgpt")


def test_academy_shares_api_keys_with_its_teachers_but_never_subscriptions(client, ai_env):
    # La administración de la academia demo comparte una clave de API.
    admin_token = teacher_login(client)  # la profesora demo es owner de la academia demo
    assert client.get("/api/v1/admin/ai").status_code == 200
    shared = client.put(
        "/api/v1/admin/ai/providers",
        json={"provider": "openrouter", "secret": "sk-or-academia", "models": _models("x/shared")},
        headers={"X-CSRF-Token": admin_token},
    )
    assert shared.status_code == 200, shared.text
    assert "sk-or-academia" not in shared.text
    subscription = client.put(
        "/api/v1/admin/ai/providers",
        json={"provider": "claude-code", "secret": "tok", "accept_personal": True},
        headers={"X-CSRF-Token": admin_token},
    )
    assert subscription.status_code == 400

    teacher = _user_id(config.TEACHER_EMAIL)
    conn = connect()
    try:
        workspace_id = int(conn.execute("SELECT id FROM workspaces WHERE slug = 'academia-demo'").fetchone()["id"])
    finally:
        conn.close()
    groups = credentials.model_groups(teacher, workspace_id)["groups"]
    assert any(g["source"] == "workspace" and g["provider"] == "openrouter" for g in groups)
    resolved = credentials.resolve(
        teacher, workspace_id, {"source": "workspace", "provider": "openrouter", "model": "x/shared"}
    )
    assert resolved["source"] == "workspace" and resolved["api_key"] == "sk-or-academia"
    # Fuera de la academia (otro espacio) la clave compartida no se puede usar.
    learner = _user_id(config.SELF_LEARNER_EMAIL)
    outside = credentials.resolve(learner, workspace_id, {"source": "workspace", "provider": "openrouter", "model": "x/shared"})
    assert outside["source"] == "platform"


def test_students_cannot_manage_academy_ai(client, ai_env):
    token = login_and_csrf(client)
    assert client.get("/api/v1/admin/ai").status_code == 403
    response = client.put(
        "/api/v1/admin/ai/providers", json={"provider": "openrouter", "secret": "k"}, headers={"X-CSRF-Token": token}
    )
    assert response.status_code == 403


def test_regenerating_someone_elses_job_uses_the_requesters_credentials(client, ai_env):
    token = teacher_login(client)
    _put(client, token, provider="claude-code", secret="tok-profe", accept_personal=True)
    teacher = _user_id(config.TEACHER_EMAIL)
    admin = _user_id(config.ADMIN_EMAIL)
    store.create_job(
        job_id="job-ajeno", owner_id=teacher, title="Unidad", source_names=[],
        provider="claude-code", model="", languages=["es"],
        job_config={"ai": {"source": "user", "provider": "claude-code", "model": "default"}},
    )
    assert pipeline._settings("job-ajeno")["api_key"] == "tok-profe"
    # Otra persona (p. ej. la administración) regenera: nunca con la suscripción del autor.
    other = pipeline._settings("job-ajeno", actor_id=admin)
    assert other["source"] == "platform"
    assert other.get("api_key") != "tok-profe"


def test_jobs_keep_the_model_chosen_in_the_studio(client, ai_env):
    token = self_learner_login(client)
    _put(client, token, provider="openrouter", secret="sk-or-333333", models=_models("a/one", "b/two"))
    choice = {"source": "user", "provider": "openrouter", "model": "b/two"}
    response = client.post(
        "/api/v1/authoring/jobs",
        data={"title": "Unidad", "languages": ["es"], "ai": json.dumps(choice)},
        files={"files": ("apuntes.txt", b"Texto de prueba del documento.", "text/plain")},
        headers={"X-CSRF-Token": token},
    )
    assert response.status_code == 202, response.text
    job = store.get_job(response.json()["id"], with_log=False)
    assert job["provider"] == "openrouter" and job["model"] == "b/two"
    assert job["config"]["ai"] == choice
    assert pipeline._settings(job["id"])["model"] == "b/two"


def test_rotating_the_secret_makes_stored_credentials_unusable(client, ai_env, monkeypatch):
    token = self_learner_login(client)
    _put(client, token, provider="openrouter", secret="sk-or-123456", models=_models("anthropic/claude-sonnet-5.5"))
    uid = _user_id(config.SELF_LEARNER_EMAIL)
    monkeypatch.setattr(config, "SECRET_KEY", "otro-secreto")
    assert credentials.resolve(uid)["source"] == "platform"
    view = _provider(credentials.public(uid), "openrouter")["config"]
    assert view["ready"] is False and view["key_readable"] is False


def _store_chatgpt(uid: int, expires_at: float) -> None:
    creds = {"client_id": "c", "access_token": "at-old", "refresh_token": "rt-1", "expires_at": expires_at, "account": "a@b"}
    credentials.store_secret("user", uid, "chatgpt", json.dumps(creds), actor_id=uid, accept_personal=True)
    credentials.save_provider("user", uid, "chatgpt", actor_id=uid, models=_models("gpt-6.1-sol"))


def test_chatgpt_token_is_refreshed_once_and_rotated(client, ai_env, monkeypatch):
    self_learner_login(client)
    uid = _user_id(config.SELF_LEARNER_EMAIL)
    _store_chatgpt(uid, time.time() + 30)  # caduca enseguida
    calls = []

    def fake_refresh(creds):
        calls.append(creds["refresh_token"])
        return {**creds, "access_token": "at-new", "refresh_token": "rt-2", "expires_at": time.time() + 3600}

    monkeypatch.setattr(credentials, "_refresh_chatgpt", fake_refresh)
    resolved = credentials.resolve(uid, choice={"source": "user", "provider": "chatgpt", "model": "gpt-6.1-sol"})
    assert resolved["provider"] == "chatgpt" and resolved["api_key"] == "at-new"
    # El token de refresco rotado queda guardado: la siguiente vez ya no se renueva.
    assert credentials.chatgpt_access_token(uid) == "at-new"
    assert calls == ["rt-1"]
    stored = json.loads(credentials.secret_for("user", uid, "chatgpt"))
    assert stored["refresh_token"] == "rt-2"


def test_revoked_chatgpt_session_asks_to_link_again(client, ai_env, monkeypatch):
    from nas.adk.models.errors import LlmAuthError

    self_learner_login(client)
    uid = _user_id(config.SELF_LEARNER_EMAIL)
    _store_chatgpt(uid, time.time() - 10)

    def revoked(creds):
        raise LlmAuthError("refresh_token_reused")

    monkeypatch.setattr(credentials, "_refresh_chatgpt", revoked)
    assert credentials.chatgpt_access_token(uid) is None
    assert credentials.resolve(uid, choice={"source": "user", "provider": "chatgpt", "model": "gpt-6.1-sol"})["source"] == "platform"
    assert _provider(credentials.public(uid), "chatgpt")["config"]["key_configured"] is False


def test_model_catalog_extraction():
    from webapp.authoring import catalog

    assert catalog.extract_models({"data": [{"id": "b"}, {"id": "a/x", "name": "A X"}, {"id": "b"}]}) == [
        {"id": "a/x", "label": "A X"},
        {"id": "b", "label": "b"},
    ]
    assert catalog.extract_models({"models": [{"slug": "gpt-6", "display_name": "GPT-6"}]}) == [
        {"id": "gpt-6", "label": "GPT-6"}
    ]
    assert catalog.extract_models(None) == []


def test_link_sessions_belong_to_their_owner(client, ai_env):
    import asyncio

    from webapp.authoring import links

    async def scenario():
        link_id, url = await links.start_chatgpt(1, None)
        assert url.startswith("https://auth.openai.com/api/accounts/authorize?")
        with pytest.raises(links.LinkError) as other:
            await links.finish_chatgpt(link_id, 2, "http://127.0.0.1:1455/auth/callback?code=x")
        assert other.value.status == 404
        # Sigue disponible para su dueño (no se consumió con el intento ajeno).
        await links.cancel(link_id, 1)
        with pytest.raises(links.LinkError):
            await links.finish_chatgpt(link_id, 1, "http://127.0.0.1:1455/auth/callback?code=x")

    asyncio.run(scenario())
    # El identificador de la instalación es estable.
    assert links.chatgpt_host_id() == links.chatgpt_host_id()


def test_model_catalog_endpoint_for_a_saved_provider(client, ai_env):
    token = self_learner_login(client)
    _put(client, token, provider="deepseek", secret="sk-ds-444444", models=_models("deepseek-chat"))
    response = client.post("/api/v1/account/ai/providers/deepseek/models", headers={"X-CSRF-Token": token})
    assert response.status_code == 200 and response.json()["models"]
