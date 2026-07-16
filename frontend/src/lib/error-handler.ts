// lib/error-handler.ts
// Centralized API error extraction helper

import axios from "axios";

interface ApiErrorData {
  detail?: string;
  code?: string;
  request_id?: string;
}

/**
 * Extract a human-readable error message from an API error.
 * Handles Axios errors with detail/code fields, generic Error objects,
 * and falls back to a provided default message.
 */
export function getApiErrorMessage(error: unknown, fallback = "An error occurred"): string {
  if (!axios.isAxiosError(error)) {
    return error instanceof Error ? error.message : fallback;
  }

  const status = error.response?.status;
  const data = error.response?.data as ApiErrorData | undefined;

  // Prefer the detail field from the backend
  if (typeof data?.detail === "string" && data.detail) {
    return data.detail;
  }

  // HTTP status-specific fallbacks
  switch (status) {
    case 401:
      return "Authentication required. Please log in again.";
    case 403:
      return "You do not have permission to perform this action.";
    case 404:
      return "The requested resource was not found.";
    case 409:
      return "This action conflicts with the current state. Please refresh and try again.";
    case 413:
      return "The uploaded file exceeds the maximum allowed size.";
    case 422:
      return "The submitted data failed validation. Please check your input.";
    case 500:
      return "An internal server error occurred. Please try again later.";
    case 502:
      return "An external service is unavailable. Please try again later.";
    case 503:
      return "The service is temporarily unavailable. Please try again later.";
    default:
      return error.message || fallback;
  }
}
