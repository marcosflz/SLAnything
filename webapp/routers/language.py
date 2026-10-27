"""Cambio de idioma mediante cookie y redirección segura."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from webapp.i18n import DEFAULT_LANG, LANG_COOKIE, SUPPORTED_LANGS, normalize_lang
from webapp.templating import redirect_target

router = APIRouter()


def _set_language(request: Request, lang: str) -> RedirectResponse:
    target = redirect_target(request)
    response = RedirectResponse(target, status_code=303)
    response.set_cookie(
        LANG_COOKIE,
        lang,
        max_age=365 * 86400,
        httponly=False,
        samesite="lax",
        path="/",
    )
    return response


@router.get("/idioma/{lang}")
def switch_language(lang: str, request: Request):
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    return _set_language(request, lang)


@router.get("/language/{lang}", include_in_schema=False)
def switch_language_alias(lang: str, request: Request):
    """Alias en inglés para enlaces y documentación."""
    return switch_language(normalize_lang(lang), request)
