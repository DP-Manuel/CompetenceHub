const READ = "/api/v1/admin/coach-management";
const WRITE = "/api/v1/admin/coaches";
const LIFE = { draft: "Entwurf", active: "Aktiv", paused: "Pausiert", inactive: "Inaktiv", archived: "Archiviert" };
const REV = { draft: "Entwurf", submitted: "Eingereicht", abandoned: "Abgeschlossen ohne Freigabe" };
const PUB = { published: "Veröffentlicht", withdrawn: "Zurückgezogen", not_published: "Nicht veröffentlicht" };
const ENV = { preview: "GitHub Preview", production: "Production" };
const APPROVAL = { content_review: "Inhalt geprüft", person_consent: "Einwilligung belegt", preview: "Preview freigegeben", production: "Production freigegeben" };
const CATEGORY = { personalentwicklung: "Personalentwicklung", persoenlichkeitsentwicklung: "Persönlichkeitsentwicklung", karrierecoaching: "Karrierecoaching" };
const TYPES = { lecture: "Vortrag", workshop: "Workshop", coaching: "Coaching", individual: "Individuelles Angebot", other: "Sonstiges" };

function node(tag, text = "", cls = "") {
  const item = document.createElement(tag);
  if (text) item.textContent = text;
  if (cls) item.className = cls;
  return item;
}
function button(text, action, cls = "button button-secondary") {
  const item = node("button", text, cls);
  item.type = "button";
  item.addEventListener("click", action);
  return item;
}
function selectField(label, values, value, id) {
  const control = node("select");
  for (const [key, title] of Object.entries(values)) {
    const option = node("option", title);
    option.value = key;
    control.append(option);
  }
  control.value = value;
  return field(label, control, id);
}
function field(label, control, id) {
  const wrap = node("div", "", "field");
  const caption = node("label", label);
  caption.htmlFor = id;
  control.id = id;
  control.name = id.replace("cm-", "");
  wrap.append(caption, control);
  return wrap;
}
function inputField(label, id, value, max, multiline = false, required = false) {
  const input = node(multiline ? "textarea" : "input");
  input.value = value || "";
  input.maxLength = max;
  input.required = required;
  if (multiline) input.rows = 4;
  return field(label, input, id);
}
function date(value) {
  return new Intl.DateTimeFormat("de-DE", {dateStyle: "medium", timeStyle: "short"}).format(new Date(value));
}

