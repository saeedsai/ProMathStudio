/* Task-first progressive disclosure while preserving existing computation modules. */
(()=>{'use strict';
const $=id=>document.getElementById(id);
if(!$('calculator-panel')||!$('graph-panel')||!$('data-panel'))return;
const css=document.createElement('style');
css.textContent=`
#workspace-task-guide{background:#fff;border:1px solid #dce4f2;border-radius:14px;padding:15px 17px;margin:12px 0 20px;box-shadow:0 4px 18px #1c30570c}
#workspace-task-guide .task-heading{font-size:13px;font-weight:790;color:#243552;margin-bottom:9px}
#workspace-task-guide .task-choices{display:flex;flex-wrap:wrap;gap:8px}
#workspace-task-guide .task-choice{border:1px solid #d2dbed;border-radius:10px;background:#f8faff;color:#435271;padding:9px 13px;font-size:12px;font-weight:650;min-height:40px}
#workspace-task-guide .task-choice[aria-pressed="true"]{border-color:#5672db;background:#eaf0ff;color:#2c46a5}
#workspace-task-guide .task-choice:hover{border-color:#798ce0}
#workspace-task-guide .task-description{color:#65738b;font-size:12px;margin:10px 0 0}
.task-disclosure{border:1px solid #e1e7f2;border-radius:11px;background:#fbfcff;margin:9px 0;padding:0 12px}
.task-disclosure>summary{cursor:pointer;color:#435c9c;font-weight:730;font-size:13px;padding:11px 2px}
.task-disclosure[open]>summary{border-bottom:1px solid #e8edf6;margin-bottom:10px}
.task-disclosure .calc-quick-options,.task-disclosure .graph-controls{margin:8px 0 14px}
#ui-calc-history{align-self:start}
#ui-graph-table>.dt-graph-tools{margin:4px 0 12px}
#ui-editor-python .python-wrap{margin-top:9px}
#workspace-task-guide button:focus-visible,.task-disclosure>summary:focus-visible{outline:3px solid #93a5ed;outline-offset:2px}
@media(max-width:700px){#workspace-task-guide{padding:12px}#workspace-task-guide .task-choice{flex:1 1 calc(50% - 8px)}.task-disclosure{padding:0 9px}}
`;
document.head.append(css);
function wrap(id,title,node){
 if(!node||!node.parentNode)throw Error('Missing workspace form for '+id);
 const d=document.createElement('details');d.className='task-disclosure';d.id=id;
 const s=document.createElement('summary');s.textContent=title;
 node.parentNode.insertBefore(d,node);d.append(s,node);return d;
}
wrap('ui-calc-settings','Angle, precision and number display',$('calculator-panel').querySelector('.calc-quick-options'));
wrap('ui-calc-history','History and examples',$('calculator-panel').querySelector('.calc-history-wrap'));
wrap('ui-solver-assumptions','Variable assumptions (optional)',$('cas-assumptions'));
wrap('ui-graph-axes','Axes and numeric ranges',$('graph-panel').querySelector('.graph-controls'));
wrap('ui-graph-table','Plot a Data Table',$('graph-panel').querySelector('.dt-graph-tools'));
wrap('ui-editor-python','Generated Python / SymPy code',$('python-output').closest('.python-wrap'));
const tasks={
 calculator:[['basic','Calculate','Type an expression and press Calculate.'],['matrix','Matrices','Choose a matrix operation.','#matrix-tools'],['variables','Variables','Set named values for calculations.','#calc-variable-panel'],['settings','Number settings','Change angles and number display.','#ui-calc-settings'],['history','History','See previous results and examples.','#ui-calc-history']],
 editor:[['basic','Write equation','Write an expression and see its live preview.'],['examples','Try examples','Select an example to insert.','#examples'],['notebook','My equations','Reopen saved equations.','#notebook'],['python','Python code','Show the generated SymPy code.','#ui-editor-python']],
 solver:[['basic','Symbolic solve','Choose an algebra or calculus operation.'],['numerical','Numerical methods','Roots, integrals, systems and PDEs.','#num-details'],['ode','ODE initial values','Solve initial-value differential equations.','#ode-details'],['assumptions','Assumptions','Configure variable restrictions.','#ui-solver-assumptions']],
 graph:[['basic','Plot functions','Enter functions and plot in 2D or 3D.'],['table','Plot table data','Select data, axes and chart type.','#ui-graph-table'],['axes','Axis limits','Adjust visible coordinate ranges.','#ui-graph-axes'],['appearance','Appearance','Choose colors and line styles.','#graph-appearance']],
 data:[['basic','Edit table','Edit cells directly, or use a context menu.'],['filter','Filter and sort','Show row filters and sorting.','#data-menu-navigation > details:nth-child(2)'],['combine','Combine tables','Join, union or compare tables.','#data-menu-navigation > details:nth-child(3)'],['files','Import / Export','Open spreadsheet file actions.','#data-menu-navigation > details:nth-child(4)'],['python','Python','Run your own analysis code in the worker.','#data-menu-navigation > details:nth-child(5)']]
};
const guide=document.createElement('section');guide.id='workspace-task-guide';guide.setAttribute('aria-label','Choose a workspace task');
guide.innerHTML='<div class="task-heading">What would you like to do?</div><div class="task-choices" role="group" aria-label="Workspace tasks"></div><p class="task-description" id="task-description"></p>';
$('workspace-subtitle').after(guide);
let activeMode='';
const mode=()=>document.querySelector('.workspace-tab.active[data-workspace]')?.dataset.workspace||'editor';
function selectTask(key,scroll=false){
 const task=(tasks[activeMode]||tasks.editor).find(x=>x[0]===key)||(tasks[activeMode]||tasks.editor)[0];
 for(const b of guide.querySelectorAll('.task-choice'))b.setAttribute('aria-pressed',String(b.dataset.task===task[0]));
 $('task-description').textContent=task[2];
 const dest=task[3]?document.querySelector(task[3]):null;
 if(dest?.tagName==='DETAILS'){
   if(dest.parentElement?.id==='data-menu-navigation')for(const d of dest.parentElement.children)if(d!==dest)d.open=false;
   dest.open=true;
 }
 if(activeMode==='solver')$('symbolic-panel').querySelector('.cas-wrap').hidden=['numerical','ode'].includes(task[0]);
 if(scroll&&dest){dest.scrollIntoView({block:'nearest',behavior:'smooth'});if(dest.tagName==='DETAILS')dest.querySelector('summary')?.focus({preventScroll:true});}
}
function selectMode(m){
 activeMode=tasks[m]?m:'editor';
 const bar=guide.querySelector('.task-choices');bar.replaceChildren();
 for(const [key,label] of tasks[activeMode]){
  const b=document.createElement('button');b.type='button';b.className='task-choice';b.dataset.task=key;b.textContent=label;
  b.addEventListener('click',()=>selectTask(key,true));bar.append(b);
 }
 selectTask('basic');
}
selectMode(mode());
document.addEventListener('click',event=>{
 const id=event.target?.closest('button')?.id;
 if(['ode-to-graph','num-to-graph','dt-send-graph'].includes(id))$('ui-graph-table').open=true;
},true);
new MutationObserver(()=>{const next=mode();if(next!==activeMode)selectMode(next);}).observe(document.querySelector('.workspace-bar'),{attributes:true,attributeFilter:['class'],subtree:true});
window.MathStudio.workspaceTasks={select:selectTask,current:()=>activeMode};
})();