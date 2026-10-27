/* Bounded offline XLSX import: validates ZIP structure and OpenXML before replacing any Data Tables state. */
(()=>{'use strict';
const M=window.MathStudio, panel=document.getElementById('data-panel');
if(!M?.dataTables||!panel)return;
const MAX_FILE=5000000,MAX_PART=5000000,MAX_TOTAL=12000000,MAX_ENTRIES=64;
const textDecoder=new TextDecoder('utf-8',{fatal:true});
const MAIN='http://schemas.openxmlformats.org/spreadsheetml/2006/main';
const REL='http://schemas.openxmlformats.org/officeDocument/2006/relationships';
const PKG='http://schemas.openxmlformats.org/package/2006/relationships';
const $=id=>document.getElementById(id);
const u16=(v,p)=>v.getUint16(p,true),u32=(v,p)=>v.getUint32(p,true);
function fail(message){throw Error('XLSX import: '+message);}
function crc32(data){
 let crc=0xffffffff;
 for(const byte of data){crc^=byte;for(let j=0;j<8;j++)crc=(crc>>>1)^((crc&1)?0xedb88320:0);}
 return (crc^0xffffffff)>>>0;
}
async function inflate(data,expected){
 if(typeof DecompressionStream!=='function')fail('This browser cannot decode compressed XLSX files.');
 let reader;
 try{
  reader=new Blob([data]).stream().pipeThrough(new DecompressionStream('deflate-raw')).getReader();
  const chunks=[];let size=0;
  while(true){
   const {value,done}=await reader.read();if(done)break;
   size+=value.length;
   if(size>expected||size>MAX_PART){await reader.cancel().catch(()=>{});fail('Decompressed ZIP part exceeds declared size.');}
   chunks.push(value);
  }
  if(size!==expected)fail('Decompressed ZIP part size mismatch.');
  const result=new Uint8Array(size);let offset=0;
  for(const chunk of chunks){result.set(chunk,offset);offset+=chunk.length;}
  return result;
 }catch(e){if(String(e.message).startsWith('XLSX import:'))throw e;fail('Invalid compressed ZIP part.');}
}
async function unzip(input){
 const bytes=input instanceof Uint8Array?input:new Uint8Array(input);
 if(bytes.length<22||bytes.length>MAX_FILE)fail('Workbook must be a ZIP file of at most 5 MB.');
 const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
 let end=-1;
 for(let p=bytes.length-22;p>=Math.max(0,bytes.length-65557);p--)
  if(u32(view,p)===0x06054b50&&p+22+u16(view,p+20)===bytes.length){end=p;break;}
 if(end<0)fail('Missing ZIP central-directory end record.');
 if(u16(view,end+4)||u16(view,end+6)||u16(view,end+8)!==u16(view,end+10))fail('Multi-disk ZIP archives are unsupported.');
 const count=u16(view,end+10),size=u32(view,end+12),offset=u32(view,end+16);
 if(!count||count>MAX_ENTRIES||size===0xffffffff||offset===0xffffffff||offset+size!==end)fail('Invalid ZIP directory bounds.');
 let p=offset,total=0;const entries=[],seen=new Set(),ranges=[];
 for(let i=0;i<count;i++){
  if(p+46>end||u32(view,p)!==0x02014b50)fail('Malformed ZIP central directory.');
  const flags=u16(view,p+8),method=u16(view,p+10),crc=u32(view,p+16),compressed=u32(view,p+20),plain=u32(view,p+24);
  const nl=u16(view,p+28),extra=u16(view,p+30),comment=u16(view,p+32),local=u32(view,p+42);
  if(p+46+nl+extra+comment>end||!nl)fail('Malformed ZIP directory entry.');
  if((flags&1)||(flags&~0x0808)||![0,8].includes(method))fail('Encrypted or unsupported ZIP compression.');
  if(compressed>MAX_FILE||plain>MAX_PART||compressed===0xffffffff||plain===0xffffffff)fail('ZIP part size limit exceeded.');
  total+=plain;if(total>MAX_TOTAL)fail('Total decompressed workbook exceeds 12 MB.');
  let name;
  try{name=textDecoder.decode(bytes.subarray(p+46,p+46+nl));}catch{fail('Invalid ZIP entry name encoding.');}
  if(name.includes('\\')||name.startsWith('/')||name.includes('..')||name.includes(':')||/[\u0000-\u001f]/.test(name)||name.endsWith('/'))fail('Unsafe ZIP entry path.');
  if(seen.has(name.toLowerCase()))fail('Duplicate ZIP entry.');seen.add(name.toLowerCase());
  if(local+30>offset||u32(view,local)!==0x04034b50)fail('Invalid ZIP local header.');
  const ln=u16(view,local+26),le=u16(view,local+28),start=local+30+ln+le;
  if(u16(view,local+6)!==flags||u16(view,local+8)!==method||start+compressed>offset)fail('ZIP local entry mismatch.');
  if(ln!==nl||!bytes.subarray(local+30,local+30+ln).every((b,j)=>b===bytes[p+46+j]))fail('ZIP entry names disagree.');
  ranges.push([local,start+compressed]);
  entries.push({name,method,crc,compressed,plain,start});
  p+=46+nl+extra+comment;
 }
 if(p!==end)fail('ZIP directory contains unexpected bytes.');
 ranges.sort((a,b)=>a[0]-b[0]);
 for(let i=1;i<ranges.length;i++)if(ranges[i][0]<ranges[i-1][1])fail('Overlapping ZIP entries.');
 const allowed=new Set(['[Content_Types].xml','_rels/.rels','xl/workbook.xml','xl/_rels/workbook.xml.rels',
  'xl/worksheets/sheet1.xml','xl/worksheets/sheet2.xml','xl/sharedStrings.xml','xl/styles.xml',
  'xl/theme/theme1.xml','xl/calcChain.xml','docProps/app.xml','docProps/core.xml']);
 for(const entry of entries)if(!allowed.has(entry.name))fail('Unsupported or unsafe workbook part: '+entry.name);
 const parts=new Map();
 for(const entry of entries){
  const compressed=bytes.subarray(entry.start,entry.start+entry.compressed);
  const data=entry.method===0?compressed:await inflate(compressed,entry.plain);
  if(data.length!==entry.plain||crc32(data)!==entry.crc)fail('ZIP part size or CRC mismatch: '+entry.name);
  parts.set(entry.name,data);
 }
 return parts;
}
function xml(parts,name,namespace,root){
 const bytes=parts.get(name);if(!bytes)fail('Missing workbook part: '+name);
 let str;try{str=textDecoder.decode(bytes);}catch{fail('Invalid UTF-8 XML in '+name);}
 if(/<!DOCTYPE|<!ENTITY/i.test(str))fail('DTD and XML entities are forbidden.');
 const doc=new DOMParser().parseFromString(str,'application/xml');
 if(doc.querySelector('parsererror')||doc.documentElement.localName!==root||doc.documentElement.namespaceURI!==namespace)
  fail('Malformed or unsupported XML in '+name);
 return doc.documentElement;
}
const children=(node,name,ns)=>Array.from(node?.children||[]).filter(e=>e.localName===name&&e.namespaceURI===ns);
const child=(node,name,ns)=>children(node,name,ns)[0];
function fromExcel(formula){
 if(/[\[\]]/.test(formula))fail('External workbook formulas are unsupported.');
 return String(formula).replace(/("(?:[^"]|"")*")|((?:'(?:[^']|'')+'|[A-Za-z_][A-Za-z0-9_.]*)!)?(\$?[A-Za-z]{1,3})(\$?)([1-9]\d*)/g,
  (whole,literal,sheet,col,anchor,row)=>{
   if(literal)return literal;
   const n=Number(row)-1;
   if(!Number.isSafeInteger(n)||n<1||n>1000)fail('Formula references a header or unsupported row.');
   return (sheet||'')+col+anchor+n;
  });
}
function colIndex(letters){let n=0;for(const ch of letters)n=n*26+ch.charCodeAt(0)-64;return n-1;}
function textValue(node){
 const texts=Array.from(node?.getElementsByTagNameNS(MAIN,'t')||[]);
 return texts.map(t=>t.textContent||'').join('');
}
function parseStrings(parts){
 if(!parts.has('xl/sharedStrings.xml'))return [];
 const root=xml(parts,'xl/sharedStrings.xml',MAIN,'sst');
 const strings=children(root,'si',MAIN).map(textValue);
 if(strings.length>32032||strings.some(s=>s.length>8000))fail('Shared string count or length exceeds limits.');
 return strings;
}
function readSheet(parts,path,shared,name){
 const root=xml(parts,path,MAIN,'worksheet'),data=child(root,'sheetData',MAIN);
 if(!data)fail('Missing sheetData.');
 const rowMap=new Map();let width=0,maxRow=1;
 for(const row of children(data,'row',MAIN)){
  const n=Number(row.getAttribute('r'));
  if(!Number.isSafeInteger(n)||n<1||n>1001||rowMap.has(n))fail('Invalid or duplicate worksheet row.');
  const values=new Map();
  for(const cell of children(row,'c',MAIN)){
   const ref=cell.getAttribute('r')||'',match=/^([A-Z]{1,3})([1-9]\d*)$/.exec(ref);
   if(!match||Number(match[2])!==n)fail('Invalid cell address.');
   const col=colIndex(match[1]);if(col<0||col>=32||values.has(col))fail('Invalid or duplicate worksheet column.');
   width=Math.max(width,col+1);
   const type=cell.getAttribute('t')||'',formula=child(cell,'f',MAIN),v=child(cell,'v',MAIN);
   let value='';
   if(formula){
    if(n===1||formula.getAttribute('t')||formula.getAttribute('ref'))fail('Unsupported formula type or header formula.');
    value='='+fromExcel(formula.textContent||'');
    if(value==='=')fail('Empty worksheet formula.');
   }else if(type==='inlineStr')value=textValue(child(cell,'is',MAIN));
   else if(type==='s'){
    const idx=Number(v?.textContent);
    if(!Number.isSafeInteger(idx)||idx<0||idx>=shared.length)fail('Invalid shared string index.');
    value=shared[idx];
   }else if(type==='b')value=v?.textContent==='1'?'1':v?.textContent==='0'?'0':fail('Invalid boolean cell.');
   else if(type===''||type==='n'||type==='str'){
    value=v?.textContent||'';
    if(type!=='str'&&value&&!Number.isFinite(Number(value)))fail('Invalid numeric cell.');
   }else fail('Unsupported Excel cell type.');
   if(value.length>8000)fail('Cell text exceeds 8,000 characters.');
   values.set(col,value);
  }
  rowMap.set(n,values);maxRow=Math.max(maxRow,n);
 }
 if(!width)fail('Worksheet has no columns.');
 const materialize=n=>Array.from({length:width},(_,i)=>rowMap.get(n)?.get(i)||'');
 const columns=materialize(1);
 const rows=Array.from({length:maxRow-1},(_,i)=>materialize(i+2));
 return {name,columns,rows};
}
async function parse(input){
 const parts=await unzip(input);
 xml(parts,'[Content_Types].xml','http://schemas.openxmlformats.org/package/2006/content-types','Types');
 const rootRels=xml(parts,'_rels/.rels',PKG,'Relationships');
 if(!children(rootRels,'Relationship',PKG).some(e=>e.getAttribute('Type')?.endsWith('/officeDocument')&&e.getAttribute('Target')==='xl/workbook.xml'&&!e.getAttribute('TargetMode')))
  fail('Missing or unsafe workbook relationship.');
 const workbook=xml(parts,'xl/workbook.xml',MAIN,'workbook');
 const relRoot=xml(parts,'xl/_rels/workbook.xml.rels',PKG,'Relationships'),rels=new Map();
 for(const rel of children(relRoot,'Relationship',PKG)){
  const id=rel.getAttribute('Id'),target=rel.getAttribute('Target'),type=rel.getAttribute('Type');
  if(!id||rels.has(id)||rel.getAttribute('TargetMode'))fail('Duplicate or external workbook relationship.');
  if(type?.endsWith('/worksheet')){
   if(!/^worksheets\/sheet[12]\.xml$/.test(target||''))fail('Unsupported worksheet target.');
   rels.set(id,'xl/'+target);
  }
 }
 const sheets=children(child(workbook,'sheets',MAIN),'sheet',MAIN);
 if(!sheets.length||sheets.length>2)fail('Import supports one or two sheets.');
 const names=new Set(),shared=parseStrings(parts),result=[];
 for(const sheet of sheets){
  const name=sheet.getAttribute('name')||'',id=sheet.getAttributeNS(REL,'id');
  if(!name||name.length>31||/[\[\]:*?\/\\]/.test(name)||/^'|'$/.test(name)||names.has(name.toLowerCase()))
   fail('Invalid or duplicate worksheet name.');
  names.add(name.toLowerCase());
  const path=rels.get(id);
  if(!path||!parts.has(path))fail('Missing worksheet relationship.');
  result.push(readSheet(parts,path,shared,name));
 }
 return result;
}
async function load(input){
 const tables=await parse(input);
 const prior=M.dataTables.exportState();
 const state={version:1,selected:null,tables:tables.map((t,i)=>({id:'sheet-'+(i+1),...t}))};
 try{M.dataTables.restoreState(state);}
 catch(e){M.dataTables.restoreState(prior);throw e;}
 return tables.length;
}
const area=document.createElement('details');area.id='xlsx-import-details';
area.innerHTML='<summary>Excel XLSX import · offline</summary>'+
 '<p>Import up to two sheets and 1,000 rows per sheet (5 MB ZIP / 12 MB expanded). Replaces all current Data Tables sheets after confirmation. Unsupported Excel features are rejected, not silently discarded.</p>'+
 '<div class="data-toolbar"><label>Workbook<input type="file" id="xlsx-import-file" accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"></label>'+
 '<button id="xlsx-import" type="button" class="secondary">Import XLSX</button></div>'+
 '<p id="xlsx-import-status" role="status" aria-live="polite"></p>';
panel.append(area);
$('xlsx-import').addEventListener('click',async()=>{
 const status=$('xlsx-import-status');
 try{
  const file=$('xlsx-import-file').files?.[0];
  if(!file)fail('Choose an XLSX workbook first.');
  if(file.size>MAX_FILE)fail('Workbook exceeds 5 MB.');
  const bytes=new Uint8Array(await file.arrayBuffer());
  const tables=await parse(bytes);
  if(!confirm('Replace all existing Data Tables sheets with '+tables.length+' imported sheet(s)?'))return;
  const prior=M.dataTables.exportState();
  try{M.dataTables.restoreState({version:1,selected:null,tables:tables.map((t,i)=>({id:'sheet-'+(i+1),...t}))});}
  catch(e){M.dataTables.restoreState(prior);throw e;}
  status.textContent='Imported '+tables.length+' sheet(s) successfully.';
 }catch(e){status.textContent=e.message;}
});
M.xlsxImport={parse,load,fromExcel};
})();
