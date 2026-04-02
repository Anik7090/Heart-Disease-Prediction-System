import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function encodeUserId(userId: string): string {
  // Simple reversible encoding using base64 + salt
  const salt = "stream_room_2024"; // Add a salt for security
  const encoded = btoa(userId + salt);
  // Replace URL-unsafe characters
  return encoded.replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
}

export function decodeUserId(encodedId: string): string | null {
  try {
    // Restore URL-unsafe characters
    const restored = encodedId.replace(/-/g, "+").replace(/_/g, "/");
    // Add padding if needed
    const padded = restored + "=".repeat((4 - (restored.length % 4)) % 4);
    const decoded = atob(padded);
    const salt = "stream_room_2024";

    // Remove salt and return userId
    if (decoded.endsWith(salt)) {
      return decoded.slice(0, -salt.length);
    }
    return null;
  } catch (error) {
    console.log(error);
    return null;
  }
}

// In-memory token storage (use Redis or DB in production)
export const verificationTokens = new Map<
  string,
  {
    userId: string;
    createdAt: Date;
    originalUserId: string;
  }
>();
