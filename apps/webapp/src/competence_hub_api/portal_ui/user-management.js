"use strict";

export function createUserManagement({request, reload, prepareInvitation}) {
  const dialog = document.createElement("dialog");
  dialog.className = "user-management-dialog";
  dialog.id = "user-management-dialog";
  dialog.setAttribute("aria-labelledby", "user-management-title");
  dialog.innerHTML = `<form class="dialog-form" id="user-management-form">
    <div class="dialog-heading"><h2 id="user-management-title" tabindex="-1">Zugang verwalten</h2>
    <button type="button" class="button button-quiet" data-close aria-label="Dialog schließen">×</button></div>
    <p id="user-management-identity"></p>
    <div class="field"><label for="user-management-action">Änderung</label>
    <select id="user-management-action"><option value="suspend">Konto sperren</option><option value="deactivate">Konto deaktivieren</option>
    <option value="enable">Konto wieder freigeben</option><option value="set_role">Rolle und Zuordnung ändern</option>
    <option value="revoke_invitation">Offene Einladung widerrufen</option></select></div>
    <div class="field" id="user-management-role-field" hidden><label for="user-management-role">Neue einzelne Rolle</label>
    <select id="user-management-role"><option value="internal">Intern</option><option value="calendar_reviewer">Kalenderprüfung</option>
    <option value="coach">Coach</option><option value="admin">Administration</option></select></div>
    <div class="field" id="user-management-coach-field" hidden><label for="user-management-coach">Bestätigte Coach-UUID</label>
    <input id="user-management-coach" list="coach-mapping-options" autocomplete="off" maxlength="36"></div>
    <p>Bestehende Sitzungen und offene Zugangslinks werden beendet. Die Anmeldung muss danach erneut erfolgen. Eine noch ausstehende Erstaktivierung kann hier nicht übersprungen werden.</p>
    <label class="check-row"><input id="user-management-confirm" type="checkbox" required>Identität, Rolle und gegebenenfalls Coachzuordnung sind geprüft.</label>
    <p id="user-management-error" class="form-error" role="alert" tabindex="-1" hidden></p>
    <div class="button-row"><button type="submit" class="button button-primary">Änderung übernehmen</button>
    <button type="button" class="button button-secondary" data-close>Abbrechen</button>
    <button type="button" class="text-button" id="user-management-reload" hidden>Aktuellen Kontostand laden</button></div>
    <details><summary>Administrative Änderungen</summary><button type="button" class="text-button" id="user-management-audit-load">Letzte Änderungen laden</button>
    <ul id="user-management-audit" aria-live="polite"></ul></details>
    </form>`;
  document.body.append(dialog);
  const get = id => dialog.querySelector(`#${id}`);
  let selected = null, trigger = null, busy = false;
  const errors = {
    reauthentication_required:"Bitte melden Sie sich für diese Änderung erneut mit MFA an.",
    account_version_conflict:"Der Kontostand wurde zwischenzeitlich geändert. Bitte laden Sie ihn neu.",
    account_self_protection:"Der eigene administrative Zugang wird hier nicht geändert.",
    last_admin_protection:"Der letzte aktive Administrator muss erhalten bleiben.",
    activation_required:"Für dieses Konto ist zuerst die persönliche Erstaktivierung erforderlich.",
    coach_mapping_conflict:"Diese Coachzuordnung ist nicht verfügbar oder bereits anderweitig vergeben.",
    account_scope_conflict:"Diese Änderung passt nicht zum aktuellen Zugang.",
  };
  function updateFields() {
    const role = get("user-management-action").value === "set_role";
    const coach = role && get("user-management-role").value === "coach";
    get("user-management-role-field").hidden = !role;
    get("user-management-coach-field").hidden = !coach;
    get("user-management-coach").required = coach;
    get("user-management-confirm").checked = false;
  }
  function close() { if (busy) return; dialog.close(); if (trigger?.isConnected) trigger.focus(); }
  for (const button of dialog.querySelectorAll("[data-close]")) button.addEventListener("click", close);
  dialog.addEventListener("cancel", event => {event.preventDefault();close();});
  dialog.addEventListener("keydown", event => {
    if (event.key !== "Tab") return;
    const controls=Array.from(dialog.querySelectorAll("button,input,select,textarea,summary,a[href],[tabindex='0']"))
      .filter(node => !node.disabled && node.getClientRects().length);
    const first=controls[0],last=controls.at(-1),active=document.activeElement;
    if (!first) {event.preventDefault();return;}
    if (event.shiftKey && (active===first || !controls.includes(active))) {
      event.preventDefault();last.focus();
    } else if (!event.shiftKey && active===last) {event.preventDefault();first.focus();}
  });
  get("user-management-action").addEventListener("change", updateFields);
  get("user-management-role").addEventListener("change", updateFields);
  get("user-management-reload").addEventListener("click", async () => {close();await reload();});
  get("user-management-audit-load").addEventListener("click", async () => {
    const target = selected;
    const list = get("user-management-audit"); list.replaceChildren();
    try {
      const response = await request(`/api/v1/admin/users/${target.id}/audit`);
      if (!response.ok) throw new Error("unavailable");
      const data = await response.json(); if (selected !== target || !dialog.open) return;
      for (const entry of data.items) {
        const row = document.createElement("li");
        const names = {suspend:"Konto gesperrt", deactivate:"Konto deaktiviert", enable:"Konto freigegeben",set_role:"Rolle/Zuordnung geändert",revoke_invitation:"Einladung widerrufen"};
        row.textContent = `${new Date(entry.occurred_at).toLocaleString("de-DE")} · ${names[entry.action.split(".").at(-1)] || entry.action} · ${entry.outcome}`;
        list.append(row);
      }
      if (!data.items.length) list.textContent = "Noch keine administrativen Änderungen vorhanden.";
    } catch { if (selected === target) list.textContent = "Änderungen derzeit nicht verfügbar."; }
  });
  get("user-management-form").addEventListener("submit", async event => {
    event.preventDefault(); if (busy || !selected) return;
    const target = selected;
    const error = get("user-management-error"); error.hidden = true;
    const action = get("user-management-action").value;
    const payload = {action, expected_version:selected.version};
    if (action === "set_role") {
      payload.role = get("user-management-role").value;
      if (payload.role === "coach") payload.coach_id = get("user-management-coach").value.trim();
    }
    busy = true; const submit = dialog.querySelector("[type=submit]"); submit.disabled = true;
    try {
      const response = await request(`/api/v1/admin/users/${target.id}`, {method:"PATCH",csrf:"session",body:payload});
      if (selected !== target || !dialog.open) return;
      if (!response.ok) {
        const problem = await response.json(); error.textContent = errors[problem.code] || "Änderung nicht möglich. Bitte Berechtigung und Angaben prüfen.";
        get("user-management-reload").hidden = problem.code !== "account_version_conflict";
        error.hidden = false; error.focus(); return;
      }
      busy = false; close(); await reload();
    } catch { if(selected === target && dialog.open) {error.textContent = "Änderung konnte nicht bestätigt werden. Bitte den Kontostand prüfen, bevor Sie erneut speichern.";error.hidden=false;error.focus();} }
    finally {if(selected === target) {busy = false;submit.disabled = false;}}
  });
  return {
    reset() {
      selected=null;trigger=null;busy=false;if (dialog.open) dialog.close();
      get("user-management-form").reset();get("user-management-identity").textContent="";
      get("user-management-audit").replaceChildren();get("user-management-error").textContent="";
      dialog.querySelector("[type=submit]").disabled=false;
    },
    appendActions(row, user, actorId) {
      const actions = document.createElement("div"); actions.className = "button-row";
      const button = document.createElement("button"); button.type="button";button.className="button button-secondary";button.textContent="Zugang verwalten";
      button.disabled = user.id === actorId;
      if (button.disabled) button.title="Der eigene administrative Zugang bleibt unverändert.";
      button.addEventListener("click", () => {
        selected=user;trigger=button;
        get("user-management-form").reset();get("user-management-error").hidden=true;get("user-management-reload").hidden=true;
        get("user-management-audit").replaceChildren();dialog.querySelector("details").open=false;
        get("user-management-identity").textContent=`${user.display_name} · ${user.email}`;
        get("user-management-role").value=user.roles[0] || "internal";
        get("user-management-coach").value=user.coach_id || "";
        get("user-management-action").value=user.status==="pending_activation" ? "revoke_invitation" : "suspend";
        updateFields();dialog.showModal();get("user-management-title").focus();
      });actions.append(button);
      if (user.status === "pending_activation") {
        const invite = document.createElement("button");invite.type="button";invite.className="text-button";invite.textContent="Einladung neu vorbereiten";
        invite.addEventListener("click", () => prepareInvitation(user));actions.append(invite);
      }
      row.append(actions);
    },
  };
}
