/* ProMathStudio Data Tables workspace. SPDX-License-Identifier: MIT.
   No eval / Function / external runtime; data, formulas and files remain in-browser. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const MAX_ROWS = 6000, MAX_COLUMNS = 32, MAX_BYTES = 1000000, MAX_DISPLAY = 150;
  const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const el = (tag, attrs, text) => { const e=document.createElement(tag); for(const [k,v] of Object.entries(attrs||{})){if(k==='class')e.className=v;else e.setAttribute(k,v);}if(text!==undefined)e.textContent=String(text);return e;};
  const csvCell = value => {const s=String(value??'');return /[",\n\r]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;};
  const deep = value => JSON.parse(JSON.stringify(value));
  const colLetter = idx => {let a=''; for(let i=idx+1;i;i=Math.floor((i-1)/26))a=String.fromCharCode(65+(i-1)%26)+a; return a;};
  const colIndex = s => {let n=0;for(const c of s.toUpperCase())n=n*26+c.charCodeAt(0)-64;return n-1;};
  const css = `
    .data-inner{padding:20px}.data-toolbar{display:flex;flex-wrap:wrap;align-items:end;gap:8px;margin:12px 0}
    .data-toolbar button{font-size:12px;min-height:37px}.data-toolbar label{display:flex;flex-direction:column;gap:5px;font-weight:650;font-size:12px;color:#51617d}
    .data-toolbar input,.data-toolbar select{border:1px solid #d3dbec;border-radius:8px;padding:9px;background:white;color:#26334f;max-width:230px}
    .dt-tabs{display:flex;gap:5px;overflow-x:auto;border-bottom:1px solid #dce3f0;margin:14px 0 0;padding-bottom:6px}
    .dt-tab{background:#f7f9ff;color:#465977;border:1px solid #d3dff1;border-radius:8px;padding:10px 15px;white-space:nowrap}
    .dt-tab.active{background:#eaf0ff;border-color:#718ce7;color:#304cbb;font-weight:800}
    .dt-grid-scroll{overflow:auto;border:1px solid #dfe5f0;max-height:520px;border-radius:10px;margin-top:12px}
    .dt-sheet{border-spacing:0;border-collapse:separate;min-width:680px}.dt-sheet th,.dt-sheet td{padding:0;border-bottom:1px solid #e3e8f2;border-right:1px solid #e3e8f2}
    .dt-sheet thead th{position:sticky;top:0;background:#eaf0ff;z-index:2}.dt-rownum{position:sticky;left:0;min-width:43px;text-align:center!important;background:#f2f6fd!important;padding:9px!important;color:#8290a7;z-index:2}
    .dt-sheet input{width:135px;min-height:35px;border:0;background:transparent;padding:7px 10px;font:13px Consolas,monospace;color:#293750}
    .dt-sheet input:focus{outline:2px solid #667de9;background:#f0f4ff}.dt-sheet input.dt-error{background:#fff0f0;color:#bb2342}
    .dt-box{margin-top:22px;padding-top:15px;border-top:1px solid #e3e9f2}.dt-box h3{font-size:15px;margin:0 0 9px}
    .dt-graph-tools{background:#f7faff;border:1px solid #dbe4f3;border-radius:12px;padding:12px 15px;margin:14px 0}
    #dt-graph-chart{padding:12px;border:1px solid #dce4f0;border-radius:12px;margin:10px 0}#dt-graph-chart canvas{display:block;max-width:100%;height:auto}
    #dt-advanced summary{color:#415bc6;cursor:pointer;font-weight:700}#about-panel a{color:#3852b6}
    @media(max-width:760px){.data-inner{padding:12px}.dt-sheet input{width:112px}.data-toolbar button{padding:8px}}
  `;
  document.head.append(el('style',{},css));
  const tab = el('button',{type:'button',class:'workspace-tab','data-workspace':'data'},'▤ Data tables');
  const menu = document.querySelector('.workspace-bar'); menu.append(tab);
  tab.addEventListener('click',()=>window.MathStudio.advanced.mode('data'));
  const panel = $('data-panel'); panel.innerHTML = `
    <div class="panel-head"><div class="panel-title"><span class="step">01</span> Data tables <span class="cas-label">Spreadsheet · SQL-style operations</span></div><span class="small-note">Multiple tables · formulas · CSV / JSON</span></div>
    <div class="data-inner"><div class="data-toolbar">
      <button id="dt-new" class="primary" type="button">＋ New table</button><button id="dt-copy" class="secondary" type="button">Duplicate</button>
      <button id="dt-rename" class="secondary" type="button">Rename</button><button id="dt-remove" class="secondary" type="button">Delete table</button>
      <button id="dt-add-row" class="secondary" type="button">＋ Row</button><button id="dt-add-col" class="secondary" type="button">＋ Column</button><button id="dt-to-working" class="secondary" type="button">↑ Cell to Working equation</button>
      <button id="dt-remove-row" class="secondary" type="button">− Last row</button><button id="dt-remove-col" class="secondary" type="button">− Last column</button>
    </div><nav class="dt-tabs" id="dt-tabs" aria-label="Open tables"></nav>
    <div class="data-toolbar"><label>Filter rows<input type="search" id="dt-filter" placeholder="Search all columns"></label>
      <label>Sort by<select id="dt-sortcol"></select></label><label>Direction<select id="dt-sortdir"><option value="asc">Ascending</option><option value="desc">Descending</option></select></label>
      <button id="dt-sort" class="secondary" type="button">Sort table</button><button id="dt-clear-filter" class="secondary" type="button">Clear filter</button></div>
    <p id="dt-status" class="graph-data-muted" role="status">Start editing cells or import data.</p>
    <div class="table-zoom-toolbar"><label for="table-zoom">Table zoom <output id="table-zoom-value">100%</output></label><button type="button" id="table-zoom-out" class="secondary" title="Zoom out">−</button><input id="table-zoom" type="range" min="50" max="200" value="100" step="10"><button type="button" id="table-zoom-in" class="secondary" title="Zoom in">＋</button><button type="button" class="secondary" id="table-zoom-reset">100%</button></div><div class="dt-grid-scroll"><div id="table-zoom-content"><table class="dt-sheet" id="dt-sheet" aria-label="Editable spreadsheet"></table></div></div>
    <p class="graph-data-muted">Select a cell to edit. Formulas begin with <code>=</code>; examples: <code>=A1*B1</code>, <code>=SUM(B1:B4)</code>, <code>=AVERAGE(A1:A9)</code>, <code>=IF(A1&gt;1,B1,0)</code>, <code>=Data2!A1</code>. Row 1 is the first data row; column names are displayed separately.</p>
    <section class="dt-box"><h3>Database operations</h3><div class="data-toolbar">
      <label>Left table<select id="dt-left"></select></label><label>Right table<select id="dt-right"></select></label>
      <label>Operation<select id="dt-op"><option value="inner">INNER JOIN</option><option value="left">LEFT JOIN</option><option value="right">RIGHT JOIN</option><option value="full">FULL OUTER JOIN</option><option value="unionall">UNION ALL</option><option value="union">UNION DISTINCT</option><option value="intersect">INTERSECT</option><option value="except">EXCEPT</option></select></label>
      <label>Left key<select id="dt-left-key"></select></label><label>Right key<select id="dt-right-key"></select></label>
      <button id="dt-run" class="primary" type="button">Run → New table</button></div></section>
    <section class="dt-box"><h3>Import / export</h3><div class="data-toolbar">
      <label>Import CSV / TSV / JSON<input id="dt-import" type="file" accept=".csv,.tsv,.json,text/csv,application/json"></label>
      <button id="dt-export-csv" class="secondary" type="button">↓ Export CSV</button><button id="dt-export-json" class="secondary" type="button">↓ Export JSON</button>
      <button id="dt-send-graph" class="primary" type="button">↗ Show in graphs</button></div>
      <details id="dt-advanced"><summary>Advanced dataset preview / X, Y, Z mapping</summary></details></section></div>`;
  const oldImporter=$('graph-data-panel');if(oldImporter)$('dt-advanced').append(oldImporter);
  const graphControls=el('div',{class:'dt-graph-tools'});
  graphControls.innerHTML=`<div class="data-toolbar">
    <label>Table<select id="dt-graph-table"></select></label>
    <label>Graph type<select id="dt-chart-type"><option value="scatter">2D scatter</option><option value="line">2D line</option><option value="scatter3d">3D scatter</option><option value="grid3d">3D grid mesh</option><option value="bar">Bar chart</option><option value="pie">Pie chart</option></select></label>
    <label>Category / X<select id="dt-graph-x"></select></label><label>Values / Y<select id="dt-graph-y"></select></label>
    <label id="dt-graph-z-label">Z<select id="dt-graph-z"></select></label>
    <button id="dt-plot-table" class="primary" type="button">Plot table</button><button id="dt-add-series" class="secondary" type="button">＋ Add series</button><button id="dt-clear-series" class="secondary" type="button">Clear added series</button></div>
    <p class="graph-data-muted" id="dt-chart-status" role="status">Select a data table and chart.</p>`;
  $('graph-examples').after(graphControls);
  const chartDiv=el('div',{id:'dt-graph-chart'}); chartDiv.hidden=true;
  chartDiv.innerHTML='<canvas id="dt-chart-canvas" width="1160" height="650" aria-label="Table bar or pie chart" role="img"></canvas><button id="dt-chart-download" class="secondary" type="button">↓ Export PNG</button>';
  document.querySelector('.graph-canvas-wrap').before(chartDiv);
  const about=el('details',{id:'about-panel',class:'panel'});
  about.style.padding='16px 22px';about.innerHTML='<summary style="cursor:pointer;font-weight:750">About ProMathStudio · Contact · License</summary><p>Created by <strong>Saeed Mohammad Salehi</strong>. Contact: <a href="mailto:Saeedmsalehi1990@gmail.com">Saeedmsalehi1990@gmail.com</a>.</p><p>© 2026 Saeed Mohammad Salehi. MIT License: <a href="https://github.com/saeedsai/ProMathStudio/blob/main/LICENSE">View license</a>.</p>';
  $('connected-hub').after(about);

  let tables=[],selected=null,serial=1,chartSelection=null,focusedCell=null;
  const active=()=>tables.find(t=>t.id===selected)||tables[0];
  const notify=(msg,error=false)=>{const n=$('dt-status');n.textContent=msg;n.style.color=error?'#ad3248':'#576c86';};
  const makeTable=(name='Table',columns=['A','B','C'],rows=[['','',''],['','',''],['','','']])=>{
    if(tables.length>=20)throw Error('Maximum 20 tables per workbook.');
    const unique=uniqueName(name);const table={id:'sheet-'+(serial++),name:unique,columns:columns.map(String),rows:rows.map(r=>columns.map((_,i)=>r[i]===undefined?'':String(r[i])))};
    validate(table);tables.push(table);selected=table.id;render();save();return table;
  };
  const uniqueName=(n,excludeId=null)=>{let base=String(n||'Table').replace(/[^a-zA-Z0-9_ ]/g,'_').trim().slice(0,44)||'Table';let title=base,number=2;while(tables.some(t=>t.id!==excludeId&&t.name.toLowerCase()===title.toLowerCase()))title=base+'_'+number++;return title;};
  const validate=t=>{if(!t||!Array.isArray(t.columns)||!Array.isArray(t.rows)||!t.columns.length||t.columns.length>MAX_COLUMNS||t.rows.length>MAX_ROWS)throw Error('Table exceeds 32 columns or 6,000 rows.');for(const row of t.rows)if(!Array.isArray(row)||row.length!==t.columns.length)throw Error('Inconsistent data row width.');};
  const getByName=name=>tables.find(t=>t.name.toLowerCase()===String(name).toLowerCase());
  const value=(t,r,c,stack=new Set())=>{
    if(!t||r<0||r>=t.rows.length||c<0||c>=t.columns.length)return 0;
    const raw=t.rows[r][c];if(!String(raw).startsWith('='))return raw;
    const key=t.id+':'+r+':'+c;
    if(stack.has(key))throw Error('#CYCLE');if(stack.size>180)throw Error('#DEPTH');
    const next=new Set(stack);next.add(key);return formula(raw.slice(1),t,next);
  };
  // Structural edits preserve the referenced cell identity, including $-anchored
  // addresses. References to a deleted cell become an explicit #REF! error.
  const referencePattern=/((?:'[^']+'|[A-Za-z_][A-Za-z0-9_]*)!)?(\$?)([A-Za-z]{1,3})(\$?)([1-9]\d*)/g;
  function shiftReferences(edited,axis,index,delta){
    for(const sheet of tables)for(const row of sheet.rows)for(let c=0;c<row.length;c++){
      const raw=String(row[c]);if(!raw.startsWith('='))continue;
      row[c]=raw.replace(referencePattern,(match,prefix,colAnchor,letters,rowAnchor,digits,offset,whole)=>{
        // Never rewrite a substring of an identifier, decimal literal or name.
        if(offset&&/[A-Za-z0-9_.$]/.test(whole[offset-1]))return match;
        const after=whole[offset+match.length];
        if(after&&/[A-Za-z0-9_.$]/.test(after))return match;
        const name=prefix?prefix.slice(0,-1).replace(/^'|'$/g,''):sheet.name;
        if(name.toLowerCase()!==edited.name.toLowerCase())return match;
        const position=axis==='row'?Number(digits)-1:colIndex(letters);
        if(delta<0&&position===index)return '#REF!';
        const moved=position>=index+(delta<0?1:0)?position+delta:position;
        if(moved===position)return match;
        return (prefix||'')+colAnchor+(axis==='column'?colLetter(moved):letters)+rowAnchor+(axis==='row'?moved+1:digits);
      });
    }
  }
  // Stable full-row sort preserves referenced cell identity in all sheets.
  // Unsafe noncontiguous ranges abort before any workbook mutation.
  function sortRows(column,direction='asc'){
    const t=active();
    if(!Number.isInteger(column)||column<0||column>=t.columns.length)throw Error('Invalid sort column.');
    if(direction!=='asc'&&direction!=='desc')throw Error('Invalid sort direction.');
    const values=evaluated(t),sign=direction==='desc'?-1:1;
    const order=t.rows.map((row,i)=>({row,i})).sort((a,b)=>{
      const cmp=String(values[a.i][column]).localeCompare(String(values[b.i][column]),undefined,{numeric:true});
      return sign*cmp||a.i-b.i;
    });
    if(order.every((entry,i)=>entry.i===i))return;
    const newRow=Array(t.rows.length);order.forEach((entry,i)=>{newRow[entry.i]=i;});
    const rangePattern=/(\$?[A-Za-z]{1,3}\$?[1-9]\d*):(\$?[A-Za-z]{1,3}\$?[1-9]\d*)/g;
    const rowOf=ref=>Number(/[1-9]\d*$/.exec(ref)[0])-1;
    const rewrite=(raw,sheet)=>{
      if(!String(raw).startsWith('='))return raw;
      const ranges=[];
      let next=String(raw).replace(rangePattern,(match,left,right,offset,whole)=>{
        if((offset&&/[A-Za-z0-9_.$'!]/.test(whole[offset-1]))||/[A-Za-z0-9_.$']/.test(whole[offset+match.length]||''))return match;
        if(sheet.id!==t.id)return match;
        const lo=Math.min(rowOf(left),rowOf(right)),hi=Math.max(rowOf(left),rowOf(right));
        if(hi>=newRow.length)throw Error('Cannot sort: formula range '+match+' exceeds the table.');
        const positions=[];for(let i=lo;i<=hi;i++)positions.push(newRow[i]);
        const lower=Math.min(...positions),upper=Math.max(...positions);
        if(upper-lower+1!==positions.length)throw Error('Cannot sort: formula range '+match+' would split into noncontiguous rows.');
        const forward=rowOf(left)<=rowOf(right);
        const mapped=left.replace(/[1-9]\d*$/,String((forward?lower:upper)+1))+':'+right.replace(/[1-9]\d*$/,String((forward?upper:lower)+1));
        const token='\uE000'+ranges.length+'\uE001';ranges.push(mapped);return token;
      });
      next=next.replace(referencePattern,(match,prefix,colAnchor,letters,rowAnchor,digits,offset,whole)=>{
        if((offset&&/[A-Za-z0-9_.$']/.test(whole[offset-1]))||/[A-Za-z0-9_.$']/.test(whole[offset+match.length]||''))return match;
        const name=prefix?prefix.slice(0,-1).replace(/^'|'$/g,''):sheet.name;
        if(name.toLowerCase()!==t.name.toLowerCase())return match;
        const old=Number(digits)-1;if(old>=newRow.length)return match;
        return (prefix||'')+colAnchor+letters+rowAnchor+(newRow[old]+1);
      });
      return next.replace(/\uE000(\d+)\uE001/g,(_,i)=>ranges[Number(i)]);
    };
    const rewritten=tables.map(sheet=>sheet.rows.map(row=>row.map(cell=>rewrite(cell,sheet))));
    for(let i=0;i<tables.length;i++)tables[i].rows=tables[i].id===t.id?order.map(entry=>rewritten[i][entry.i]):rewritten[i];
    focusedCell=null;render();save();
  }
  function structuralEdit(axis,index,delta,values){
    const t=active(),size=axis==='row'?t.rows.length:t.columns.length,limit=axis==='row'?MAX_ROWS:MAX_COLUMNS;
    if(!Number.isInteger(index)||index<0||index>size||(delta<0&&index===size))throw Error('Invalid '+axis+' position.');
    if(delta>0&&size>=limit)throw Error('Maximum '+limit+' '+(axis==='row'?'rows':'columns')+'.');
    if(delta<0&&axis==='column'&&size<=1)throw Error('A table needs one column.');
    if(axis==='row'&&delta>0&&values&&values.length!==t.columns.length)throw Error('Row width mismatch.');
    shiftReferences(t,axis,index,delta);
    if(axis==='row'){
      if(delta>0)t.rows.splice(index,0,values?values.map(v=>String(v).slice(0,8000)):t.columns.map(()=>''));
      else t.rows.splice(index,1);
    }else{
      if(delta>0){t.columns.splice(index,0,'Column'+(size+1));t.rows.forEach(r=>r.splice(index,0,''));}
      else{t.columns.splice(index,1);t.rows.forEach(r=>r.splice(index,1));}
    }
    render();save();
  }
  const number=v=>{if(v===null||v==='')return 0;const n=Number(v);if(!Number.isFinite(n))throw Error('Not numeric: '+v);return n;};
  const splitArgs=str=>{const out=[];let depth=0,start=0;for(let i=0;i<str.length;i++){if(str[i]==='(')depth++;else if(str[i]===')')depth--;else if(str[i]===','&&depth===0){out.push(str.slice(start,i));start=i+1;}}out.push(str.slice(start));return out;};
  function formula(expr,t,stack){
    expr=String(expr).trim();if(expr.length>500)throw Error('#LIMIT');
    const ifMatch=/^IF\((.*)\)$/i.exec(expr);
    if(ifMatch){const args=splitArgs(ifMatch[1]);if(args.length!==3)throw Error('#IF');const m=/^(.*?)(>=|<=|!=|<>|==|=|>|<)(.*)$/.exec(args[0]);const test=m?(()=>{const a=compute(m[1],t,stack),b=compute(m[3],t,stack);return ({'>':a>b,'<':a<b,'>=':a>=b,'<=':a<=b,'=':a===b,'==':a===b,'!=':a!==b,'<>':a!==b})[m[2]];})():Boolean(compute(args[0],t,stack));return compute(args[test?1:2],t,stack);}
    return compute(expr,t,stack);
  }
  function compute(expr,t,stack){
    if(String(expr).includes('#REF!'))throw Error('#REF!');
    expr=String(expr).replace(/\b([A-Za-z][A-Za-z0-9_]*)\(([^()]*)\)/g,(all,name,body)=>{
      const fn=window.MathStudio.customFunctions?.list().find(f=>f.name.toLowerCase()===name.toLowerCase());
      if(!fn)return all;
      const values=splitArgs(body).map(part=>compute(part,t,stack));
      return '('+window.MathStudio.customFunctions.evaluate(name,values)+')';
    });
    expr=String(expr).replace(/\bIF\(([^()]*)\)/gi,(all,body)=>'('+number(formula('IF('+body+')',t,stack))+')');
    // Aggregations accept ranges or comma-separated arguments. Nested expressions are supported by the recursive evaluator.
    expr=String(expr).replace(/\b(SUM|AVERAGE|AVG|MIN|MAX|COUNT)\s*\(([^()]*)\)/gi,(all,fn,body)=>{
      const nums=[];for(const arg of splitArgs(body)){const range=/^(\$?)([A-Z]+)(\$?)(\d+):(\$?)([A-Z]+)(\$?)(\d+)$/i.exec(arg.trim());
        if(range){const c0=colIndex(range[2]),r0=+range[4]-1,c1=colIndex(range[6]),r1=+range[8]-1;
          if((Math.abs(c1-c0)+1)*(Math.abs(r1-r0)+1)>6000)throw Error('#RANGE');
          for(let rr=Math.min(r0,r1);rr<=Math.max(r0,r1);rr++)for(let cc=Math.min(c0,c1);cc<=Math.max(c0,c1);cc++){const v=value(t,rr,cc,stack);if(v!==''&&Number.isFinite(Number(v)))nums.push(Number(v));}
        } else {const v=compute(arg,t,stack);if(Number.isFinite(Number(v)))nums.push(Number(v));}}
      const upper=fn.toUpperCase();const x=upper==='SUM'?nums.reduce((a,b)=>a+b,0):upper==='COUNT'?nums.length:upper==='AVERAGE'||upper==='AVG'?(nums.reduce((a,b)=>a+b,0)/(nums.length||1)):upper==='MIN'?Math.min(...nums):Math.max(...nums);
      return '('+(Number.isFinite(x)?x:0)+')';
    });
    // Limited token grammar intentionally avoids eval()/Function() and script execution.
    const src=expr.trim();const rx=/\s*(?:((?:'[^']+'|[A-Za-z_][A-Za-z0-9_]*)!\$?[A-Za-z]+\$?\d+|\$?[A-Za-z]+\$?\d+)|((?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?)|([()+\-*/^]))/giy;
    const tokens=[];let pos=0;
    while(pos<src.length){rx.lastIndex=pos;const m=rx.exec(src);if(!m||m.index!==pos)throw Error('#FORMULA');tokens.push(m[1]?{type:'cell',v:m[1]}:m[2]?{type:'num',v:Number(m[2])}:{type:m[3]});pos=rx.lastIndex;if(tokens.length>400)throw Error('#LIMIT');}
    let at=0;const peek=()=>tokens[at]?.type;
    function primary(){const tok=tokens[at++];if(!tok)throw Error('#FORMULA');if(tok.type==='num')return tok.v;
      if(tok.type==='cell'){let target=t,ref=tok.v;const bang=ref.lastIndexOf('!');if(bang>=0){target=getByName(ref.slice(0,bang).replace(/^'|'$/g,''));ref=ref.slice(bang+1);if(!target)throw Error('#SHEET');}
        const m=/^(\$?)([A-Za-z]+)(\$?)(\d+)$/.exec(ref);if(!m)throw Error('#REF');return number(value(target,Number(m[4])-1,colIndex(m[2]),stack));}
      if(tok.type==='('){const v=addition();if(peek()!==')')throw Error('#PAREN');at++;return v;}
      if(tok.type==='+'||tok.type==='-'){const v=primary();return tok.type==='-'?-v:v;}throw Error('#FORMULA');}
    function power(){let v=primary();if(peek()==='^'){at++;v=Math.pow(v,power());}return v;}
    function mult(){let v=power();while(peek()==='*'||peek()==='/'){const op=tokens[at++].type,r=power();v=op==='*'?v*r:v/r;}return v;}
    function addition(){let v=mult();while(peek()==='+'||peek()==='-'){const op=tokens[at++].type,r=mult();v=op==='+'?v+r:v-r;}return v;}
    const result=addition();if(at!==tokens.length||!Number.isFinite(result))throw Error('#VALUE');return Number(result.toPrecision(13));
  }
  const evaluated=t=>t.rows.map((row,r)=>row.map((_,c)=>{try{return value(t,r,c);}catch(e){return e.message.startsWith('#')?e.message:'#ERR';}}));
  function save(){try{localStorage.setItem('mathstudio-tables-v1',JSON.stringify(exportState()));}catch{notify('Browser storage is unavailable or full; export the project JSON to keep this workbook.',true);}}
  function exportState(){return {version:1,selected,tables:deep(tables)};}
  function restoreState(state){
    if(!state||!Array.isArray(state.tables)){tables=[];selected=null;makeTable('Data1',['x','y','z'],[['0','0','0'],['1','1','1'],['2','4','8']]);return;}
    if(state.tables.length>20)throw Error('Too many imported tables.');
    const next=state.tables.map((t,i)=>({id:'sheet-'+(i+1),name:String(t.name||'Table'+i).slice(0,48),columns:(t.columns||[]).map(v=>String(v).slice(0,80)),rows:(t.rows||[]).map(r=>r.map(v=>String(v??'').slice(0,8000)))}));
    next.forEach(validate);const names=next.map(t=>t.name.toLowerCase());if(new Set(names).size!==names.length)throw Error('Duplicate table names in project.');
    tables=next;serial=next.length+1;const old=(state.tables||[]).find(t=>t.id===state.selected);selected=old?next[state.tables.indexOf(old)].id:next[0]?.id;
    if(!tables.length)makeTable('Data1',['x','y','z'],[['0','0','0']]); else {render();save();}
  }
  function optionList(sel,list,preferred){const prior=preferred===undefined?sel.value:String(preferred);sel.replaceChildren();for(const [v,text] of list){sel.append(el('option',{value:String(v)},text));}if(list.some(([v])=>String(v)===prior))sel.value=prior;}
  const tableOptions=()=>tables.map(t=>[t.id,t.name]);
  function refreshMenus(){for(const id of ['dt-left','dt-right','dt-graph-table'])optionList($(id),tableOptions(),$(id).value||selected);
    const l=tables.find(t=>t.id===$('dt-left').value)||active(),r=tables.find(t=>t.id===$('dt-right').value)||active();
    if(l)optionList($('dt-left-key'),l.columns.map((h,i)=>[i,h]));if(r)optionList($('dt-right-key'),r.columns.map((h,i)=>[i,h]));
    refreshGraphColumns();}
  function refreshGraphColumns(){const t=tables.find(v=>v.id===$('dt-graph-table').value)||active();if(!t)return;
    const options=t.columns.map((n,i)=>[i,n]);for(const id of ['dt-graph-x','dt-graph-y','dt-graph-z'])optionList($(id),options);
    if(!$('dt-graph-y').value&&t.columns.length>1)$('dt-graph-y').value='1';if(!$('dt-graph-z').value&&t.columns.length>2)$('dt-graph-z').value='2';}
  function render(){const t=active();if(!t)return;selected=t.id;
    $('dt-tabs').replaceChildren();for(const sheet of tables){const b=el('button',{type:'button',class:'dt-tab'+(sheet.id===t.id?' active':'')},sheet.name+' ('+sheet.rows.length+')');b.addEventListener('click',()=>{selected=sheet.id;$('dt-filter').value='';render();save();});$('dt-tabs').append(b);}
    optionList($('dt-sortcol'),t.columns.map((n,i)=>[i,n]));const grid=$('dt-sheet');grid.replaceChildren();const head=el('thead'),hr=el('tr');hr.append(el('th',{class:'dt-rownum'},'#'));
    for(let c=0;c<t.columns.length;c++){const th=el('th');const input=el('input',{'aria-label':'Column '+colLetter(c),value:t.columns[c]});input.value=t.columns[c];input.addEventListener('change',()=>{t.columns[c]=input.value.slice(0,80)||colLetter(c);save();render();});th.append(input);hr.append(th);}head.append(hr);grid.append(head);
    const body=el('tbody');const q=$('dt-filter').value.trim().toLowerCase(),rows=evaluated(t),show=[];
    for(let r=0;r<t.rows.length;r++)if(!q||rows[r].some(v=>String(v).toLowerCase().includes(q)))show.push(r);
    for(const r of show.slice(0,MAX_DISPLAY)){const tr=el('tr');tr.append(el('th',{class:'dt-rownum'},r+1));for(let c=0;c<t.columns.length;c++){
      const td=el('td');const val=rows[r][c],input=el('input',{'aria-label':colLetter(c)+(r+1),'data-row':r,'data-col':c});
      input.value=String(val??'');if(String(val).startsWith('#'))input.classList.add('dt-error');
      input.addEventListener('focus',()=>{focusedCell={id:t.id,r,c};input.value=t.rows[r][c];input.select();});
      input.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();input.blur();}});
      input.addEventListener('change',()=>{t.rows[r][c]=input.value.slice(0,8000);save();});
      input.addEventListener('blur',()=>{t.rows[r][c]=input.value.slice(0,8000);save();requestAnimationFrame(render);});td.append(input);tr.append(td);
    }body.append(tr);}grid.append(body);
    notify(t.name+' · '+t.rows.length+' rows × '+t.columns.length+' columns'+(show.length>MAX_DISPLAY?' · displaying first '+MAX_DISPLAY+' rows':'')+(q?' · '+show.length+' matching rows':''));
    refreshMenus();}
  const safeAction=fn=>{try{fn();}catch(error){notify(error.message,true);}};
  $('dt-new').addEventListener('click',()=>safeAction(()=>makeTable('Data'+(tables.length+1),['A','B','C'],[['','',''],['','',''],['','','']])));
  $('dt-copy').addEventListener('click',()=>safeAction(()=>{const t=active();makeTable(t.name+'_copy',t.columns,t.rows);}));
  $('dt-rename').addEventListener('click',()=>safeAction(()=>{const t=active(),name=prompt('Table name (letters, numbers, underscores):',t.name);if(name===null)return;t.name=uniqueName(name,t.id);save();render();}));
  $('dt-remove').addEventListener('click',()=>safeAction(()=>{if(tables.length===1)throw Error('Keep at least one table.');if(!confirm('Delete selected table?'))return;tables=tables.filter(t=>t.id!==selected);selected=tables[0].id;render();save();}));
  $('dt-add-row').addEventListener('click',()=>safeAction(()=>structuralEdit('row',active().rows.length,1)));
  $('dt-add-col').addEventListener('click',()=>safeAction(()=>structuralEdit('column',active().columns.length,1)));
  $('dt-remove-row').addEventListener('click',()=>safeAction(()=>{if(active().rows.length)structuralEdit('row',active().rows.length-1,-1);}));
  $('dt-remove-col').addEventListener('click',()=>safeAction(()=>structuralEdit('column',active().columns.length-1,-1)));
  $('dt-to-working').addEventListener('click',()=>safeAction(()=>{const t=active(),cell=focusedCell?.id===t.id?focusedCell:{r:0,c:0};const val=String(value(t,cell.r,cell.c)||'');window.MathStudio.bridge.select(val,'data tables',{archive:true});notify('Sent cell '+colLetter(cell.c)+(cell.r+1)+' to the shared Working equation.');}));
  $('dt-filter').addEventListener('input',render);$('dt-clear-filter').addEventListener('click',()=>{$('dt-filter').value='';render();});
  $('dt-sort').addEventListener('click',()=>safeAction(()=>sortRows(Number($('dt-sortcol').value),$('dt-sortdir').value)));
  for(const id of ['dt-left','dt-right'])$(id).addEventListener('change',refreshMenus);
  function operation(type,l,r,lkey=0,rkey=0){const A=evaluated(l),B=evaluated(r),isJoin=['inner','left','right','full'].includes(type);
    if(isJoin){const headers=l.columns.concat(r.columns.map(h=>l.columns.includes(h)?r.name+'_'+h:h));const out=[];
      const matched=new Set();for(let i=0;i<A.length;i++){let ok=false;for(let j=0;j<B.length;j++)if(String(A[i][lkey])===String(B[j][rkey])){out.push(A[i].concat(B[j]));ok=true;matched.add(j);if(out.length>MAX_ROWS)throw Error('Join exceeds 6,000 rows.');}
        if(!ok&&['left','full'].includes(type))out.push(A[i].concat(r.columns.map(()=>'')));}
      if(['right','full'].includes(type))for(let j=0;j<B.length;j++)if(!matched.has(j))out.push(l.columns.map(()=>'' ).concat(B[j]));
      if(out.length>MAX_ROWS||headers.length>MAX_COLUMNS)throw Error('Operation exceeds 6,000 rows or 32 columns.');return {headers,rows:out};}
    if(l.columns.length!==r.columns.length)throw Error('Set operations require matching column counts.');
    const key=row=>JSON.stringify(row.map(v=>String(v))),setB=new Set(B.map(key));let out;
    if(type==='unionall')out=A.concat(B);else if(type==='union')out=Array.from(new Map(A.concat(B).map(row=>[key(row),row])).values());
    else if(type==='intersect')out=Array.from(new Map(A.filter(row=>setB.has(key(row))).map(row=>[key(row),row])).values());
    else if(type==='except')out=Array.from(new Map(A.filter(row=>!setB.has(key(row))).map(row=>[key(row),row])).values());
    else throw Error('Unsupported table operation.');
    if(out.length>MAX_ROWS)throw Error('Result exceeds 6,000 rows.');return {headers:l.columns.slice(),rows:out};}
  $('dt-run').addEventListener('click',()=>safeAction(()=>{const l=tables.find(t=>t.id===$('dt-left').value),r=tables.find(t=>t.id===$('dt-right').value);if(!l||!r)throw Error('Select two tables.');const mode=$('dt-op').value,result=operation(mode,l,r,Number($('dt-left-key').value),Number($('dt-right-key').value));const resultTable=makeTable(l.name+'_'+mode+'_'+r.name,result.headers,result.rows);notify('Created '+resultTable.name+' with '+result.rows.length+' rows.');}));
  const download=(filename,contents,mime)=>{const url=URL.createObjectURL(new Blob([contents],{type:mime}));const a=el('a',{href:url,download:filename});document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);};
  $('dt-export-csv').addEventListener('click',()=>safeAction(()=>{const t=active(),rows=[t.columns,...evaluated(t)];download(t.name+'.csv',rows.map(row=>row.map(csvCell).join(',')).join('\r\n')+'\r\n','text/csv;charset=utf-8');}));
  $('dt-export-json').addEventListener('click',()=>safeAction(()=>{const t=active(),rows=evaluated(t);download(t.name+'.json',JSON.stringify(rows.map(row=>Object.fromEntries(t.columns.map((h,i)=>[h,row[i]]))),null,2),'application/json');}));
  $('dt-import').addEventListener('change',async event=>{const file=event.target.files?.[0];if(!file)return;try{
    if(file.size>MAX_BYTES)throw Error('Import file exceeds 1 MB.');if(!/\.(csv|tsv|json)$/i.test(file.name))throw Error('Choose CSV, TSV or JSON.');
    const text=await file.text(),decoder=window.MathStudio.graphData;const tbl=/\.json$/i.test(file.name)?decoder.parseJSON(text):decoder.parseCSV(text);
    const t=makeTable(file.name.replace(/\.(csv|tsv|json)$/i,''),tbl.headers,tbl.rows);notify('Imported '+file.name+': '+t.rows.length+' rows.');
  }catch(e){notify('Import failed: '+e.message,true);}finally{event.target.value='';}});
  // Existing chart-data importer is now in the Data Tables tab. Imports there also create a sheet.
  $('graph-data-file').addEventListener('change',async event=>{const file=event.target.files?.[0];if(!file)return;try{if(file.size>MAX_BYTES)throw Error('File too large');const text=await file.text();const tbl=/\.json$/i.test(file.name)?window.MathStudio.graphData.parseJSON(text):window.MathStudio.graphData.parseCSV(text);makeTable(file.name.replace(/\.[^.]+$/,''),tbl.headers,tbl.rows);}catch(e){notify('Import failed: '+e.message,true);}});
  function chartColumns(){const t=tables.find(x=>x.id===$('dt-graph-table').value)||active();if(!t)return;const opts=t.columns.map((h,i)=>[i,h]);
    optionList($('dt-graph-x'),opts);optionList($('dt-graph-y'),opts);optionList($('dt-graph-z'),opts);
    if(!chartSelection||chartSelection.table!==t.id){$('dt-graph-x').value='0';$('dt-graph-y').value=String(Math.min(1,t.columns.length-1));$('dt-graph-z').value=String(Math.min(2,t.columns.length-1));}
    $('dt-graph-z-label').hidden=!['scatter3d','grid3d'].includes($('dt-chart-type').value);
  }
  $('dt-graph-table').addEventListener('change',chartColumns);
  $('dt-chart-type').addEventListener('change',chartColumns);
  function drawCategorical(t,kind,xi,yi){const rows=evaluated(t),sums=new Map();for(const row of rows){const key=String(row[xi]??'').trim();const v=Number(row[yi]);if(!key||!Number.isFinite(v))continue;sums.set(key,(sums.get(key)||0)+v);}
    let entries=[...sums.entries()];if(entries.length>24){entries=entries.slice(0,23).concat([['Other',entries.slice(23).reduce((sum,x)=>sum+x[1],0)]]);}
    if(!entries.length)throw Error('Select a numeric values column with nonempty category labels.');
    const canvas=$('dt-chart-canvas'),ctx=canvas.getContext('2d'),w=canvas.width,h=canvas.height;
    ctx.clearRect(0,0,w,h);ctx.fillStyle='#fff';ctx.fillRect(0,0,w,h);ctx.fillStyle='#1d2a49';ctx.font='bold 25px Arial';ctx.fillText(t.name+' — '+(kind==='pie'?'Pie':'Bar')+' chart',45,45);
    const colors=Array.from({length:24},(_,i)=>window.MathStudio.graphAppearance?.color(i)||'#536be8');
    if(kind==='bar'){const margin=90,max=Math.max(0,...entries.map(e=>e[1])),min=Math.min(0,...entries.map(e=>e[1]));const lo=Math.min(0,min),hi=Math.max(1,max),barW=(w-2*margin)/entries.length;
      ctx.strokeStyle='#90a1c6';ctx.beginPath();ctx.moveTo(margin,100);ctx.lineTo(margin,h-95);ctx.lineTo(w-margin,h-95);ctx.stroke();
      for(let i=0;i<entries.length;i++){const [name,v]=entries[i],x=margin+i*barW+barW*.13,bw=barW*.74;
        const y0=100+(hi/(hi-lo))*(h-195),y=100+(hi-v)/(hi-lo)*(h-195);ctx.fillStyle=colors[i%colors.length];ctx.fillRect(x,Math.min(y,y0),bw,Math.max(1,Math.abs(y-y0)));
        ctx.fillStyle='#566783';ctx.font='12px Arial';ctx.save();ctx.translate(x+bw/2,h-84);ctx.rotate(-Math.PI/6);ctx.fillText(name.slice(0,14),-4,0);ctx.restore();
        ctx.font='bold 12px Arial';ctx.fillText(String(+v.toFixed(4)),x,Math.min(y,y0)-8);}}
    else{const positive=entries.filter(v=>v[1]>0),sum=positive.reduce((a,b)=>a+b[1],0);if(!sum)throw Error('Pie chart requires positive values.');let angle=-Math.PI/2;
      for(let i=0;i<positive.length;i++){const [name,v]=positive[i],end=angle+v/sum*Math.PI*2;ctx.beginPath();ctx.moveTo(400,330);ctx.arc(400,330,230,angle,end);ctx.closePath();ctx.fillStyle=colors[i%colors.length];ctx.fill();angle=end;
        ctx.fillRect(760,115+i*24,13,13);ctx.fillStyle='#2b3d59';ctx.font='15px Arial';ctx.fillText(name.slice(0,30)+' · '+(100*v/sum).toFixed(1)+'%',783,127+i*24);}}
    chartDiv.hidden=false;document.querySelector('#graph-panel .graph-canvas-wrap').classList.add('workspace-hidden');$('dt-chart-status').textContent=kind+' chart of '+entries.length+' categories from '+t.name+'.';
  }
  function sendToGraph(){const t=tables.find(x=>x.id===$('dt-graph-table').value)||active();if(!t)throw Error('No table selected.');const x=Number($('dt-graph-x').value),y=Number($('dt-graph-y').value),z=Number($('dt-graph-z').value),kind=$('dt-chart-type').value;
    if(x===y||(['scatter3d','grid3d'].includes(kind)&&(x===z||y===z)))throw Error('Choose different X/Y/Z columns.');
    chartSelection={table:t.id,kind,x,y,z};window.MathStudio.advanced.mode('graph');
    if(kind==='bar'||kind==='pie'){drawCategorical(t,kind,x,y);return;}
    chartDiv.hidden=true;document.querySelector('#graph-panel .graph-canvas-wrap').classList.remove('workspace-hidden');
    window.MathStudio.advanced[kind==='scatter3d'||kind==='grid3d'?'plot3D':'plot2D']();
    const chart=window.MathStudio.graphData;chart.loadTable({headers:t.columns,rows:evaluated(t)},t.name,{x,y,z});
    $('graph-data-x').value=String(x);$('graph-data-y').value=String(y);$('graph-data-z').value=String(z);
    $('graph-data-style').value=kind==='line'?'line':kind==='grid3d'?'grid':'points';chart.refresh();
    const input=$('graph-input');if(input.value.trim()==='y = sin(x)\ny = cos(x)')input.value='';
    $('graph-plot').click();$('dt-chart-status').textContent='Plotted '+t.name+' as '+kind+'. Equation plots can also be added.';
  }
  $('dt-plot-table').addEventListener('click',()=>safeAction(sendToGraph));
  $('dt-add-series').addEventListener('click',()=>safeAction(()=>{
    const table=tables.find(t=>t.id===$('dt-graph-table').value)||active(),kind=$('dt-chart-type').value;
    if(['bar','pie'].includes(kind))throw Error('Overlay supports 2D/3D scatter, line, and grid.');
    const mode=['scatter3d','grid3d'].includes(kind)?'3d':'2d';
    window.MathStudio.advanced.mode('graph');
    if(window.MathStudio.advanced.currentGraphMode()!==mode){if(mode==='3d')window.MathStudio.advanced.plot3D();else window.MathStudio.advanced.plot2D();}
    chartDiv.hidden=true;document.querySelector('#graph-panel .graph-canvas-wrap').classList.remove('workspace-hidden');
    const mapping={x:Number($('dt-graph-x').value),y:Number($('dt-graph-y').value),z:Number($('dt-graph-z').value),mode,style:kind==='line'?'line':kind==='grid3d'?'grid':'points'};
    window.MathStudio.graphData.addTable({headers:table.columns,rows:evaluated(table)},table.name,mapping);
    $('dt-chart-status').textContent='Added series from '+table.name+'. Select another Y column or table to overlay.';
  }));
  $('dt-clear-series').addEventListener('click',()=>window.MathStudio.graphData.clearExtra());
  $('dt-send-graph').addEventListener('click',()=>safeAction(()=>{$('dt-graph-table').value=active().id;chartColumns();sendToGraph();}));
  // Export PNG via the canvas data URL; handle binary bytes without string-encoding conversion.
  $('dt-chart-download').onclick=()=>{const a=el('a',{href:$('dt-chart-canvas').toDataURL('image/png'),download:'ProMathStudio_chart.png'});document.body.append(a);a.click();a.remove();};
  window.MathStudio.dataTables={appendExpression:text=>{const t=active();if(t.rows.length>=MAX_ROWS)throw Error('Maximum 6,000 rows');const row=t.columns.map(()=>'' );row[0]=String(text).slice(0,8000);t.rows.push(row);render();save();return t;},get tables(){return tables;},get active(){return active();},exportState,restoreState,formula:(expr,sheet)=>formula(expr,getByName(sheet)||active(),new Set()),operation,plot:sendToGraph,create:makeTable,calculate:table=>evaluated(table||active()),importData:(table,name)=>makeTable(name,table.headers,table.rows),insertRow:(i,v)=>structuralEdit('row',i,1,v),deleteRow:i=>structuralEdit('row',i,-1),insertColumn:i=>structuralEdit('column',i,1),deleteColumn:i=>structuralEdit('column',i,-1),sortRows,refresh:()=>{render();save()}};
  try{const stored=JSON.parse(localStorage.getItem('mathstudio-tables-v1')||'null');restoreState(stored);}catch{restoreState(null);}
})();

