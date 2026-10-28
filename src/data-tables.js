/* ProMathStudio Data Tables workspace. SPDX-License-Identifier: MIT.
   No eval / Function / external runtime; data, formulas and files remain in-browser. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const MAX_ROWS = 6000, MAX_COLUMNS = 32, MAX_BYTES = 1000000, MAX_DISPLAY = 150;
  const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const el = (tag, attrs, text) => { const e=document.createElement(tag); for(const [k,v] of Object.entries(attrs||{})){if(k==='class')e.className=v;else e.setAttribute(k,v);}if(text!==undefined)e.textContent=String(text);return e;};
  const csvCell = value => {const s=String(value??'');return (s===''||/[",\n\r]/.test(s))?'"'+s.replace(/"/g,'""')+'"':s;};
  // Quote alternate separator characters too: the shared importer sniffs CSV/TSV
  // delimiters from the header and must not mistake commas/semicolons for tabs.
  const tsvCell = value => {const s=String(value??'');return (s===''||/[,;\t\r\n"]/.test(s))?'"'+s.replace(/"/g,'""')+'"':s;};
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
    <details id="dt-code-library" class="dt-box"><summary>Functions &amp; Code Library</summary>
      <label for="dt-library-search">Search formulas and Python recipes</label>
      <label for="dt-library-category">Category</label>
      <select id="dt-library-category"><option value="">All</option><option value="Formula">Formulas</option><option value="Python">Python recipes</option><option value="Operation">Table operations</option></select>
      <input id="dt-library-search" type="search" placeholder="SUM, IF, filter, group..." autocomplete="off">
      <div class="data-toolbar"><label>Snippet name<input id="dt-snippet-name" maxlength="60" placeholder="My formula"></label><label>Type<select id="dt-snippet-kind"><option>Formula</option><option>Python</option></select></label><label>Snippet<textarea id="dt-snippet-code" rows="2" maxlength="8000" placeholder="=SUM(A1:A5)"></textarea></label><button id="dt-snippet-save" type="button" class="secondary">Save snippet</button></div>
      <div class="data-toolbar"><button id="dt-snippet-export" type="button" class="secondary">Export snippets JSON</button><button id="dt-snippet-import" type="button" class="secondary">Import snippets JSON</button><input id="dt-snippet-file" type="file" accept=".json,application/json" hidden aria-label="Choose saved snippets JSON file"></div>
      <div id="dt-snippet-preview" hidden tabindex="-1" role="group" aria-label="Review snippet import"><p id="dt-snippet-preview-summary" role="status"></p><ul id="dt-snippet-preview-list" aria-label="Snippets in import" style="max-height:240px;overflow:auto;overflow-wrap:anywhere"></ul><label id="dt-snippet-conflict-label" hidden><input id="dt-snippet-skip-conflicts" type="checkbox"> Skip conflicting names and keep saved versions</label><button id="dt-snippet-apply" class="primary" type="button">Apply import</button><button id="dt-snippet-cancel" class="secondary" type="button">Cancel import</button></div>
      <div id="dt-library-results" aria-live="polite"></div>
      <section id="dt-snippet-inspect" hidden role="region" aria-label="Full saved snippet preview">
        <p id="dt-snippet-inspect-label"></p>
        <textarea id="dt-snippet-inspect-code" readonly rows="12" aria-label="Read-only full snippet source" style="display:block;box-sizing:border-box;width:100%;max-width:100%;font-family:monospace;white-space:pre;overflow:auto"></textarea>
        <button id="dt-snippet-inspect-close" type="button" class="secondary">Close snippet preview</button>
      </section>
      <p id="dt-library-message" role="status" class="graph-data-muted">Select a spreadsheet cell or use the Python editor before inserting.</p>
    </details>
    <p class="graph-data-muted">Select a cell to edit. Formulas begin with <code>=</code>; examples: <code>=A1*B1</code>, <code>=SUM(B1:B4)</code>, <code>=AVERAGE(A1:A9)</code>, <code>=IF(A1&gt;1,B1,0)</code>, <code>=Data2!A1</code>. Row 1 is the first data row; column names are displayed separately.</p>
    <section class="dt-box"><h3>Database operations</h3><div class="data-toolbar">
      <label>Left table<select id="dt-left"></select></label><label>Right table<select id="dt-right"></select></label>
      <label>Operation<select id="dt-op"><option value="inner">INNER JOIN</option><option value="left">LEFT JOIN</option><option value="right">RIGHT JOIN</option><option value="full">FULL OUTER JOIN</option><option value="unionall">UNION ALL</option><option value="union">UNION DISTINCT</option><option value="intersect">INTERSECT</option><option value="except">EXCEPT</option></select></label>
      <label>Left key<select id="dt-left-key"></select></label><label>Right key<select id="dt-right-key"></select></label>
      <button id="dt-run" class="primary" type="button">Run → New table</button></div></section>
    <section class="dt-box"><h3>Import / export</h3><div class="data-toolbar">
      <label>Import CSV / TSV / JSON<input id="dt-import" type="file" accept=".csv,.tsv,.json,text/csv,application/json"></label>
      <button id="dt-export-csv" class="secondary" type="button">↓ Export CSV</button><button id="dt-export-source-csv" class="secondary" type="button" title="Export original cell text and formulas. External spreadsheet applications may execute formulas in this CSV.">↓ Export formulas CSV</button><button id="dt-export-tsv" class="secondary" type="button" title="Export calculated values as tab-separated text; text containing commas, semicolons or tabs is safely quoted.">↓ Export TSV</button><button id="dt-export-json" class="secondary" type="button">↓ Export JSON</button>
      <button id="dt-send-graph" class="primary" type="button">↗ Show in graphs</button></div>
      <details id="dt-advanced"><summary>Advanced dataset preview / X, Y, Z mapping</summary></details></section></div>`;
  // The library is a catalog, not an evaluator: insert only, never run code.
  const dataLibrary = [
    {name:'SUM',kind:'Formula',sample:'=SUM(A1:A5)',help:'Sum a numeric cell range.'},
    {name:'AVERAGE',kind:'Formula',sample:'=AVERAGE(A1:A5)',help:'Average numeric cells.'},
    {name:'MIN',kind:'Formula',sample:'=MIN(A1:A5)',help:'Smallest numeric value.'},
    {name:'MAX',kind:'Formula',sample:'=MAX(A1:A5)',help:'Largest numeric value.'},
    {name:'COUNT',kind:'Formula',sample:'=COUNT(A1:A5)',help:'Count numeric cells.'},
    {name:'MEDIAN',kind:'Formula',sample:'=MEDIAN(A1:A5)',help:'Median of numeric cells; ignores text and blanks.'},
    {name:'Nested aggregates',kind:'Formula',sample:'=SUM(MEDIAN(A1:A5),COUNT(A1:A5))',help:'Combine numeric summaries; nested functions are evaluated from the inside out.'},
    {name:'IF',kind:'Formula',sample:'=IF(A1>0,B1,0)',help:'Conditional formula.'},
    {name:'Cross-table reference',kind:'Formula',sample:'=Data2!A1',help:'Reference another table by name.'},
    {name:'Filter rows',kind:'Python',sample:"result = next(iter(tables.values())).query('value > 0')",help:'Edit the column name and condition before running.'},
    {name:'Group and sum',kind:'Python',sample:"result = next(iter(tables.values())).groupby('category', as_index=False).sum(numeric_only=True)",help:'Edit the category column before running.'},
    {name:'Missing values',kind:'Python',sample:"result = next(iter(tables.values())).dropna()",help:'Drop rows containing missing values.'},
    {name:'INNER JOIN',kind:'Operation',operation:'inner',sample:'INNER JOIN',help:'Combine matching rows using selected key columns.'},
    {name:'LEFT JOIN',kind:'Operation',operation:'left',sample:'LEFT JOIN',help:'Preserve every row of the left table.'},
    {name:'UNION ALL',kind:'Operation',operation:'unionall',sample:'UNION ALL',help:'Append rows, including duplicates.'},
    {name:'INTERSECT',kind:'Operation',operation:'intersect',sample:'INTERSECT',help:'Keep rows present in both tables.'},
    {name:'EXCEPT',kind:'Operation',operation:'except',sample:'EXCEPT',help:'Keep left-table rows absent from the right table.'}
  ];
  const snippetStorageKey='promathstudio-data-snippets-v1';
  let customDataSnippets=[];
  try {
    const stored=JSON.parse(localStorage.getItem(snippetStorageKey)||'[]');
    if(Array.isArray(stored))customDataSnippets=stored.filter(e=>e&&typeof e.name==='string'&&e.name.length<=60&&['Formula','Python'].includes(e.kind)&&typeof e.sample==='string'&&e.sample.length<=8000).slice(0,40).map(e=>({name:e.name,kind:e.kind,sample:e.sample,help:'Saved user snippet',custom:true}));
  }catch{customDataSnippets=[];}
  let editingSnippetName=null;
  function persistDataSnippets(next){
    // Commit to storage first: a quota/security failure must not mutate the live catalog.
    try{localStorage.setItem(snippetStorageKey,JSON.stringify(next));}
    catch{return false;}
    customDataSnippets=next;
    return true;
  }
  // Versioned, data-only interchange. Existing localStorage format stays unchanged.
  const SNIPPET_FILE_FORMAT='promathstudio-snippets', SNIPPET_FILE_VERSION=1;
  const MAX_SNIPPET_FILE_BYTES=400000;
  $('dt-snippet-export').addEventListener('click',()=>{
    const payload={format:SNIPPET_FILE_FORMAT,version:SNIPPET_FILE_VERSION,
      snippets:customDataSnippets.map(({name,kind,sample})=>({name,kind,sample}))};
    const blob=new Blob([JSON.stringify(payload,null,2)+'\n'],{type:'application/json'});
    const url=URL.createObjectURL(blob);
    const link=el('a',{href:url,download:'promathstudio-snippets.json'});
    document.body.append(link);link.click();link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
    $('dt-library-message').textContent='Exported '+payload.snippets.length+' saved snippets as JSON.';
  });
  // Import is a two-phase transaction: validate and preview without touching storage.
  // Conflicting saved names are never overwritten; users may explicitly skip them.
  let pendingSnippetImport=null;
  const snippetPreview=$('dt-snippet-preview');
  const snippetSkipConflicts=$('dt-snippet-skip-conflicts');
  function closeSnippetPreview(){
    pendingSnippetImport=null;
    snippetPreview.hidden=true;
    $('dt-snippet-conflict-label').hidden=true;
    snippetSkipConflicts.checked=false;
    $('dt-snippet-apply').disabled=false;
  }
  function planSnippetImport(imported){
    const next=customDataSnippets.slice(),conflicts=[];
    let added=0,unchanged=0;
    for(const entry of imported){
      const existing=next.find(e=>e.name.toLowerCase()===entry.name.toLowerCase());
      if(existing){
        if(existing.kind!==entry.kind||existing.sample!==entry.sample)conflicts.push(entry.name);
        else unchanged++;
      }else{
        if(next.length>=40)throw Error('Maximum 40 saved snippets; import not applied.');
        next.push(entry);added++;
      }
    }
    return {next,added,unchanged,conflicts};
  }
  $('dt-snippet-import').addEventListener('click',()=>$('dt-snippet-file').click());
  $('dt-snippet-cancel').addEventListener('click',()=>{
    closeSnippetPreview();
    $('dt-library-message').textContent='Snippet import canceled; saved snippets unchanged.';
    $('dt-snippet-import').focus();
  });
  // Escape closes an import preview without touching the saved catalog.
  snippetPreview.addEventListener('keydown',event=>{
    if(event.key!=='Escape'||snippetPreview.hidden)return;
    event.preventDefault();closeSnippetPreview();
    $('dt-library-message').textContent='Snippet import canceled; saved snippets unchanged.';
    $('dt-snippet-import').focus();
  });
  snippetSkipConflicts.addEventListener('change',()=>{
    $('dt-snippet-apply').disabled=!!pendingSnippetImport?.plan.conflicts.length&&!snippetSkipConflicts.checked;
  });
  $('dt-snippet-apply').addEventListener('click',()=>{
    if(!pendingSnippetImport)return;
    const message=$('dt-library-message');
    try{
      const {plan,snapshot}=pendingSnippetImport;
      if(snapshot!==JSON.stringify(customDataSnippets))
        throw Error('Saved snippets changed during preview; choose the file again.');
      if(plan.conflicts.length&&!snippetSkipConflicts.checked)
        throw Error('Name conflict: select Skip conflicting names or cancel.');
      if(plan.added&&!persistDataSnippets(plan.next))
        throw Error('Storage unavailable; import not applied.');
      renderDataLibrary();
      message.textContent='Imported '+plan.added+' snippets; '+plan.unchanged+' already saved.'+
        (plan.conflicts.length?' '+plan.conflicts.length+' conflicts skipped.':'');
      closeSnippetPreview();
    }catch(error){
      closeSnippetPreview();
      message.textContent='Snippet import rejected: '+(error instanceof Error?error.message:'Import failed');
    }
  });
  $('dt-snippet-file').addEventListener('change',async event=>{
    const file=event.target.files?.[0],message=$('dt-library-message');
    if(!file)return;
    closeSnippetPreview();
    try{
      if(file.size>MAX_SNIPPET_FILE_BYTES)throw Error('Snippet file exceeds 400 KB.');
      const payload=JSON.parse(await file.text());
      if(!payload||Array.isArray(payload)||payload.format!==SNIPPET_FILE_FORMAT||
         payload.version!==SNIPPET_FILE_VERSION||!Array.isArray(payload.snippets)||
         payload.snippets.length>40)throw Error('Unsupported snippet JSON format or version.');
      const imported=[],seen=new Set();
      for(const entry of payload.snippets){
        if(!entry||Array.isArray(entry)||typeof entry.name!=='string'||
           !entry.name.trim()||entry.name!==entry.name.trim()||entry.name.length>60||
           !['Formula','Python'].includes(entry.kind)||typeof entry.sample!=='string'||
           !entry.sample.trim()||entry.sample.length>8000||
           (entry.kind==='Formula'&&!entry.sample.startsWith('='))){
          throw Error('Invalid snippet name, type or code.');
        }
        const key=entry.name.toLowerCase();
        if(seen.has(key))throw Error('Duplicate snippet names in import.');
        seen.add(key);
        imported.push({name:entry.name,kind:entry.kind,sample:entry.sample,
          help:'Saved user snippet',custom:true});
      }
      const plan=planSnippetImport(imported);
      pendingSnippetImport={plan,snapshot:JSON.stringify(customDataSnippets)};
      $('dt-snippet-preview-summary').textContent='Preview: '+plan.added+' new, '+
        plan.unchanged+' already saved, '+plan.conflicts.length+' name conflicts.'+
        (plan.conflicts.length?' Name conflict: '+plan.conflicts.join(', ')+'.':'');
      const previewList=$('dt-snippet-preview-list');
      previewList.replaceChildren();
      for(const entry of imported){
        const existing=customDataSnippets.find(e=>e.name.toLowerCase()===entry.name.toLowerCase());
        const state=!existing?'new':existing.kind===entry.kind&&existing.sample===entry.sample?
          'already saved':'name conflict — saved version kept';
        const item=document.createElement('li');
        // Use textContent: imported names and code must never become executable markup.
        item.textContent=entry.name+' ('+entry.kind+') — '+state+': '+entry.sample.slice(0,120);
        previewList.append(item);
      }
      $('dt-snippet-conflict-label').hidden=!plan.conflicts.length;
      $('dt-snippet-apply').disabled=!!plan.conflicts.length;
      snippetPreview.hidden=false;
      snippetPreview.focus();
      message.textContent='Review the import preview before applying. No snippets have changed.';
    }catch(error){
      closeSnippetPreview();
      message.textContent='Snippet import rejected: '+(error instanceof Error?error.message:'Invalid JSON file');
    }finally{event.target.value='';}
  });
  $('dt-snippet-save').addEventListener('click',()=>{
    const name=$('dt-snippet-name').value.trim(),kind=$('dt-snippet-kind').value,sample=$('dt-snippet-code').value;
    const message=$('dt-library-message');
    if(!name||name.length>60||!['Formula','Python'].includes(kind)||!sample.trim()||sample.length>8000||(kind==='Formula'&&!sample.startsWith('='))){
      message.textContent='Enter a name and valid snippet (formulas must begin with =).';return;
    }
    const collision=customDataSnippets.find(e=>e.name.toLowerCase()===name.toLowerCase()&&e.name.toLowerCase()!==editingSnippetName?.toLowerCase());
    if(collision){message.textContent='A snippet with that name exists. Select Edit to change it.';return;}
    const previous=editingSnippetName===null?-1:customDataSnippets.findIndex(e=>e.name.toLowerCase()===editingSnippetName.toLowerCase());
    if(editingSnippetName!==null&&previous<0){message.textContent='The selected snippet no longer exists.';editingSnippetName=null;return;}
    if(previous<0&&customDataSnippets.length>=40){message.textContent='Maximum 40 saved snippets.';return;}
    const entry={name,kind,sample,help:'Saved user snippet',custom:true};
    const next=customDataSnippets.slice();
    if(previous>=0)next[previous]=entry;else next.push(entry);
    if(!persistDataSnippets(next)){message.textContent='Storage unavailable; snippet was not saved.';return;}
    editingSnippetName=null;
    $('dt-snippet-save').textContent='Save snippet';
    renderDataLibrary();message.textContent='Saved '+name+'.';
  });
  // Store the logical cell coordinates: the grid is rebuilt on blur, so
  // retaining the old input element would silently break toolbar insertion.
  let lastLibraryCell=null;
  panel.addEventListener('focusin',event=>{
    if(event.target.matches('#dt-sheet td input')){
      lastLibraryCell={id:active()?.id,r:Number(event.target.dataset.row),c:Number(event.target.dataset.col)};
    }
  });
  // Inspection is read-only and never inserts or executes a saved snippet.
  let inspectReturnFocus=null;
  function closeSnippetInspection(){
    const preview=$('dt-snippet-inspect');
    if(preview.hidden)return;
    preview.hidden=true;
    $('dt-snippet-inspect-code').value='';
    const target=inspectReturnFocus;
    inspectReturnFocus=null;
    if(target?.isConnected)target.focus();else $('dt-library-search').focus();
  }
  $('dt-snippet-inspect-close').addEventListener('click',closeSnippetInspection);
  $('dt-snippet-inspect').addEventListener('keydown',event=>{
    if(event.key==='Escape'&&!$('dt-snippet-inspect').hidden){
      event.preventDefault();event.stopPropagation();closeSnippetInspection();
    }
  });
  function renderDataLibrary(){
    const query=$('dt-library-search').value.trim().toLowerCase();
    const category=$('dt-library-category').value;
    const root=$('dt-library-results');root.replaceChildren();
    for(const entry of dataLibrary.concat(customDataSnippets).filter(e=>(!category||e.kind===category)&&(e.name+' '+e.kind+' '+e.help).toLowerCase().includes(query))){
      const item=el('div',{class:'data-toolbar'});
      const summary=entry.custom&&entry.sample.length>120?entry.sample.slice(0,120)+'…':entry.sample;
      const description=el('span',{},entry.kind+' · '+entry.name+' — '+entry.help+' Example: '+summary);
      const insert=el('button',{type:'button',class:'secondary','aria-label':(entry.kind==='Operation'?'Choose ':'Insert ')+entry.name},entry.kind==='Operation'?'Choose':'Insert');
      insert.addEventListener('click',()=>{
        const message=$('dt-library-message');
        if(entry.kind==='Formula'){
          const cell=lastLibraryCell,t=active();
          if(!cell||cell.id!==t?.id||!t.rows[cell.r]||cell.c<0||cell.c>=t.columns.length){
            message.textContent='Select a spreadsheet data cell first.';return;
          }
          // A formula replaces the entire cell, never concatenates two formulas.
          t.rows[cell.r][cell.c]=entry.sample.slice(0,8000);
          save();render();
          const field=$('dt-sheet').querySelector('td input[data-row="'+cell.r+'"][data-col="'+cell.c+'"]');
          field?.focus();
          message.textContent='Inserted '+entry.name+' into '+colLetter(cell.c)+(cell.r+1)+'.';
        }else if(entry.kind==='Python'){
          const target=$('dt-python-code');
          if(!target){message.textContent='Python editor is unavailable.';return;}
          const start=Number.isInteger(target.selectionStart)?target.selectionStart:target.value.length;
          const end=Number.isInteger(target.selectionEnd)?target.selectionEnd:start;
          target.setRangeText(entry.sample,start,end,'end');
          target.dispatchEvent(new Event('input',{bubbles:true}));
          // The Python editor is inside a disclosure; reveal it after the click
          // bubbles so the outside-click menu handler cannot immediately close it.
          requestAnimationFrame(()=>{
            const menu=$('data-menu-navigation')?.querySelector(':scope > details:nth-child(5)');
            if(menu)menu.open=true;
            target.focus();
          });
          message.textContent='Inserted '+entry.name+' into Python editor. Code has not run.';
        }else{
          const selector=$('dt-op');
          if(!selector){message.textContent='Table operation controls are unavailable.';return;}
          selector.value=entry.operation;
          selector.dispatchEvent(new Event('change',{bubbles:true}));
          requestAnimationFrame(()=>{
            const menu=$('data-menu-navigation')?.querySelector(':scope > details:nth-child(3)');
            if(menu)menu.open=true;
            selector.focus();
          });
          message.textContent='Selected '+entry.name+'. Choose tables and click Run to execute.';
        }
      });
      item.append(description,insert);
      if(entry.custom){
        const edit=el('button',{type:'button',class:'secondary','aria-label':'Edit snippet '+entry.name},'Edit');
        edit.addEventListener('click',()=>{
          editingSnippetName=entry.name;
          $('dt-snippet-name').value=entry.name;
          $('dt-snippet-kind').value=entry.kind;
          $('dt-snippet-code').value=entry.sample;
          $('dt-snippet-save').textContent='Update snippet';
          $('dt-snippet-name').focus();
          $('dt-library-message').textContent='Editing '+entry.name+'. Change the name to rename it.';
        });
        const remove=el('button',{type:'button',class:'secondary','aria-label':'Delete snippet '+entry.name},'Delete');
        remove.addEventListener('click',()=>{
          if(!window.confirm('Delete saved snippet "'+entry.name+'"?'))return;
          const next=customDataSnippets.filter(e=>e.name!==entry.name);
          if(!persistDataSnippets(next)){
            $('dt-library-message').textContent='Storage unavailable; snippet was not deleted.';return;
          }
          if(editingSnippetName===entry.name){
            editingSnippetName=null;
            $('dt-snippet-save').textContent='Save snippet';
          }
          renderDataLibrary();
          $('dt-library-message').textContent='Deleted '+entry.name+'.';
        });
        const inspect=el('button',{type:'button',class:'secondary','aria-label':'View full snippet '+entry.name},'View full');
        inspect.addEventListener('click',()=>{
          inspectReturnFocus=inspect;
          $('dt-snippet-inspect-label').textContent=entry.kind+' snippet: '+entry.name+' ('+entry.sample.length+' characters)';
          $('dt-snippet-inspect-code').value=entry.sample;
          $('dt-snippet-inspect').hidden=false;
          $('dt-snippet-inspect-code').focus();
        });
        item.append(inspect,edit,remove);
      }
      root.append(item);
    }
    if(!root.childElementCount)root.append(el('p',{},'No matching functions or recipes.'));
  }
  $('dt-library-search').addEventListener('input',renderDataLibrary);
  $('dt-library-category').addEventListener('change',renderDataLibrary);
  renderDataLibrary();
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
  // Protect complete aggregate ranges before scalar reference rewriting.
  // Deleting inside a range shrinks its surviving rectangle; an empty range is #REF!.
  const structuralRangePattern=/((?:'[^']+'|[A-Za-z_][A-Za-z0-9_]*)!)?(\$?[A-Za-z]{1,3}\$?[1-9]\d*):(\$?[A-Za-z]{1,3}\$?[1-9]\d*)/g;
  function shiftReferences(edited,axis,index,delta){
    const coord=ref=>{const m=/^(\$?)([A-Za-z]{1,3})(\$?)([1-9]\d*)$/.exec(ref);
      return axis==='row'?Number(m[4])-1:colIndex(m[2]);};
    const at=(ref,pos)=>axis==='row'?ref.replace(/[1-9]\d*$/,String(pos+1))
      :ref.replace(/^(\$?)[A-Za-z]{1,3}(?=\$?[1-9]\d*$)/,(_,anchor)=>anchor+colLetter(pos));
    for(const sheet of tables)for(const row of sheet.rows)for(let c=0;c<row.length;c++){
      const raw=String(row[c]);if(!raw.startsWith('='))continue;
      const ranges=[];
      let next=raw.replace(structuralRangePattern,(match,prefix,left,right,offset,whole)=>{
        if((offset&&/[A-Za-z0-9_.$'!]/.test(whole[offset-1]))||/[A-Za-z0-9_.$']/.test(whole[offset+match.length]||''))return match;
        const name=prefix?prefix.slice(0,-1).replace(/^'|'$/g,''):sheet.name;
        let mapped=match;
        if(name.toLowerCase()===edited.name.toLowerCase()){
          const a=coord(left),b=coord(right),lo=Math.min(a,b),hi=Math.max(a,b);
          if(delta>0)mapped=(prefix||'')+at(left,a>=index?a+delta:a)+':'+at(right,b>=index?b+delta:b);
          else{const lower=lo-(index<lo?1:0),upper=hi-(index<=hi?1:0);
            mapped=upper<lower?'#REF!':(prefix||'')+
              at(left,a<=b?lower:upper)+':'+at(right,a<=b?upper:lower);}
        }
        // Also protect foreign-sheet ranges: their second endpoint inherits the prefix.
        const token='\uE000'+ranges.length+'\uE001';ranges.push(mapped);return token;
      });
      next=next.replace(referencePattern,(match,prefix,colAnchor,letters,rowAnchor,digits,offset,whole)=>{
        if(offset&&/[A-Za-z0-9_.$]/.test(whole[offset-1]))return match;
        const after=whole[offset+match.length];if(after&&/[A-Za-z0-9_.$]/.test(after))return match;
        const name=prefix?prefix.slice(0,-1).replace(/^'|'$/g,''):sheet.name;
        if(name.toLowerCase()!==edited.name.toLowerCase())return match;
        const position=axis==='row'?Number(digits)-1:colIndex(letters);
        if(delta<0&&position===index)return '#REF!';
        const moved=position>=index+(delta<0?1:0)?position+delta:position;
        if(moved===position)return match;
        return (prefix||'')+colAnchor+(axis==='column'?colLetter(moved):letters)+rowAnchor+(axis==='row'?moved+1:digits);
      });
      row[c]=next.replace(/\uE000(\d+)\uE001/g,(_,i)=>ranges[Number(i)]);
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
    const rangePattern=/((?:'[^']+'|[A-Za-z_][A-Za-z0-9_]*)!)?(\$?[A-Za-z]{1,3}\$?[1-9]\d*):(\$?[A-Za-z]{1,3}\$?[1-9]\d*)/g;
    const rowOf=ref=>Number(/[1-9]\d*$/.exec(ref)[0])-1;
    const rewrite=(raw,sheet)=>{
      if(!String(raw).startsWith('='))return raw;
      const ranges=[];
      let next=String(raw).replace(rangePattern,(match,prefix,left,right,offset,whole)=>{
        if((offset&&/[A-Za-z0-9_.$'!]/.test(whole[offset-1]))||/[A-Za-z0-9_.$']/.test(whole[offset+match.length]||''))return match;
        const target=prefix?prefix.slice(0,-1).replace(/^'|'$/g,''):sheet.name;
        let mapped=match;
        if(target.toLowerCase()===t.name.toLowerCase()){
          const lo=Math.min(rowOf(left),rowOf(right)),hi=Math.max(rowOf(left),rowOf(right));
          if(hi>=newRow.length)throw Error('Cannot sort: formula range '+match+' exceeds the table.');
          const positions=[];for(let i=lo;i<=hi;i++)positions.push(newRow[i]);
          const lower=Math.min(...positions),upper=Math.max(...positions);
          if(upper-lower+1!==positions.length)throw Error('Cannot sort: formula range '+match+' would split into noncontiguous rows.');
          const forward=rowOf(left)<=rowOf(right);
          mapped=(prefix||'')+left.replace(/[1-9]\d*$/,String((forward?lower:upper)+1))+':'+
            right.replace(/[1-9]\d*$/,String((forward?upper:lower)+1));
        }
        // Always shield both endpoints from the scalar reference rewrite.
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
  // Find comparisons only at the top level: nested IF conditions may contain
  // their own comparisons, which must not split the outer condition.
  function ifComparison(expr){
    let depth=0;
    for(let i=0;i<expr.length;i++){
      const ch=expr[i];
      if(ch==='('){depth++;continue;}
      if(ch===')'){if(--depth<0)throw Error('#IF');continue;}
      if(depth)continue;
      const op=/^(>=|<=|!=|<>|==|=|>|<)/.exec(expr.slice(i));
      if(op){
        const left=expr.slice(0,i),right=expr.slice(i+op[0].length);
        if(!left.trim()||!right.trim())throw Error('#IF');
        return {left,right,op:op[0]};
      }
    }
    if(depth!==0)throw Error('#IF');
    return null;
  }
  function formula(expr,t,stack){
    expr=String(expr).trim();if(expr.length>500)throw Error('#LIMIT');
    // A whole-expression IF must close at the matching parenthesis, not the
    // last ')' of an adjacent expression such as IF(...)+IF(...).
    const ifStart=/^IF\s*\(/i.exec(expr);
    let close=-1;
    if(ifStart){
      let depth=0;
      for(let i=ifStart[0].length-1;i<expr.length;i++){
        if(expr[i]==='(')depth++;
        else if(expr[i]===')'&&--depth===0){close=i;break;}
      }
    }
    if(ifStart&&close===expr.length-1){
      const args=splitArgs(expr.slice(ifStart[0].length,close));
      if(args.length!==3||args.some(arg=>!arg.trim()))throw Error('#IF');
      const m=ifComparison(args[0]);
      const test=m?(()=>{
        const a=compute(m.left,t,stack),b=compute(m.right,t,stack);
        return ({'>':a>b,'<':a<b,'>=':a>=b,'<=':a<=b,'=':a===b,'==':a===b,'!=':a!==b,'<>':a!==b})[m.op];
      })():Boolean(compute(args[0],t,stack));
      // Evaluate only the selected branch: unused #REF!, cycles and errors
      // must not poison a valid spreadsheet conditional.
      return compute(args[test?1:2],t,stack);
    }
    return compute(expr,t,stack);
  }
  function expandIfCalls(expr,t,stack){
    let count=0;
    while(true){
      const match=/\bIF\s*\(/i.exec(expr);
      if(!match)break;
      const open=match.index+match[0].length-1;
      let depth=0,end=-1;
      for(let i=open;i<expr.length;i++){
        if(expr[i]==='(')depth++;
        else if(expr[i]===')'&&--depth===0){end=i;break;}
      }
      if(end<0)throw Error('#IF');
      const result=formula(expr.slice(match.index,end+1),t,stack);
      expr=expr.slice(0,match.index)+String(number(result))+expr.slice(end+1);
      if(++count>40)throw Error('#LIMIT');
    }
    return expr;
  }
  function compute(expr,t,stack){
    expr=expandIfCalls(String(expr),t,stack);
    if(expr.includes('#REF!'))throw Error('#REF!');
    // Custom functions and aggregates may wrap one another. Reduce innermost
    // calls in alternating passes, without eval or eager IF branch evaluation.
    const customPattern=/\b([A-Za-z][A-Za-z0-9_]*)\s*\(([^()]*)\)/g;
    const aggregatePattern=/\b(SUM|AVERAGE|AVG|MIN|MAX|COUNT|MEDIAN)\s*\(([^()]*)\)/gi;
    let compositionPasses=0;
    while(true){
      let changed=false;
      expr=String(expr).replace(customPattern,(all,name,body)=>{
        const fn=window.MathStudio.customFunctions?.find(name);
        if(!fn)return all;
        const args=splitArgs(body);
        if(args.length!==fn.params.length||args.some(arg=>!arg.trim()))throw Error('#ARGS');
        const values=args.map(part=>compute(part,t,stack));
        const result=window.MathStudio.customFunctions.evaluate(name,values);
        if(!Number.isFinite(result))throw Error('#VALUE');
        changed=true;
        return String(result);
      });
      aggregatePattern.lastIndex=0;
      if(aggregatePattern.test(expr)){
        changed=true;
        expr=String(expr).replace(aggregatePattern,(all,fn,body)=>{
      const nums=[];for(const arg of splitArgs(body)){const range=/^((?:'[^']+'|[A-Za-z_][A-Za-z0-9_]*)!)?(\$?)([A-Z]+)(\$?)(\d+):(\$?)([A-Z]+)(\$?)(\d+)$/i.exec(arg.trim());
        if(range){const target=range[1]?getByName(range[1].slice(0,-1).replace(/^'|'$/g,'')):t;
          if(!target)throw Error('#SHEET');
          const c0=colIndex(range[3]),r0=+range[5]-1,c1=colIndex(range[7]),r1=+range[9]-1;
          if((Math.abs(c1-c0)+1)*(Math.abs(r1-r0)+1)>6000)throw Error('#RANGE');
          // Unpopulated in-grid rows are blank; invalid workbook coordinates must not silently become zero.
          if(r0<0||r1<0||r0>=MAX_ROWS||r1>=MAX_ROWS||c0<0||c1<0||c0>=MAX_COLUMNS||c1>=MAX_COLUMNS)throw Error('#REF!');
          for(let rr=Math.min(r0,r1);rr<=Math.max(r0,r1);rr++)for(let cc=Math.min(c0,c1);cc<=Math.max(c0,c1);cc++){
            // value() returns zero for missing coordinates, but an unpopulated spreadsheet cell is blank, not numeric zero.
            if(rr>=target.rows.length||cc>=target.columns.length)continue;
            const v=value(target,rr,cc,stack);
            if(v!==''&&String(v).trim()!==''&&Number.isFinite(Number(v)))nums.push(Number(v));
          }
        } else {const v=compute(arg,t,stack);if(Number.isFinite(Number(v)))nums.push(Number(v));}}
      const upper=fn.toUpperCase();
      let x;
      if(upper==='MEDIAN'){
        if(!nums.length)throw Error('#NUM!');
        const ordered=nums.slice().sort((a,b)=>a-b),mid=Math.floor(ordered.length/2);
        x=ordered.length%2?ordered[mid]:ordered[mid-1]/2+ordered[mid]/2;
      }else{
        x=upper==='SUM'?nums.reduce((a,b)=>a+b,0):upper==='COUNT'?nums.length:upper==='AVERAGE'||upper==='AVG'?(nums.reduce((a,b)=>a+b,0)/(nums.length||1)):upper==='MIN'?Math.min(...nums):Math.max(...nums);
      }
      // Emit a scalar token, not '(scalar)': parenthesized intermediate values
      // would prevent the next innermost-first pass from matching outer calls.
      return String(Number.isFinite(x)?x:0);
        });
      }
      if(!changed)break;
      if(++compositionPasses>40)throw Error('#LIMIT');
    }
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
    if(isJoin){
      if(!Number.isInteger(lkey)||lkey<0||lkey>=l.columns.length||
         !Number.isInteger(rkey)||rkey<0||rkey>=r.columns.length)throw Error('Invalid join key.');
      const headers=l.columns.concat(r.columns.map(h=>l.columns.includes(h)?r.name+'_'+h:h));
      if(headers.length>MAX_COLUMNS)throw Error('Operation exceeds 32 columns.');
      // Index the right-hand keys once. Preserve original right-row order and
      // duplicate-key Cartesian matches, including empty-string keys.
      const rightIndex=new Map();
      for(let j=0;j<B.length;j++){
        const key=String(B[j][rkey]),bucket=rightIndex.get(key);
        if(bucket)bucket.push(j);else rightIndex.set(key,[j]);
      }
      const out=[],matched=new Set();
      const append=row=>{if(out.length>=MAX_ROWS)throw Error('Join exceeds 6,000 rows.');out.push(row);};
      for(const leftRow of A){
        const hits=rightIndex.get(String(leftRow[lkey]));
        if(hits){for(const j of hits){append(leftRow.concat(B[j]));matched.add(j);}}
        else if(type==='left'||type==='full')append(leftRow.concat(r.columns.map(()=>'')));
      }
      if(type==='right'||type==='full')
        for(let j=0;j<B.length;j++)if(!matched.has(j))append(l.columns.map(()=>'').concat(B[j]));
      return {headers,rows:out};
    }
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
  $('dt-export-tsv').addEventListener('click',()=>safeAction(()=>{const t=active(),rows=[t.columns,...evaluated(t)];download(t.name+'.tsv',rows.map(row=>row.map(tsvCell).join('\t')).join('\r\n')+'\r\n','text/tab-separated-values;charset=utf-8');}));
  // Formula source export is opt-in; the original CSV still exports calculated values.
  // CSV spreadsheet viewers may execute imported formulas; users choose when to open.
  $('dt-export-source-csv').addEventListener('click',()=>safeAction(()=>{
    const t=active(),rows=[t.columns,...t.rows];
    download(t.name+'_formulas.csv',rows.map(row=>row.map(csvCell).join(',')).join('\r\n')+'\r\n','text/csv;charset=utf-8');
  }));
  $('dt-export-json').addEventListener('click',()=>safeAction(()=>{const t=active();
    // JSON objects cannot represent duplicate property names without losing cells.
    // CSV and project JSON remain available for workbooks with repeated headers.
    if(new Set(t.columns).size!==t.columns.length)throw Error('JSON export requires unique column headers; rename duplicates before exporting.');
    const rows=evaluated(t);download(t.name+'.json',JSON.stringify(rows.map(row=>Object.fromEntries(t.columns.map((h,i)=>[h,row[i]]))),null,2),'application/json');}));
  $('dt-import').addEventListener('change',async event=>{const file=event.target.files?.[0];if(!file)return;try{
    if(file.size>MAX_BYTES)throw Error('Import file exceeds 1 MB.');if(!/\.(csv|tsv|json)$/i.test(file.name))throw Error('Choose CSV, TSV or JSON.');
    const text=await file.text(),decoder=window.MathStudio.graphData;
    // One-column tabular imports are valid sheets, but never XY graph datasets.
    const options={allowSingleColumn:true,delimiterHint:/\.tsv$/i.test(file.name)?'\t':','};
    const tbl=/\.json$/i.test(file.name)?decoder.parseJSON(text,options):decoder.parseCSV(text,options);
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

