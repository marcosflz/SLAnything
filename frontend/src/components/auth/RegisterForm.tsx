"use client";

import { Building2, KeyRound, User as UserIcon } from "lucide-react";
import { useState, type FormEvent } from "react";

import { Icon } from "@/components/ui";
import { ApiClientError, apiPost } from "@/lib/client";
import { pick, t } from "@/lib/messages";
import type { Lang } from "@/lib/types";
import { cn } from "@/lib/utils";

type RegisterResponse = {
  ok: boolean;
  next?: string;
};

export type AccountType = "individual" | "academy" | "join";

const TYPES: Array<{
  value: AccountType;
  icon: typeof UserIcon;
  title: [string, string];
  text: [string, string];
}> = [
  {
    value: "individual",
    icon: UserIcon,
    title: ["Cuenta individual", "Individual account"],
    text: ["Aprendo por mi cuenta y creo mis propias unidades.", "I learn on my own and create my own units."],
  },
  {
    value: "academy",
    icon: Building2,
    title: ["Academia", "Academy"],
    text: ["Enseño a un grupo: profesorado, alumnado y analítica.", "I teach a group: teachers, students and analytics."],
  },
  {
    value: "join",
    icon: KeyRound,
    title: ["Código de clase", "Class code"],
    text: ["Soy alumno y mi profesor me ha dado un código.", "I'm a student and my teacher gave me a code."],
  },
];

/**
 * Alta de cuenta (ADR-021): cuenta individual, academia o unirse a una clase.
 * Con `invite` (enlace de invitación) no se elige tipo: la cuenta entra en la
 * academia con el rol de la invitación y no recibe espacio personal.
 */
export function RegisterForm({
  lang,
  next,
  initialType = "individual",
  invite,
  inviteLabel,
}: {
  lang: Lang;
  next: string;
  initialType?: AccountType;
  invite?: string;
  inviteLabel?: string;
}) {
  const [account, setAccount] = useState<AccountType>(initialType);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [academyName, setAcademyName] = useState("");
  const [joinCode, setJoinCode] = useState("");
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
        account,
        academy_name: account === "academy" ? academyName : null,
        join_code: account === "join" ? joinCode : null,
        invite: invite ?? null,
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

        {invite ? (
          <div className="flash flash-success" role="status">
            <Icon name="users" /> <span>{inviteLabel}</span>
          </div>
        ) : (
          <fieldset className="m-0 grid gap-2 border-0 p-0">
            <legend className="mb-2 text-sm font-medium">
              {pick(lang, "¿Cómo vas a usar SLAnything?", "How will you use SLAnything?")}
            </legend>
            {TYPES.map((type) => {
              const selected = account === type.value;
              return (
                <label
                  key={type.value}
                  className={cn(
                    "flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition",
                    selected ? "border-primary bg-primary-soft" : "border-border hover:border-border-strong"
                  )}
                >
                  <input
                    type="radio"
                    name="account"
                    value={type.value}
                    checked={selected}
                    onChange={() => setAccount(type.value)}
                    className="sr-only"
                  />
                  <type.icon
                    className={cn("mt-0.5 size-4 shrink-0", selected ? "text-primary" : "text-muted-foreground")}
                    aria-hidden="true"
                  />
                  <span className="min-w-0">
                    <span className="block text-sm font-medium">{pick(lang, ...type.title)}</span>
                    <span className="block text-xs text-muted-foreground">{pick(lang, ...type.text)}</span>
                  </span>
                </label>
              );
            })}
          </fieldset>
        )}

        {!invite && account === "academy" ? (
          <div className="field">
            <label htmlFor="academy_name">{pick(lang, "Nombre de la academia", "Academy name")}</label>
            <input
              id="academy_name"
              type="text"
              required
              minLength={2}
              maxLength={80}
              value={academyName}
              onChange={(event) => setAcademyName(event.target.value)}
              placeholder={pick(lang, "Por ejemplo, IES Cervantes · 2º Bachillerato", "For example, Riverside High · Year 12")}
            />
          </div>
        ) : null}

        {!invite && account === "join" ? (
          <div className="field">
            <label htmlFor="join_code">{pick(lang, "Código de clase", "Class code")}</label>
            <input
              id="join_code"
              type="text"
              required
              minLength={4}
              maxLength={16}
              autoComplete="off"
              value={joinCode}
              onChange={(event) => setJoinCode(event.target.value.toUpperCase())}
              placeholder="ABCD2345"
            />
          </div>
        ) : null}

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
          <Icon name="arrow-right" />{" "}
          {invite
            ? pick(lang, "Crear cuenta y unirme", "Create account and join")
            : account === "academy"
              ? pick(lang, "Crear mi academia", "Create my academy")
              : account === "join"
                ? pick(lang, "Crear cuenta y unirme", "Create account and join")
                : t(lang, "Crear mi cuenta")}
        </button>
      </form>
    </>
  );
}
