/* Searchable Engineering Toolbox: route to existing tested tools, never duplicate solvers. */
(()=>{'use strict';
const M=window.MathStudio,host=document.getElementById('engineering-panel'),bar=document.querySelector('.workspace-bar');
if(!M?.advanced?.mode||!host||!bar)return;
const disciplines=Object.freeze([
 ['physics','Physics'],['mechanical','Mechanical engineering'],['electrical','Electrical engineering'],
 ['electronics','Electronics engineering'],['fluids','Fluid mechanics'],['aerospace','Aerospace engineering'],
 ['control','Control Theory'],['gnss','GNSS positioning'],['signals','Signal engineering']
].map(([id,title])=>Object.freeze({id,title})));
const raw=[
 ['matrix.solve.real.small','Small real linear systems','Solve 2×2 or 3×3 Ax=b using the shared scaled-pivot Matrix solver.','physics mechanical electrical electronics fluids aerospace','matrix linear algebra','calculator','matrix'],
 ['control.equilibrium.real.small','Control state equilibrium','Solve ẋ=−Ax+b for 2 or 3 states; equilibrium does not prove stability.','mechanical electrical electronics aerospace control','control steady-state','graph','ct-equilibrium'],
 ['ode.ivp.scalar','Scalar ODE initial-value solver','Run existing RK4 or adaptive RK45; not a stiff solver.','physics mechanical fluids aerospace','ode rk45 integration','editor','ode'],
 ['gnss.positioning.least.squares','GNSS least-squares positioning','GNSS satellite-position observations and coordinate-frame handling are not yet implemented.','gnss','gnss positioning navigation'],
 ['signals.spectral.analysis','Signal spectral analysis','Dedicated sampling/windowing/spectrum workflow is not yet implemented.','signals electronics','fft spectral frequency'],
 ['control.frequency.response','Control frequency response','Bode and frequency response analysis is not yet implemented.','control electrical','bode control stability'],
 ['thermal.cycle.analysis','Thermodynamic cycle analysis','Cycle efficiency calculations are not yet implemented.','physics mechanical','thermal energy'],
 ['structures.beam.deflection','Beam deflection and stress','Structural loading workflows are not yet implemented.','mechanical aerospace','beam mechanics'],
 ['circuits.network.analysis','Circuit network analysis','General nodal circuit analysis is not yet implemented.','electrical electronics','circuit kirchhoff'],
 ['electronics.digital.logic','Digital logic simulation','Digital logic timing is not yet implemented.','electronics','logic digital'],
 ['fluids.pipe.network','Pipe network pressure loss','Pipe network calculations are not yet implemented.','fluids mechanical','hydraulic pipe'],
 ['aerospace.orbit.propagation','Orbital propagation','Orbit propagation is not yet implemented.','aerospace physics','orbit spaceflight']
];
const ids=new Set(),valid=new Set(disciplines.map(d=>d.id));
const tools=Object.freeze(raw.map(([id,title,description,domains,tags,mode,target])=>{
 const disciplineIds=Object.freeze(domains.split(' ')),status=mode?'available':'planned';
 if(ids.has(id)||disciplineIds.some(d=>!valid.has(d))||Boolean(mode)!==Boolean(target))throw Error('Invalid Engineering catalog: '+id);
 ids.add(id);
 return Object.freeze({id,title,description,disciplines:disciplineIds,tags,status,route:mode?Object.freeze({mode,target}):null});
}));
function filter(discipline='',query=''){
 if(discipline&&!valid.has(discipline))return [];
 const q=String(query).trim().toLocaleLowerCase();
 return tools.filter(t=>(!discipline||t.disciplines.includes(discipline))&&
 (!q||[t.id,t.title,t.description,t.tags].join(' ').toLocaleLowerCase().includes(q)));
}
const tab=document.createElement('button');tab.type='button';tab.className='workspace-tab';
tab.dataset.workspace='engineering';tab.textContent='⚙ Engineering Toolbox';
tab.addEventListener('click',()=>M.advanced.mode('engineering'));bar.append(tab);
const style=document.createElement('style');
style.textContent='#engineering-panel .eng-filters,#eng-results{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:12px 0}'+
 '#engineering-panel label{display:flex;flex-direction:column;gap:5px;font-weight:700}'+
 '#engineering-panel input,#engineering-panel select{width:100%;min-width:0;box-sizing:border-box;padding:10px;border:1px solid #c2cfdb;border-radius:9px}'+
 '#engineering-panel .eng-card{min-width:0;border:1px solid #d8e4e8;border-radius:12px;padding:13px;overflow-wrap:anywhere}'+
 '#engineering-panel .eng-card h3{font-size:15px;margin:6px 0}'+
 '#engineering-panel .eng-card p,#eng-status{font-size:12px;color:#536879}'+
 '#engineering-panel .eng-card button{min-height:40px;padding:8px 12px;border:1px solid #29817b;border-radius:9px;background:#e6f5f2;color:#174b48;cursor:pointer}'+
 '#engineering-panel .eng-card button:focus-visible{outline:3px solid #29817b;outline-offset:2px}'+
 '@media(max-width:440px){#engineering-panel .eng-filters,#eng-results{grid-template-columns:minmax(0,1fr)}}';
document.head.append(style);
host.innerHTML='<div class="panel-head"><div class="panel-title">Engineering Toolbox</div></div>'+
 '<p>Search nine engineering disciplines. Available tools open existing workflows; planned tools have no runnable actions. Units and engineering certification are not provided by this catalog.</p>'+
 '<div class="eng-filters"><label>Discipline<select id="eng-discipline"></select></label>'+
 '<label>Search tools<input id="eng-search" type="search" autocomplete="off" placeholder="Name or keyword"></label></div>'+
 '<p id="eng-status" role="status" aria-live="polite"></p><div id="eng-results" aria-label="Engineering tool results"></div>';
const select=document.getElementById('eng-discipline'),search=document.getElementById('eng-search');
const status=document.getElementById('eng-status'),results=document.getElementById('eng-results');
for(const [id,title] of [['','All nine disciplines'],...disciplines.map(d=>[d.id,d.title])]){
 const opt=document.createElement('option');opt.value=id;opt.textContent=title;select.append(opt);
}
function openTool(t){
 if(t.status!=='available')return;
 M.advanced.mode(t.route.mode);
 requestAnimationFrame(()=>{
  if(t.route.target==='ct-equilibrium'){
   document.getElementById('control-theory-toolbox').open=true;
   const panel=document.getElementById('ct-equilibrium');panel.open=true;
   panel.querySelector('summary').focus({preventScroll:true});
  }else M.workspaceTasks?.select(t.route.target,true);
 });
}
function render(){
 const matches=filter(select.value,search.value);results.replaceChildren();
 for(const t of matches){
  const card=document.createElement('article');card.className='eng-card';card.dataset.toolId=t.id;
  const label=document.createElement('strong');label.textContent=t.status==='available'?'Available in existing workspace':'Planned · not implemented';
  const heading=document.createElement('h3');heading.textContent=t.title;
  const description=document.createElement('p');description.textContent=t.description;
  card.append(label,heading,description);
  if(t.status==='available'){
   const button=document.createElement('button');button.type='button';button.textContent='Open existing tool';
   button.addEventListener('click',()=>openTool(t));card.append(button);
  }else{const note=document.createElement('span');note.textContent='No runnable tool yet';card.append(note);}
  results.append(card);
 }
 const available=matches.filter(t=>t.status==='available').length;
 status.textContent=matches.length+' unique tools · '+available+' available · '+(matches.length-available)+' planned';
 if(!matches.length){const empty=document.createElement('p');empty.textContent='No matching tools. Try another search.';results.append(empty);}
}
select.addEventListener('change',render);search.addEventListener('input',render);render();
M.engineeringCatalog=Object.freeze({disciplines,tools,filter});
// The saved mode may have been restored before this late-added tab existed.
if(M.advanced.currentMode()==='engineering')M.advanced.mode('engineering');
})();
