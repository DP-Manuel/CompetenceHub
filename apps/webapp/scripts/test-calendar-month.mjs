import assert from "node:assert/strict";
import { test } from "node:test";
import { buildMonthLayout, berlinDay, monthKeys, calendarInstantLabel } from "./cal1_demo/calendar-month.mjs";

const event = (start, end, id = "demo-one") => ({
  id, starts_at: start, ends_at: end, title: "DEMO: Workshop", topic: { name: "Demo-Thema" },
});
const segments = layout => layout.weeks.flatMap(week => week.days.flatMap(day => day.segments));
const keys = (item, month) => segments(buildMonthLayout([item], month)).map(segment => segment.day);

const cases = [
  ["single day", "2026-11-28T09:00+01:00", "2026-11-28T17:18+01:00", "2026-11", ["2026-11-28"]],
  ["reported Nov28 17:18 to Nov29 17:18", "2026-11-28T17:18+01:00", "2026-11-29T17:18+01:00", "2026-11", ["2026-11-28", "2026-11-29"]],
  ["four days across weekend", "2026-11-27T10:00+01:00", "2026-11-30T16:00+01:00", "2026-11", ["2026-11-27", "2026-11-28", "2026-11-29", "2026-11-30"]],
  ["midnight excludes next day", "2026-11-28T17:18+01:00", "2026-11-29T00:00+01:00", "2026-11", ["2026-11-28"]],
  ["multiday midnight excludes third day", "2026-11-28T17:18+01:00", "2026-11-30T00:00+01:00", "2026-11", ["2026-11-28", "2026-11-29"]],
  ["one millisecond after midnight includes day", "2026-11-28T17:18+01:00", "2026-11-29T00:00:00.001+01:00", "2026-11", ["2026-11-28", "2026-11-29"]],
  ["start at midnight", "2026-11-28T00:00+01:00", "2026-11-28T01:00+01:00", "2026-11", ["2026-11-28"]],
  ["November side of month boundary", "2026-11-30T22:00+01:00", "2026-12-01T03:00+01:00", "2026-11", ["2026-11-30"]],
  ["December side of month boundary", "2026-11-30T22:00+01:00", "2026-12-01T03:00+01:00", "2026-12", ["2026-12-01"]],
  ["midnight next month not included", "2026-11-30T22:00+01:00", "2026-12-01T00:00+01:00", "2026-12", []],
  ["December side of year boundary", "2026-12-31T22:00+01:00", "2027-01-01T03:00+01:00", "2026-12", ["2026-12-31"]],
  ["January side of year boundary", "2026-12-31T22:00+01:00", "2027-01-01T03:00+01:00", "2027-01", ["2027-01-01"]],
  ["spring change two civil days", "2026-03-28T17:18+01:00", "2026-03-29T17:18+02:00", "2026-03", ["2026-03-28", "2026-03-29"]],
  ["23 hour day is one civil day", "2026-03-29T00:00+01:00", "2026-03-30T00:00+02:00", "2026-03", ["2026-03-29"]],
  ["autumn change two civil days", "2026-10-24T17:18+02:00", "2026-10-25T17:18+01:00", "2026-10", ["2026-10-24", "2026-10-25"]],
  ["25 hour day is one civil day", "2026-10-25T00:00+02:00", "2026-10-26T00:00+01:00", "2026-10", ["2026-10-25"]],
  ["repeated autumn clock hour", "2026-10-25T02:30+02:00", "2026-10-25T02:30+01:00", "2026-10", ["2026-10-25"]],
  ["UTC instant belongs to Berlin next day", "2026-11-28T23:30Z", "2026-11-29T01:00Z", "2026-11", ["2026-11-29"]],
  ["leap day", "2028-02-28T17:00+01:00", "2028-03-01T17:00+01:00", "2028-02", ["2028-02-28", "2028-02-29"]],
  ["event outside visible month", "2026-12-01T09:00Z", "2026-12-01T10:00Z", "2026-11", []],
];
for (const [label, start, end, month, expected] of cases) {
  test(label, () => assert.deepEqual(keys(event(start, end), month), expected));
}

