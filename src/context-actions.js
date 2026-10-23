/* ProMathStudio: accessible, contextual commands. No eval or hidden clipboard access. */
(()=>{
  'use strict';
  const $=id=>document.getElementById(id), MS=window.MathStudio;
  const popup=document.createElement('div');popup.id='workspace-context-menu';popup.className='context-actions';popup.setAttribute('role','menu');popup.setAttribute('aria-label','Contextual workspace actions');popup.tabIndex=-1;popup.hidden=true;document.body.append(popup);
  let selection=null,internalClipboard='',returnFocus=null;
  const status=text=>{const id=selection?.area==='table'?'dt-status':selection?.area==='calc'?'calc-message':'hub-status';const e=$(id);if(e)e.textContent=text;};
  const note=e=>{status(e.message||String(e));};
  const close=()=>{popup.hidden=true;selection=null;};
  const copy=async data=>{internalClipboard=String(data??'');try{if(navigator.clipboard?.writeText)await navigator.clipboard.writeText(internalClipboard);}catch{}return internalClipboard;};
  const paste=async()=>{try{if(navigator.clipboard?.readText){const r=await navigator.clipboard.readText();if(r!==undefined)return r;}}catch{}return internalClipboard;};
  const insert=(el,value)=>{if(!el)return;const start=el.selectionStart??el.value.length,end=el.selectionEnd??start;el.setRangeText(String(value),start,end,'end');el.dispatchEvent(new Event('input',{bubbles:true}));el.focus();};
  const active=()=>MS.dataTables?.active;
  const update=()=>MS.dataTables?.refresh?.();
  const validate=(t,rows=t.rows.length,cols=t.columns.length)=>{if(rows>6000||cols>32)throw Error('The workbook supports up to 6,000 rows and 32 columns.');};
  function rowInsert(index,values){const t=active();validate(t,t.rows.length+1);t.rows.splice(index,0,values?values.map(x=>String(x).slice(0,8000)):t.columns.map(()=>''));update();}
  function rowDelete(index){const t=active();if(!t.rows[index])throw Error('Row not found.');if(!confirm('Delete row '+(index+2)+'? This cannot be undone.'))return;t.rows.splice(index,1);update();}
  function colInsert(index){const t=active();validate(t,t.rows.length,t.columns.length+1);t.columns.splice(index,0,'Column'+(t.columns.length+1));t.rows.forEach(row=>row.splice(index,0,''));update();}
  function colDelete(index){const t=active();if(t.columns.length<=1)throw Error('Keep at least one column.');if(!confirm('Delete column '+t.columns[index]+'? This cannot be undone.'))return;t.columns.splice(index,1);t.rows.forEach(row=>row.splice(index,1));update();}
  const validCoord=(r,c)=>{const t=active();if(!t||r<0||c<0||r>=t.rows.length||c>=t.columns.length)throw Error('Selected table cell is unavailable.');return t;};
  const setCell=(r,c,v)=>{const t=validCoord(r,c);t.rows[r][c]=String(v??'').slice(0,8000);update();};
  const csvEscape=v=>String(v??'').includes('\t')||String(v).includes('\n')?'"'+String(v).replace(/"/g,'""')+'"':String(v??'');
  function parseClipboard(content){return String(content).replace(/\r\n/g,'\n').split('\n').filter((s,i,arr)=>i<arr.length-1||s!=='').map(line=>line.split('\t'));}
  const pasteCells=async(r,c)=>{const text=await paste();if(!text){status('Clipboard is empty.');return;}const t=active(),rows=parseClipboard(text);if(!rows.length)return;const maxWidth=Math.max(...rows.map(x=>x.length)),maxRows=r+rows.length,maxCols=c+maxWidth;validate(t,maxRows,maxCols);
    while(t.rows.length<maxRows)t.rows.push(t.columns.map(()=>''));while(t.columns.length<maxCols){t.columns.push('Column'+(t.columns.length+1));t.rows.forEach(x=>x.push(''));}
    rows.forEach((row,ri)=>row.forEach((v,ci)=>{t.rows[r+ri][c+ci]=String(v).slice(0,8000);}));update();status('Pasted '+rows.length+' row(s) into table.');};
  function filterEquals(column,content){const t=active(),filter=$('dt-filter-column'),op=$('dt-filter-op'),value=$('dt-filter-value');if(!filter||!t)return;
    const details=$('data-menu-navigation')?.querySelectorAll('details')[1];if(details)details.open=true;
    filter.value=String(column);op.value='eq';value.value=String(content);$('dt-filter-apply').click();}
  function openPalette(){const btn=$('quick-symbols');if(!btn)return;const body=document.body;if(!body.classList.contains('library-open'))btn.click();$('palette-search')?.focus();}
  const dispatchRoute=(dest,raw)=>{const bridge=MS.bridge;bridge?.transfer(dest,raw,{source:'context menu'});};
  const item=(title,run,{danger=false}={})=>({title,run,danger});
  function actions(sel){const {area,kind,row:r,col:c,raw,target}=sel,items=[];const t=active();
    if(area==='table'){
      if(kind==='cell'){
        const src=()=>String(t.rows[r]?.[c]??'');
        items.push(item('Copy cell (formula)',()=>copy(src())),item('Copy displayed value',()=>copy(MS.dataTables.calculate(t)[r]?.[c]??'')),item('Cut cell',async()=>{await copy(src());setCell(r,c,'');}),item('Paste into cell / range',()=>pasteCells(r,c)),item('Clear cell',()=>setCell(r,c,'')),item('Send cell → Working equation',()=>{$('dt-to-working').click();}),item('Filter column = this value',()=>filterEquals(c,MS.dataTables.calculate(t)[r][c])),item('Insert row above',()=>rowInsert(r)),item('Insert row below',()=>rowInsert(r+1)),item('Duplicate row below',()=>rowInsert(r+1,t.rows[r].slice())),item('Delete this row',()=>rowDelete(r),{danger:true}),item('Insert column left',()=>colInsert(c)),item('Insert column right',()=>colInsert(c+1)),item('Delete this column',()=>colDelete(c),{danger:true}));
      }else if(kind==='row'){
        items.push(item('Copy row (tab-separated)',()=>copy(t.rows[r].map(csvEscape).join('\t'))),item('Paste row',()=>pasteCells(r,0)),item('Insert row above',()=>rowInsert(r)),item('Insert row below',()=>rowInsert(r+1)),item('Duplicate row',()=>rowInsert(r+1,t.rows[r].slice())),item('Delete row',()=>rowDelete(r),{danger:true}));
      }else if(kind==='column'){
        items.push(item('Rename column',()=>{const name=prompt('Column header',t.columns[c]);if(name!==null){t.columns[c]=String(name).slice(0,80)||t.columns[c];update();}}),item('Copy column',()=>copy([t.columns[c],...t.rows.map(row=>row[c])].map(csvEscape).join('\n'))),item('Filter by column…',()=>{$('dt-filter-column').value=String(c);const details=$('data-menu-navigation')?.querySelectorAll('details')[1];if(details)details.open=true;}),item('Sort ascending',()=>{$('dt-sortcol').value=String(c);$('dt-sortdir').value='asc';$('dt-sort').click();}),item('Sort descending',()=>{$('dt-sortcol').value=String(c);$('dt-sortdir').value='desc';$('dt-sort').click();}),item('Insert column left',()=>colInsert(c)),item('Insert column right',()=>colInsert(c+1)),item('Delete column',()=>colDelete(c),{danger:true}));
      }else if(kind==='tab'){
        items.push(item('Rename table',()=>{$('dt-rename').click();}),item('Duplicate table',()=>{$('dt-copy').click();}),item('Export CSV',()=>{$('dt-export-csv').click();}),item('Export JSON',()=>{$('dt-export-json').click();}),item('Delete table',()=>{$('dt-remove').click();},{danger:true}));
      }else {
        items.push(item('New table',()=>{$('dt-new').click();}),item('Add row',()=>{$('dt-add-row').click();}),item('Add column',()=>{$('dt-add-col').click();}),item('Import CSV/JSON',()=>{$('dt-import').click();}),item('Export as CSV',()=>{$('dt-export-csv').click();}),item('Export as JSON',()=>{$('dt-export-json').click();}));
      }
    } else if(area==='calc'){
      const input=$('calc-input');items.push(item('Calculate expression',()=>{$('calc-execute').click();}),item('Open symbol library',openPalette),item('Copy expression',()=>copy(input.value)),item('Paste expression',async()=>insert(input,await paste())),item('Copy numeric result',()=>copy($('calc-result-plain').textContent.replace(/^=\s*/,''))),item('Use result as expression',()=>{input.value=$('calc-result-plain').textContent.replace(/^=\s*/,'');input.focus();}),item('Binary mode',()=>{$('calc-radix').value='bin';}),item('Hexadecimal mode',()=>{$('calc-radix').value='hex';}),item('Decimal mode',()=>{$('calc-radix').value='dec';}),item('Send to Symbolic Solver',()=>dispatchRoute('solver',input.value)),item('Clear expression',()=>{$('calc-clear').click();}));
    }else if(area==='editor'||area==='solver'||area==='graph'){
      const input=$(area==='graph'?'graph-input':'equation-input');const value=input?.value||'';
      items.push(item('Copy expression',()=>copy(value)),item('Paste expression',async()=>insert(input,await paste())),item('Open symbol library',openPalette));
      if(area==='editor'){items.push(item('Save equation in notebook',()=>$('add-btn').click()),item('Copy LaTeX',()=>$('copy-latex').click()),item('Send to Solver',()=>dispatchRoute('solver',value)),item('Send to Calculator',()=>dispatchRoute('calculator',value)));}
      if(area==='solver')items.push(item('Run symbolic operation',()=>$('cas-run').click()),item('Save solved results',()=>$('cas-save').click()),item('Open numerical solver',()=>$('num-open')?.click()));
      if(area==='graph')items.push(item('Plot functions',()=>$('graph-plot').click()),item('Reset graph view',()=>$('graph-reset').click()),item('Export PNG',()=>$('graph-save').click()),item('Send to editor',()=>dispatchRoute('editor',value)));
      items.push(item('Clear expression',()=>{input.value='';input.dispatchEvent(new Event('input',{bubbles:true}));}));
    }else if(area==='graph-canvas')items.push(item('Export graph PNG',()=>$('graph-save').click()),item('Reset graph view',()=>$('graph-reset').click()),item('Show plotted expression in Editor',()=>dispatchRoute('editor',$('graph-input').value)));
    else if(area==='chart')items.push(item('Export chart PNG',()=>$('dt-chart-download').click()),item('Show data tables',()=>MS.advanced.mode('data')));
    else if(area==='notebook'){
      const wrap=target.closest('.equation-item');const buttons=[...wrap.querySelectorAll('button')],by=x=>buttons.find(b=>(b.textContent||'').trim()===x);
      if(by('Edit'))items.push(item('Edit equation',()=>by('Edit').click()));
      if(by('Copy'))items.push(item('Copy equation',()=>by('Copy').click()));
      if(by('Delete'))items.push(item('Delete equation',()=>by('Delete').click(),{danger:true}));
      const route=wrap.querySelector('.hub-notebook-route');if(route)for(const [v,title] of [['calculator','Send to Calculator'],['solver','Send to Solver'],['graph2d','Plot as 2D graph']])items.push(item(title,()=>{route.value=v;route.dispatchEvent(new Event('change',{bubbles:true}));}));
    }else if(area==='working'){
      const field=$('hub-expression');items.push(item('Copy working equation',()=>copy(field.value)),item('Paste working equation',async()=>insert(field,await paste())));
      for(const [v,title] of [['editor','Send to Editor'],['calculator','Send to Calculator'],['solver','Send to Solver'],['graph2d','Send to 2D Graph'],['graph3d','Send to 3D Graph']])items.push(item(title,()=>dispatchRoute(v,field.value)));
    }
    return items;
  }
  function detect(target){
    const tab=target.closest('#dt-tabs .dt-tab');if(tab){const tabs=[...$('dt-tabs').children],index=tabs.indexOf(tab);if(index>=0)return {area:'table',kind:'tab',tabIndex:index,target};}
    if(target.closest('#dt-sheet')){const colHead=target.closest('thead th');if(colHead){const col=colHead.cellIndex-1;if(col>=0)return {area:'table',kind:'column',col,target};return {area:'table',kind:'general',target};}
      const cell=target.closest('tbody td'),rowHead=target.closest('tbody th');if(cell){const input=cell.querySelector('input');return {area:'table',kind:'cell',row:Number(input.dataset.row),col:Number(input.dataset.col),target};}
      if(rowHead){const row=Number(rowHead.textContent)-2;return {area:'table',kind:'row',row,target};}return {area:'table',kind:'general',target};}
    if(target.closest('#data-panel'))return {area:'table',kind:'general',target};
    if(target.closest('#calc-input')||target.closest('#calc-result-math')||target.closest('#calc-result-plain')||target.closest('#calc-buttons'))return {area:'calc',target};
    if(target.closest('#equation-input'))return {area:document.querySelector('[data-workspace="solver"].active')?'solver':'editor',target};
    if(target.closest('#graph-input'))return {area:'graph',target};
    if(target.closest('#graph-canvas'))return {area:'graph-canvas',target};
    if(target.closest('#dt-chart-canvas'))return {area:'chart',target};
    if(target.closest('.equation-item'))return {area:'notebook',target};
    if(target.closest('#hub-expression'))return {area:'working',target};
    return null;
  }
  function open(event){const sel=detect(event.target);if(!sel){close();return false;}
    if(sel.kind==='tab'){const b=$('dt-tabs').children[sel.tabIndex];if(b&&!b.classList.contains('active'))b.click();}
    const commands=actions(sel);if(!commands.length)return false;
    selection=sel;returnFocus=event.target;popup.replaceChildren();
    const heading=document.createElement('div');heading.className='context-heading';heading.textContent=sel.area==='table'?'Data Tables — '+(sel.kind||'actions'):sel.area+' actions';popup.append(heading);
    for(const cmd of commands){const b=document.createElement('button');b.type='button';b.setAttribute('role','menuitem');b.textContent=cmd.title;if(cmd.danger)b.style.color='#b03648';b.addEventListener('click',async()=>{close();try{await cmd.run();}catch(e){note(e);}});popup.append(b);}
    popup.hidden=false;popup.style.left='0px';popup.style.top='0px';const rect=popup.getBoundingClientRect();const x=Math.max(6,Math.min(event.clientX||20,innerWidth-rect.width-6)),y=Math.max(6,Math.min(event.clientY||20,innerHeight-rect.height-6));popup.style.left=x+'px';popup.style.top=y+'px';popup.focus({preventScroll:true});return true;
  }
  document.addEventListener('contextmenu',e=>{if(popup.contains(e.target))return;if(detect(e.target)){e.preventDefault();open(e);}else close();},true);
  document.addEventListener('pointerdown',e=>{if(!popup.hidden&&!popup.contains(e.target))close();},true);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!popup.hidden){e.preventDefault();close();returnFocus?.focus?.({preventScroll:true});}
    if((e.shiftKey&&e.key==='F10'||e.key==='ContextMenu')&&detect(document.activeElement)){e.preventDefault();const rect=document.activeElement.getBoundingClientRect();open({target:document.activeElement,clientX:rect.left+25,clientY:rect.top+25});}
    if(!popup.hidden&&['ArrowDown','ArrowUp'].includes(e.key)){e.preventDefault();const opts=[...popup.querySelectorAll('[role=menuitem]')],i=opts.indexOf(document.activeElement),delta=e.key==='ArrowDown'?1:-1;opts[(i+delta+opts.length)%opts.length]?.focus();}
  },true);
  // Touch and pen long press are alternatives to mouse right-click.
  let longPress=null,start=null;
  document.addEventListener('pointerdown',e=>{if(e.pointerType==='mouse'||!detect(e.target))return;start={x:e.clientX,y:e.clientY,target:e.target};clearTimeout(longPress);longPress=setTimeout(()=>{if(start)open({...start});start=null;},600);},false);
  document.addEventListener('pointermove',e=>{if(start&&Math.hypot(e.clientX-start.x,e.clientY-start.y)>12){start=null;clearTimeout(longPress);}},false);
  for(const event of ['pointerup','pointercancel','scroll'])document.addEventListener(event,()=>{start=null;clearTimeout(longPress);},true);
  // Bitwise functions and base-specific literals can be added from a collapsed tool group.
  const controls=document.createElement('details');controls.className='programmer-tools';controls.innerHTML='<summary>Binary · Hex · Bitwise tools</summary><div class="calc-prog-buttons"></div><small>Examples: 0b1010+0xF, band(0xFF,0b1010), bxor(15,3), shl(3,2). Unprefixed digits use the selected input radix. Exact conversion works for large standalone literals.</small>';
  $('calc-buttons').before(controls);const wrapper=controls.querySelector('div');
  for(const [label,value] of [['0b','0b'],['0x','0x'],['AND','band(, )'],['OR','bor(, )'],['XOR','bxor(, )'],['NOT','bnot('],['<<','shl(, )'],['>>','shr(, )']]){const btn=document.createElement('button');btn.type='button';btn.textContent=label;btn.title='Insert '+value;btn.addEventListener('click',()=>insert($('calc-input'),value));wrapper.append(btn);}
  // Append to existing help page, retaining previous topical help.
  const topics=$('help-topics');if(topics){const detail=document.createElement('details');detail.className='help-topic';detail.innerHTML='<summary>Right-click actions and binary/hexadecimal calculator</summary><p>Right-click a table cell, row number, column header or table tab for Copy, Paste, Insert, Delete, Sort and Filter. Right-click expressions in Calculator, Editor, Solver or Graph for relevant commands. On mobile, long-press a cell. Shift+F10 opens a menu from the keyboard. Destructive actions require confirmation. Table edits retain existing literal formulas; row/column insertions do not automatically rewrite references.</p><p>Calculator accepts <code>0b1010</code> and <code>0xFF</code>, DEC/BIN/HEX input modes, and bitwise functions <code>band</code>, <code>bor</code>, <code>bxor</code>, <code>bnot</code>, <code>shl</code>, <code>shr</code>. Scientific expressions use decimal unless base mode is active. Binary/hex arithmetic is limited to exact 53-bit integers, while standalone integer literal conversion supports BigInt.</p>';topics.append(detail);}
  MS.contextActions={openAt:(target,x=40,y=40)=>open({target,clientX:x,clientY:y}),close,clipboard:()=>internalClipboard,pasteCells};
})();
