/* ProMathStudio advanced mathematics and progressive workspace interface.
   No eval(), no external plotting service, no mutation of source table data. */
(()=>{'use strict';
const $=id=>document.getElementById(id), studio=window.MathStudio;
if(!studio||!studio.dataTables) return;
const graphic=$('dt-chart-status');
const fitArea=document.createElement('section');fitArea.id='curve-fit-tools';fitArea.className='curve-fit-tools';
fitArea.innerHTML=`<div class="fit-head"><strong>Curve fitting</strong><span>Fit selected numeric X / Y columns</span></div>
<div class="data-toolbar"><label>Model<select id="fit-model"><option value="none">No fit</option><option value="linear">Linear y=a+bx</option><option value="poly">Polynomial</option><option value="exp">Exponential y=a exp(bx)</option><option value="log">Logarithmic y=a+b ln(x)</option><option value="power">Power y=a x^b</option><option value="gaussian">Gaussian bell curve</option></select></label>
<label id="fit-degree-wrap" hidden>Polynomial degree<select id="fit-degree"><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option></select></label>
<button type="button" class="primary" id="fit-run">Fit and show on graph</button><button type="button" class="secondary" id="fit-clear">Clear fit curve</button></div>
<div class="fit-result" id="fit-result" role="status">Select a numeric table and a fit model.</div>`;
graphic.insertAdjacentElement('afterend',fitArea);
$('fit-model').addEventListener('change',()=>{$('fit-degree-wrap').hidden=$('fit-model').value!=='poly';});
let currentFit=null,lastEquation='';
function finite(v){const x=Number(v);return typeof v!=='boolean'&&v!==null&&String(v).trim()!==''&&Number.isFinite(x)?x:null;}
function linearSolve(rows,ys){
 const n=rows.length,m=rows[0].length;
 if(n<m)throw Error('Not enough valid measurements for this polynomial degree.');
 // Modified Gram-Schmidt least squares to avoid unstable normal equations.
 const qs=[],rs=Array.from({length:m},()=>Array(m).fill(0));
 for(let j=0;j<m;j++){
  let v=rows.map(r=>r[j]);
  for(let i=0;i<j;i++){const dot=qs[i].reduce((a,q,k)=>a+q*v[k],0);rs[i][j]=dot;v=v.map((value,k)=>value-dot*qs[i][k]);}
  const length=Math.hypot(...v);if(length<1e-10)throw Error('This model is singular for the chosen X values. Try a lower degree or different data.');
  rs[j][j]=length;qs[j]=v.map(a=>a/length);
 }
 const values=qs.map(q=>q.reduce((a,v,i)=>a+v*ys[i],0));
 const coefficients=Array(m).fill(0);
 for(let i=m-1;i>=0;i--){let c=values[i];for(let j=i+1;j<m;j++)c-=rs[i][j]*coefficients[j];coefficients[i]=c/rs[i][i];}
 return coefficients;
}
function fmt(n){if(!Number.isFinite(n))throw Error('Numerical fitting was unstable.');if(Math.abs(n)<1e-12)return '0';let s=Number(n.toPrecision(10)).toString();if(/[eE]/.test(s))s=n.toFixed(Math.abs(n)<1?12:5).replace(/0+$/,'').replace(/\.$/,'');return s;}
function analyze(points,model,degree=2){
 const pairs=points.filter(([x,y])=>Number.isFinite(x)&&Number.isFinite(y));
 if(pairs.length<2)throw Error('Select numeric X/Y columns with at least two valid rows.');
 let selected=pairs;
 if(['log','power'].includes(model))selected=selected.filter(([x])=>x>0);
 if(['exp','power','gaussian'].includes(model))selected=selected.filter(([,y])=>y>0);
 if(selected.length<2)throw Error('This model needs positive X/Y values.');
 const xs=selected.map(p=>p[0]),ys=selected.map(p=>p[1]);
 const xmean=xs.reduce((a,b)=>a+b,0)/xs.length;
 const spread=Math.max(1e-12,...xs.map(x=>Math.abs(x-xmean)));
 let rowValues,objective,formula,predict,coeffs;
 if(model==='linear'||model==='poly'||model==='exp'||model==='gaussian'){
  const n=model==='linear'||model==='exp'?1:model==='gaussian'?2:degree;
  const powers=xs.map(x=>{const u=(x-xmean)/spread;return Array.from({length:n+1},(_,i)=>Math.pow(u,i));});
  objective=(model==='exp'||model==='gaussian')?ys.map(Math.log):ys;
  coeffs=linearSolve(powers,objective);
  const u='((x-('+fmt(xmean)+'))/('+fmt(spread)+'))';
  const poly=coeffs.map((c,i)=>'('+fmt(c)+')'+(i?'*('+u+')^'+i:'')).join('+');
  if(model==='exp') {formula='exp('+poly+')';predict=x=>Math.exp(coeffs[0]+coeffs[1]*(x-xmean)/spread);}
  else if(model==='gaussian'){
   if(coeffs[2]>=-1e-10)throw Error('This dataset cannot be fitted to a bell-shaped Gaussian (non-negative curvature).');
   formula='exp('+poly+')';predict=x=>Math.exp(coeffs.reduce((a,c,i)=>a+c*Math.pow((x-xmean)/spread,i),0));
  }else{formula=poly;predict=x=>coeffs.reduce((a,c,i)=>a+c*Math.pow((x-xmean)/spread,i),0);}
 }else{
  const u=xs.map(x=>model==='log'?Math.log(x):Math.log(x));
  objective=model==='power'?ys.map(Math.log):ys;
  coeffs=linearSolve(u.map(x=>[1,x]),objective);
  formula=model==='log'?'('+fmt(coeffs[0])+')+('+fmt(coeffs[1])+')*ln(x)':'exp('+fmt(coeffs[0])+')*x^('+fmt(coeffs[1])+')';
  predict=x=>model==='log'?coeffs[0]+coeffs[1]*Math.log(x):Math.exp(coeffs[0])*Math.pow(x,coeffs[1]);
 }
 const mean=ys.reduce((a,b)=>a+b,0)/ys.length;let ss=0,total=0;
 for(let i=0;i<ys.length;i++){const estimate=predict(xs[i]);if(!Number.isFinite(estimate))throw Error('Numerical overflow in fitted model.');ss+=(ys[i]-estimate)**2;total+=(ys[i]-mean)**2;}
 const r2=total>0?1-ss/total:(ss<1e-15?1:0);
 return {model,degree,formula,coefficients:coeffs,r2,rmse:Math.sqrt(ss/ys.length),used:ys.length,excluded:points.length-ys.length};
}
function fitTable(t,x,y,model,degree){const computed=studio.dataTables.calculate(t),pairs=computed.map(r=>[finite(r[x]),finite(r[y])]).filter(p=>p[0]!==null&&p[1]!==null);return analyze(pairs,model,degree);}
function putFit(){try{
 const model=$('fit-model').value;if(model==='none')throw Error('Select a fitting model.');
 const kind=$('dt-chart-type').value;if(!['scatter','line'].includes(kind))throw Error('Fitting supports 2D scatter and line charts. Select one of those first.');
 const table=studio.dataTables.tables.find(t=>t.id===$('dt-graph-table').value),xi=Number($('dt-graph-x').value),yi=Number($('dt-graph-y').value);
 if(!table||xi===yi)throw Error('Choose a table with different X and Y columns.');
 const fit=fitTable(table,xi,yi,model,Number($('fit-degree').value));
 const graph=$('graph-input');
 if(lastEquation){graph.value=graph.value.split('\n').filter(x=>x.trim()!==lastEquation).join('\n');}
 lastEquation='y='+fit.formula;graph.value=[graph.value.trim(),lastEquation].filter(Boolean).join('\n');
 studio.dataTables.plot(); // Ensures same measurements appear as dots as well as the fitted curve.
 $('graph-input').value=[...new Set($('graph-input').value.split('\n').filter(Boolean).concat([lastEquation]))].join('\n');
 $('graph-plot').click();
 currentFit={...fit,table:table.id,x:xi,y:yi};
 const out=$('fit-result');out.textContent='y = '+fit.formula+'  |  R² = '+fit.r2.toFixed(6)+'  |  RMSE = '+fit.rmse.toPrecision(5)+'  |  n = '+fit.used+(fit.excluded?' ('+fit.excluded+' excluded)':'');out.classList.remove('error');
 }catch(err){$('fit-result').textContent=err.message;$('fit-result').classList.add('error');}
}
$('fit-run').addEventListener('click',putFit);
$('fit-clear').addEventListener('click',()=>{if(lastEquation){$('graph-input').value=$('graph-input').value.split('\n').filter(x=>x.trim()!==lastEquation).join('\n');lastEquation='';$('graph-plot').click();}currentFit=null;$('fit-result').textContent='Fit removed; data table unchanged.';});
studio.curveFit={analyze,fitTable,get last(){return currentFit;},get active(){return !!currentFit;},exportState:()=>({model:$('fit-model').value,degree:$('fit-degree').value,lastEquation}),restoreState:s=>{if(!s)return;$('fit-model').value=s.model||'none';$('fit-degree').value=s.degree||'2';$('fit-degree-wrap').hidden=$('fit-model').value!=='poly';lastEquation=String(s.lastEquation||'').slice(0,2000);}};
// Floating/sliding library and contextual help. Keep underlying semantic form controls intact.
const css=document.createElement('style');css.textContent=`
  .shell{display:block!important}.shell main{max-width:1360px;margin:auto;padding-top:72px}
  .shell aside{position:fixed!important;top:0;left:0;height:100vh!important;width:min(322px,92vw);transform:translateX(-105%);display:flex!important;z-index:115;padding:26px 20px;transition:transform .22s ease;overflow-y:auto;box-shadow:10px 0 35px #10172c22}
  body.library-open .shell aside{transform:translateX(0)}
  #ui-overlay{position:fixed;inset:0;background:#10172755;z-index:110;display:none}
  body.library-open #ui-overlay{display:block}
  #quick-menu{position:fixed;top:12px;right:16px;z-index:130;display:flex;gap:7px;padding:7px;background:#ffffffee;border:1px solid #dfe5f3;border-radius:12px;box-shadow:0 5px 25px #26345618;backdrop-filter:blur(10px)}
  #quick-menu button{border:0;background:#eef2ff;padding:9px 12px;border-radius:9px;font-size:12px;font-weight:750;color:#3b51ab}
  #quick-menu button:hover{background:#dbe5ff}
  #quick-menu #quick-symbols{display:none}body.ws-editor #quick-symbols{display:block!important}
  #examples .examples{display:none}body.examples-open #examples .examples{display:grid}
  #examples{min-height:65px;scroll-margin-top:76px}
  body.examples-open #examples{position:fixed;right:0;top:65px;width:min(660px,95vw);height:calc(100vh - 75px);overflow:auto;padding:20px;background:#fff;border-radius:14px 0 0 14px;z-index:120;box-shadow:-10px 0 70px #071b3455;margin:0}
  body.examples-open #examples .examples{grid-template-columns:repeat(2,minmax(0,1fr))}
  body.examples-open #ui-overlay{display:block}
  .fit-head{display:flex;justify-content:space-between;align-items:center;font-size:13px;color:#2c3860;margin:0 0 6px}
  .fit-head span{font-size:11px;color:#73839b}.curve-fit-tools{border:1px solid #dce5f5;background:#f9fbff;border-radius:11px;padding:14px;margin:13px 0}
  .fit-result{font:12px/1.6 Consolas,monospace;word-break:break-word;color:#285877;padding:8px}.fit-result.error{color:#b52e40}
  #graph-controls-collapsible:not([open]) .graph-controls{display:none}
  #graph-controls-collapsible>summary{padding:9px;color:#4560ac;cursor:pointer;font-weight:700;font-size:12px}
  .ui-options[hidden]{display:none!important}.ui-options{position:fixed;right:14px;top:68px;z-index:120;background:#fff;border:1px solid #d9e2f5;padding:16px;border-radius:13px;box-shadow:0 15px 50px #111c3855;width:min(320px,92vw)}
  .ui-options label{display:flex;align-items:center;gap:12px;padding:9px 2px;font-size:13px}
  .ui-options h3{margin:0;font-size:16px}
  body:not(.ui-history-on) .calc-history-wrap{display:none!important}
  body:not(.ui-python-on) #python-output{display:none!important}
  body:not(.ui-python-on) .python-wrap{display:none!important}
  body:not(.ui-details-on) .cas-technical,body:not(.ui-details-on) .cas-intro{display:none}
  .help-topic{border-top:1px solid #e1e7f0;padding:12px 0}.help-topic summary{font-weight:700;cursor:pointer;color:#354da1}
  @media(max-width:760px){.shell main{padding-top:74px}#quick-menu{left:8px;right:8px;justify-content:space-evenly}#quick-menu button{padding:8px 7px;font-size:11px}body.examples-open #examples .examples{grid-template-columns:1fr}}
  @media(prefers-reduced-motion:reduce){.shell aside{transition:none}}
`;document.head.appendChild(css);
const overlay=document.createElement('div');overlay.id='ui-overlay';overlay.setAttribute('aria-hidden','true');document.body.append(overlay);
const quick=document.createElement('nav');quick.id='quick-menu';quick.setAttribute('aria-label','Quick navigation and help');
quick.innerHTML=`<button id="quick-symbols" type="button" aria-label="Open math symbols menu">∑ Symbols</button><button id="quick-examples" type="button">★ Examples</button><button id="quick-options" type="button">⚙ Options</button><button id="quick-help" type="button">? Help</button>`;
document.body.appendChild(quick);
const options=document.createElement('section');options.className='ui-options';options.id='ui-options';options.hidden=true;options.innerHTML='<h3>Workspace display</h3><label><input type="checkbox" id="ui-history">Calculator history</label><label><input type="checkbox" id="ui-python">Show Python code</label><label><input type="checkbox" id="ui-details">Advanced explanations</label><button type="button" class="secondary" id="ui-close">Close</button>';
document.body.appendChild(options);
function closeMenus(){document.body.classList.remove('library-open','examples-open');options.hidden=true;}
overlay.addEventListener('click',closeMenus);
$('quick-symbols').addEventListener('click',()=>{const next=!document.body.classList.contains('library-open');closeMenus();document.body.classList.toggle('library-open',next);$('palette-search').focus();});
$('quick-examples').addEventListener('click',()=>{const next=!document.body.classList.contains('examples-open');closeMenus();document.body.classList.toggle('examples-open',next);if(next)$('example-category').focus();});
$('quick-options').addEventListener('click',()=>{const next=options.hidden;closeMenus();options.hidden=!next;});
$('quick-help').addEventListener('click',()=>{closeMenus();$('help-dialog').showModal();});
$('ui-close').addEventListener('click',closeMenus);
for(const [box,cls] of [['ui-history','ui-history-on'],['ui-python','ui-python-on'],['ui-details','ui-details-on']])$(''+box).addEventListener('change',e=>document.body.classList.toggle(cls,e.target.checked));
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeMenus();});
for(const b of document.querySelectorAll('[data-workspace]'))b.addEventListener('click',()=>{closeMenus();document.body.classList.remove('ws-editor');document.body.classList.toggle('ws-editor',b.dataset.workspace==='editor');});
document.body.classList.add('ws-editor');
// Examples are in a contextual sliding drawer. Selecting one closes the drawer.
$('examples-list').addEventListener('click',e=>{if(e.target.closest('button'))closeMenus();});
// Compact advanced controls: hide axes settings until opened; preserve IDs.
const controls=document.querySelector('#graph-panel .graph-controls');if(controls){const detail=document.createElement('details');detail.id='graph-controls-collapsible';detail.innerHTML='<summary>Axis ranges and advanced graph settings</summary>';controls.parentNode.insertBefore(detail,controls);detail.append(controls);}
// Help menu: organized nested topics augment existing syntax guide.
const helpBody=$('help-dialog').querySelector('.help-body');const guide=document.createElement('div');guide.id='help-topics';
guide.innerHTML=`<details class="help-topic" open><summary>Start here · Five workspaces</summary><p><strong>Calculate</strong> for numeric input; <strong>Equation editor</strong> for live math and Word/LaTeX; <strong>Symbolic solver</strong> for transformations, ODE/PDE; <strong>Data tables</strong> for CSV/JSON and formulas; <strong>Graphs</strong> for functions, data and curve fitting. Use the Working equation panel at the bottom to send inputs between tools.</p></details>
<details class="help-topic"><summary>Curve fitting from a data table</summary><p>Open Graphs, choose a numeric X/Y table and 2D scatter or line. Select a fitting model, then press Fit. The curve is added to the equation plot, with R², RMSE and sample size shown. Exponential/Gaussian require positive Y; logarithmic/power also require positive X. Fit statistics are descriptive, not proof of an underlying physical law.</p></details>
<details class="help-topic"><summary>Laplace / Fourier transform</summary><p>Equation editor examples: <code>laplace(exp(-2*t),t,s)</code> and <code>fourier(exp(-x^2),x,k)</code>. In Solver, select Laplace/Fourier, enter the expression without the wrapper, and choose input and output variables. Fourier uses the SymPy <code>exp(-2πikx)</code> convention. Advanced transforms require SymPy and an initial internet connection.</p></details>
<details class="help-topic"><summary>Solving ODEs and PDEs</summary><p>Example ODE: <code>diff(y(t),t)+y(t)=0</code> with variable t; choose Solve ODE. Example PDE: <code>pdiff(u(x,t),t)+pdiff(u(x,t),x)=0</code>; choose Solve PDE. SymPy only solves supported classes and may report an unsupported equation. Initial/boundary conditions are not handled by these controls.</p></details>
<details class="help-topic"><summary>Physics reference equations</summary><p>In Equation Editor, open Examples, then select Physics · Mechanics, Electromagnetism, Thermodynamics, Waves & optics, Quantum & relativity, or Fluids & engineering. Reference equations use conventional notation; units and assumptions must be checked before applying them.</p></details>`;
helpBody.prepend(guide);$('help-btn').textContent='? Help & guides';
})();

