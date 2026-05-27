// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from "vitest";

// vitest 2 + jsdom 25 + Node 26 doesn't auto-expose localStorage. Polyfill it.
function memoryStorage() {
  const store = new Map();
  return {
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => store.set(k, String(v)),
    removeItem: (k) => store.delete(k),
    clear: () => store.clear(),
  };
}
vi.stubGlobal("localStorage", memoryStorage());

vi.mock("../api/client", () => {
  const post = vi.fn();
  const get = vi.fn();
  return {
    default: { post, get },
    API_BASE_URL: "http://test",
    configureClient: vi.fn(),
  };
});

import client from "../api/client";
import { authState, isAuthenticated, login, logout } from "../api/auth";

describe("auth store", () => {
  beforeEach(() => {
    authState.token = null;
    authState.user = null;
    localStorage.clear();
    client.post.mockReset();
    client.get.mockReset();
  });

  it("starts unauthenticated", () => {
    expect(isAuthenticated()).toBe(false);
    expect(authState.token).toBeNull();
  });

  it("login persists token and user", async () => {
    client.post.mockResolvedValue({ data: { access_token: "tok-123" } });
    client.get.mockResolvedValue({
      data: { id: 1, username: "admin", is_admin: true },
    });

    await login("admin", "admin");

    expect(authState.token).toBe("tok-123");
    expect(authState.user).toEqual({ id: 1, username: "admin", is_admin: true });
    expect(localStorage.getItem("pi-nvr-token")).toBe("tok-123");
    expect(isAuthenticated()).toBe(true);
  });

  it("logout clears state and storage", async () => {
    client.post.mockResolvedValue({ data: { access_token: "tok-xyz" } });
    client.get.mockResolvedValue({
      data: { id: 1, username: "admin", is_admin: true },
    });
    await login("admin", "admin");

    logout();
    expect(authState.token).toBeNull();
    expect(authState.user).toBeNull();
    expect(localStorage.getItem("pi-nvr-token")).toBeNull();
    expect(isAuthenticated()).toBe(false);
  });
});
