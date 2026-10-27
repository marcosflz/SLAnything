import { NextResponse, type NextRequest } from "next/server";

/**
 * Compatibilidad con el contrato `?lang=es|en` de la etapa Jinja.
 * Convierte el parámetro en la ruta `/idioma/{lang}`, que es la que escribe la
 * cookie, y conserva el resto de la URL en `next`.
 */
export default function proxy(request: NextRequest) {
  const lang = request.nextUrl.searchParams.get("lang");
  if (lang !== "es" && lang !== "en") {
    return NextResponse.next();
  }

  const nextUrl = request.nextUrl.clone();
  nextUrl.searchParams.delete("lang");
  const target = `${nextUrl.pathname}${nextUrl.search}`;
  const host = request.headers.get("host") ?? request.nextUrl.host;
  const protocol =
    request.headers.get("x-forwarded-proto") ??
    request.nextUrl.protocol.replace(":", "");
  const destination = new URL(
    `/idioma/${lang}?next=${encodeURIComponent(target)}`,
    `${protocol}://${host}`
  );

  return NextResponse.redirect(destination, 307);
}

export const config = {
  matcher: ["/((?!api/|_next/|static/|idioma/|favicon.ico).*)"],
};
