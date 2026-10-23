/* ProMathStudio: numerical mathematics, advanced table filters and isolated Python workspace.
   No eval/Function is used in the JS numerical solver or table filter. */
(()=>{'use strict';
const $=id=>document.getElementById(id), M=window.MathStudio;
if(!M?.advanced||!M?.dataTables)return;
const el=(tag,attrs={},value)=>{const n=document.createElement(tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(value!==undefined)n.textContent=String(value);return n;};
const nInput=(id,value,type='number')=>`<input id="${id}" type="${type}" value="${value}" />`;
const finite=(x,label='Number')=>{const n=Number(x);if(!Number.isFinite(n))throw Error(label+' must be finite.');return n;};
const intRange=(value,min,max,label)=>{const n=finite(value,label);if(!Number.isInteger(n)||n<min||n>max)throw Error(label+' must be '+min+'–'+max+'.');return n;};
const exprLimit=(expr)=>{expr=String(expr||'').trim();if(!expr||expr.length>1500)throw Error('Provide a mathematical expression (maximum 1,500 characters).');return expr;};
const val=(expr,env={})=>{const z=M.advanced.numeric(exprLimit(expr),{variables:env,angle:'rad'});if(Math.abs(z.im)>1e-8||!Number.isFinite(z.re))throw Error('The numerical function must return a finite real number.');return z.re;};
const eqValue=(expr,env={})=>{const i=expr.indexOf('=');if(i<0)return val(expr,env);if(expr[i+1]==='=')throw Error('Use a single = for an equation.');return val(expr.slice(0,i),env)-val(expr.slice(i+1),env);};
const normalizeRoot=(x,epsilon)=>Number(Number(x).toPrecision(Math.min(15,Math.max(7,Math.ceil(-Math.log10(epsilon))+3))));
function dedupe(roots,tol){roots.sort((a,b)=>a-b);return roots.filter((r,i)=>i===0||Math.abs(r-roots[i-1])>Math.max(tol*10,1e-6));}
function scalarRoots(expression,variable='x',lo=-10,hi=10,{samples=350,tolerance=1e-9,maxIterations=90}={}){
  exprLimit(expression);if(!/^[A-Za-z][A-Za-z0-9_]*$/.test(variable))throw Error('Specify one variable such as x.');
  lo=finite(lo);hi=finite(hi);if(!(hi>lo))throw Error('Root search requires max > min.');
  samples=intRange(samples,20,1600,'Samples');tolerance=finite(tolerance);if(tolerance<=0||tolerance>0.01)throw Error('Tolerance must be between 0 and 0.01.');
  const f=x=>{try{return eqValue(expression,{[variable]:x});}catch{return NaN;}};
  const found=[],h=(hi-lo)/samples;
  for(let k=0;k<=samples;k++){
    const x=lo+k*h,y=f(x);if(Number.isFinite(y)&&Math.abs(y)<tolerance*10)found.push(x);
    if(k===0)continue;
    let a=x-h,b=x,fa=f(a),fb=y;
    if(!Number.isFinite(fa)||!Number.isFinite(fb)||fa*fb>=0)continue;
    // Bisection has a convergence guarantee if the residual is continuous in the bracket.
    for(let it=0;it<maxIterations;it++){
      const mid=(a+b)/2,fm=f(mid);if(!Number.isFinite(fm))break;
      if(Math.abs(fm)<tolerance||b-a<tolerance){a=b=mid;break;}
      if(fa*fm<0){b=mid;fb=fm;}else{a=mid;fa=fm;}
    }
    const root=(a+b)/2,fr=f(root);if(Number.isFinite(fr)&&Math.abs(fr)<Math.sqrt(tolerance))found.push(root);
  }
  // Damped Newton seeds help locate tangential roots without sign changes.
  for(let k=0;k<=samples;k+=Math.max(1,Math.floor(samples/50))){
    let x=lo+k*h;
    for(let it=0;it<35;it++){
      const y=f(x);if(!Number.isFinite(y))break;
      if(Math.abs(y)<tolerance*10 && it>0){ /* keep refining flat roots until the Newton step stabilizes */ }
      const step=1e-5*Math.max(1,Math.abs(x)),dy=(f(x+step)-f(x-step))/(2*step);
      if(!Number.isFinite(dy)||Math.abs(dy)<1e-13)break;
      const dx=Math.max(-(hi-lo)/3,Math.min((hi-lo)/3,y/dy));x-=dx;
      if(x<lo||x>hi)break;
      if(Math.abs(dx)<Math.max(1e-9,tolerance*3)&&Math.abs(f(x))<tolerance*10){found.push(x);break;}
    }
  }
  const roots=dedupe(found.filter(x=>x>=lo-1e-8&&x<=hi+1e-8).map(x=>Math.abs(x)<1e-10?0:normalizeRoot(x,tolerance)),Math.sqrt(tolerance));
  return {type:'roots',variable,expression,roots,domain:[lo,hi],samples,tolerance,note:'Real roots found within the specified interval; roots outside the interval or near discontinuities may be missed.'};
}
function gaussian(A,b){const n=b.length,rows=A.map((r,i)=>[...r,b[i]]);for(let col=0;col<n;col++){
  let pivot=col;for(let i=col+1;i<n;i++)if(Math.abs(rows[i][col])>Math.abs(rows[pivot][col]))pivot=i;
  if(Math.abs(rows[pivot][col])<1e-13)throw Error('Singular Jacobian or system; try a different initial guess.');
  [rows[pivot],rows[col]]=[rows[col],rows[pivot]];
  for(let i=col+1;i<n;i++){const fac=rows[i][col]/rows[col][col];for(let j=col;j<=n;j++)rows[i][j]-=fac*rows[col][j];}
}const x=Array(n).fill(0);for(let i=n-1;i>=0;i--){let v=rows[i][n];for(let j=i+1;j<n;j++)v-=rows[i][j]*x[j];x[i]=v/rows[i][i];}return x;}
function systemRoots(expressions,variables,initial,{tolerance=1e-9,maxIterations=65}={}){
  const exprs=String(expressions).split(/[;\n]+/).map(x=>x.trim()).filter(Boolean),vars=String(variables).split(',').map(x=>x.trim()).filter(Boolean);
  if(vars.length<2||vars.length>3||new Set(vars).size!==vars.length||exprs.length!==vars.length)throw Error('Enter 2–3 equations and the same number of distinct variables.');
  if(vars.some(v=>!/^[A-Za-z][A-Za-z0-9_]*$/.test(v)))throw Error('Invalid variable name.');
  let x=Array.isArray(initial)?initial.map(Number):String(initial).split(',').map(Number);
  if(x.length!==vars.length||x.some(n=>!Number.isFinite(n)))throw Error('Initial guesses must be comma-separated finite numbers.');
  const evaluate=v=>{const env=Object.fromEntries(vars.map((name,i)=>[name,v[i]]));return exprs.map(expr=>eqValue(expr,env));};
  const norm=v=>Math.max(...v.map(Math.abs));let iterations=0,converged=false;
  for(let it=0;it<maxIterations;it++){
    const f=evaluate(x);iterations=it+1;if(!Number.isFinite(norm(f)))break;
    if(norm(f)<tolerance){converged=true;break;}
    const J=vars.map((name,j)=>{const h=1e-5*Math.max(1,Math.abs(x[j])),a=x.slice(),b=x.slice();a[j]+=h;b[j]-=h;const f1=evaluate(a),f0=evaluate(b);return f.map((_,i)=>(f1[i]-f0[i])/(2*h));});
    let step=gaussian(f.map((_,i)=>vars.map((_,j)=>J[j][i])),f);
    let damp=1,next=x.map((v,i)=>v-damp*step[i]);
    while(damp>1/1024&&(!next.every(Number.isFinite)||norm(evaluate(next))>norm(f))){damp/=2;next=x.map((v,i)=>v-damp*step[i]);}
    if(damp<=1/1024)break;x=next;
  }
  const residual=norm(evaluate(x));if(residual<Math.sqrt(tolerance))converged=true;
  return {type:'system',variables:vars,values:x,iterations,residual,converged,note:'Damped Newton method finds a local solution near the provided initial guess; results are not globally exhaustive.'};
}
// -u''(x)=source(x); Dirichlet u(a)=left, u(b)=right. Thomas tridiagonal solver.
function poisson1D({a=0,b=1,nx=40,source='pi^2*sin(pi*x)',left=0,right=0}={}){
  a=finite(a);b=finite(b);nx=intRange(nx,4,200,'Spatial intervals');if(b<=a)throw Error('Domain end must exceed start.');
  left=finite(left);right=finite(right);const h=(b-a)/nx;
  const lower=[],diag=[],upper=[],rhs=[];
  for(let i=1;i<nx;i++){const x=a+i*h;const f=val(source,{x});lower.push(-1);diag.push(2);upper.push(-1);rhs.push(h*h*f+(i===1?left:0)+(i===nx-1?right:0));}
  for(let i=1;i<rhs.length;i++){const m=lower[i]/diag[i-1];diag[i]-=m*upper[i-1];rhs[i]-=m*rhs[i-1];}
  const interior=Array(rhs.length);interior[rhs.length-1]=rhs.at(-1)/diag.at(-1);
  for(let i=rhs.length-2;i>=0;i--)interior[i]=(rhs[i]-upper[i]*interior[i+1])/diag[i];
  const rows=Array.from({length:nx+1},(_,i)=>[a+i*h,i===0?left:i===nx?right:interior[i-1]]);
  return {type:'poisson',columns:['x','u'],rows,nx,h,method:'Centered second-order finite differences, tridiagonal Thomas solver',note:'Solves -u_xx=f(x) on [a,b] with fixed Dirichlet endpoints. Check the mesh for convergence.'};
}
// Forward-time centered-space; resample nt to obey CFL if necessary, with an explicit upper work budget.
function heat1D({a=0,b=1,nx=40,nt=160,alpha=0.1,endTime=0.1,initial='sin(pi*x)',left=0,right=0}={}){
  a=finite(a);b=finite(b);nx=intRange(nx,4,100,'Spatial intervals');nt=intRange(nt,1,1500,'Time steps');
  alpha=finite(alpha);endTime=finite(endTime);left=finite(left);right=finite(right);
  if(b<=a||alpha<=0||endTime<=0)throw Error('Require b>a, diffusivity >0, and final time >0.');
  const dx=(b-a)/nx,dt=endTime/nt,r=alpha*dt/(dx*dx);
  if(r>.5+1e-12)throw Error('Unstable explicit heat solve (α Δt / Δx² = '+r.toFixed(3)+' > 0.5). Increase time steps or lower spatial resolution.');
  let u=Array.from({length:nx+1},(_,i)=>i===0?left:i===nx?right:val(initial,{x:a+i*dx}));
  const rows=[],stride=Math.max(1,Math.ceil(nt/120));
  for(let t=0;t<=nt;t++){
    if(t%stride===0||t===nt)for(let i=0;i<=nx;i++)rows.push([a+i*dx,t*dt,u[i]]);
    if(t===nt)break;
    const next=u.slice();for(let i=1;i<nx;i++)next[i]=u[i]+r*(u[i-1]-2*u[i]+u[i+1]);
    next[0]=left;next[nx]=right;u=next;
  }
  return {type:'heat',columns:['x','t','u'],rows,nx,nt,dt,dx,cfl:r,method:'Explicit FTCS finite difference; CFL≤0.5',note:'Solves u_t=α u_xx with fixed Dirichlet boundaries and prescribed initial profile. The time grid is sampled for graph display.'};
}
// Unified expression input: the exact calculator parser is also used by the numerical solvers.
const numerical={scalarRoots,systemRoots,poisson1D,heat1D,evaluate:val};M.numerical=numerical;
const style=el('style');style.textContent=`
#numerical-panel{margin-top:18px;background:#f9fbff;border:1px solid #dce4f6;border-radius:12px;padding:15px}
#numerical-panel .num-fields{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:11px;margin:12px 0}
#numerical-panel .num-fields label[hidden]{display:none!important}
#numerical-panel label,#python-panel label,.dt-filter-advanced label{display:flex;flex-direction:column;gap:5px;font-size:12px;font-weight:700;color:#566784}
#numerical-panel input,#numerical-panel select,#python-panel textarea,.dt-filter-advanced input,.dt-filter-advanced select{padding:9px;border:1px solid #cdd8ec;border-radius:9px;color:#283752;background:white;width:100%}
#num-output,#python-output-result{white-space:pre-wrap;overflow-wrap:anywhere;padding:12px;background:#fff;border:1px solid #dce5f3;border-radius:10px;max-height:330px;overflow:auto;font:12px/1.6 Consolas,monospace}
#num-output.error,#python-output-result.error{color:#a82241;background:#fff2f4}
#data-workflow-toolbar{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:9px;padding:6px 0 14px}
#data-menu-navigation{display:flex;flex-wrap:wrap;gap:8px}
.dt-action-menu{position:relative;border:1px solid #d6dff1;background:#f5f8ff;border-radius:9px}
.dt-action-menu summary{list-style:none;cursor:pointer;padding:10px 14px;font-size:13px;font-weight:700;color:#415aab}
.dt-action-menu summary::-webkit-details-marker{display:none}
.dt-action-menu[open]{z-index:30}
.dt-action-menu .dt-action-content{position:absolute;top:100%;left:0;z-index:35;min-width:min(440px,85vw);max-width:90vw;max-height:70vh;overflow:auto;padding:16px;border:1px solid #d8e3f3;border-radius:11px;box-shadow:0 12px 40px #24385b30;background:#fff}
.dt-action-menu .dt-action-content .dt-box{border:none;margin:0;padding:0}
.dt-action-menu .dt-action-content .data-toolbar{display:flex;flex-wrap:wrap;gap:7px}
.dt-action-menu .dt-action-content button{margin:3px}
.dt-filter-advanced{padding:11px;border:1px solid #dfe7f5;border-radius:10px}
.dt-filter-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:7px;align-items:end}
#python-panel textarea{min-height:160px;resize:vertical;font:13px/1.6 Consolas,monospace}
#python-panel .py-note{font-size:12px;color:#6b7890}
#numeric-calculus-guide{margin:7px 0;font-size:12px;color:#6b7890}
@media(max-width:700px){.dt-action-menu .dt-action-content{position:fixed;left:3%;top:70px;max-width:94vw;min-width:94vw}.dt-filter-row{grid-template-columns:1fr}#numerical-panel .num-fields{grid-template-columns:1fr 1fr}}
`;document.head.append(style);
function menu(name,content){const details=el('details',{class:'dt-action-menu'});const summary=el('summary',{},name+' ▾'),inner=el('div',{class:'dt-action-content'});inner.append(content);details.append(summary,inner);return details;}
function simplifyTable(){const data=$('data-panel'),area=data.querySelector('.data-inner');if(!area)return;
  const bar=el('div',{id:'data-workflow-toolbar'}),nav=el('nav',{id:'data-menu-navigation','aria-label':'Table actions'});
  const toolbars=area.querySelectorAll(':scope > .data-toolbar');const first=toolbars[0],search=toolbars[1];
  const tableMenu=menu('Table',first), filterMenu=menu('Filter',el('div'));
  const filterContent=filterMenu.querySelector('.dt-action-content');
  filterContent.append(search);
  const operationBox=[...area.querySelectorAll(':scope > .dt-box')].find(x=>x.querySelector('#dt-run'));
  const importBox=[...area.querySelectorAll(':scope > .dt-box')].find(x=>x.querySelector('#dt-import'));
  const opMenu=menu('Combine',operationBox),importMenu=menu('Files',importBox);
  const pythonMenu=menu('Python',el('div',{id:'python-panel'}));
  nav.append(tableMenu,filterMenu,opMenu,importMenu,pythonMenu);bar.append(nav);
  const quick=el('div',{class:'data-toolbar'});
  const add=el('button',{class:'secondary',type:'button'},'＋ Row');add.addEventListener('click',()=>$('dt-add-row').click());
  const showFilter=el('button',{class:'secondary',type:'button'},'Filter rows');showFilter.addEventListener('click',()=>{filterMenu.open=true;closeOtherMenus(filterMenu);});
  const openPython=el('button',{class:'secondary',type:'button'},'Python');openPython.addEventListener('click',()=>{pythonMenu.open=true;closeOtherMenus(pythonMenu);});
  quick.append(add,showFilter,openPython);bar.append(quick);
  area.insertBefore(bar,area.querySelector('#dt-tabs'));
  for(const m of nav.children)m.querySelector('summary').addEventListener('click',()=>{if(!m.open)closeOtherMenus(m)});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')for(const m of nav.children)m.open=false;});
  function closeOtherMenus(except){for(const m of nav.children)if(m!==except)m.open=false;}
  return {filterContent,pythonContent:pythonMenu.querySelector('.dt-action-content'),menus:nav};
}
const menus=simplifyTable();
// Structured filter: applied to evaluated values, never changes source rows or formulas.
const filterState={byTable:new Map()};
const filterControls=el('section',{class:'dt-filter-advanced'});
filterControls.innerHTML='<strong>Column filter</strong><div class="dt-filter-row"><label>Column<select id="dt-filter-column"></select></label><label>Condition<select id="dt-filter-op"><option value="contains">Contains</option><option value="eq">Equals</option><option value="neq">Not equal</option><option value="gt">Greater than</option><option value="gte">Greater or equal</option><option value="lt">Less than</option><option value="lte">Less or equal</option><option value="starts">Starts with</option><option value="empty">Empty</option></select></label><label>Value<input id="dt-filter-value" placeholder="e.g. 10" /></label></div><div class="data-toolbar"><button type="button" class="primary" id="dt-filter-apply">Apply filter</button><button type="button" class="secondary" id="dt-filter-reset">Remove column filter</button></div><p id="dt-filter-report" class="graph-data-muted">Filter does not delete rows.</p>';
menus.filterContent.append(filterControls);
const matches=(v,op,raw)=>{const str=String(v??''),q=String(raw);if(op==='empty')return !str.trim();if(op==='contains')return str.toLowerCase().includes(q.toLowerCase());if(op==='starts')return str.toLowerCase().startsWith(q.toLowerCase());if(op==='eq'||op==='neq')return (op==='eq')===(str.toLowerCase()===q.toLowerCase());const a=Number(v),b=Number(raw);if(!Number.isFinite(a)||!Number.isFinite(b)||!String(raw).trim())return false;return ({gt:a>b,gte:a>=b,lt:a<b,lte:a<=b})[op];};
function filterTable(){const t=M.dataTables.active;if(!t)return;const col=$('dt-filter-column'),prev=col.value;col.replaceChildren();t.columns.forEach((name,i)=>col.append(el('option',{value:i},name)));if([...col.options].some(x=>x.value===prev))col.value=prev;
  const rule=filterState.byTable.get(t.id);if(!rule){$('dt-filter-report').textContent='No column filter applied.';for(const tr of $('dt-sheet').querySelectorAll('tbody tr'))tr.hidden=false;return;}
  col.value=String(rule.column);$('dt-filter-op').value=rule.op;$('dt-filter-value').value=rule.value;
  const rows=M.dataTables.calculate(t);let shown=0;
  for(const tr of $('dt-sheet').querySelectorAll('tbody tr')){const label=tr.querySelector('th')?.textContent||'',index=Number(label)-2;
    const show=Number.isInteger(index)&&index>=0&&matches(rows[index]?.[rule.column],rule.op,rule.value);tr.hidden=!show;if(show)shown++;
  }
  $('dt-filter-report').textContent=shown+' visible rows match the column filter.';
}
$('dt-filter-apply').addEventListener('click',()=>{const rule={column:Number($('dt-filter-column').value),op:$('dt-filter-op').value,value:$('dt-filter-value').value};
  filterState.byTable.set(M.dataTables.active.id,rule);filterTable();});
$('dt-filter-reset').addEventListener('click',()=>{filterState.byTable.delete(M.dataTables.active.id);filterTable();});
// Observe table re-render (import, sorting, edits). Avoid re-render calls within observation.
let observeLock=false;new MutationObserver(()=>{if(observeLock)return;observeLock=true;queueMicrotask(()=>{observeLock=false;filterTable();});}).observe($('dt-sheet'),{childList:true,subtree:false});
filterTable();
// Extended calculator: same grammar as editor, with user-provided scalar substitutions.
const calc=document.querySelector('#calculator-panel .calc-main');const bindings=el('details',{id:'calc-variable-panel'});
bindings.innerHTML='<summary style="cursor:pointer;color:#4865ab;font-weight:700">Variable assignments &amp; advanced numeric math</summary><p id="numeric-calculus-guide">Use the Equation Editor functions directly. Examples: <code>diff(sin(x),x,pi/3)</code>, <code>int(x^2,x,0,3)</code>, <code>sum(k^2,k,1,10)</code>, or <code>prod(k,k,1,5)</code>. Assign variables with one name=value per line.</p><label style="display:block">Variables<textarea id="calc-variables" rows="3" placeholder="x=2&#10;y=3" style="width:100%;border:1px solid #cfdaee;border-radius:9px;padding:10px"></textarea></label><button type="button" class="secondary" id="calc-variable-apply">Apply variables</button><p id="calc-variables-status" class="graph-data-muted"></p>';
calc.querySelector('.calc-result').before(bindings);const variables={};
M.extraMath={variables};
$('calc-variable-apply').addEventListener('click',()=>{try{for(const key of Object.keys(variables))delete variables[key];for(const line of $('calc-variables').value.split(/[;\n]+/)){
  if(!line.trim())continue;const m=/^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$/.exec(line);if(!m)throw Error('Use one variable=value per line.');
  if(['Ans','pi','e','i','tau'].includes(m[1]))throw Error('Reserved mathematical constant: '+m[1]);
  variables[m[1]]=val(m[2],variables);
} $('calc-variables-status').textContent='Applied '+Object.keys(variables).length+' variables to the shared calculator evaluator.';
}catch(err){$('calc-variables-status').textContent=err.message;}});
// Numerical solvers with explicit scope. Output rows are kept until user chooses to export.
const panel=el('section',{id:'numerical-panel'});if(M.advanced.currentMode()!=='solver')panel.classList.add('workspace-hidden');panel.innerHTML=`
<details id="num-details"><summary style="font-weight:750;cursor:pointer;color:#3c50ae">Numerical methods · nonlinear equations &amp; PDEs</summary>
<p class="graph-data-muted">Numerical approximations require a domain, guess, mesh or boundary values. Reported results are approximate, not general symbolic solutions.</p>
<div class="num-fields"><label>Method<select id="num-method"><option value="scalar">Real nonlinear roots: bracket + Newton</option><option value="system">2–3 nonlinear equations: damped Newton</option><option value="poisson">1D Poisson: -u_xx = source</option><option value="heat">1D heat: u_t = α u_xx</option></select></label><label>Equation / source / initial expression<input id="num-expression" value="sin(x)-x/2=0" /></label><label>Unknown(s)<input id="num-variable" value="x" /></label><label>Initial guess(es)<input id="num-guess" value="1,1" /></label></div>
<div class="num-fields"><label>Domain start${nInput('num-start',-10)}</label><label>Domain end${nInput('num-end',10)}</label><label>Spatial intervals${nInput('num-nx',40)}</label><label>Time steps${nInput('num-nt',200)}</label><label>Final time${nInput('num-time',0.1)}</label><label>Diffusivity α${nInput('num-alpha',0.1)}</label><label>Boundary u(start)${nInput('num-left',0)}</label><label>Boundary u(end)${nInput('num-right',0)}</label></div>
<div class="data-toolbar"><button id="num-run" class="primary" type="button">Solve numerically</button><button id="num-to-table" class="secondary" type="button" disabled>Save output to Data Tables</button><button id="num-to-graph" class="secondary" type="button" disabled>Show numerical results in Graphs</button></div><pre id="num-output" role="status">Choose a method and enter conditions.</pre></details>`;
$('symbolic-panel').after(panel);
// Progressive disclosure: a selected numerical method reveals only its required inputs.
const numMode=$('num-method'),defaults={scalar:'sin(x)-x/2=0',system:'x^2+y^2=5; x-y=1',poisson:'pi^2*sin(pi*x)',heat:'sin(pi*x)'};
const visMap={scalar:['num-expression','num-variable','num-start','num-end'],system:['num-expression','num-variable','num-guess'],poisson:['num-expression','num-start','num-end','num-nx','num-left','num-right'],heat:['num-expression','num-start','num-end','num-nx','num-nt','num-time','num-alpha','num-left','num-right']};
let lastMethod='scalar';
function showMethod(){const mode=numMode.value;
  const active=new Set(visMap[mode]||[]);
  for(const id of ['num-expression','num-variable','num-guess','num-start','num-end','num-nx','num-nt','num-time','num-alpha','num-left','num-right']){
    const label=$(id).closest('label');if(label)label.hidden=!active.has(id);
  }
  if(mode!==lastMethod){
    if($('num-expression').value===defaults[lastMethod])$('num-expression').value=defaults[mode];
    if(mode==='system'){$('num-variable').value='x,y';}
    else if(mode!=='scalar'){$('num-start').value='0';$('num-end').value='1';$('num-variable').value='x';}
    else $('num-variable').value='x';
    lastMethod=mode;
  }
  const label=$('num-expression').closest('label');if(label)label.firstChild.textContent=mode==='scalar'?'Equation or residual':mode==='system'?'Equations (semicolon or new line)':mode==='poisson'?'Source function f(x)':'Initial profile u(x,0)';
}
numMode.addEventListener('change',showMethod);showMethod();
const casToolbar=$('cas-run')?.parentElement;if(casToolbar){const open=el('button',{type:'button',class:'secondary',id:'num-open'},'Numerical methods / PDE');open.addEventListener('click',()=>{M.advanced.mode('solver');$('num-details').open=true;panel.scrollIntoView({block:'start',behavior:'smooth'});});casToolbar.append(open);}
let lastNumeric=null;const failure=(e)=>{const node=$('num-output');node.textContent=e.message;node.classList.add('error');};
function runNumerical(){try{
  const mode=$('num-method').value,expr=$('num-expression').value,v=$('num-variable').value;
  const a=finite($('num-start').value),b=finite($('num-end').value),nx=$('num-nx').value,left=$('num-left').value,right=$('num-right').value;
  let result;
  if(mode==='scalar')result=scalarRoots(expr,v,a,b);
  else if(mode==='system')result=systemRoots(expr,v,$('num-guess').value);
  else if(mode==='poisson')result=poisson1D({a,b,nx,source:expr,left,right});
  else result=heat1D({a,b,nx,nt:$('num-nt').value,alpha:$('num-alpha').value,endTime:$('num-time').value,initial:expr,left,right});
  lastNumeric=result;$('num-output').classList.remove('error');
  $('num-output').textContent=result.type==='roots'?`Roots in [${a}, ${b}]: ${result.roots.length?result.roots.join(', '):'(none detected)'}\n${result.note}`:
    result.type==='system'?`Converged: ${result.converged}\n${result.variables.map((v,i)=>v+' = '+result.values[i].toPrecision(12)).join('\n')}\nResidual: ${result.residual.toExponential(3)}; iterations: ${result.iterations}\n${result.note}`:
      `${result.method}\n${result.rows.length} output rows\n${result.type==='heat'?'CFL r='+result.cfl.toPrecision(5)+'\n':''}${result.note}`;
  $('num-to-table').disabled=false;$('num-to-graph').disabled=!['poisson','heat'].includes(result.type);
}catch(err){lastNumeric=null;$('num-to-table').disabled=$('num-to-graph').disabled=true;failure(err);}}
$('num-run').addEventListener('click',runNumerical);
function numericalTable(){if(!lastNumeric)throw Error('Run a numerical method first.');const type=lastNumeric.type;
  let table;if(type==='roots')table={headers:[lastNumeric.variable,'residual'],rows:lastNumeric.roots.map(root=>[root,eqValue(lastNumeric.expression,{[lastNumeric.variable]:root})])};
  else if(type==='system')table={headers:['variable','value'],rows:lastNumeric.variables.map((v,i)=>[v,lastNumeric.values[i]])};
  else table={headers:lastNumeric.columns,rows:lastNumeric.rows};
  return M.dataTables.importData(table,'Numerical_'+type);
}
$('num-to-table').addEventListener('click',()=>{try{numericalTable();M.advanced.mode('data');}catch(e){failure(e);}});
$('num-to-graph').addEventListener('click',()=>{try{const t=numericalTable();M.advanced.mode('graph');$('dt-graph-table').value=t.id;$('dt-graph-table').dispatchEvent(new Event('change',{bubbles:true}));$('dt-chart-type').value=t.columns.length===3?'grid3d':'line';$('dt-graph-x').value='0';$('dt-graph-y').value=t.columns.length===3?'1':'1';$('dt-graph-z').value='2';$('dt-plot-table').click();}catch(e){failure(e);}});
// Python data-workbook execution, with explicit user action only and isolated Web Worker.
const code=menus.pythonContent.querySelector('#python-panel');
code.innerHTML=`<h3>Python for your tables</h3><p class="py-note">Optional Pyodide + pandas + SymPy, initially downloaded via CDN. Code runs only when you click Run, inside a worker with no DOM access. Scripts may access the network; only execute your own code.</p>
<label>Script<textarea id="dt-python-code" spellcheck="false"># Each table is a pandas DataFrame keyed by name.\n# Set 'result' to a DataFrame or a dict of named DataFrames.\nprint(list(tables))\nresult = next(iter(tables.values())).describe(include='all').reset_index()</textarea></label>
<div class="data-toolbar"><button class="primary" id="dt-python-run" type="button">▶ Run Python</button><button class="secondary" id="dt-python-stop" type="button">Stop</button><button class="secondary" id="dt-python-example" type="button">Example: groupby</button></div><pre id="python-output-result" role="status">Run to see standard output and import results into new tables.</pre>`;
let pyWorker=null,pyUrl=null,pyBusy=false,pyTimeout=null,pyLast=null;
function stopPy(){if(pyWorker)pyWorker.terminate();pyWorker=null;if(pyUrl)URL.revokeObjectURL(pyUrl);pyUrl=null;clearTimeout(pyTimeout);pyBusy=false;$('dt-python-run').disabled=false;}
$('dt-python-stop').addEventListener('click',()=>{stopPy();$('python-output-result').textContent='Python execution stopped. No results were imported.';});
$('dt-python-example').addEventListener('click',()=>{$('dt-python-code').value=`import pandas as pd\nname, df = next(iter(tables.items()))\nprint('Input:', name, len(df), 'rows')\n# Pick a category and numeric value column from your own table.\nif len(df.columns) >= 2:\n    df[df.columns[1]] = pd.to_numeric(df.iloc[:,1],errors='coerce')\n    result = df.groupby(df.columns[0], dropna=False)[df.columns[1]].sum().reset_index()\nelse:\n    result = df.copy()`;});
const pyWorkerCode=`'use strict';
const BASE='https://cdn.jsdelivr.net/pyodide/v0.29.1/full/';let ready=null;
self.onmessage=async ({data})=>{try{
 if(!ready)ready=(async()=>{importScripts(BASE+'pyodide.js');const py=await loadPyodide({indexURL:BASE});await py.loadPackage(['pandas','sympy']);return py;})();
 const py=await ready;
 py.globals.set('studio_input_json',JSON.stringify(data.workbook));
 py.globals.set('studio_user_code',data.code);
 const payload=await py.runPythonAsync(
   'import io, json, sys, traceback, contextlib\\n' +
   'import pandas as pd\\n' +
   'import sympy as sp\\n' +
   'raw=json.loads(studio_input_json)\\n' +
   'tables={t["name"]:pd.DataFrame(t["rows"],columns=t["columns"]) for t in raw}\\n' +
   'for frame in tables.values():\\n' +
   '    for col in frame.columns:\\n' +
   '        nums=pd.to_numeric(frame[col],errors="coerce")\\n' +
   '        if len(frame)>0 and nums.notna().all():frame[col]=nums\\n' +
   'result=None\\n' +
   'capture=io.StringIO()\\n' +
   'caught=None\\n' +
   'with contextlib.redirect_stdout(capture):\\n' +
   '    try:\\n' +
   '        exec(compile(studio_user_code,"<User Python>","exec"), {"__builtins__":__builtins__,"pd":pd,"sp":sp,"tables":tables}, result_env:={})\\n' +
   '    except Exception:\\n' +
   '        caught=traceback.format_exc()\\n' +
   'if caught:raise RuntimeError(caught)\\n' +
   'res=result_env.get("result")\\n' +
   'if isinstance(res,pd.DataFrame):res={"PythonResult":res}\\n' +
   'elif res is None:res={}\\n' +
   'if not isinstance(res,dict):raise ValueError("result must be a DataFrame or dict of DataFrames")\\n' +
   'output=[]\\n' +
   'for name,df in res.items():\\n' +
   '    if not isinstance(df,pd.DataFrame):raise ValueError("Every result must be a pandas DataFrame")\\n' +
   '    if len(df)>6000 or len(df.columns)>32:raise ValueError("Result exceeds 6,000 rows or 32 columns")\\n' +
   '    clean=df.astype(object).where(pd.notnull(df),None)\\n' +
   '    output.append({"name":str(name)[:44],"columns":[str(c) for c in df.columns],"rows":clean.values.tolist()})\\n' +
   'json.dumps({"stdout":capture.getvalue()[:12000],"tables":output},default=str)');
 self.postMessage({ok:true,payload:JSON.parse(payload)});
}catch(e){self.postMessage({ok:false,error:String(e.message||e)});}};`;
$('dt-python-run').addEventListener('click',()=>{if(pyBusy)return;try{
 const user=$('dt-python-code').value;
 if(user.length>12000)throw Error('Python script exceeds 12,000 characters.');
 if(M.dataTables.tables.length>20)throw Error('Too many input tables.');
 const workbook=M.dataTables.tables.map(t=>({name:t.name,columns:t.columns,rows:M.dataTables.calculate(t)}));
 const workerSrc=pyWorkerCode;pyUrl=URL.createObjectURL(new Blob([workerSrc],{type:'text/javascript'}));pyWorker=new Worker(pyUrl);pyBusy=true;$('dt-python-run').disabled=true;
 const status=$('python-output-result');status.classList.remove('error');status.textContent='Loading Python/pandas (internet required on first use)…';
 pyWorker.onmessage=({data})=>{
   if(!data.ok){status.textContent=data.error;status.classList.add('error');stopPy();return;}
   const output=data.payload;status.textContent=String(output.stdout||'')+'\n';
   try{for(const t of output.tables||[])M.dataTables.importData({headers:t.columns,rows:t.rows},t.name);
     status.textContent+='\nImported '+(output.tables||[]).length+' result table(s).';}
   catch(e){status.textContent+='\nResult import failed: '+e.message;status.classList.add('error');}
   stopPy();
 };
 pyWorker.onerror=e=>{status.textContent='Python worker could not start. Check your connection or CDN access.';status.classList.add('error');stopPy();};
 pyWorker.postMessage({code:user,workbook});
 pyTimeout=setTimeout(()=>{if(pyBusy){status.textContent='Python timed out during execution. Simplify the code and try again.';status.classList.add('error');stopPy();}},75000);
}catch(err){$('python-output-result').textContent=err.message;}});
M.dataTools={filter:(rule)=>{if(rule)filterState.byTable.set(M.dataTables.active.id,rule);else filterState.byTable.delete(M.dataTables.active.id);filterTable();},getFilteredRows:()=>[...$('dt-sheet').querySelectorAll('tbody tr')].filter(tr=>!tr.hidden).length,stopPython:stopPy};
// Extend Help menu with explicit numerical/Python workflows.
const topics=$('help-topics');if(topics)topics.insertAdjacentHTML('beforeend',`<details class="help-topic"><summary>Numerical nonlinear equations and PDE methods</summary><p>Solver → Numerical methods. Roots: interval and tolerance; systems: 2–3 equations and initial guesses; Poisson: -u″=f with Dirichlet endpoints; Heat: u_t=αu_xx, initial profile and endpoints. Explicit heat method requires α Δt/Δx² ≤ 0.5. Numerical results are approximate, not guaranteed globally or for every PDE. Save to Data Tables and graph.</p></details><details class="help-topic"><summary>Data Tables: filters, menus and Python</summary><p>Use Table, Filter, Combine, Files, or Python submenus above the sheet. Filter lets you choose a column and a numeric or text condition without modifying source rows. Python runs selected code through a Pyodide/pandas worker and can return a new DataFrame as <code>result</code>. Only run trusted code. Use Save Project to keep derived tables.</p></details>`);
})();
