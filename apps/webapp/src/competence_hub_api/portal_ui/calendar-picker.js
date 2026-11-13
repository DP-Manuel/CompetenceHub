// Datepicker1.3.4 owns calendar rendering/month arithmetic. This adapter keeps
// the API's Berlin instants separate from date-only UI and supplies day focus.
export function dateOnly(value) {
  const found=/^(\d{2})\.(\d{2})\.(\d{4})$/.exec(String(value||'').trim());
  if(!found)return null;
  const [day,month,year]=found.slice(1).map(Number),date=new Date(year,month-1,day);
  return year>=2000 && date.getFullYear()===year && date.getMonth()===month-1 && date.getDate()===day?date:null;
}
const label=date=>`${String(date.getDate()).padStart(2,'0')}.${String(date.getMonth()+1).padStart(2,'0')}.${date.getFullYear()}`;
export function createCalendarPicker(form,inputs) {
  const panel=form.querySelector('#calendar-date-panel'),mount=panel.querySelector('[data-datepicker]');
  const heading=panel.querySelector('[data-picker-heading]');let active=null,picker=null,selectionFocus=false;
  const captions={starts_at:'Beginn wählen',ends_at:'Ende wählen',decision_deadline:'Entscheidungsfrist wählen'};
  const key=date=>date?Date.UTC(date.getFullYear(),date.getMonth(),date.getDate()):null;
  function decorate() {
    mount.querySelectorAll('.prev-btn').forEach(e=>e.setAttribute('aria-label','Vorheriger Monat'));
    mount.querySelectorAll('.next-btn').forEach(e=>e.setAttribute('aria-label','Nächster Monat'));
    const focus=mount.querySelector('.datepicker-cell.focused:not(.disabled)')||mount.querySelector('.datepicker-cell.day:not(.disabled)');
    mount.querySelectorAll('.datepicker-cell.day').forEach(cell=>{
      const date=new Date(Number(cell.dataset.date)),dateLabel=label(date);
      cell.setAttribute('role','button');cell.tabIndex=cell===focus?0:-1;
      const ends=[cell.classList.contains('cal-range-start')?'Beginn':'',cell.classList.contains('cal-range-end')?'Ende':''].filter(Boolean);
      const edge=ends.length?' · '+ends.join(' und '):'';
      cell.setAttribute('aria-label',dateLabel+edge);cell.setAttribute('aria-pressed',String(cell.classList.contains('selected')||Boolean(edge)));
      cell.setAttribute('aria-disabled',String(cell.classList.contains('disabled')));
    });
  }
  if(window.Datepicker) {
    mount.addEventListener('click',event=>{if(event.target.closest('.datepicker-cell.day'))selectionFocus=true;},true);
    picker=new window.Datepicker(mount,{language:'de',format:'dd.mm.yyyy',weekStart:1,maxView:0,
      buttonClass:'calendar-month-button',prevArrow:'‹',nextArrow:'›',
      beforeShowDay(date){
        if(active==='decision_deadline')return {};
        const current=key(date),start=key(dateOnly(inputs.starts_at.value)),end=key(dateOnly(inputs.ends_at.value));
        return {classes:[current===start?'cal-range-start':'',current===end?'cal-range-end':'',
          start!==null && end!==null && current>start && current<end?'cal-range-middle':''].filter(Boolean).join(' ')};
      }});
    mount.addEventListener('changeDate',()=>{
      if(!active || panel.hidden)return;
      const date=picker.getDate();if(!date)return;
      inputs[active].value=label(date);
      if(active==='starts_at' && !inputs.ends_at.value)inputs.ends_at.value=label(date);
      inputs[active].dispatchEvent(new Event('input',{bubbles:true}));
      picker.refresh('picker',true);decorate();
      if(selectionFocus){selectionFocus=false;queueMicrotask(()=>{decorate();mount.querySelector(`[data-date="${+date}"]`)?.focus({preventScroll:true});});}
      panel.querySelector('[data-picker-selection]').textContent=inputs.starts_at.value && inputs.ends_at.value && active!=='decision_deadline'
        ?`Beginn ${inputs.starts_at.value} · Ende ${inputs.ends_at.value}`:`Ausgewählt: ${label(date)}`;
    });
    mount.addEventListener('click',()=>queueMicrotask(decorate));
    mount.addEventListener('keydown',event=>{
      const cell=event.target.closest('.datepicker-cell.day');
      if(!cell)return;
      if(['Enter',' '].includes(event.key)){event.preventDefault();event.stopPropagation();cell.click();return;}
      const step={ArrowRight:1,ArrowLeft:-1,ArrowDown:7,ArrowUp:-7,Home:-(new Date(Number(cell.dataset.date)).getDay()+6)%7,
        End:6-(new Date(Number(cell.dataset.date)).getDay()+6)%7}[event.key];
      if(step!==undefined) {
        event.preventDefault();event.stopPropagation();const date=new Date(Number(cell.dataset.date));date.setDate(date.getDate()+step);
        let next=mount.querySelector(`[data-date="${+date}"]`);
        if(!next){mount.querySelector(step>0?'.next-btn':'.prev-btn').click();next=mount.querySelector(`[data-date="${+date}"]`);}
        if(next){mount.querySelectorAll('.datepicker-cell.day').forEach(e=>e.tabIndex=-1);next.tabIndex=0;next.focus();}
      } else if(['PageDown','PageUp'].includes(event.key)) {
        event.preventDefault();event.stopPropagation();mount.querySelector(event.key==='PageDown'?'.next-btn':'.prev-btn').click();decorate();mount.querySelector('.datepicker-cell.day[tabindex="0"]')?.focus();
      }
    },true);
  }
  function hide() {panel.hidden=true;form.querySelectorAll('[data-pick-date]').forEach(button=>button.setAttribute('aria-expanded','false'));}
  form.querySelectorAll('[data-pick-date]').forEach(button=>button.addEventListener('click',()=>{
    if(!picker)return;
    active=button.dataset.pickDate;panel.hidden=false;heading.textContent=captions[active];
    form.querySelectorAll('[data-pick-date]').forEach(item=>item.setAttribute('aria-expanded',String(item===button)));
    const current=dateOnly(inputs[active].value);
    picker.setDate(current||{clear:true});picker.refresh('picker',true);decorate();
    panel.scrollIntoView({block:'nearest'});mount.querySelector('.datepicker-cell.day[tabindex="0"]')?.focus();
  }));
  panel.querySelector('[data-close-picker]').addEventListener('click',()=>{hide();inputs[active]?.focus();});
  panel.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();event.stopPropagation();hide();inputs[active]?.focus();}},true);
  return {hide,refresh(){if(picker){picker.refresh('picker',true);decorate();}}};
}
