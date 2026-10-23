import { describe, expect, it } from "vitest";
import {
  billedInputTokens,
  cacheBustCauses,
  formatCacheHitRate,
  formatPrefixReuse,
  parseCacheMeter,
} from "./cache_meter";

const base = {
  schema: "simplicio.cache-meter/v1",
  status: "measured",
  requests: 1,
  session_hit_rate: 0.99,
  tolerance_tokens: 16,
  ttl_secs: 300,
  busts: [],
  per_request: [
    {
      index: 0,
      model: "claude",
      input: 10,
      read: 990,
      write: 0,
      request_share: 0.99,
      cumulative_share: 0.99,
      prefix_reuse: 0.99,
    },
  ],
};

describe("cache meter display rules", () => {
  it.each([
    [0.49, 100, "49%"],
    [0.991, 100, "99%"],
    [0.995, 100, "99.5%"],
    [0.9995, 100, "99.95%"],
    [1, 100, "100%"],
  ])("formats %s as %s", (rate, billed, expected) => {
    expect(formatCacheHitRate(rate, billed)).toBe(expected);
  });

  it("hides the rate before any input is billed", () => {
    expect(formatCacheHitRate(0, 0)).toBeNull();
    expect(formatCacheHitRate(0.99, 0)).toBeNull();
    expect(formatCacheHitRate(null, 100)).toBeNull();
  });

  it("formats prefix reuse with the same rounding contract", () => {
    expect(formatPrefixReuse(0.995)).toBe("99.5%");
    expect(formatPrefixReuse(null)).toBeNull();
  });

  it("labels every attributed cause", () => {
    expect(cacheBustCauses({ request_index: 1, expected_read: 10, actual_read: 1, attribution: ["ttl_gap", "unknown"] }))
      .toBe("intervalo TTL, desconhecida");
  });
});

describe("cache meter parser", () => {
  it("accepts a measured receipt and sums billed input", () => {
    const receipt = parseCacheMeter(base);
    expect(receipt.status).toBe("measured");
    expect(billedInputTokens(receipt)).toBe(1000);
    expect(formatCacheHitRate(receipt.session_hit_rate, billedInputTokens(receipt))).toBe("99%");
  });

  it("accepts an unmeasured receipt without a rate", () => {
    const receipt = parseCacheMeter({ ...base, status: "unmeasured", session_hit_rate: null, requests: 0, per_request: [] });
    expect(receipt.session_hit_rate).toBeNull();
  });

  it("rejects a fabricated or inconsistent receipt", () => {
    expect(() => parseCacheMeter({ ...base, session_hit_rate: 1.2 })).toThrow("cache_meter_invalid");
    expect(() => parseCacheMeter({ ...base, requests: 2 })).toThrow("cache_meter_invalid");
    expect(() => parseCacheMeter({ ...base, status: "unmeasured" })).toThrow("cache_meter_invalid");
    expect(() => parseCacheMeter({ ...base, busts: [{ request_index: 0, expected_read: 1, actual_read: 0, attribution: ["invented"] }] }))
      .toThrow("cache_meter_invalid");
  });
});
