/**
 * Token Storage
 *
 * Handles storing and retrieving authentication tokens
 * using localStorage.
 */

const TOKEN_KEY = "auth_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const EXPIRY_KEY = `${TOKEN_KEY}_expiry`;

export interface TokenData {
  accessToken: string;
  refreshToken?: string;
  expiresAt?: number;
}

class TokenStorage {
  private tokenKey: string;
  private refreshTokenKey: string;

  constructor(
    tokenKey: string = TOKEN_KEY,
    refreshTokenKey: string = REFRESH_TOKEN_KEY
  ) {
    this.tokenKey = tokenKey;
    this.refreshTokenKey = refreshTokenKey;
  }

  /**
   * Get the stored access token.
   */
  getAccessToken(): string | null {
    if (typeof window === "undefined") {
      return null;
    }

    return localStorage.getItem(this.tokenKey);
  }

  /**
   * Store an access token.
   */
  setAccessToken(token: string): void {
    if (typeof window === "undefined") {
      return;
    }

    localStorage.setItem(this.tokenKey, token);
  }

  /**
   * Get the stored refresh token.
   */
  getRefreshToken(): string | null {
    if (typeof window === "undefined") {
      return null;
    }

    return localStorage.getItem(this.refreshTokenKey);
  }

  /**
   * Store a refresh token.
   */
  setRefreshToken(token: string): void {
    if (typeof window === "undefined") {
      return;
    }

    localStorage.setItem(this.refreshTokenKey, token);
  }

  /**
   * Store access token, refresh token,
   * and optionally the expiry time.
   */
  setTokens(
    accessToken: string,
    refreshToken: string,
    expiresIn?: number
  ): void {
    this.setAccessToken(accessToken);
    this.setRefreshToken(refreshToken);

    if (expiresIn !== undefined) {
      this.setExpiry(expiresIn);
    }
  }

  /**
   * Get both stored tokens.
   */
  getTokens(): TokenData | null {
    const accessToken = this.getAccessToken();
    const refreshToken = this.getRefreshToken();

    if (!accessToken) {
      return null;
    }

    return {
      accessToken,
      refreshToken: refreshToken || undefined,
      expiresAt: this.getExpiry() || undefined,
    };
  }

  /**
   * Remove access and refresh tokens.
   */
  remove(): void {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.removeItem(this.tokenKey);
  localStorage.removeItem(this.refreshTokenKey);
  localStorage.removeItem(EXPIRY_KEY);
}

  /**
   * Check whether an access token exists.
   */
  has(): boolean {
    return this.getAccessToken() !== null;
  }

  /**
   * Get token expiry timestamp.
   */
  getExpiry(): number | null {
    if (typeof window === "undefined") {
      return null;
    }

    const expiry = localStorage.getItem(EXPIRY_KEY);

    return expiry ? parseInt(expiry, 10) : null;
  }

  /**
   * Store token expiry.
   *
   * @param expiresIn Lifetime in seconds.
   */
  setExpiry(expiresIn: number): void {
    if (typeof window ==="undefined") {
      return;
    }

    const expiry = Date.now() + expiresIn * 1000;

    localStorage.setItem(EXPIRY_KEY, expiry.toString());
  }

  /**
   * Determine whether the access token has expired.
   */
  isExpired(): boolean {
    const expiry = this.getExpiry();

    if (!expiry) {
      return false;
    }

    return Date.now() >= expiry;
  }

  /**
   * Clear all authentication data.
   */
  clear(): void {
    this.remove();

    if (typeof window === "undefined") {
      return;
    }

    localStorage.removeItem(EXPIRY_KEY);
  }
}

/**
 * Singleton instance.
 */
export const tokenStorage = new TokenStorage();

/**
 * Default export.
 */
export default tokenStorage;