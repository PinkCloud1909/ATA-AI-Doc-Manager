/**
 * lib/api/auth.ts
 *
 * Backend auth flow:
 *  POST /api/v1/auth/register → MeResponse
 *  POST /api/v1/auth/login    → TokenResponse
 *  GET  /api/v1/auth/me        → MeResponse
 *
 * JWT stored via authToken.ts (localStorage + cookie).
 */

import apiClient from "./client";
import { setStoredAccessToken, clearStoredAccessToken } from "./authToken";
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  MeResponse,
} from "@/types/user";

export const authApi = {
  /** Login with username/password, store JWT, return token info. */
  login: async (username: string, password: string): Promise<TokenResponse> => {
    const payload: LoginRequest = { username: username.trim(), password };
    const { data } = await apiClient.post<TokenResponse>("/auth/login", payload);
    setStoredAccessToken(data.access_token, data.expires_in);
    return data;
  },

  /** Get current user profile (requires valid JWT). */
  me: async (): Promise<MeResponse> => {
    const { data } = await apiClient.get<MeResponse>("/auth/me");
    return data;
  },

  /** Register a new account. Returns profile directly (no auto-login). */
  register: async (username: string, password: string): Promise<MeResponse> => {
    const payload: RegisterRequest = { username: username.trim(), password };
    const { data } = await apiClient.post<MeResponse>("/auth/register", payload);
    return data;
  },

  /** Logout — clears stored JWT. */
  logout: async (): Promise<void> => {
    clearStoredAccessToken();
  },
};
