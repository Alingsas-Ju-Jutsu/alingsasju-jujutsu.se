const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const script = fs.readFileSync(
  path.join(__dirname, "../assets/js/grading-times.js"),
  "utf8"
);

function render(dates, instant, kind = "grading") {
  const dateField = kind === "grading" ? "gradingDate" : "exceptionDate";
  const entries = dates.map((date) => ({ dataset: { [dateField]: date }, hidden: false }));
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
      querySelectorAll: (selector) => {
        const expected = kind === "grading"
          ? ".training-schedule__gradings"
          : ".training-schedule__exceptions";
        return selector === expected ? [section] : [];
      },
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

test("exceptions expire individually after their Swedish calendar date", () => {
  const page = render(["2026-10-22", "2026-10-25"], "2026-10-22T21:59:00Z", "exception");
  assert.deepEqual(page.entries.map((entry) => entry.hidden), [false, false]);
  page.setNow("2026-10-22T22:00:00Z");
  page.refresh();
  assert.deepEqual(page.entries.map((entry) => entry.hidden), [true, false]);
  assert.equal(page.section.hidden, false);
  page.setNow("2026-10-25T23:00:00Z");
  page.resume();
  assert.equal(page.section.hidden, true);
});

test("exceptions with invalid or missing dates stay visible", () => {
  const page = render(["2026-02-30", ""], "2027-01-01T00:00:00Z", "exception");
  assert.deepEqual(page.entries.map((entry) => entry.hidden), [false, false]);
  assert.equal(page.section.hidden, false);
  assert.equal(page.warnings.length, 1);
});

test("grading and exception sections are evaluated independently", () => {
  const grading = { dataset: { gradingDate: "2026-11-25" }, hidden: false };
  const exception = { dataset: { exceptionDate: "2026-10-22" }, hidden: false };
  const gradingSection = { hidden: false, querySelectorAll: () => [grading] };
  const exceptionSection = { hidden: false, querySelectorAll: () => [exception] };
  class Clock extends Date {
    constructor(...args) {
      super(...(args.length ? args : ["2026-11-06T12:00:00Z"]));
    }
  }
  vm.runInNewContext(script, {
    Date: Clock,
    Intl,
    console,
    document: {
      querySelectorAll: (selector) => selector === ".training-schedule__gradings"
        ? [gradingSection] : [exceptionSection],
      addEventListener: () => {},
    },
    window: { setInterval: () => {} },
  });
  assert.equal(gradingSection.hidden, false);
  assert.equal(grading.hidden, false);
  assert.equal(exception.hidden, true);
  assert.equal(exceptionSection.hidden, true);
});
