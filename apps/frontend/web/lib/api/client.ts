// apps/frontend/web/lib/api/client.ts

import { tokenStorage } from "@/services/storage/token";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000/api/v1";

/* -------------------------------------------------------------------------- */
/* Types                                                                      */
/* -------------------------------------------------------------------------- */

export interface ApiErrorResponse {
  error?: string;
  message?: string;
  detail?: string;
  details?: Record<string, unknown> | null;
}

export class ApiError extends Error {
  status: number;
  code?: string;
  details?: Record<string, unknown> | null;

  constructor(
    message: string,
    status: number,
    code?: string,
    details?: Record<string, unknown> | null
  ) {
    super(
      typeof message === "string"
        ? message
        : JSON.stringify(message)
    );

    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

/* -------------------------------------------------------------------------- */
/* API Client                                                                 */
/* -------------------------------------------------------------------------- */

class ApiClient {
  /**
   * In-flight refresh, shared so that concurrent 401s trigger only one
   * refresh request instead of a stampede.
   */
  private refreshPromise: Promise<string | null> | null = null;

  /**
   * Exchange the stored refresh token for a new access token.
   *
   * Returns the new access token, or null when refresh is not possible
   * (no refresh token stored, or the refresh call itself was rejected).
   */
  private async performRefresh(): Promise<string | null> {
    const refreshToken = tokenStorage.getRefreshToken();

    if (!refreshToken) {
      return null;
    }

    try {
      // Deliberately uses bare `fetch`, not `this.request`, so that a
      // failing refresh cannot recurse back into the 401 handler.
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        tokenStorage.clear();
        return null;
      }

      const data = (await response.json()) as {
        access_token: string;
        refresh_token?: string | null;
        expires_in?: number;
      };

      tokenStorage.setAccessToken(data.access_token);

      if (data.refresh_token) {
        tokenStorage.setRefreshToken(data.refresh_token);
      }

      if (typeof data.expires_in === "number") {
        tokenStorage.setExpiry(data.expires_in);
      }

      return data.access_token;
    } catch {
      tokenStorage.clear();
      return null;
    }
  }

  /**
   * Refresh the access token, collapsing concurrent callers onto one request.
   */
  private refreshAccessToken(): Promise<string | null> {
    if (!this.refreshPromise) {
      this.refreshPromise = this.performRefresh().finally(() => {
        this.refreshPromise = null;
      });
    }

    return this.refreshPromise;
  }

  /**
   * Perform an HTTP request against the API.
   *
   * On a 401 the client attempts a single silent token refresh and retries
   * the original request once. This previously did not exist, so an expired
   * access token surfaced as a hard failure even though a valid refresh
   * token was sitting in storage.
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await this.send(endpoint, options);

    if (response.status === 401 && !endpoint.startsWith("/auth/")) {
      const newToken = await this.refreshAccessToken();

      if (newToken) {
        // Retry once with the refreshed credential.
        const retry = await this.send(endpoint, options);

        return this.parse<T>(retry);
      }
    }

    return this.parse<T>(response);
  }

  /**
   * Issue a single HTTP call, attaching the current access token.
   */
  private async send(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const token = tokenStorage.getAccessToken();

    const headers = new Headers(options.headers);

    /*
     * Only set Content-Type when a request actually has a body.
     */
    if (options.body !== undefined && options.body !== null) {
      if (!headers.has("Content-Type")) {
        headers.set("Content-Type", "application/json");
      }
    }

    /*
     * Attach the access token automatically when available.
     */
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    return fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
  }

  /**
   * Decode a response, throwing ApiError for non-2xx statuses.
   */
  private async parse<T>(response: Response): Promise<T> {
    /* ---------------------------------------------------------------------- */
    /* Successful responses                                                   */
    /* ---------------------------------------------------------------------- */

    if (response.ok) {
      /*
       * 204 No Content has no response body.
       */
      if (response.status === 204) {
        return undefined as T;
      }

      /*
       * Some successful endpoints may return an empty body.
       */
      const contentType = response.headers.get("content-type");

      if (!contentType || !contentType.includes("application/json")) {
        return undefined as T;
      }

      return response.json() as Promise<T>;
    }

    /* ---------------------------------------------------------------------- */
    /* Error responses                                                        */
    /* ---------------------------------------------------------------------- */

    let errorData: ApiErrorResponse = {};

    try {
      const contentType = response.headers.get("content-type");

      if (
        contentType &&
        contentType.includes("application/json")
      ) {
        errorData = await response.json();
      }
    } catch {
      // Ignore JSON parsing errors.
    }

    const rawMessage =
      errorData.message ??
      errorData.detail ??
      errorData.error;

    const message =
      typeof rawMessage === "string"
        ? rawMessage
        : rawMessage !== undefined
          ? JSON.stringify(rawMessage)
          : `Request failed with status ${response.status}.`;

    throw new ApiError(
      message,
      response.status,
      errorData.error,
      errorData.details
    );
  }

  /* ------------------------------------------------------------------------ */
  /* GET                                                                      */
  /* ------------------------------------------------------------------------ */

  get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: "GET",
    });
  }

  /* ------------------------------------------------------------------------ */
  /* POST                                                                     */
  /* ------------------------------------------------------------------------ */

  post<T>(
    endpoint: string,
    body?: unknown
  ): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      ...(body !== undefined
        ? {
            body: JSON.stringify(body),
          }
        : {}),
    });
  }

  /* ------------------------------------------------------------------------ */
  /* PUT                                                                      */
  /* ------------------------------------------------------------------------ */

  put<T>(
    endpoint: string,
    body?: unknown
  ): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PUT",
      ...(body !== undefined
        ? {
            body: JSON.stringify(body),
          }
        : {}),
    });
  }

  /* ------------------------------------------------------------------------ */
  /* PATCH                                                                    */
  /* ------------------------------------------------------------------------ */

  patch<T>(
    endpoint: string,
    body?: unknown
  ): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PATCH",
      ...(body !== undefined
        ? {
            body: JSON.stringify(body),
          }
        : {}),
    });
  }

  /* ------------------------------------------------------------------------ */
  /* DELETE                                                                   */
  /* ------------------------------------------------------------------------ */

  delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: "DELETE",
    });
  }
}

/* -------------------------------------------------------------------------- */
/* Export                                                                     */
/* -------------------------------------------------------------------------- */

export const apiClient = new ApiClient();