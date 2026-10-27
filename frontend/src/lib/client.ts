export class ApiClientError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  let data: unknown = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const detail =
      typeof (data as { detail?: unknown })?.detail === "string"
        ? (data as { detail: string }).detail
        : `Error ${response.status}`;
    throw new ApiClientError(response.status, detail);
  }
  return data as T;
}

export async function apiGetClient<T>(path: string): Promise<T> {
  const response = await fetch(path, { cache: "no-store" });
  return parseResponse<T>(response);
}

async function apiSend<T>(
  path: string,
  method: string,
  body?: unknown,
  csrf?: string
): Promise<T> {
  const response = await fetch(path, {
    method,
    headers: {
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      ...(csrf ? { "X-CSRF-Token": csrf } : {}),
    },
    body: body !== undefined ? JSON.stringify(body ?? {}) : undefined,
  });
  return parseResponse<T>(response);
}

export async function apiPost<T>(
  path: string,
  body: unknown,
  csrf?: string
): Promise<T> {
  return apiSend<T>(path, "POST", body, csrf);
}

export async function apiPut<T>(
  path: string,
  body: unknown,
  csrf?: string
): Promise<T> {
  return apiSend<T>(path, "PUT", body, csrf);
}

export async function apiDelete<T>(path: string, csrf?: string): Promise<T> {
  return apiSend<T>(path, "DELETE", undefined, csrf);
}

export async function apiPostForm<T>(path: string, body: unknown): Promise<T> {
  return apiPost<T>(path, body);
}

export async function apiUpload<T>(
  path: string,
  body: FormData,
  csrf?: string
): Promise<T> {
  const response = await fetch(path, {
    method: "POST",
    headers: csrf ? { "X-CSRF-Token": csrf } : undefined,
    body,
  });
  return parseResponse<T>(response);
}
