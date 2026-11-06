const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const script = fs.readFileSync(
  path.join(__dirname, "../assets/js/grading-times.js"),
  "utf8"
);

function render(dates, instant) {
  const entries = dates.map((date) => ({ dataset: { gradingDate: date }, hidden: false }));
  const section = {
    hidden: false,
    querySelectorAll: () => entries,
  };
  const warnings = [];
  let now = instant;
  let refresh;
  let onVisibilityChange;
  class Clock extends Date {
    constructor(...args) {
      super(...(args.length ? args : [now]));
    }
  }
  vm.runInNewContext(script, {
    Date: Clock,
    Intl,
    console: { warn: (message) => warnings.push(message) },
    document: {
      querySelectorAll: () => [section],
      addEventListener: (event, listener) => {
        assert.equal(event, "visibilitychange");
        onVisibilityChange = listener;
      },
    },
    window: {
      setInterval: (listener, delay) => {
        assert.equal(delay, 60000);
        refresh = listener;
      },
    },
  });
  return {
    entries, section, warnings,
    setNow: (value) => { now = value; },
    refresh: () => refresh(),
    resume: () => onVisibilityChange(),
  };
}

test("each grading remains visible through its date in Sweden", () => {
  const page = render(["2026-11-22", "2026-11-25"], "2026-11-22T22:59:00Z");
  assert.deepEqual(page.entries.map((entry) => entry.hidden), [false, false]);
  page.setNow("2026-11-22T23:00:00Z");
  page.refresh();
  assert.deepEqual(page.entries.map((entry) => entry.hidden), [true, false]);
  assert.equal(page.section.hidden, false);
  page.setNow("2026-11-25T23:00:00Z");
  page.resume();
  assert.equal(page.section.hidden, true);
});

test("uses Swedish summer time and retains entries without dates", () => {
  const page = render(["2026-06-22", ""], "2026-06-22T21:59:00Z");
  assert.equal(page.entries[0].hidden, false);
  page.setNow("2026-06-22T22:00:00Z");
  page.refresh();
  assert.equal(page.entries[0].hidden, true);
  assert.equal(page.entries[1].hidden, false);
  assert.equal(page.section.hidden, false);
});

test("invalid dates stay visible and produce a warning", () => {
  const page = render(["2026-02-30", "22 november"], "2027-01-01T00:00:00Z");
  page.refresh();
  assert.deepEqual(page.entries.map((entry) => entry.hidden), [false, false]);
  assert.equal(page.section.hidden, false);
  assert.equal(page.warnings.length, 2);
});
