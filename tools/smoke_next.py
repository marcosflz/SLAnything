"""Smoke test HTTP del frontend Next.js contra un FastAPI real.

Uso (con ambos servidores arrancados):

    uv run python tools/smoke_next.py
    uv run python tools/smoke_next.py --base http://127.0.0.1:3000
"""

from __future__ import annotations

import argparse
import sys

import httpx


PUBLIC_PAGES = [
    ("/", "Convierte cualquier material"),
    ("/cursos", "Elige qué quieres aprender"),
    ("/entrar", "Entrar"),
    ("/registro", "Crear cuenta"),
]

# Páginas comunes a cualquier perfil, con o sin cursos.
AUTHENTICATED_PAGES = [
    ("/", "SLAnything"),
    ("/cursos", "Elige qué quieres aprender"),
    ("/progreso", "Mi progreso"),
    ("/cuenta", "Mi cuenta"),
]

# Solo con AULA_SAMPLE_COURSES=1 (curso de ejemplo del repositorio).
SAMPLE_PAGES = [
    ("/cursos/llm-desde-cero", "Programa del curso"),
    ("/curso", "Programa del curso"),
    ("/leccion/que-es-un-llm", "¿Qué es un LLM?"),
    ("/quiz/quiz-capitulo-1", "Autoevaluación"),
    ("/glosario", "Glosario"),
    ("/recursos", "Recursos"),
    ("/buscar?q=token", "token"),
]

# (correo, contraseña, páginas que deben abrirse, páginas restringidas)
PROFILES = [
    ("profe@slanything.local", "profe1234", ["/estudio", "/profesor", "/analitica", "/admin"], ["/plataforma"]),
    ("autodidacta@slanything.local", "auto1234", ["/estudio"], ["/admin", "/plataforma"]),
    ("admin@slanything.local", "admin1234", ["/plataforma", "/plataforma/usuarios", "/plataforma/invitaciones", "/plataforma/ia"], []),
]

RESTRICTED_MARKER = "Acceso restringido"


def _check_profile(base: str, email: str, password: str, allowed: list[str], denied: list[str]) -> int:
    failures = 0
    with httpx.Client(base_url=base, timeout=20, follow_redirects=True) as client:
        logged = client.post("/api/v1/auth/login", json={"email": email, "password": password, "next": "/"})
        if logged.status_code != 200:
            print(f"login {email} -> {logged.status_code} FALLA")
            return 1
        for path in allowed:
            page = client.get(path)
            ok = page.status_code == 200 and RESTRICTED_MARKER not in page.text
            print(f"{email.split('@')[0]} {path} -> {page.status_code} {'ok' if ok else 'FALLA'}")
            failures += 0 if ok else 1
        if "/estudio" in allowed:
            # Quien crea unidades ve con qué proveedor genera y puede usar el suyo.
            studio_ok = "Generarás con" in client.get("/estudio").text
            account_ok = "Proveedor de IA" in client.get("/cuenta").text
            print(f"{email.split('@')[0]} proveedor de IA -> {'ok' if studio_ok and account_ok else 'FALLA'}")
            failures += 0 if studio_ok and account_ok else 1
        for path in denied:
            page = client.get(path)
            ok = page.status_code == 200 and RESTRICTED_MARKER in page.text
            print(f"{email.split('@')[0]} {path} (restringida) -> {'ok' if ok else 'FALLA'}")
            failures += 0 if ok else 1
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:3000")
    parser.add_argument("--email", default="alumno@slanything.local")
    parser.add_argument("--password", default="alumno1234")
    args = parser.parse_args()

    with httpx.Client(base_url=args.base, timeout=20, follow_redirects=True) as client:
        health = client.get("/salud")
        print(f"/salud -> {health.status_code}")
        if health.status_code != 200:
            print("El backend no responde a través de Next.", file=sys.stderr)
            return 1
        samples = bool(health.json().get("ejemplos"))
        print(f"cursos de ejemplo: {'activos' if samples else 'desactivados'}")
        signup_open = bool(client.get("/api/v1/public").json()["site"].get("signup_open"))
        print(f"registro: {'abierto' if signup_open else 'solo por invitación'}")

        failures = 0
        for path, marker in PUBLIC_PAGES:
            response = client.get(path)
            ok = response.status_code == 200 and marker in response.text
            print(f"{path} (anónimo) -> {response.status_code} {'ok' if ok else 'FALLA'}")
            if not ok:
                failures += 1

        register_page = client.get("/registro").text
        ok = ("Cuenta individual" in register_page) if signup_open else ("solo por invitación" in register_page)
        print(f"/registro según el modo -> {'ok' if ok else 'FALLA'}")
        failures += 0 if ok else 1

        login = client.post(
            "/api/v1/auth/login",
            json={"email": args.email, "password": args.password, "next": "/"},
        )
        print(f"login -> {login.status_code}")
        if login.status_code != 200:
            print(login.text, file=sys.stderr)
            return 1
        if "aula_session" not in client.cookies:
            print("No se recibió la cookie aula_session a través del rewrite.", file=sys.stderr)
            return 1

        pages = AUTHENTICATED_PAGES + (SAMPLE_PAGES if samples else [])
        for path, marker in pages:
            response = client.get(path)
            ok = response.status_code == 200 and marker in response.text
            print(f"{path} -> {response.status_code} {'ok' if ok else 'FALLA'}")
            if not ok:
                failures += 1

        # El alumnado no tiene proveedor de IA propio (ADR-024).
        account = client.get("/cuenta").text
        ok = "Proveedor de IA" not in account
        print(f"alumno /cuenta sin proveedor de IA -> {'ok' if ok else 'FALLA'}")
        failures += 0 if ok else 1
        # El alumnado solo consume: el Estudio está restringido.
        studio = client.get("/estudio")
        ok = studio.status_code == 200 and RESTRICTED_MARKER in studio.text
        print(f"alumno /estudio (restringida) -> {'ok' if ok else 'FALLA'}")
        failures += 0 if ok else 1

        target = "/curso" if samples else "/cursos"
        marker = "Course syllabus" if samples else "Choose what you want to learn"
        switch = client.get(f"/idioma/en?next={target}", follow_redirects=False)
        english = client.get(target)
        ok = (
            switch.status_code == 303
            and switch.headers.get("location") == target
            and client.cookies.get("aula_lang") == "en"
            and english.status_code == 200
            and marker in english.text
        )
        print(f"/idioma/en -> {switch.status_code} {'ok' if ok else 'FALLA'}")
        if not ok:
            failures += 1

        legacy = client.get("/cursos?lang=en", follow_redirects=False)
        ok = (
            legacy.status_code == 307
            and "/idioma/en" in legacy.headers.get("location", "")
        )
        print(f"/cursos?lang=en -> {legacy.status_code} {'ok' if ok else 'FALLA'}")
        if not ok:
            failures += 1
        client.get("/idioma/es?next=/cursos", follow_redirects=False)

    for email, password, allowed, denied in PROFILES:
        failures += _check_profile(args.base, email, password, allowed, denied)

    if failures:
        print(f"\n{failures} comprobaciones fallidas.", file=sys.stderr)
        return 1
    print("\nSmoke test correcto.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
