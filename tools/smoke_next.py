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
    ("/", "SLAnything"),
    ("/cursos", "Construye un LLM desde cero"),
    ("/cursos/llm-desde-cero", "Acceso abierto"),
    ("/entrar", "Entrar"),
    ("/registro", "Crear"),
]

AUTHENTICATED_PAGES = [
    ("/", "SLAnything"),
    ("/cursos", "Construye un LLM desde cero"),
    ("/cursos/llm-desde-cero", "Programa del curso"),
    ("/curso", "Programa del curso"),
    ("/leccion/que-es-un-llm", "¿Qué es un LLM?"),
    ("/quiz/quiz-capitulo-1", "Autoevaluación"),
    ("/progreso", "Mi progreso"),
    ("/glosario", "Glosario"),
    ("/recursos", "Recursos"),
    ("/buscar?q=token", "token"),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:3000")
    parser.add_argument("--email", default="demo@aulallm.local")
    parser.add_argument("--password", default="demo1234")
    args = parser.parse_args()

    with httpx.Client(base_url=args.base, timeout=20, follow_redirects=True) as client:
        health = client.get("/salud")
        print(f"/salud -> {health.status_code}")
        if health.status_code != 200:
            print("El backend no responde a través de Next.", file=sys.stderr)
            return 1

        failures = 0
        for path, marker in PUBLIC_PAGES:
            response = client.get(path)
            ok = response.status_code == 200 and marker in response.text
            print(f"{path} (anónimo) -> {response.status_code} {'ok' if ok else 'FALLA'}")
            if not ok:
                failures += 1

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

        for path, marker in AUTHENTICATED_PAGES:
            response = client.get(path)
            ok = response.status_code == 200 and marker in response.text
            print(f"{path} -> {response.status_code} {'ok' if ok else 'FALLA'}")
            if not ok:
                failures += 1

        switch = client.get("/idioma/en?next=/curso", follow_redirects=False)
        english = client.get("/curso")
        ok = (
            switch.status_code == 303
            and switch.headers.get("location") == "/curso"
            and client.cookies.get("aula_lang") == "en"
            and english.status_code == 200
            and "Course syllabus" in english.text
        )
        print(f"/idioma/en -> {switch.status_code} {'ok' if ok else 'FALLA'}")
        if not ok:
            failures += 1

        legacy = client.get("/curso?lang=en", follow_redirects=False)
        ok = (
            legacy.status_code == 307
            and "/idioma/en" in legacy.headers.get("location", "")
        )
        print(f"/curso?lang=en -> {legacy.status_code} {'ok' if ok else 'FALLA'}")
        if not ok:
            failures += 1
        client.get("/idioma/es?next=/curso", follow_redirects=False)

        teacher = httpx.Client(base_url=args.base, timeout=20, follow_redirects=True)
        try:
            logged = teacher.post(
                "/api/v1/auth/login",
                json={
                    "email": "profe@aulallm.local",
                    "password": "profe1234",
                    "next": "/profesor",
                },
            )
            page = teacher.get("/profesor")
            ok = logged.status_code == 200 and page.status_code == 200
            print(f"/profesor -> {page.status_code} {'ok' if ok else 'FALLA'}")
            if not ok:
                failures += 1
        finally:
            teacher.close()

    if failures:
        print(f"\n{failures} comprobaciones fallidas.", file=sys.stderr)
        return 1
    print("\nSmoke test correcto.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
