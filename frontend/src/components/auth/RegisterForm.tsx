"use client";

import { useState, type FormEvent } from "react";

import { Icon } from "@/components/ui";
import { ApiClientError, apiPost } from "@/lib/client";
import { t } from "@/lib/messages";
import type { Lang } from "@/lib/types";

type RegisterResponse = {
  ok: boolean;
  next?: string;
};

export function RegisterForm({ lang, next }: { lang: Lang; next: string }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setBusy(true);

    try {
      const data = await apiPost<RegisterResponse>("/api/v1/auth/register", {
        name,
        email,
        password,
        password2,
        next,
      });
      window.location.href = data.next || "/";
    } catch (caught) {
      setError(
        caught instanceof ApiClientError
          ? caught.message
          : t(lang, "Algo se ha roto")
      );
      setBusy(false);
    }
  }

  return (
    <>
      {error ? (
        <div className="flash flash-danger" role="alert">
          <Icon name="alert" /> <span>{error}</span>
        </div>
      ) : null}

      <form className="auth-form" onSubmit={handleSubmit} aria-busy={busy}>
        <input type="hidden" name="next" value={next} />
        <div className="field">
          <label htmlFor="name">{t(lang, "Nombre")}</label>
          <input
            id="name"
            type="text"
            name="name"
            autoComplete="name"
            required
            minLength={2}
            maxLength={80}
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder={t(lang, "Cómo quieres que te llamemos")}
          />
        </div>
        <div className="field">
          <label htmlFor="email">{t(lang, "Correo electrónico")}</label>
          <input
            id="email"
            type="email"
            name="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
          />
        </div>
        <div className="field">
          <label htmlFor="password">{t(lang, "Contraseña")}</label>
          <input
            id="password"
            type="password"
            name="password"
            autoComplete="new-password"
            required
            minLength={8}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder={t(lang, "Al menos 8 caracteres")}
          />
        </div>
        <div className="field">
          <label htmlFor="password2">{t(lang, "Repite la contraseña")}</label>
          <input
            id="password2"
            type="password"
            name="password2"
            autoComplete="new-password"
            required
            minLength={8}
            value={password2}
            onChange={(event) => setPassword2(event.target.value)}
            placeholder={t(lang, "Otra vez, para evitar erratas")}
          />
        </div>
        <button
          className="btn btn-primary btn-lg btn-block"
          type="submit"
          disabled={busy}
        >
          <Icon name="arrow-right" /> {t(lang, "Crear mi cuenta")}
        </button>
      </form>
    </>
  );
}
