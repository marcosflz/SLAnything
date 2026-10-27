import { NextResponse, type NextRequest } from "next/server";

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ lang: string }> }
) {
  const { lang } = await context.params;
  const target = lang === "en" ? "en" : "es";
  const rawNext = request.nextUrl.searchParams.get("next") ?? "/";
  const next =
    rawNext.startsWith("/") && !rawNext.startsWith("//") ? rawNext : "/";

  // Redirección relativa: conserva el origen real (127.0.0.1 o localhost) y,
  // por tanto, la cookie de idioma que acabamos de escribir.
  const response = new NextResponse(null, {
    status: 303,
    headers: { Location: next },
  });
  response.cookies.set("aula_lang", target, {
    path: "/",
    maxAge: 365 * 86400,
    sameSite: "lax",
    httpOnly: false,
  });
  return response;
}
