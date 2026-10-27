"use client";

import { useState, type FormEvent } from "react";

import { Icon } from "@/components/ui";
import { ApiClientError, apiPost } from "@/lib/client";
import { t } from "@/lib/messages";
import type { Lang } from "@/lib/types";

type LoginResponse = {
  ok: boolean;
  next?: string;
};

export function LoginForm({ lang, next }: { lang: Lang; next: string }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setBusy(true);

    try {
      const data = await apiPost<LoginResponse>("/api/v1/auth/login", {
        email,
        password,
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
          <label htmlFor="email">{t(lang, "Correo electrónico")}</label>
          <input
            id="email"
            type="email"
            name="email"
            autoComplete="email"
            required
            placeholder="you@example.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </div>
        <div className="field">
          <label htmlFor="password">{t(lang, "Contraseña")}</label>
          <input
            id="password"
            type="password"
            name="password"
            autoComplete="current-password"
            required
            placeholder="••••••••"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>
        <button
          className="btn btn-primary btn-lg btn-block"
          type="submit"
          disabled={busy}
        >
          <Icon name="lock" /> {t(lang, "Entrar al aula")}
        </button>
      </form>
    </>
  );
}
