/* Global "Find a tool" search. Discovery only: it indexes existing tool panels, workspace
   tasks and the Engineering catalog, then routes to them through public APIs. It never runs a
   computation, clears inputs or duplicates a tool implementation. SPDX-License-Identifier: MIT. */
(()=>{'use strict';
const M=window.MathStudio,bar=document.querySelector('.workspace-bar'),main=document.querySelector('main');
if(!M?.advanced?.mode||!bar||!main)return;
const MAX_RESULTS=12;
// Small, data-only synonym map: query word -> extra terms that also count as a match.
const SYNONYMS=Object.freeze({
 integral:['integration','quadrature','simpson'],integrate:['integral','integration','quadrature'],
 root:['brent','roots','bracket','nonlinear'],zero:['root','brent'],
 units:['unit','conversion','dimensional'],unit:['conversion','dimensional'],convert:['conversion','unit'],
 beam:['structural','deflection'],structure:['beam','structural'],structures:['beam','structural'],
 stats:['statistics','distribution','hypothesis','descriptive'],statistics:['distribution','descriptive'],
 spline:['interpolation','pchip'],interpolate:['interpolation'],
 ode:['differential','rk4','rk45','initial-value'],differential:['ode'],
 lp:['linear programming','optimization','simplex'],optimize:['optimization','minimization','minimize'],
 curve:['implicit','polar','parametric'],curves:['implicit','polar','parametric'],
 plot:['graph'],chart:['graph','plot'],fft:['spectrum','fourier'],fourier:['fft','spectrum'],
 eigen:['eigenvalues','eigenanalysis'],excel:['xlsx'],spreadsheet:['table','xlsx'],
 matrices:['matrix'],complex:['argand'],control:['bode','nyquist','locus']
});
const PANEL_MODES=Object.freeze({'numerical-panel':'editor','symbolic-panel':'editor'});
const norm=s=>String(s??'').replace(/\s+/g,' ').trim();
const fold=s=>norm(s).toLocaleLowerCase();
const words=s=>fold(s).split(/[^\p{L}\p{N}]+/u).filter(Boolean);

function workspaceLabel(mode){
 const tab=bar.querySelector('button[data-workspace="'+mode+'"]');
 return tab?norm(tab.textContent).replace(/^[^\p{L}\p{N}]+/u,''):mode||'All workspaces';
}
// The workspace that shows an element, from its enclosing workspace panel.
function modeOf(el){
 const modes=new Set([...bar.querySelectorAll('button[data-workspace]')].map(b=>b.dataset.workspace));
 for(let n=el;n&&n!==main;n=n.parentElement){
  if(n.id&&PANEL_MODES[n.id])return PANEL_MODES[n.id];
  const m=n.id&&n.id.endsWith('-panel')?n.id.slice(0,-6):'';
  if(m&&modes.has(m))return m;
  // Unnamed top-level panels belong to the Equation station (editor, preview, Python).
  if(n.parentElement===main&&n.tagName==='SECTION'&&n.classList.contains('panel')&&!n.id)return 'editor';
 }
 return null; // Shared panels that are visible in every workspace.
}
function ownText(details,selector,limit){
 let text='';
 for(const node of details.querySelectorAll(selector)){
  if(node.closest('details')!==details)continue;
  text+=' '+norm(node.textContent);if(text.length>limit)break;
 }
 return text.slice(0,limit);
}

let index=[],byId=new Map();
function build(){
 const items=[],byPanel=new Map();
 for(const d of main.querySelectorAll('details[id]')){
  if(d.closest('#tool-search'))continue;
  const summary=d.querySelector(':scope>summary');if(!summary)continue;
  const title=norm(summary.textContent).replace(/^[^\p{L}\p{N}]+/u,'');if(!title)continue;
  const mode=modeOf(d);
  const item={id:'panel:'+d.id,kind:'panel',title,mode,status:'available',targetId:d.id,task:null,
   nested:Boolean(d.parentElement?.closest('details[id]')),
   keywords:[d.id.replace(/-/g,' '),ownText(d,'h2,h3,h4,legend,option',1500)]};
  items.push(item);byPanel.set(d.id,item);
 }
 for(const t of M.workspaceTasks?.list?.()||[]){
  const target=t.selector?document.querySelector(t.selector):null;
  const merged=target?.id?byPanel.get(target.id):null;
  if(merged&&merged.mode===t.mode){merged.keywords.push(t.label,t.description);merged.task=t;continue;}
  items.push({id:'task:'+t.mode+':'+t.key,kind:'task',title:t.label,mode:t.mode,status:'available',
   targetId:target?.id||null,task:t,keywords:[t.description]});
 }
 for(const t of M.engineeringCatalog?.tools||[]){
  // Catalog entries stay separate: their single route may select a preset (for example a beam animation).
  const tags=[t.tags,t.description,...t.disciplines];
  items.push({id:'catalog:'+t.id,kind:'catalog',title:t.title,mode:t.route?.mode||'engineering',
   status:t.status==='available'?'available':'planned',catalogId:t.id,keywords:['engineering',...tags]});
 }
 for(const item of items){
  item.workspace=item.kind==='catalog'&&item.status==='available'&&item.mode!=='engineering'?'Engineering Toolbox · opens in '+workspaceLabel(item.mode):workspaceLabel(item.mode);
  item.titleFolded=fold(item.title);item.titleWords=words(item.title);
  item.haystack=fold([item.title,item.workspace,...item.keywords].join(' '));
  item.hayWords=words(item.haystack);
 }
 index=items;byId=new Map(items.map(i=>[i.id,i]));return items.length;
}
function contains(text,list,term){
 // Very short terms (for example "lp") must start a word to avoid noisy substring hits.
 return term.length<=2?list.some(w=>w.startsWith(term)):text.includes(term);
}
function search(query){
 const terms=words(query);if(!terms.length)return [];
 if(!index.length)build();
 const q=fold(query),out=[];
 for(const item of index){
  let score=0,ok=true;
  for(const term of terms){
   const variants=[[term,1],...(SYNONYMS[term]||[]).map(s=>[fold(s),0.6])];
   let best=0;
   for(const [v,weight] of variants){
    let s=0;
    if(contains(item.titleFolded,item.titleWords,v)){s=10;if(item.titleWords.some(w=>w.startsWith(v)))s+=4;}
    else if(contains(item.haystack,item.hayWords,v))s=3;
    best=Math.max(best,s*weight);
   }
   if(!best){ok=false;break;}
   score+=best;
  }
  if(!ok)continue;
  if(item.titleFolded.startsWith(q))score+=5;
  if(item.kind==='panel')score+=item.nested?-2:1; // Prefer whole tool panels over sub-sections and routes.
  if(item.status==='planned')score-=4;
  out.push([score,item]);
 }
 out.sort((a,b)=>b[0]-a[0]||a[1].title.localeCompare(b[1].title));
 return out.slice(0,MAX_RESULTS).map(([,item])=>item);
}

function revealPanel(id){
 const el=document.getElementById(id);if(!el)return false;
 if(el.tagName==='DETAILS')el.open=true;
 for(let n=el.parentElement;n;n=n.parentElement)if(n.tagName==='DETAILS')n.open=true;
 const reduce=window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
 el.scrollIntoView({block:'start',behavior:reduce?'auto':'smooth'});
 const focusable=el.querySelector(':scope>summary')||el.querySelector('input,select,textarea,button');
 focusable?.focus({preventScroll:true});
 return true;
}
function openItem(item){
 if(!item||item.status!=='available')return false;
 if(item.kind==='catalog')return Boolean(M.engineeringCatalog?.open?.(item.catalogId));
 if(item.mode)M.advanced.mode(item.mode);
 // Wait for workspace observers to switch the task picker before selecting or revealing.
 requestAnimationFrame(()=>{
  if(item.task&&M.workspaceTasks?.current?.()===item.task.mode)M.workspaceTasks.select(item.task.key,false);
  if(item.targetId)revealPanel(item.targetId);
  else if(item.task)document.getElementById('workspace-task-select')?.focus({preventScroll:true});
 });
 return true;
}

const css=document.createElement('style');
css.textContent=
 '#tool-search{position:relative;flex:1 1 300px;min-width:0;display:flex;align-items:center;gap:8px;margin-left:auto;padding:0 2px}'+
 '#tool-search label{font:750 12px system-ui,sans-serif;color:#435c9c;white-space:nowrap}'+
 '#tool-search-input{flex:1 1 auto;width:100%;min-width:0;min-height:40px;box-sizing:border-box;padding:8px 12px;border:1px solid #c9d4e8;border-radius:10px;background:#f8faff;color:#1f3157;font:14px system-ui,sans-serif}'+
 '#tool-search-input:focus-visible{outline:3px solid #93a5ed;outline-offset:2px;background:#fff}'+
 '#tool-search kbd{font:11px ui-monospace,monospace;border:1px solid #c9d4e8;border-radius:5px;padding:1px 5px;color:#596987;background:#fff}'+
 '#tool-search-popup{position:absolute;top:calc(100% + 6px);left:0;right:0;z-index:60;background:#fff;border:1px solid #cdd7e8;border-radius:12px;box-shadow:0 12px 32px #1c30572a;padding:4px;max-height:min(62vh,460px);overflow:auto;box-sizing:border-box}'+
 '#tool-search-list{list-style:none;margin:0;padding:0}'+
 '#tool-search-list [role=option]{display:flex;align-items:center;gap:8px;min-height:40px;box-sizing:border-box;justify-content:center;padding:7px 10px;border-radius:8px;cursor:pointer;overflow-wrap:anywhere}'+
 '#tool-search-list .ts-text{display:flex;flex-direction:column;gap:2px;flex:1 1 auto;min-width:0}'+
 '#tool-search-list [role=option] strong{font-size:13px;color:#1f3157}'+
 '#tool-search-list [role=option] span{font-size:11px;color:#596987}'+
 '#tool-search-list [role=option][aria-disabled=true]{cursor:default}'+
 '#tool-search-list [role=option][aria-disabled=true] strong{color:#6b7891}'+
 '#tool-search-list [role=option]:hover{background:#f1f5fd}'+
 '#tool-search-list [role=option][aria-selected=true]{background:#e6edfc;outline:2px solid #5b74d6;outline-offset:-2px}'+
 '#tool-search .ts-badge{display:inline-block;margin-left:6px;padding:0 6px;border-radius:999px;background:#fdf1de;color:#7a4b00;font-size:10px;font-weight:700}'+
 '#tool-search .ts-pin{flex:0 0 auto;min-width:40px;min-height:40px;border:1px solid transparent;border-radius:8px;background:transparent;color:#596987;font:18px system-ui,sans-serif;cursor:pointer}'+
 '#tool-search .ts-pin:hover{background:#e6edfc;border-color:#c9d4e8}'+
 '#tool-search .ts-pin[aria-pressed=true]{color:#a35b00}'+
 '#tool-search .ts-pin:focus-visible,#tool-search .ts-browse summary:focus-visible,#tool-search .ts-browse-item:focus-visible{outline:3px solid #93a5ed;outline-offset:1px}'+
 '#tool-search .ts-group-label{padding:8px 10px 2px;font:750 11px system-ui,sans-serif;color:#435c9c;text-transform:uppercase;letter-spacing:.04em}'+
 '#tool-search .ts-group-list{list-style:none;margin:0;padding:0}'+
 '#tool-search .ts-browse{border-top:1px solid #e3e9f4;margin-top:4px;padding-top:2px}'+
 '#tool-search .ts-browse summary{display:flex;align-items:center;min-height:40px;box-sizing:border-box;padding:6px 10px;border-radius:8px;cursor:pointer;font:700 13px system-ui,sans-serif;color:#1f3157}'+
 '#tool-search .ts-browse summary:hover{background:#f1f5fd}'+
 '#tool-search .ts-browse-group{margin-left:8px}'+
 '#tool-search .ts-browse-group>summary{font-weight:650;color:#435c9c}'+
 '#tool-search .ts-browse-group ul{list-style:none;margin:0;padding:0 0 4px 8px}'+
 '#tool-search .ts-browse-item{display:block;width:100%;min-height:40px;box-sizing:border-box;padding:6px 10px;border:0;border-radius:8px;background:transparent;color:#1f3157;font:13px system-ui,sans-serif;text-align:left;cursor:pointer;overflow-wrap:anywhere}'+
 '#tool-search .ts-browse-item:hover{background:#f1f5fd}'+
 '#tool-search-empty{margin:0;padding:10px;font-size:12px;color:#596987}'+
 '#tool-search .ts-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}'+
 '@media(max-width:760px){#tool-search{grid-column:1/-1;flex-basis:100%;margin-left:0}#tool-search kbd{display:none}}';
document.head.append(css);

const wrap=document.createElement('div');wrap.id='tool-search';wrap.setAttribute('role','search');
const label=document.createElement('label');label.htmlFor='tool-search-input';label.textContent='Find a tool';
const input=document.createElement('input');
Object.assign(input,{id:'tool-search-input',type:'search',autocomplete:'off',spellcheck:false,placeholder:'Search tools: integral, matrix, beam, units…'});
input.setAttribute('role','combobox');input.setAttribute('aria-autocomplete','list');
input.setAttribute('aria-expanded','false');input.setAttribute('aria-controls','tool-search-list');
input.setAttribute('aria-describedby','tool-search-hint');input.setAttribute('aria-keyshortcuts','/ Control+K Meta+K Alt+P');
const kbd=document.createElement('kbd');kbd.textContent='/';kbd.setAttribute('aria-hidden','true');
const hint=document.createElement('span');hint.id='tool-search-hint';hint.className='ts-sr';
hint.textContent='Press slash or Control+K to search. Use arrow keys to choose a result and Enter to open it. Alt+P pins or unpins the chosen tool. With an empty field, recent and pinned tools are listed; press Tab to browse all tools by workspace.';
const popup=document.createElement('div');popup.id='tool-search-popup';popup.hidden=true;
const list=document.createElement('ul');list.id='tool-search-list';list.setAttribute('role','listbox');list.setAttribute('aria-label','Matching tools');
const empty=document.createElement('p');empty.id='tool-search-empty';empty.hidden=true;
empty.textContent='No matching tools. Try another word, such as root, plot or table.';
const status=document.createElement('p');status.id='tool-search-status';status.className='ts-sr';
status.setAttribute('role','status');status.setAttribute('aria-live','polite');
const browse=document.createElement('details');browse.className='ts-browse';browse.hidden=true;
const browseSummary=document.createElement('summary');browseSummary.textContent='Browse all tools';
const browseBody=document.createElement('div');browse.append(browseSummary,browseBody);
popup.append(list,empty,browse);wrap.append(label,input,kbd,hint,popup,status);bar.append(wrap);

// Recent and pinned tools come from the optional per-viewer preferences module (no storage here).
const NO_PREFS=Object.freeze({recent:()=>[],pinned:()=>[],isPinned:()=>false,addRecent:()=>false,setPinned:()=>false,togglePin:()=>false,limits:{recent:8,pins:20}});
const prefs=M.toolPrefs||NO_PREFS;
const openable=id=>byId.get(id)?.status==='available';
function remember(item){prefs.addRecent(item.id,openable);}
let results=[],opts=[],active=-1,quick=false;
function setActive(i){
 active=results.length?Math.max(-1,Math.min(i,results.length-1)):-1;
 for(const [n,opt] of opts.entries())opt.setAttribute('aria-selected',String(n===active));
 if(active>=0){input.setAttribute('aria-activedescendant',opts[active].id);opts[active].scrollIntoView({block:'nearest'});}
 else input.removeAttribute('aria-activedescendant');
}
function close(){popup.hidden=true;input.setAttribute('aria-expanded','false');setActive(-1);}
function syncPin(button,item){
 const on=prefs.isPinned(item.id);
 button.setAttribute('aria-pressed',String(on));
 button.setAttribute('aria-label',(on?'Unpin ':'Pin ')+item.title);button.title=on?'Unpin tool':'Pin tool';
 button.textContent=on?'★':'☆';
}
function makeOption(item,n){
 const opt=document.createElement('li');opt.id='tool-search-opt-'+n;opt.setAttribute('role','option');
 opt.setAttribute('aria-selected','false');opt.dataset.toolId=item.id;
 const text=document.createElement('div');text.className='ts-text';
 const name=document.createElement('strong');name.textContent=item.title;
 if(item.status==='planned'){
  opt.setAttribute('aria-disabled','true');
  const badge=document.createElement('span');badge.className='ts-badge';badge.textContent='Planned';name.append(badge);
 }
 const where=document.createElement('span');where.textContent=item.status==='planned'?item.workspace+' · not yet available':item.workspace;
 text.append(name,where);opt.append(text);
 if(item.status==='available'){
  // Out of the Tab order: the input keeps focus and Alt+P is the keyboard equivalent.
  const pin=document.createElement('button');pin.type='button';pin.className='ts-pin';pin.tabIndex=-1;
  syncPin(pin,item);
  pin.addEventListener('click',e=>{e.stopPropagation();togglePin(n);});
  opt.append(pin);
 }
 opt.addEventListener('click',()=>choose(n));
 opts.push(opt);return opt;
}
function quickGroup(key,title,items){
 const group=document.createElement('li');group.setAttribute('role','group');group.dataset.group=key;
 const head=document.createElement('div');head.id='tool-search-group-'+key;head.className='ts-group-label';
 head.setAttribute('role','presentation');head.textContent=title;
 group.setAttribute('aria-labelledby',head.id);
 const inner=document.createElement('ul');inner.className='ts-group-list';inner.setAttribute('role','none');
 for(const item of items){results.push(item);inner.append(makeOption(item,results.length-1));}
 group.append(head,inner);return group;
}
function renderQuick(){
 if(!index.length)build();
 quick=true;results=[];opts=[];list.replaceChildren();
 const recent=prefs.recent(openable).map(id=>byId.get(id)),pinned=prefs.pinned(openable).map(id=>byId.get(id));
 if(recent.length)list.append(quickGroup('recent','Recent tools',recent));
 if(pinned.length)list.append(quickGroup('pinned','Pinned tools',pinned));
 list.setAttribute('aria-label','Recent and pinned tools');
 empty.textContent='No recent or pinned tools yet. Type to search, or browse all tools below.';
 empty.hidden=results.length>0;list.hidden=!results.length;browse.hidden=false;
 popup.hidden=false;input.setAttribute('aria-expanded','true');
 setActive(-1);
}
function render(){
 if(!norm(input.value)){
  if(document.activeElement===input)renderQuick();else{list.replaceChildren();results=[];opts=[];close();}
  status.textContent='';return;
 }
 quick=false;results=search(input.value);opts=[];list.replaceChildren();
 list.setAttribute('aria-label','Matching tools');
 empty.textContent='No matching tools. Try another word, such as root, plot or table.';
 browse.hidden=true;
 for(const [n,item] of results.entries())list.append(makeOption(item,n));
 empty.hidden=results.length>0;list.hidden=!results.length;
 popup.hidden=false;input.setAttribute('aria-expanded','true');
 setActive(results.findIndex(r=>r.status==='available'));
 status.textContent=results.length?results.length+(results.length===1?' tool':' tools')+' found.':'No matching tools.';
}
function togglePin(n){
 const item=results[n];if(!item||item.status!=='available')return;
 const on=prefs.togglePin(item.id,openable);
 if(on===null){status.textContent='You can pin up to '+prefs.limits.pins+' tools. Unpin one first.';return;}
 status.textContent=(on?'Pinned ':'Unpinned ')+item.title+'.';
 if(quick){const keep=active;renderQuick();setActive(Math.min(keep,results.length-1));}
 else for(const opt of opts)if(opt.dataset.toolId===item.id){const b=opt.querySelector('.ts-pin');if(b)syncPin(b,item);}
}
function choose(n){
 const item=results[n];if(!item)return;
 if(item.status!=='available'){status.textContent=item.title+' is planned and not yet available.';setActive(n);return;}
 close();input.value='';status.textContent='Opening '+item.title+'.';
 if(openItem(item))remember(item);
}
// "Browse all tools": every openable indexed tool, grouped by workspace, built when expanded.
function browseGroups(){
 if(!index.length)build();
 const order=[...bar.querySelectorAll('button[data-workspace]')].map(b=>b.dataset.workspace);
 const groups=new Map(order.map(mode=>[mode,[]]));
 for(const item of index){
  if(item.status!=='available')continue;
  const mode=item.kind==='catalog'?'engineering':item.mode||'shared';
  if(!groups.has(mode))groups.set(mode,[]);
  groups.get(mode).push(item);
 }
 return [...groups].filter(([,items])=>items.length).map(([mode,items])=>({mode,label:mode==='shared'?'Shared panels':workspaceLabel(mode),
  items:items.slice().sort((a,b)=>a.title.localeCompare(b.title))}));
}
function renderBrowse(){
 const frag=document.createDocumentFragment();
 for(const g of browseGroups()){
  const d=document.createElement('details');d.className='ts-browse-group';d.dataset.mode=g.mode;
  const s=document.createElement('summary');s.textContent=g.label+' ('+g.items.length+')';
  const ul=document.createElement('ul');
  for(const item of g.items){
   const li=document.createElement('li'),b=document.createElement('button');
   b.type='button';b.className='ts-browse-item';b.dataset.toolId=item.id;b.textContent=item.title;
   b.addEventListener('click',()=>{close();input.value='';status.textContent='Opening '+item.title+'.';if(openItem(item))remember(item);});
   li.append(b);ul.append(li);
  }
  d.append(s,ul);frag.append(d);
 }
 browseBody.replaceChildren(frag);
}
browse.addEventListener('toggle',()=>{if(browse.open)renderBrowse();});
let quietFocus=false;
// Keep focus in the input while a result is clicked.
popup.addEventListener('mousedown',e=>e.preventDefault());
popup.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();close();quietFocus=true;input.focus();}});
input.addEventListener('focus',()=>{build();if(quietFocus){quietFocus=false;return;}render();});
input.addEventListener('input',render);
wrap.addEventListener('focusout',()=>setTimeout(()=>{if(!wrap.contains(document.activeElement))close();},0));
input.addEventListener('keydown',e=>{
 if(e.key==='ArrowDown'||e.key==='ArrowUp'){
  e.preventDefault();if(popup.hidden){render();return;}
  if(!results.length)return;
  const step=e.key==='ArrowDown'?1:-1;setActive(active<0?(step>0?0:results.length-1):(active+step+results.length)%results.length);
 }else if(e.key==='Enter'){
  e.preventDefault();
  if(active>=0)choose(active);else if(!quick){const first=results.findIndex(r=>r.status==='available');if(first>=0)choose(first);}
 }else if(e.key==='Escape'){
  e.preventDefault();
  if(!popup.hidden)close();else{input.value='';status.textContent='';}
 }else if(e.altKey&&!e.ctrlKey&&!e.metaKey&&e.code==='KeyP'){
  e.preventDefault();if(!popup.hidden&&active>=0)togglePin(active);
 }
});
function editable(t){return t instanceof Element&&(t.isContentEditable||Boolean(t.closest('input,textarea,select,[contenteditable]:not([contenteditable="false"])')));}
function focusSearch(){input.focus();input.select();}
document.addEventListener('keydown',e=>{
 if((e.ctrlKey||e.metaKey)&&!e.altKey&&!e.shiftKey&&e.key.toLowerCase()==='k'){e.preventDefault();focusSearch();return;}
 if(e.key==='/'&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&!e.defaultPrevented&&!editable(e.target)){e.preventDefault();focusSearch();}
});
build();
const publicItem=item=>Object.freeze({id:item.id,title:item.title,workspace:item.workspace,mode:item.mode,kind:item.kind,status:item.status});
M.toolSearch=Object.freeze({
 search:query=>search(query).map(publicItem),
 open:id=>{if(!index.some(i=>i.id===id))build();const item=index.find(i=>i.id===id);const ok=openItem(item);if(ok)remember(item);return ok;},
 refresh:build,focus:focusSearch,synonyms:SYNONYMS,
 recent:()=>prefs.recent(openable).map(id=>publicItem(byId.get(id))),
 pinned:()=>prefs.pinned(openable).map(id=>publicItem(byId.get(id))),
 pin:(id,on=true)=>{if(!index.length)build();return openable(id)?prefs.setPinned(id,Boolean(on),openable):false;},
 browse:()=>browseGroups().map(g=>Object.freeze({mode:g.mode,label:g.label,items:g.items.map(publicItem)}))
});
})();
