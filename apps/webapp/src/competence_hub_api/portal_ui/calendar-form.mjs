import {createCalendarPicker,dateOnly} from './calendar-picker.js';
const pad = value => String(value).padStart(2, "0");
const formatter = new Intl.DateTimeFormat("de-DE", {timeZone:"Europe/Berlin", year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hourCycle:"h23"});
export function germanDateTime(value) {
  const p = Object.fromEntries(formatter.formatToParts(new Date(value)).map(part => [part.type,part.value]));
  return `${p.day}.${p.month}.${p.year} ${p.hour}:${p.minute}`;
}
export function localParts(value) {
  const text = String(value || "").trim();
  const de = /^(\d{2})\.(\d{2})\.(\d{4})[ T](\d{2}):(\d{2})$/.exec(text);
  const iso = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/.exec(text);
  if (!de && !iso) return null;
  const [year,month,day,hour,minute] = (de ? [de[3],de[2],de[1],de[4],de[5]] : iso.slice(1)).map(Number);
  const probe = new Date(Date.UTC(year,month-1,day,hour,minute));
  if (year < 2000 || year > 9999 || month < 1 || month > 12 || day < 1 || hour > 23 || minute > 59
      || probe.getUTCFullYear() !== year || probe.getUTCMonth() !== month-1 || probe.getUTCDate() !== day) return null;
  return {year,month,day,hour,minute,label:`${pad(day)}.${pad(month)}.${year} ${pad(hour)}:${pad(minute)}`};
}
export function berlinInstant(value, original = null) {
  const p = localParts(value);
  if (!p) return {error:"date_format"};
  // Keep an untouched existing instant, including seconds and a repeated DST hour.
  if (original && Number.isFinite(Date.parse(original)) && germanDateTime(original) === p.label) return {value:original};
  const naive = Date.UTC(p.year,p.month-1,p.day,p.hour,p.minute);
  const candidates = [60,120].map(minutes => new Date(naive-minutes*60000).toISOString())
    .filter(instant => germanDateTime(instant) === p.label);
  if (!candidates.length) return {error:"date_gap"};
  if (candidates.length > 1) return {error:"date_ambiguous"};
  return {value:candidates[0]};
}
const fields = {title:"calendar-title",topic_id:"calendar-topic",summary:"calendar-summary",starts_at:"calendar-starts-at",
  ends_at:"calendar-ends-at",time_zone:"calendar-time-zone",format:"calendar-format",public_location:"calendar-location",
  capacity:"calendar-capacity",review_threshold:"calendar-review-threshold",decision_deadline:"calendar-decision-deadline",price_display_text:"calendar-price"};
