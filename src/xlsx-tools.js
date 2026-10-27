/* Offline, dependency-free bounded XLSX export for one or two Data Tables sheets. */
(()=>{'use strict';
const M=window.MathStudio, panel=document.getElementById('data-panel');
if(!M?.dataTables||!panel)return;
const $=id=>document.getElementById(id), utf8=new TextEncoder();
const MAX_ROWS=1000,MAX_COLS=32,MAX_BYTES=5000000;
const badXML=/[\u0000-\u0008\u000b\u000c\u000e-\u001f\ufffe\uffff]/;
function xml(value){
 const s=String(value);
 if(badXML.test(s))throw Error('XLSX cannot contain XML control characters.');
 return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
}
function column(index){let s='';for(let n=index+1;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;}
function formulaToExcel(formula){
 // Data Tables row 1 is the first DATA row; XLSX row 1 holds column headers.
 // Do not rewrite cell-like tokens inside Excel double-quoted string literals.
 return String(formula).replace(/(?<![A-Za-z0-9_.])("(?:[^"]|"")*")|(?<![A-Za-z0-9_.])((?:'(?:[^']|'')+'|[A-Za-z_][A-Za-z0-9_.]*)!)?(\$?[A-Za-z]{1,3})(\$?)([1-9]\d*)(?![A-Za-z0-9_.(])/g,
  (whole,literal,sheet,col,anchor,row)=>{
   if(literal)return literal;
   const shifted=Number(row)+1;
   if(!Number.isSafeInteger(shifted)||shifted>1048576)throw Error('Formula reference exceeds Excel row limits.');
   return (sheet||'')+col+anchor+shifted;
  });
}
function cell(ref,value){
 const s=String(value??'');
 if(!s)return '';
 if(s.length>8000)throw Error('XLSX cell text exceeds 8,000 characters.');
 if(s.startsWith('=')){
  if(s.length===1)throw Error('XLSX formula must not be empty.');
  return '<c r="'+ref+'"><f>'+xml(formulaToExcel(s.slice(1)))+'</f></c>';
 }
 // Preserve leading zeros and values that Excel would round beyond 15 digits.
 const isNumeric=/^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?$/.test(s);
 const significant=s.replace(/^[+-]?0*\.?0*/,'').replace(/[eE].*$/,'').replace(/\D/g,'').length;
 if(isNumeric&&significant<=15&&Number.isFinite(Number(s)))
  return '<c r="'+ref+'"><v>'+xml(s)+'</v></c>';
 return '<c r="'+ref+'" t="inlineStr"><is><t xml:space="preserve">'+xml(s)+'</t></is></c>';
}
function worksheet(table){
 const cols=table.columns, rows=table.rows;
 if(!Array.isArray(cols)||!cols.length||cols.length>MAX_COLS||!Array.isArray(rows)||rows.length>MAX_ROWS)
  throw Error('XLSX export supports 1–32 columns and at most 1,000 data rows per sheet.');
 const line=(values,index)=>{
  if(!Array.isArray(values)||values.length>cols.length)throw Error('Invalid XLSX row shape.');
  const parts=values.map((v,i)=>cell(column(i)+index,v)).join('');
  return '<row r="'+index+'">'+parts+'</row>';
 };
 const lines=[line(cols,1)];
 for(let i=0;i<rows.length;i++)lines.push(line(rows[i],i+2));
 return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'+
  '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'+
  '<sheetData>'+lines.join('')+'</sheetData></worksheet>';
}
function crc32(data){
 let crc=0xffffffff;
 for(const byte of data){crc^=byte;for(let j=0;j<8;j++)crc=(crc>>>1)^((crc&1)?0xedb88320:0);}
 return (crc^0xffffffff)>>>0;
}
function zipStore(entries){
 const locals=[],centers=[];let offset=0,total=22;
 const u16=(dv,pos,n)=>dv.setUint16(pos,n,true),u32=(dv,pos,n)=>dv.setUint32(pos,n>>>0,true);
 for(const [name,content] of entries){
  const nameBytes=utf8.encode(name),bytes=utf8.encode(content),crc=crc32(bytes);
  if(bytes.length>MAX_BYTES)throw Error('XLSX XML part exceeds the export size limit.');
  const local=new Uint8Array(30),lv=new DataView(local.buffer);
  u32(lv,0,0x04034b50);u16(lv,4,20);u16(lv,8,0);u32(lv,14,crc);
  u32(lv,18,bytes.length);u32(lv,22,bytes.length);u16(lv,26,nameBytes.length);
  const central=new Uint8Array(46),cv=new DataView(central.buffer);
  u32(cv,0,0x02014b50);u16(cv,4,20);u16(cv,6,20);u32(cv,16,crc);
  u32(cv,20,bytes.length);u32(cv,24,bytes.length);u16(cv,28,nameBytes.length);u32(cv,42,offset);
  locals.push(local,nameBytes,bytes);centers.push(central,nameBytes);
  offset+=local.length+nameBytes.length+bytes.length;
  total+=local.length+central.length+2*nameBytes.length+bytes.length;
  if(total>MAX_BYTES)throw Error('XLSX export exceeds 5 MB; select smaller sheets.');
 }
 const centralSize=centers.reduce((n,b)=>n+b.length,0);
 const end=new Uint8Array(22),ev=new DataView(end.buffer);
 u32(ev,0,0x06054b50);u16(ev,8,entries.length);u16(ev,10,entries.length);
 u32(ev,12,centralSize);u32(ev,16,offset);
 const result=new Uint8Array(total);let p=0;
 for(const part of [...locals,...centers,end]){result.set(part,p);p+=part.length;}
 if(p!==total)throw Error('XLSX ZIP size mismatch.');
 return result;
}
function build({tables=M.dataTables.tables.slice(0,2)}={}){
 if(!Array.isArray(tables)||tables.length<1||tables.length>2)throw Error('Choose one or two tables for XLSX export.');
 const names=new Set();
 for(const t of tables){
  if(!t||typeof t.name!=='string'||!t.name.trim()||t.name.length>31||/[\[\]:*?\/\\]/.test(t.name)||/^'|'$/.test(t.name))
   throw Error('Excel sheet names must be 1–31 characters without []:*?/\\ or outer apostrophes.');
  if(names.has(t.name.toLowerCase()))throw Error('XLSX sheet names must be unique.');
  names.add(t.name.toLowerCase());
 }
 const sheets=tables.map(worksheet);
 const base='http://schemas.openxmlformats.org/';
 const types='<?xml version="1.0" encoding="UTF-8"?>'+
  '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'+
  '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'+
  '<Default Extension="xml" ContentType="application/xml"/>'+
  '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'+
  tables.map((_,i)=>'<Override PartName="/xl/worksheets/sheet'+(i+1)+'.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>').join('')+'</Types>';
 const rels='<?xml version="1.0" encoding="UTF-8"?>'+
  '<Relationships xmlns="'+base+'package/2006/relationships">'+
  '<Relationship Id="rId1" Type="'+base+'officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>';
 const workbook='<?xml version="1.0" encoding="UTF-8"?>'+
  '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="'+base+'officeDocument/2006/relationships">'+
  '<sheets>'+tables.map((t,i)=>'<sheet name="'+xml(t.name)+'" sheetId="'+(i+1)+'" r:id="rId'+(i+1)+'"/>').join('')+
  '</sheets><calcPr fullCalcOnLoad="1"/></workbook>';
 const bookRels='<?xml version="1.0" encoding="UTF-8"?>'+
  '<Relationships xmlns="'+base+'package/2006/relationships">'+
  tables.map((_,i)=>'<Relationship Id="rId'+(i+1)+'" Type="'+base+'officeDocument/2006/relationships/worksheet" Target="worksheets/sheet'+(i+1)+'.xml"/>').join('')+'</Relationships>';
 const entries=[['[Content_Types].xml',types],['_rels/.rels',rels],['xl/workbook.xml',workbook],
  ['xl/_rels/workbook.xml.rels',bookRels]];
 sheets.forEach((s,i)=>entries.push(['xl/worksheets/sheet'+(i+1)+'.xml',s]));
 return zipStore(entries);
}
const area=document.createElement('details');area.id='xlsx-export-details';
area.innerHTML='<summary>Excel XLSX export · offline</summary>'+
 '<p>Export one or two selected Data Tables sheets (up to 1,000 data rows per sheet) with text, numbers and formulas. For bounded offline import, open Excel XLSX import below.</p>'+
 '<div class="data-toolbar"><label>First sheet<select id="xlsx-first"></select></label>'+
 '<label>Second sheet (optional)<select id="xlsx-second"></select></label>'+
 '<button id="xlsx-export" type="button" class="secondary">Download XLSX</button></div>'+
 '<p id="xlsx-status" role="status" aria-live="polite"></p>';
panel.append(area);
function refresh(){
 const tables=M.dataTables.tables,first=$('xlsx-first'),second=$('xlsx-second');
 const oldFirst=first.value,oldSecond=second.value;
 const options=(sel,blank)=>{sel.replaceChildren();if(blank)sel.add(new Option('(none)',''));
  for(const t of tables)sel.add(new Option(t.name,t.id));};
 options(first,false);options(second,true);
 first.value=tables.some(t=>t.id===oldFirst)?oldFirst:(M.dataTables.active?.id||tables[0]?.id||'');
 second.value=tables.some(t=>t.id===oldSecond)?oldSecond:(tables.find(t=>t.id!==first.value)?.id||'');
}
area.addEventListener('toggle',()=>{if(area.open)refresh();});
$('xlsx-export').addEventListener('click',()=>{
 try{
  const ids=[$('xlsx-first').value,$('xlsx-second').value].filter(Boolean);
  if(new Set(ids).size!==ids.length)throw Error('Choose two different sheets.');
  const tables=ids.map(id=>M.dataTables.tables.find(t=>t.id===id));
  if(tables.some(t=>!t))throw Error('Selected sheet no longer exists.');
  const bytes=build({tables});
  const url=URL.createObjectURL(new Blob([bytes],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}));
  const a=document.createElement('a');a.href=url;a.download='ProMathStudio.xlsx';document.body.append(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
  $('xlsx-status').textContent='Exported '+tables.length+' sheet(s), '+bytes.length+' bytes.';
 }catch(e){$('xlsx-status').textContent='XLSX export error: '+e.message;}
});
M.xlsxTools={build,formulaToExcel};
})();
