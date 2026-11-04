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

let index=[];
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
 index=items;return items.length;
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
 '#tool-search-list [role=option]{display:flex;flex-direction:column;gap:2px;min-height:40px;box-sizing:border-box;justify-content:center;padding:7px 10px;border-radius:8px;cursor:pointer;overflow-wrap:anywhere}'+
 '#tool-search-list [role=option] strong{font-size:13px;color:#1f3157}'+
 '#tool-search-list [role=option] span{font-size:11px;color:#596987}'+
 '#tool-search-list [role=option][aria-disabled=true]{cursor:default}'+
 '#tool-search-list [role=option][aria-disabled=true] strong{color:#6b7891}'+
 '#tool-search-list [role=option]:hover{background:#f1f5fd}'+
 '#tool-search-list [role=option][aria-selected=true]{background:#e6edfc;outline:2px solid #5b74d6;outline-offset:-2px}'+
 '#tool-search .ts-badge{display:inline-block;margin-left:6px;padding:0 6px;border-radius:999px;background:#fdf1de;color:#7a4b00;font-size:10px;font-weight:700}'+
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
input.setAttribute('aria-describedby','tool-search-hint');input.setAttribute('aria-keyshortcuts','/ Control+K Meta+K');
const kbd=document.createElement('kbd');kbd.textContent='/';kbd.setAttribute('aria-hidden','true');
const hint=document.createElement('span');hint.id='tool-search-hint';hint.className='ts-sr';
hint.textContent='Press slash or Control+K to search. Use arrow keys to choose a result and Enter to open it.';
const popup=document.createElement('div');popup.id='tool-search-popup';popup.hidden=true;
const list=document.createElement('ul');list.id='tool-search-list';list.setAttribute('role','listbox');list.setAttribute('aria-label','Matching tools');
const empty=document.createElement('p');empty.id='tool-search-empty';empty.hidden=true;
empty.textContent='No matching tools. Try another word, such as root, plot or table.';
const status=document.createElement('p');status.id='tool-search-status';status.className='ts-sr';
status.setAttribute('role','status');status.setAttribute('aria-live','polite');
popup.append(list,empty);wrap.append(label,input,kbd,hint,popup,status);bar.append(wrap);

let results=[],active=-1;
function setActive(i){
 active=results.length?Math.max(-1,Math.min(i,results.length-1)):-1;
 for(const [n,opt] of [...list.children].entries())opt.setAttribute('aria-selected',String(n===active));
 if(active>=0){input.setAttribute('aria-activedescendant','tool-search-opt-'+active);list.children[active].scrollIntoView({block:'nearest'});}
 else input.removeAttribute('aria-activedescendant');
}
function close(){popup.hidden=true;input.setAttribute('aria-expanded','false');setActive(-1);}
function render(){
 results=search(input.value);list.replaceChildren();
 if(!norm(input.value)){close();status.textContent='';return;}
 for(const [n,item] of results.entries()){
  const opt=document.createElement('li');opt.id='tool-search-opt-'+n;opt.setAttribute('role','option');
  opt.setAttribute('aria-selected','false');opt.dataset.toolId=item.id;
  const name=document.createElement('strong');name.textContent=item.title;
  if(item.status==='planned'){
   opt.setAttribute('aria-disabled','true');
   const badge=document.createElement('span');badge.className='ts-badge';badge.textContent='Planned';name.append(badge);
  }
  const where=document.createElement('span');where.textContent=item.status==='planned'?item.workspace+' · not yet available':item.workspace;
  opt.append(name,where);
  opt.addEventListener('click',()=>choose(n));
  list.append(opt);
 }
 empty.hidden=results.length>0;list.hidden=!results.length;
 popup.hidden=false;input.setAttribute('aria-expanded','true');
 setActive(results.findIndex(r=>r.status==='available'));
 status.textContent=results.length?results.length+(results.length===1?' tool':' tools')+' found.':'No matching tools.';
}
function choose(n){
 const item=results[n];if(!item)return;
 if(item.status!=='available'){status.textContent=item.title+' is planned and not yet available.';return;}
 close();input.value='';status.textContent='Opening '+item.title+'.';
 openItem(item);
}
// Keep focus in the input while a result is clicked.
popup.addEventListener('mousedown',e=>e.preventDefault());
input.addEventListener('focus',()=>{build();if(norm(input.value))render();});
input.addEventListener('input',render);
input.addEventListener('blur',()=>setTimeout(()=>{if(document.activeElement!==input)close();},0));
input.addEventListener('keydown',e=>{
 if(e.key==='Home'||e.key==='End'){
  if(popup.hidden||!results.length)return;
  e.preventDefault();
  const available=results.map((item,i)=>item.status==='available'?i:-1).filter(i=>i>=0);
  if(available.length)setActive(e.key==='Home'?available[0]:available[available.length-1]);
 }else if(e.key==='ArrowDown'||e.key==='ArrowUp'){
  e.preventDefault();if(popup.hidden&&norm(input.value)){render();return;}
  if(!results.length)return;
  const step=e.key==='ArrowDown'?1:-1;
  // Disabled planned tools remain discoverable, but keyboard focus skips them.
  const start=active<0?(step>0?-1:0):active;
  for(let offset=1;offset<=results.length;offset++){
   const candidate=(start+step*offset+results.length*2)%results.length;
   if(results[candidate].status==='available'){setActive(candidate);break;}
  }
 }else if(e.key==='Enter'){
  e.preventDefault();
  if(active>=0)choose(active);else{const first=results.findIndex(r=>r.status==='available');if(first>=0)choose(first);}
 }else if(e.key==='Escape'){
  e.preventDefault();
  if(!popup.hidden)close();else{input.value='';status.textContent='';}
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
 open:id=>{if(!index.some(i=>i.id===id))build();return openItem(index.find(i=>i.id===id));},
 refresh:build,focus:focusSearch,synonyms:SYNONYMS
});
})();