const dates = ["starts_at","ends_at","decision_deadline"];
const optional = value => String(value || "").trim() || null;
function horizon(now) {
  const limit = new Date(now), day = limit.getUTCDate();
  limit.setUTCDate(1);limit.setUTCMonth(limit.getUTCMonth()+3);
  const last = new Date(Date.UTC(limit.getUTCFullYear(),limit.getUTCMonth()+1,0)).getUTCDate();
  limit.setUTCDate(Math.min(day,last));return limit;
}
export function draftValues(data, originals = {}, now = new Date()) {
  const payload = {}, errors = [];
  const add = (field,code) => errors.push({field,code});
  for (const field of Object.keys(fields)) payload[field] = data.get(field);
  for (const field of dates) {
    const parsed = berlinInstant(payload[field], originals[field]);
    if (parsed.error) add(field,parsed.error);else payload[field] = parsed.value;
  }
  for (const [field,max] of [["title",160],["price_display_text",200]]) {
    payload[field] = String(payload[field] || "").trim();
    if (!payload[field] || payload[field].length > max) add(field,"required_text");
  }
  for (const [field,max] of [["summary",1200],["public_location",200]]) {
    payload[field] = optional(payload[field]);
    if (payload[field] && payload[field].length > max) add(field,"too_long");
  }
  if (!payload.topic_id) add("topic_id","required");
  if (payload.time_zone !== "Europe/Berlin") add("time_zone","invalid");
  if (!["online","praesenz","hybrid"].includes(payload.format)) add("format","invalid");
  if (payload.format !== "online" && !payload.public_location) add("public_location","required");
  for (const field of ["capacity","review_threshold"]) {
    const raw = String(payload[field] || "").trim();payload[field] = Number(raw);
    if (!/^\d+$/.test(raw) || !Number.isInteger(payload[field]) || payload[field] < 1 || payload[field] > 500) add(field,"integer_range");
  }
  if (payload.review_threshold > payload.capacity) add("review_threshold","threshold");
  const validDate = field => !errors.some(e => e.field === field);
  if (validDate("starts_at") && validDate("ends_at") && Date.parse(payload.ends_at) <= Date.parse(payload.starts_at)) add("ends_at","end_after_start");
  if (validDate("decision_deadline") && (Date.parse(payload.decision_deadline) < +now
      || (validDate("starts_at") && Date.parse(payload.decision_deadline) >= Date.parse(payload.starts_at)))) add("decision_deadline","deadline");
  if (validDate("starts_at") && (Date.parse(payload.starts_at) < +now || Date.parse(payload.starts_at) > +horizon(now))) add("starts_at","planning_window");
  if (validDate("ends_at") && Date.parse(payload.ends_at) > +horizon(now)) add("ends_at","planning_window");
  return {payload,errors};
}
export function fieldMessage(field, code, data, now = new Date()) {
  const future = new Date(+now+7*86400000);future.setUTCHours(15,0,0,0);
  const example = germanDateTime(future);
  if (code === "date_gap") return "Diese Uhrzeit gibt es wegen der Zeitumstellung nicht. Bitte wählen Sie eine gültige Uhrzeit, z. B. 03:00 Uhr am selben Tag.";
  if (code === "date_ambiguous") return "Diese Uhrzeit kommt bei der Zeitumstellung zweimal vor. Bitte wählen Sie eine eindeutige Uhrzeit, z. B. 03:00 Uhr. Gespeicherte Termine werden unverändert erhalten.";
  if (code === "date_format") return `Bitte geben Sie Datum und Uhrzeit als TT.MM.JJJJ HH:mm ein, z. B. ${example}.`;
  if (code === "end_after_start") {
    const start = berlinInstant(data.get("starts_at"));
    const next = start.value && Date.parse(start.value) < +horizon(now) ? Math.min(Date.parse(start.value)+3600000,+horizon(now)) : +future;
    return `Das Ende muss nach dem Beginn liegen. Beispiel: ${germanDateTime(next)} Uhr.`;
  }
  if (code === "planning_window") return `Der Zeitraum muss in der Zukunft und innerhalb der nächsten drei Monate liegen (bis ${germanDateTime(horizon(now))} Uhr). Beispiel: ${example} Uhr.`;
  if (code === "threshold") return `Die Prüfschwelle darf die maximale Teilnehmerzahl von ${/^\d{1,3}$/.test(data.get("capacity")) ? data.get("capacity") : "1 bis 500"} nicht überschreiten. Beispiel: Kapazität 10, Prüfschwelle 5.`;
  if (field === "decision_deadline") {
    const start = berlinInstant(data.get("starts_at"));
    const midpoint = start.value ? Math.floor((+now+Date.parse(start.value))/120000)*60000 : 0;
    return midpoint > +now && midpoint < Date.parse(start.value)
      ? `Die Entscheidungsfrist muss noch bevorstehen und vor Beginn liegen. Beispiel: ${germanDateTime(midpoint)} Uhr.`
      : "Wählen Sie einen Beginn mit ausreichend Vorlauf und eine künftige Frist davor. Beispiel: Beginn morgen 09:00 Uhr, Frist morgen 08:00 Uhr.";
  }
  const messages = {
    title:"Bitte geben Sie einen Titel mit höchstens 160 Zeichen ein, z. B. Gesunde Mitarbeiterführung.",
    topic_id:"Bitte wählen Sie ein freigegebenes Thema aus, z. B. Führung und Zusammenarbeit. Ohne freigegebenes Thema ist Speichern nicht möglich.",
    summary:"Die Kurzbeschreibung ist optional und darf höchstens 1200 Zeichen enthalten. Beispiel: Zweitägiger Workshop zur gesunden Mitarbeiterführung.",
    public_location:"Für Präsenz oder Hybrid geben Sie bitte einen öffentlichen Ort an, z. B. Würzburg, Seminarraum. Höchstens 200 Zeichen, keine privaten Zugangsdaten.",
    capacity:"Bitte geben Sie eine ganze Teilnehmerzahl zwischen 1 und 500 ein, z. B. 10.",
    review_threshold:"Bitte geben Sie eine ganze Prüfschwelle von 1 bis zur Kapazität ein, z. B. 5 bei Kapazität 10.",
    decision_deadline:`Die Entscheidungsfrist muss noch bevorstehen und vor dem Veranstaltungsbeginn liegen. Beispiel: einen Tag vor Beginn um 12:00 Uhr.`,
    price_display_text:"Bitte geben Sie einen Preishinweis mit höchstens 200 Zeichen ein, z. B. Preis nach Abstimmung.",
    time_zone:"Bitte wählen Sie die Zeitzone Europe/Berlin.",format:"Bitte wählen Sie Online, Präsenz oder Hybrid.",
  };
  return messages[field] || `Bitte korrigieren Sie Datum und Uhrzeit, z. B. ${example}.`;
}
export function createCalendarForm(form) {
  let originals = {};
  const controls = {};let shown=[],rendered='';
  for (const field of dates) {
    const input = form.querySelector('#'+fields[field]);
    input.type = "text";
    const choices = document.createElement("div");choices.className = "calendar-clock-choices";
    const label = {starts_at:'Beginn',ends_at:'Ende',decision_deadline:'Entscheidungsfrist'}[field];
    const make = (name,values) => {
      const wrapper=document.createElement('div');wrapper.className='field calendar-clock-part';
      const select = document.createElement("select");select.id = input.id+"-"+name;select.name=field+'_'+name;select.required=true;
      const caption=document.createElement('label');caption.htmlFor=select.id;caption.textContent=name==='hour'?'Stunde':'Minute';
      select.setAttribute("aria-label",`${label}: ${caption.textContent}`);
      select.add(new Option(name === "hour" ? "Stunde" : "Minute",""));
      values.forEach(value => select.add(new Option(pad(value),pad(value))));wrapper.append(caption,select);choices.append(wrapper);return select;
    };
    const hours = make("hour",Array.from({length:24},(_,index) => index)), minutes = make("minute",[0,15,30,45]);
    form.querySelector(`[data-clock="${field}"]`).append(choices);controls[field] = {input,hours,minutes};
  }
  const picker=createCalendarPicker(form,Object.fromEntries(dates.map(field=>[field,controls[field].input])));
  function values() {
    const data=new FormData(form);
    for(const field of dates) {
      const {input,hours,minutes}=controls[field];data.set(field,`${input.value.trim()} ${hours.value}:${minutes.value}`);
    }
    return data;
  }
  function validate() {
    const result=draftValues(values(),originals),parts=[];
    for(const field of dates) {
      const {input,hours,minutes}=controls[field];
      if(!dateOnly(input.value))parts.push({field,code:'date_format',part:'date'});
      if(!hours.value)parts.push({field,code:'required_hour',part:'hour'});
      if(!minutes.value)parts.push({field,code:'required_minute',part:'minute'});
    }
    result.errors=result.errors.filter(error=>!parts.some(part=>part.field===error.field));
    return {...result,errors:[...result.errors,...parts]};
  }
  function control(error) {
    const choice=controls[error.field];
    if(choice && error.part==='hour')return choice.hours;
    if(choice && error.part==='minute')return choice.minutes;
    if(choice && ['date_gap','date_ambiguous'].includes(error.code))return choice.hours;
    if(error.field==='ends_at' && error.code==='end_after_start' && controls.starts_at.input.value===choice.input.value) return choice.hours;
    return form.querySelector('#'+fields[error.field]);
  }
  function shortMessage({field,code,part}) {
    if(part==='hour')return 'Bitte Stunde wählen.';
    if(part==='minute')return 'Bitte Minute wählen.';
    if(code==='date_format')return 'Bitte ein gültiges Datum wählen.';
    if(code==='date_gap')return 'Diese Uhrzeit entfällt bei der Zeitumstellung.';
    if(code==='date_ambiguous')return 'Diese Uhrzeit ist wegen der Zeitumstellung uneindeutig.';
    if(code==='end_after_start')return 'Das Ende muss nach dem Beginn liegen.';
    if(code==='planning_window')return 'Bitte innerhalb der nächsten drei Monate planen.';
    if(code==='deadline')return 'Die Frist muss noch bevorstehen und vor Beginn liegen.';
    if(code==='threshold')return `Höchstens ${form.querySelector('#calendar-capacity').value||500} Teilnehmende.`;
    const messages={title:'Bitte Titel angeben (höchstens 160 Zeichen).',topic_id:'Bitte freigegebenes Thema wählen.',
      summary:'Höchstens 1200 Zeichen.',public_location:code==='too_long'?'Höchstens 200 Zeichen.':'Bitte Veranstaltungsort angeben.',
      capacity:'Bitte ganze Zahl von 1 bis 500 angeben.',review_threshold:'Bitte ganze Zahl von 1 bis zur Kapazität angeben.',
      price_display_text:'Bitte Preishinweis angeben (höchstens 200 Zeichen).',format:'Bitte Format wählen.',time_zone:'Bitte Europe/Berlin verwenden.'};
    return messages[field]||'Bitte Angabe prüfen.';
  }
  function clearDOM() {
    form.querySelectorAll('[data-calendar-field-error]').forEach(element=>element.remove());
    form.querySelectorAll('[aria-invalid]').forEach(input=>{
      const id=input.id;input.removeAttribute("aria-invalid");
      const ids = (input.getAttribute("aria-describedby") || "").split(" ").filter(value => value && value !== id+"-error");
      if (ids.length) input.setAttribute("aria-describedby",ids.join(" "));else input.removeAttribute("aria-describedby");
    });
  }
  const errorSignature=errors=>JSON.stringify(errors.map(error=>[error.field,error.code,error.part||'',shortMessage(error)]));
  function show(errors,focus=true) {
    clearDOM();shown=errors.filter(error=>error && Object.hasOwn(fields,error.field));rendered=errorSignature(shown);const data=values();
    for (const error of shown) {
      const {field,code}=error,input=control(error);
      if (input.getAttribute("aria-invalid") === "true") continue;
      const message = document.createElement("p");message.id = input.id+"-error";
      message.className = "field-error";message.dataset.calendarFieldError = "true";
      message.textContent=shortMessage(error);input.closest('.field').append(message);
      input.setAttribute("aria-invalid","true");input.setAttribute("aria-describedby",[input.getAttribute("aria-describedby"),message.id].filter(Boolean).join(" "));
      if(!['required_hour','required_minute','required','required_text'].includes(code)) {
        const help=document.createElement('details');help.className='field-help';help.dataset.calendarFieldError='true';
        const summary=document.createElement('summary');summary.textContent='Beispiel';const text=document.createElement('p');text.textContent=fieldMessage(field,code,data);
        help.append(summary,text);input.closest('.field').append(help);
      }
    }
    const first=form.querySelector('[aria-invalid="true"]');
    const summary=form.querySelector('#calendar-offer-error');summary.dataset.calendarValidation='true';
    summary.textContent=first?'Bitte markierte Angaben prüfen.':'';summary.hidden=!first;
    if(first && focus){first.scrollIntoView({block:'center'});first.focus({preventScroll:true});}
    return Boolean(first);
  }
  function locationHint() {
    const required=form.querySelector('#calendar-format').value!=='online',input=form.querySelector('#calendar-location');
    input.required=required;
    form.querySelector('#calendar-location-label').textContent=required?'Veranstaltungsort *':'Öffentlicher Hinweis (optional)';
    form.querySelector('#calendar-location-hint').textContent=required?'Bitte Veranstaltungsort angeben, z. B. Würzburg, Seminarraum.':'Nur öffentliche Angaben, keine privaten Zugangsdaten.';
    form.querySelector('#calendar-location-count').textContent=`${input.value.length} / 200 Zeichen`;
  }
  function edited() {
    locationHint();picker.refresh();
    if(shown.length){const known=new Set(shown.map(error=>error.field)),next=validate().errors.filter(error=>known.has(error.field));
      if(errorSignature(next)!==rendered)show(next,false);}
  }
  form.addEventListener('input',edited);form.addEventListener('change',edited);
  return {show,hidePicker:picker.hide,refresh:locationHint,values,
    clear(){shown=[];rendered='';clearDOM();const summary=form.querySelector('#calendar-offer-error');if(summary.dataset.calendarValidation){summary.hidden=true;summary.textContent='';delete summary.dataset.calendarValidation;}},
    reset(draft = {}) {this.clear();originals={};picker.hide();
      for (const field of dates) {
        const choice=controls[field],text=draft[field]?germanDateTime(draft[field]):'',p=localParts(text);
        originals[field]=draft[field];choice.input.value=text.slice(0,10);
        choice.minutes.querySelectorAll('[data-existing]').forEach(option=>option.remove());
        if(p && ![0,15,30,45].includes(p.minute)){const option=new Option(pad(p.minute),pad(p.minute));option.dataset.existing='true';choice.minutes.add(option);}
        choice.hours.value=p?pad(p.hour):field==='starts_at'?'09':field==='ends_at'?'10':'12';choice.minutes.value=p?pad(p.minute):'00';
      }
      locationHint();picker.refresh();
    },
    validate,
  };
}
