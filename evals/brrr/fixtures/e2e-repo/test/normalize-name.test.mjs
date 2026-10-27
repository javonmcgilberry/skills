import assert from "node:assert/strict";
import test from "node:test";
import { normalizeName } from "../src/normalize-name.mjs";

test("normalizes surrounding and repeated whitespace", () => {
  assert.equal(normalizeName("  Ada   Lovelace  "), "Ada Lovelace");
});
