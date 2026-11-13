import assert from "node:assert/strict";
import {berlinInstant, germanDateTime, localParts, draftValues, fieldMessage} from "../src/competence_hub_api/portal_ui/calendar-form.mjs";

const now = new Date("2026-11-13T10:00:00Z");
const base = {title:"Eintägiger Workshop", topic_id:"synthetic-topic",summary:"",starts_at:"20.11.2026 09:00",ends_at:"20.11.2026 16:00",time_zone:"Europe/Berlin",format:"online",public_location:"",capacity:"10",review_threshold:"5",decision_deadline:"19.11.2026 12:00",price_display_text:"Preis nach Abstimmung"};
const data = changes => new Map(Object.entries({...base,...changes}));
assert.equal(germanDateTime("2026-11-20T08:18:00Z"),"20.11.2026 09:18");
assert.equal(berlinInstant("20.11.2026 09:00").value,"2026-11-20T08:00:00.000Z");
assert.equal(berlinInstant("2026-11-20T09:00").value,"2026-11-20T08:00:00.000Z");
for (const input of ["31.02.2027 09:00","20.11.2026 24:00","20.11.2026 09:60","11/20/2026 9:00 AM",""]) assert.equal(localParts(input),null);
assert.equal(berlinInstant("28.03.2027 02:30").error,"date_gap");
assert.equal(berlinInstant("31.10.2027 02:30").error,"date_ambiguous");
for (const original of ["2027-10-31T00:30:19Z","2027-10-31T01:30:19Z","2026-11-20T08:18:27Z"]) {
  assert.equal(berlinInstant(germanDateTime(original),original).value,original);
}
assert.equal(berlinInstant("28.03.2027 03:30").value,"2027-03-28T01:30:00.000Z");
assert.equal(berlinInstant("31.10.2027 03:30").value,"2027-10-31T02:30:00.000Z");
assert.deepEqual(draftValues(data(),{},now).errors,[]);
assert.equal(draftValues(data(),{},now).payload.summary,null);
assert.deepEqual(draftValues(data({ends_at:"21.11.2026 00:00"}),{},now).errors,[]);
assert.deepEqual(draftValues(data({ends_at:"22.11.2026 16:18"}),{},now).errors,[]);
for (const [changes,field,code] of [
  [{ends_at:"20.11.2026 08:00"},"ends_at","end_after_start"],
  [{decision_deadline:"20.11.2026 09:00"},"decision_deadline","deadline"],
  [{decision_deadline:"12.11.2026 09:00"},"decision_deadline","deadline"],
  [{review_threshold:"11"},"review_threshold","threshold"],
  [{capacity:"1.5"},"capacity","integer_range"],
  [{format:"praesenz"},"public_location","required"],
  [{title:"   "},"title","required_text"],
  [{summary:"x".repeat(1201)},"summary","too_long"],
  [{ends_at:"14.02.2027 16:00"},"ends_at","planning_window"],
]) assert(draftValues(data(changes),{},now).errors.some(error => error.field === field && error.code === code));
assert(fieldMessage("ends_at","end_after_start",data(),now).includes("20.11.2026 10:00"));
assert(fieldMessage("review_threshold","threshold",data(),now).includes("10"));
console.log("Calendar form: German/ISO, one/multiday, DST gap/fold, preserved seconds/minutes, constraints and examples PASS");