export function createCoachManagement({ request, refreshCsrf, denied }) {
  const root = node("section", "", "coach-management");
  root.id = "coach-management-workspace";
  root.hidden = true;
  root.setAttribute("aria-label", "Coachverwaltung");
  let current = null;
  let dirty = false;
  let pending = false;
  let generation = 0;
  let offset = 0;
  let lifecycle = "";
  let publication = "";
  let topicOffset = 0;
  let selectedTopics = new Set();
  let offerings = [];
  let form = null;
  let error = null;
  let status = null;
  let restoreFocus = null;
  let creationAttempt = null;
  const dialogs = new Set();

  function canLeave() {
    return !pending && (!dirty || window.confirm("Ungespeicherte Änderungen verwerfen?"));
  }
  function reset() {
    generation += 1;
    dirty = false;
    current = null;
    form = null;
    selectedTopics.clear();
    offerings = [];
    creationAttempt = null;
    for (const dialog of dialogs) { dialog.close(); dialog.remove(); }
    dialogs.clear();
    root.replaceChildren();
  }
  window.addEventListener("beforeunload", (event) => {
    if (dirty || pending) { event.preventDefault(); event.returnValue = ""; }
  });
  function message(text, failed = false) {
    const target = failed ? error : status;
    if (!target) return;
    target.textContent = text;
    target.hidden = !text;
    if (failed && text) target.focus();
  }
  async function call(path, options) {
    const response = await request(path, options);
    if (response.status === 403) {
      const problem = await response.clone().json().catch(() => ({}));
      if (problem.code === "request_verification_failed") {
        throw new Error("Die Anfrageprüfung ist nicht mehr aktuell. Ihre Eingaben bleiben erhalten. Bitte erneut speichern.");
      }
    }
    if (response.status === 401 || response.status === 403) {
      reset();
      denied(response.status);
      throw new Error("Zugriff nicht mehr möglich. Bitte erneut anmelden.");
    }
    if (!response.ok) {
      const messages = {
        400: "Bitte prüfen Sie die Eingaben, Zuordnungen und Feldlängen.",
        404: "Der gewählte Datensatz ist nicht mehr verfügbar.",
        409: "Datensatz wurde inzwischen geändert oder die Aktion ist nicht mehr zulässig. Ihre Eingaben bleiben erhalten. Aktuellen Stand laden und erneut prüfen.",
        422: "Bitte prüfen Sie die Auswahl und die Eingaben.",
        503: "Die Coachverwaltung ist momentan nicht verfügbar.",
      };
      throw new Error(messages[response.status] || "Die Anfrage konnte nicht abgeschlossen werden.");
    }
    return response.json();
  }
  function notices() {
    error = node("p", "", "form-error"); error.hidden = true; error.tabIndex = -1; error.setAttribute("role", "alert");
    status = node("p", "", "form-success"); status.hidden = true; status.setAttribute("role", "status");
    root.append(error, status);
  }
  function busy(value) {
    pending = value;
    root.setAttribute("aria-busy", String(value));
    for (const control of root.querySelectorAll("button,input,textarea,select")) {
      if (value) { control.dataset.wasDisabled = String(control.disabled); control.disabled = true; }
      else if (control.dataset.wasDisabled !== undefined) {
        control.disabled = control.dataset.wasDisabled === "true";
        delete control.dataset.wasDisabled;
      }
    }
  }
  async function change(path, body, method = "POST", after = null) {
    if (pending) return;
    const ticket = generation;
    message(""); message("", true);
    busy(true);
    try {
      // Another tab can rotate the shared session's CSRF token. Refresh once,
      // then send the original optimistic version; never retry a write blindly.
      const verification = await refreshCsrf();
      if (verification.status === 401) { reset(); denied(401); return; }
      if (!verification.ok) throw new Error("Die Anfrageprüfung ist momentan nicht möglich. Ihre Eingaben bleiben erhalten.");
      const result = await call(path, {method, body, csrf: "session", headers: {Prefer: "return=minimal"}});
      if (ticket !== generation) return;
      dirty = false;
      await (after ? after(result) : open(current.id, null, false));
      message("Gespeichert.");
    } catch (failure) {
      message(failure.message === "Failed to fetch" ? "Keine Verbindung. Ihre Eingaben bleiben erhalten." : failure.message, true);
    } finally { busy(false); }
  }
  function pageNavigation(container, hasMore, at, load) {
    const nav = node("div", "", "button-row cm-pagination");
    const previous = button("Vorherige", () => load(Math.max(0, at - 10)));
    previous.disabled = at === 0;
    const next = button("Weitere", () => load(at + 10)); next.disabled = !hasMore;
    nav.append(previous, next); container.append(nav);
  }
  async function index() {
    if (!canLeave()) return;
    dirty = false; current = null;
    const ticket = ++generation;
    root.replaceChildren();
    const heading = node("div", "", "workspace-heading");
    heading.append(node("h2", "Coaches"), button("Coach anlegen", create, "button button-primary"));
    root.append(heading); notices();
    const filters = node("div", "", "cm-filters");
    const life = selectField("Lifecycle", {"": "Alle", ...LIFE}, lifecycle, "cm-filter-lifecycle");
    const pub = selectField("Veröffentlichung", {"": "Alle", preview: "GitHub Preview", production: "Production", unpublished: "Nicht veröffentlicht"}, publication, "cm-filter-publication");
    life.querySelector("select").addEventListener("change", (e) => { lifecycle=e.target.value; offset=0; index(); });
    pub.querySelector("select").addEventListener("change", (e) => { publication=e.target.value; offset=0; index(); });
    filters.append(life, pub); root.append(filters);
    try {
      const params = new URLSearchParams({limit: "10", offset: String(offset)});
      if (lifecycle) params.set("lifecycle", lifecycle);
      if (publication) params.set("publication", publication);
      const result = await call(READ + "?" + params);
      if (ticket !== generation) return;
      if (!result.items.length) root.append(node("p", offset || lifecycle || publication ? "Keine Coaches für diese Auswahl." : "Noch keine Coaches vorhanden.", "empty-state"));
      const list = node("ul", "", "cm-list");
      for (const item of result.items) {
        const row = node("li");
        const openButton = button(item.display_name, () => open(item.id), "cm-coach-link");
        const meta = node("dl", "", "cm-meta");
        for (const [key, value] of [["Lifecycle", LIFE[item.lifecycle]], ["GitHub Preview", PUB[item.preview]], ["Production", PUB[item.production]],
          ["Themen", item.topic_count], ["Aktive Angebote", item.offering_count], ["Profil", item.revision_number ? `Revision ${item.revision_number} · ${REV[item.revision_status]}` : "Noch kein Profil"]]) {
          meta.append(node("dt", key), node("dd", String(value)));
        }
        row.append(openButton, meta); list.append(row);
      }
      root.append(list);
      pageNavigation(root, result.has_more, offset, (value) => {offset=value; index();});
    } catch (failure) { message(failure.message, true); }
  }
  function modal(title, build, onConfirm, confirmText = "Bestätigen") {
    const dialog = node("dialog");
    const box = node("form", "", "dialog-form");
    const heading = node("h2", title); heading.id = "cm-dialog-title";
    dialog.setAttribute("aria-labelledby", heading.id);
    box.append(heading); build(box);
    const controls = node("div", "", "button-row");
    const confirm = node("button", confirmText, "button button-primary"); confirm.type="submit";
    const close = () => { dialog.close(); };
    controls.append(confirm, button("Abbrechen", close)); box.append(controls); dialog.append(box);
    restoreFocus = document.activeElement;
    dialog.addEventListener("close", () => { dialogs.delete(dialog); dialog.remove(); restoreFocus?.isConnected && restoreFocus.focus(); });
    box.addEventListener("submit", (event) => {
      event.preventDefault();
      const data = new FormData(box);
      close(); onConfirm(data);
    });
    dialogs.add(dialog); document.body.append(dialog); dialog.showModal();
  }
  function create() {
    modal("Coach anlegen", (box) => box.append(inputField("Anzeigename", "cm-create-name", creationAttempt?.name || "", 200, false, true)), (data) => {
      const name=String(data.get("create-name")).trim();
      if (!creationAttempt || creationAttempt.name!==name) creationAttempt={name,id:crypto.randomUUID()};
      change(WRITE, {display_name: name, client_request_id: creationAttempt.id}, "POST", (item) => {
        creationAttempt=null;
        return open(item.id, null, false);
      });
    }, "Anlegen");
  }
  function action(label, path, body, method = "POST", warning = null) {
    return button(label, () => {
      if (dirty) { message("Bitte zuerst den Profilentwurf speichern oder die Änderungen verwerfen.", true); return; }
      if (warning) modal(label, (box) => box.append(node("p", warning)), () => change(path, body, method));
      else change(path, body, method);
    });
  }
  async function open(id, revisionId = null, guard = true) {
    if (guard && !canLeave()) return;
    const ticket = ++generation;
    try {
      const item = await call(READ + "/" + id + (revisionId ? "?revision_id=" + encodeURIComponent(revisionId) : ""));
      if (ticket !== generation) return;
      current = item; dirty = false;
      renderDetail();
    } catch (failure) { message(failure.message, true); }
  }
  function renderDetail() {
    root.replaceChildren();
    const heading = node("div", "", "workspace-heading");
    const title = node("h2", current.revision?.content.display_name || current.display_name); title.tabIndex=-1;
    heading.append(title, button("Zur Coachliste", index)); root.append(heading); notices();
    const toolbar = node("div", "", "button-row cm-toolbar");
    toolbar.append(button("Aktuellen Stand laden", () => open(current.id)));
    const version = current.version;
    const base = WRITE + "/" + current.id;
    const caps = current.capabilities;
    const labels = {active: current.lifecycle === "draft" ? "Aktivieren" : "Reaktivieren", paused: "Pausieren", inactive: "Deaktivieren", archived: "Archivieren"};
    for (const target of caps.lifecycles) {
      toolbar.append(action(labels[target], base + "/lifecycle", {expected_version: version, lifecycle: target}, "PATCH",
        target === "active" ? "Die bestehende Coach-Identität und Historie bleiben erhalten. Eine Veröffentlichung erfolgt nicht automatisch." :
          "Beide Veröffentlichungsstände werden zurückgezogen; ein offener Entwurf wird abgeschlossen. Historie und Portalaccount bleiben erhalten. Bereits ausgelieferte Webseiten werden erst durch einen separat freigegebenen Release geändert."));
    }
    root.append(node("p", "Lifecycle: " + LIFE[current.lifecycle], "cm-lifecycle"), toolbar);
    const tabs = node("div", "", "cm-tabs"); tabs.setAttribute("role", "tablist"); tabs.setAttribute("aria-label", "Coachdetails");
    const panels = node("div");
    const sections = [["overview","Übersicht"], ["profile","Profil"], ["topics","Themen"], ["competencies","Kompetenzen"], ["offerings","Angebote"], ["publication","Veröffentlichung"], ["history","Historie"]];
    const selectTab = (key, focus = false) => {
      for (const tab of tabs.children) { const selected=tab.dataset.key===key; tab.setAttribute("aria-selected", String(selected)); tab.tabIndex=selected?0:-1; if(selected && focus) tab.focus(); }
      for (const panel of panels.children) panel.hidden=panel.id!=="cm-panel-"+key;
    };
    for (const [key,label] of sections) {
      const tab = button(label, () => selectTab(key)); tab.id="cm-tab-"+key; tab.dataset.key=key;
      tab.setAttribute("role","tab"); tab.setAttribute("aria-controls","cm-panel-"+key);
      tab.addEventListener("keydown", (e) => {
        const n=sections.findIndex(([k])=>k===key);
        const move = {ArrowRight:(n+1)%sections.length,ArrowLeft:(n+sections.length-1)%sections.length,Home:0,End:sections.length-1}[e.key];
        if(move!==undefined) {e.preventDefault(); selectTab(sections[move][0],true);}
      });
      tabs.append(tab);
      const panel=node("section"); panel.id="cm-panel-"+key; panel.setAttribute("role","tabpanel"); panel.setAttribute("aria-labelledby",tab.id);
      panels.append(panel);
    }
    root.append(tabs,panels);
    const panel = (id) => panels.querySelector("#cm-panel-"+id);
    const overview = node("dl", "", "cm-meta");
    const links = current.links;
    for (const [key,value] of [["Portalaccount", {none:"Nicht verknüpft",active:"Aktiv",disabled:"Deaktiviert"}[links.portal_account]],
      ["Kalenderrolle", links.calendar_role ? "Vorhanden" : "Nicht vorhanden"],
      ["Kalender-Profilpfad", links.public_profile_path || "Nicht zugeordnet"],
      ["Laufende oder künftige Kalenderangebote", links.future_calendar ? "Vorhanden; vor Pause oder Ausscheiden zurückziehen" : "Keine"],
      ["Profil", current.revision ? `Revision ${current.revision.number} · ${REV[current.revision.status]}` : "Noch kein Profil"]]) overview.append(node("dt",key),node("dd",value));
    panel("overview").append(overview);
    form=node("form"); form.id="cm-profile-form";
    form.noValidate=true;
    // Form-associated controls can live in separate accessible tab panels.
    root.append(form);
    form.addEventListener("submit", (e) => {e.preventDefault(); save();});
    panels.addEventListener("input", () => {if(caps.editable) dirty=true;});
    panels.addEventListener("change", () => {if(caps.editable) dirty=true;});
    if (current.revision) renderProfile(panel, base, version);
    else panel("profile").append(node("p", "Noch kein Profil vorhanden."));
    if (caps.new_revision) {
      const seed=current.revision?.content || {display_name: current.display_name, short_intro: "Neuer Profilentwurf", target_groups:[], topic_ids:[], competencies:[], offerings:[], assets:[]};
      panel("profile").append(action("Neue Profilrevision", base+"/revisions", {expected_version:version,content:seed}));
    }
    renderPublication(panel("publication"),base,version);
    renderHistory(panel("history"));
    selectTab("overview"); title.focus();
  }
  function renderProfile(panel, base, version) {
    const revision=current.revision, content=revision.content;
    const editable=current.capabilities.editable;
    selectedTopics=new Set(content.topic_ids);
    offerings=structuredClone(content.offerings);
    const fields=node("fieldset"); fields.disabled=!editable;
    fields.append(node("legend", `Revision ${revision.number} · ${REV[revision.status]}`));
    for(const [name,label,max,multi,required] of [["display_name","Anzeigename",200,false,true],["academic_suffix","Akademischer Zusatz",100,false,false],
      ["short_intro","Kurzbeschreibung",1000,true,true],["description","Profiltext",10000,true,false],
      ["professional_background","Beruflicher Hintergrund",4000,true,false],["profile_path","Öffentlicher Profilpfad",200,false,false]]) {
      const wrap=inputField(label,"cm-"+name,content[name],max,multi,required);
      const control=wrap.querySelector("input,textarea"); control.setAttribute("form",form.id);
      if(name==="profile_path") {control.pattern="/coaches/[a-z0-9]+(-[a-z0-9]+)*/"; control.placeholder="/coaches/coach-alpha/";}
      fields.append(wrap);
    }
    fields.append(inputField("Zielgruppen", "cm-target_groups", content.target_groups.join("\n"), 7500,true));
    fields.querySelector("#cm-target_groups").setAttribute("form",form.id);
    const asset=content.assets[0];
    const assets=node("details"); assets.append(node("summary","Porträt-Referenz"));
    for(const [key,label,max] of [["reference","Assetreferenz",200],["sha256","SHA-256",64],["alt_text","Alternativtext",250]]) {
      const wrap=inputField(label,"cm-asset-"+key,asset?.[key] || "",max);
      wrap.querySelector("input").setAttribute("form",form.id); assets.append(wrap);
    }
    const scopes=node("fieldset"); scopes.append(node("legend","Porträt-Freigaben"));
    for(const [key,label] of Object.entries(ENV)) scopes.append(checkBox(label,"cm-asset-"+key,asset?.scopes.includes(key) || false));
    scopes.append(checkBox("Porträt aktiv","cm-asset-active",asset?.active ?? true)); assets.append(scopes); fields.append(assets);
    panel("profile").append(fields);
    const skills=node("fieldset"); skills.disabled=!editable; skills.append(node("legend","Kompetenzen"),inputField("Kompetenzen","cm-competencies",content.competencies.join("\n"),12500,true));
    skills.querySelector("textarea").setAttribute("form",form.id); panel("competencies").append(skills);
    const topicArea=node("div"); panel("topics").append(topicArea); topicOffset=0;
    loadTopics(topicArea,editable,revision.topics);
    const offerArea=node("div"); panel("offerings").append(offerArea); renderOfferings(offerArea,editable);
    if(editable) {
      const controls=node("div","","button-row cm-save");
      const saveButton=node("button","Profilentwurf speichern","button button-primary"); saveButton.type="submit"; saveButton.setAttribute("form",form.id);
      controls.append(saveButton,button("Änderungen verwerfen",()=>open(current.id,revision.id)),
        action("Zur Prüfung einreichen",base+"/revisions/"+revision.id+"/submit",{expected_version:version},"POST","Die eingereichte Revision ist unveränderlich. Weitere Änderungen benötigen eine neue Revision."));
      root.append(controls);
    }
  }
  function checkBox(label, id, checked) {
    const wrap=node("label", "", "check-row"); const control=node("input"); control.type="checkbox"; control.id=id; control.checked=checked;
    control.setAttribute("form",form.id); wrap.htmlFor=id; wrap.append(control,node("span",label)); return wrap;
  }
  async function loadTopics(container, editable, snapshots) {
    const id=current.id, version=current.version, at=topicOffset;
    try {
      const result=await call(READ+"/topics?limit=10&offset="+at);
      if(!current || current.id!==id || current.version!==version || topicOffset!==at) return;
      container.replaceChildren();
      const group=node("fieldset"); group.disabled=!editable; group.append(node("legend","Themen zuordnen"));
      const combined=new Map(result.items.map(t=>[t.id,t]));
      for(const snapshot of snapshots) if(selectedTopics.has(snapshot.id) && !combined.has(snapshot.id)) combined.set(snapshot.id,snapshot);
      for(const topic of combined.values()) {
        const row=checkBox(topic.name,"cm-topic-"+topic.id,selectedTopics.has(topic.id));
        row.querySelector("input").addEventListener("change",(e)=>{if(e.target.checked) selectedTopics.add(topic.id); else selectedTopics.delete(topic.id);});
        row.querySelector("span").append(node("small",topic.categories.map(k=>CATEGORY[k]).join(" · "),"cm-topic-categories"));
        group.append(row);
      }
      if(!combined.size) group.append(node("p","Noch keine kanonischen Themen vorhanden."));
      container.append(group);
      pageNavigation(container,result.has_more,at,(value)=>{topicOffset=value; loadTopics(container,editable,snapshots);});
    } catch(failure) {message(failure.message,true);}
  }
  function captureOfferings(container) {
    offerings=[...container.querySelectorAll(".cm-offering")].map((row)=>({
      title:row.querySelector('[name="offering-title"]').value,
      type:row.querySelector('[name="offering-type"]').value,
      description:row.querySelector('[name="offering-description"]').value || null,
      active:row.querySelector('[name="offering-active"]').checked,
      ordering:Number(row.querySelector('[name="offering-ordering"]').value),
    }));
  }
  function renderOfferings(container, editable) {
    container.replaceChildren();
    const group=node("fieldset"); group.disabled=!editable; group.append(node("legend","Angebote"));
    offerings.forEach((offer,n)=>{
      const row=node("fieldset","","cm-offering"); row.append(node("legend", `Angebot ${n+1}`));
      const title=inputField("Titel",`cm-offering-title-${n}`,offer.title,250,false,true);
      const type=selectField("Typ",TYPES,offer.type,`cm-offering-type-${n}`);
      const description=inputField("Beschreibung",`cm-offering-description-${n}`,offer.description,2000,true);
      const ordering=inputField("Reihenfolge",`cm-offering-ordering-${n}`,String(offer.ordering),4);
      ordering.querySelector("input").type="number"; ordering.querySelector("input").min="0"; ordering.querySelector("input").max="1000"; ordering.querySelector("input").required=true;
      const active=checkBox("Angebot aktiv",`cm-offering-active-${n}`,offer.active);
      [title,type,description,ordering,active].forEach((wrap,i)=>{
        const control=wrap.querySelector("input,textarea,select"); control.name=["offering-title","offering-type","offering-description","offering-ordering","offering-active"][i]; control.setAttribute("form",form.id); row.append(wrap);
      }); group.append(row);
    });
    if(!offerings.length) group.append(node("p","Noch keine Angebote vorhanden."));
    if(editable && offerings.length<100) group.append(button("Angebot hinzufügen",()=>{
      captureOfferings(container); const used=new Set(offerings.map(o=>o.ordering)); let ordering=0; while(used.has(ordering)) ordering++;
      offerings.push({title:"",type:"workshop",description:null,active:true,ordering}); dirty=true; renderOfferings(container,editable);
      container.querySelector(".cm-offering:last-of-type input").focus();
    }));
    container.append(group);
  }
  function contentFromForm() {
    const read=(id)=>root.querySelector("#cm-"+id).value.trim();
    const optional=(id)=>read(id)||null;
    const lines=(id)=>read(id).split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
    captureOfferings(root.querySelector("#cm-panel-offerings"));
    const reference=read("asset-reference");
    return {display_name:read("display_name"),academic_suffix:optional("academic_suffix"),short_intro:read("short_intro"),
      description:optional("description"),professional_background:optional("professional_background"),profile_path:optional("profile_path"),
      target_groups:lines("target_groups"),competencies:lines("competencies"),topic_ids:[...selectedTopics],offerings,
      assets:reference?[{type:"portrait",reference,sha256:read("asset-sha256"),alt_text:read("asset-alt_text"),
        scopes:Object.keys(ENV).filter(e=>root.querySelector("#cm-asset-"+e).checked),active:root.querySelector("#cm-asset-active").checked}]:[]};
  }
  function save() {
    if(!current.capabilities.editable) return;
    for (const control of form.elements) {
      if (!control.checkValidity()) {
        const panel=control.closest('[role="tabpanel"]');
        if (panel) root.querySelector("#"+panel.getAttribute("aria-labelledby")).click();
        control.setAttribute("aria-invalid","true");
        control.focus(); control.reportValidity(); return;
      }
      control.removeAttribute("aria-invalid");
    }
    const content=contentFromForm();
    const labels=[...content.competencies,...content.target_groups];
    if(content.competencies.length>50 || content.target_groups.length>30 || labels.some(x=>x.length>250)
      || new Set(content.competencies.map(x=>x.toLocaleLowerCase())).size!==content.competencies.length
      || new Set(content.target_groups.map(x=>x.toLocaleLowerCase())).size!==content.target_groups.length
      || new Set(content.offerings.map(o=>o.ordering)).size!==content.offerings.length) {
      message("Bitte prüfen Sie doppelte Einträge, Feldlängen und eindeutige Angebotsreihenfolgen.",true); return;
    }
    change(WRITE+"/"+current.id+"/revisions/"+current.revision.id,{expected_version:current.version,content},"PATCH");
  }
  function renderPublication(container, base, version) {
    const revision=current.revision;
    if(revision?.status==="submitted") {
      const list=node("ul");
      for(const approval of revision.approvals) list.append(node("li",APPROVAL[approval.kind]+" · "+date(approval.occurred_at)));
      container.append(node("h3",`Freigaben · Revision ${revision.number}`),list);
      for(const kind of current.capabilities.approvals) {
        container.append(button(APPROVAL[kind],()=>modal(APPROVAL[kind],(box)=>{
          box.append(inputField("Nachweisreferenz","cm-evidence-ref","",200,false,true));
        },(data)=>change(base+"/revisions/"+revision.id+"/approvals",{expected_version:version,kind,evidence_ref:data.get("evidence-ref")}))));
      }
    }
    for(const environment of Object.keys(ENV)) {
      const section=node("section","","cm-publication"); const publication=current.publications[environment];
      section.append(node("h3",ENV[environment]),node("p",PUB[publication?.state || "not_published"]+(publication?` · Revision ${publication.revision_number}`:"")));
      if(current.capabilities.publish.includes(environment)) section.append(action(ENV[environment]+" veröffentlichen",base+"/publications/"+environment,
        {expected_version:version,revision_id:revision.id},"POST","Nur der lokale Veröffentlichungsstatus wird geändert. Ein Website-Release bleibt separat freizugeben."));
      if(current.capabilities.withdraw.includes(environment)) section.append(action(ENV[environment]+" zurückziehen",base+"/publications/"+environment+"/withdraw",
        {expected_version:version},"POST","Dieser Veröffentlichungsstand wird zurückgezogen. Bereits ausgelieferte Webseiten bleiben bis zum separat freigegebenen Release unverändert."));
      container.append(section);
    }
  }
  function renderHistory(container) {
    const revisions=node("section"), history=node("section");
    container.append(revisions,history);
    async function load(target,section,at) {
      const ticket=generation;
      try {
        const result=await call(READ+"/"+current.id+"/"+section+"?limit=10&offset="+at);
        if(ticket!==generation) return;
        target.replaceChildren(node("h3",section==="revisions"?"Profilrevisionen":"Statusverlauf"));
        const list=node("ul","","cm-history");
        for(const item of result.items) {
          const li=node("li");
          if(section==="revisions") li.append(button(`Revision ${item.number} · ${REV[item.status]}`,()=>open(current.id,item.id)));
          else {
            const parts=item.action.split(".");
            const label={create:"Coach angelegt",revision:"Profilrevision erstellt",draft:"Profilentwurf gespeichert",submit:"Profil eingereicht",approve:"Freigabe dokumentiert",revision_abandoned:"Entwurf abgeschlossen",publish:"Veröffentlichung",withdraw:"Veröffentlichung zurückgezogen",lifecycle:"Lifecycle geändert"}[parts[1]] || "Status aktualisiert";
            li.append(node("span",label+(parts[2]?" · "+(LIFE[parts[2]] || ENV[parts[2]] || ""):"")+" · "+date(item.occurred_at)));
          } list.append(li);
        }
        target.append(list); pageNavigation(target,result.has_more,at,(value)=>load(target,section,value));
      }catch(failure){message(failure.message,true);}
    }
    load(revisions,"revisions",0); load(history,"history",0);
  }
  return {root, reset, canLeave, index, async available() {
    try {const response=await request(READ+"?limit=1"); return response.ok;}catch{return false;}
  }};
}
