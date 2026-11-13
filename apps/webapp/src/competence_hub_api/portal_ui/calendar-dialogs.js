// Calendar-only cancellation, including a pending save; no stored draft deletion.
export function createCalendarDialogs({dialogs,confirmation,discard,closed}) {
  const baselines=new WeakMap(), openers=new WeakMap(), fromBack=new WeakSet();
  let question=null, removal=null, removed=null, navigating=false;
  const snapshot=form=>JSON.stringify([...form.elements].filter(e=>e.name &&
    (!['radio','checkbox'].includes(e.type)||e.checked)).map(e=>[e.name,e.value]));
  const dirty=dialog=>dialog.open && baselines.has(dialog.querySelector('form')) &&
    snapshot(dialog.querySelector('form'))!==baselines.get(dialog.querySelector('form'));
  function ask(dialog) {
    if(question)return question.promise;
    const origin=document.activeElement;
    let resolve;
    const promise=new Promise(done=>{resolve=done;});
    question={promise,resolve,origin};
    confirmation.querySelector('[data-saving-note]').hidden=dialog.querySelector('form').getAttribute('aria-busy')!=='true';
    confirmation.showModal();confirmation.querySelector('[data-keep-editing]').focus();
    return promise;
  }
  function answer(leave) {
    if(!question)return;
    const current=question;question=null;confirmation.close();
    if(!leave && current.origin?.isConnected)current.origin.focus();
    current.resolve(leave);
  }
  confirmation.querySelector('[data-keep-editing]').addEventListener('click',()=>answer(false));
  confirmation.querySelector('[data-discard-changes]').addEventListener('click',()=>answer(true));
  confirmation.addEventListener('cancel',event=>{event.preventDefault();answer(false);});
  confirmation.addEventListener('click',event=>{if(event.target===confirmation)answer(false);});
  async function close(dialog,{back=false}={}) {
    if(!dialog.open)return true;
    if((dirty(dialog)||dialog.querySelector('form').getAttribute('aria-busy')==='true') && !await ask(dialog))return false;
    // Repeated clicks share one decision; only the first completion closes.
    if(!dialog.open)return true;
    discard(dialog);baselines.delete(dialog.querySelector('form'));
    if(back)fromBack.add(dialog);
    dialog.close();return true;
  }
  for(const dialog of dialogs) {
    dialog.addEventListener('cancel',event=>{event.preventDefault();void close(dialog);});
    dialog.addEventListener('close',()=>{
      baselines.delete(dialog.querySelector('form'));
      if(history.state?.cal1Dialog?.id===dialog.id && !fromBack.has(dialog)) {
        removal=new Promise(done=>{removed=done;});history.back();
      }
      fromBack.delete(dialog);
      const origin=openers.get(dialog);if(origin?.isConnected)origin.focus();
      closed(dialog);
    });
  }
  addEventListener('popstate',async()=>{
    if(removed){removed();removed=null;removal=null;return;}
    const dialog=dialogs.find(item=>item.open);
    if(!dialog || navigating)return;
    navigating=true;
    try {
      if(!await close(dialog,{back:true}))history.pushState({...history.state,cal1Dialog:{id:dialog.id,key:crypto.randomUUID()}},'');
    } finally {navigating=false;}
  });
  addEventListener('beforeunload',event=>{
    if(dialogs.some(dirty)){event.preventDefault();event.returnValue='';}
  });
  return {dirty,close,
    forget(form){baselines.delete(form);if(question)answer(false);},
    remember(form){baselines.set(form,snapshot(form));},
    async open(dialog,focus) {
      if(removal)await removal;
      openers.set(dialog,document.activeElement);
      history.pushState({...history.state,cal1Dialog:{id:dialog.id,key:crypto.randomUUID()}},'');
      dialog.showModal();focus.focus();
    },
  };
}