test("start, continuation, end and midnight wording remain explicit", () => {
  const list = segments(buildMonthLayout([event("2026-11-27T10:00+01:00", "2026-11-30T16:00+01:00")], "2026-11"));
  assert.deepEqual(list.map(s => s.role), ["start", "continue", "continue", "end"]);
  assert.deepEqual(list.map(s => s.label), ["Beginn 10:00 Uhr", "Fortsetzung", "Fortsetzung", "Ende 16:00 Uhr"]);
  assert.equal(segments(buildMonthLayout([event("2026-11-28T17:18+01:00", "2026-11-30T00:00+01:00")], "2026-11")).at(-1).label, "Ende 00:00 Uhr (Folgetag)");
});

test("month and week clipping preserve global phase but break band at row edge", () => {
  const item = event("2026-11-28T17:18+01:00", "2026-12-02T11:30+01:00");
  const november = segments(buildMonthLayout([item], "2026-11"));
  assert.deepEqual(november.map(s => [s.day, s.connectedBefore, s.connectedAfter]), [
    ["2026-11-28", false, true], ["2026-11-29", true, false], ["2026-11-30", false, false],
  ]);
  const december = segments(buildMonthLayout([item], "2026-12"));
  assert.equal(december[0].role, "continue");
  assert.equal(december[1].role, "end");
  assert.equal(december[0].connectedBefore, false);
});

test("parallel spans use nonoverlapping stable lanes within each week", () => {
  const offers = [event("2026-11-27T10:00+01:00", "2026-11-30T12:00+01:00", "long"),
    event("2026-11-28T11:00+01:00", "2026-11-29T12:00+01:00", "parallel"),
    event("2026-11-28T13:00+01:00", "2026-11-28T15:00+01:00", "single")];
  const result = buildMonthLayout(offers, "2026-11");
  assert.equal(result.offerCount, 3);
  for (const week of result.weeks) {
    const lanes = new Map();
    for (const day of week.days) {
      assert.equal(new Set(day.segments.map(s => s.lane)).size, day.segments.length);
      for (const segment of day.segments) {
        if (lanes.has(segment.offer.id)) assert.equal(lanes.get(segment.offer.id), segment.lane);
        lanes.set(segment.offer.id, segment.lane);
      }
    }
  }
  assert.deepEqual(result, buildMonthLayout([...offers].reverse(), "2026-11"));
});

test("layout retains original object identity and never changes records", () => {
  const offer = event("2026-11-28T17:18+01:00", "2026-11-29T17:18+01:00");
  const before = JSON.stringify(offer);
  const result = buildMonthLayout([offer, offer], "2026-11");
  assert.equal(result.offerCount, 1);
  assert.equal(segments(result).length, 2);
  assert.ok(segments(result).every(segment => segment.offer === offer));
  assert.equal(JSON.stringify(offer), before);
});

test("invalid and empty intervals never produce phantom days or loops", () => {
  for (const [start, end] of [["bad", "bad"], ["2026-11-28T10:00Z", "2026-11-28T10:00Z"], ["2026-11-29T10:00Z", "2026-11-28T10:00Z"]]) {
    assert.equal(buildMonthLayout([event(start, end)], "2026-11").offerCount, 0);
  }
  assert.throws(() => buildMonthLayout([], "2026-13"), RangeError);
});

test("month navigation and day labels use Berlin regardless of machine timezone", () => {
  assert.deepEqual(monthKeys("2026-10-31T23:30Z"), ["2026-11", "2026-12", "2027-01", "2027-02"]);
  assert.equal(berlinDay("2026-11-28T23:30Z"), "2026-11-29");
  const start = calendarInstantLabel("2026-10-25T02:30+02:00");
  const end = calendarInstantLabel("2026-10-25T02:30+01:00");
  assert.notEqual(start, end, "repeated clock time must expose different time-zone abbreviations");
  const label = segments(buildMonthLayout([event("2026-10-25T02:30+02:00", "2026-10-25T02:30+01:00")], "2026-10"))[0].label;
  assert.match(label, /02:30 Uhr \(.+\) – 02:30 Uhr \(.+\)/);
});
