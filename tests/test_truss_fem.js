/* Analytical reference, equilibrium, energy and invalid-mechanism regressions. */
'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');
const fem = require('../tools/truss-fem.js');
const close = (got,want,rel=1e-9) => assert.ok(Math.abs(got-want)<=rel*Math.max(1,Math.abs(want)),String(got)+' != '+String(want));
const clone = data => JSON.parse(JSON.stringify(data));

test('built-in truss examples are immutable and getExample returns independent editable copies',()=>{
 const template=fem.examples.triangle;
 const copy=fem.getExample('triangle');
 assert.deepEqual(copy,template);
 assert.notEqual(copy,template);
 assert.notEqual(copy.nodes,template.nodes);
 assert.notEqual(copy.nodes[0],template.nodes[0]);
 assert.ok(Object.isFrozen(fem.examples));
 assert.ok(Object.isFrozen(template));
 assert.ok(Object.isFrozen(template.nodes));
 assert.ok(Object.isFrozen(template.nodes[0]));
 copy.nodes[0].x=99;
 copy.members[0].area=1;
 assert.equal(template.nodes[0].x,0);
 assert.equal(template.members[0].area,1200);
 const bar=fem.getExample('bar');
 assert.deepEqual(bar,fem.examples.bar);
 assert.notEqual(bar.members,fem.examples.bar.members);
 assert.throws(()=>fem.getExample('unknown'),/Unknown truss example/);
 assert.throws(()=>fem.getExample('toString'),/Unknown truss example/);
});

test('legacy TrussStudio.example reads return independent editable SI copies',()=>{
 const first=globalThis.TrussStudio.example;
 const second=globalThis.TrussStudio.example;
 assert.deepEqual(first,second);
 assert.notEqual(first,second);
 assert.notEqual(first.nodes,second.nodes);
 assert.notEqual(first.members,second.members);
 assert.equal(first.members[0].A,0.001);
 assert.equal(first.members[0].E,200e9);
 first.nodes[0].x=99;
 first.members[0].A=0.5;
 const fresh=globalThis.TrussStudio.example;
 assert.equal(fresh.nodes[0].x,0);
 assert.equal(fresh.members[0].A,0.001);
 assert.equal(globalThis.TrussStudio.solve(fresh).members.length,3);
});


test('truss JSON preview counts independently loaded free DOFs',()=>{
 const bar=clone(fem.examples.bar);
 let preview=fem.inspectJSON(JSON.stringify(bar));
 assert.equal(preview.freeLoadedDofCount,1);
 assert.equal(preview.freeLoadedDofCount+preview.restrainedLoadedDofCount,preview.loadedDofCount);
 bar.nodes[0].fx=2;bar.nodes[0].fy=-3;bar.nodes[1].fy=4;
 preview=fem.inspectJSON(JSON.stringify(bar));
 assert.equal(preview.freeLoadedDofCount,1);
 assert.equal(preview.restrainedLoadedDofCount,3);
 assert.equal(preview.freeLoadedDofCount+preview.restrainedLoadedDofCount,preview.loadedDofCount);
 bar.nodes[1].fx=0;
 assert.equal(fem.inspectJSON(JSON.stringify(bar)).freeLoadedDofCount,0);
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true,fx:2000,fy:-3000},
  {id:'B',x:2,y:0,fixY:true,fx:1000,fy:4000}],
  members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 assert.equal(fem.inspectJSON(JSON.stringify(legacy)).freeLoadedDofCount,1);
 assert.throws(()=>fem.inspectJSON('{bad'),/Invalid truss JSON/);
 close(fem.solve(fem.examples.bar).displacements[1].x,1e-5,1e-13);
});

test('truss JSON preview distinguishes loads at restrained DOFs',()=>{
 const bar=clone(fem.examples.bar);
 assert.equal(fem.inspectJSON(JSON.stringify(bar)).restrainedLoadedDofCount,0);
 bar.nodes[0].fx=2;bar.nodes[0].fy=-3;bar.nodes[1].fy=4;
 const preview=fem.inspectJSON(JSON.stringify(bar));
 assert.equal(preview.loadedDofCount,4);
 assert.equal(preview.restrainedLoadedDofCount,3);
 assert.equal(preview.fixedDofCount,3);
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true,fx:2000,fy:-3000},
  {id:'B',x:2,y:0,fixY:true,fx:1000,fy:4000}],
  members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 assert.equal(fem.inspectJSON(JSON.stringify(legacy)).restrainedLoadedDofCount,3);
 assert.throws(()=>fem.inspectJSON('{bad'),/Invalid truss JSON/);
 close(fem.solve(fem.examples.bar).displacements[1].x,1e-5,1e-13);
});

test('truss preview does not count zero-valued restrained loads',()=>{
 const bar=clone(fem.examples.bar);
 bar.nodes[0].fx=0;bar.nodes[0].fy=0;
 const preview=fem.inspectJSON(JSON.stringify(bar));
 assert.equal(preview.restrainedLoadedDofCount,0);
 assert.equal(preview.loadedDofCount,1);
});

test('truss JSON preview counts isolated nodes independently of connected groups',()=>{
 const bar=clone(fem.examples.bar);
 assert.equal(fem.inspectJSON(JSON.stringify(bar)).isolatedNodeCount,0);
 const disconnected=clone(bar);
 disconnected.nodes.push({id:'C',x:10,y:10},{id:'D',x:11,y:10});
 assert.equal(fem.inspectJSON(JSON.stringify(disconnected)).isolatedNodeCount,2);
 assert.equal(fem.inspectJSON(JSON.stringify(disconnected)).connectedComponentCount,3);
 disconnected.members.push({id:'CD',a:'C',b:'D',E:200,area:1000});
 assert.equal(fem.inspectJSON(JSON.stringify(disconnected)).isolatedNodeCount,0);
 assert.equal(fem.inspectJSON(JSON.stringify(disconnected)).connectedComponentCount,2);
 disconnected.nodes.push({id:'E',x:20,y:20});
 assert.equal(fem.inspectJSON(JSON.stringify(disconnected)).isolatedNodeCount,1);
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true,fx:1000},{id:'C',x:5,y:0}],
   members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 assert.equal(fem.inspectJSON(JSON.stringify(legacy)).isolatedNodeCount,1);
 assert.throws(()=>fem.inspectJSON('{bad'),/Invalid truss JSON/);
 close(fem.solve(fem.examples.bar).displacements[1].x,1e-5,1e-13);
});

test('single axial bar matches FL/EA, stress F/A, reactions and Clapeyron energy',()=>{
 const r=fem.solve(fem.examples.bar);
 close(r.displacements[1].x,1e-5,1e-13);close(r.members[0].force,1000);close(r.members[0].stress,1e6);
 close(r.reactions[0].rx,-1000);close(r.reactions[0].ry,0);close(r.elasticEnergy,.005);
 assert.ok(r.residual<1e-12);assert.ok(r.energyError<1e-12);assert.equal(r.members[0].type,'Tension');
});

test('triangle FEM: support equilibrium, symmetric compression, linear load scaling',()=>{
 const reference=fem.solve(fem.examples.triangle);
 const nodeC=reference.displacements.find(n=>n.id==='C');
 assert.ok(nodeC.y < 0 && nodeC.magnitude>0);
 close(reference.reactions.reduce((s,r)=>s+r.ry,0),20000);
 close(reference.reactions.find(r=>r.id==='A').ry,10000);
 close(reference.reactions.find(r=>r.id==='B').ry,10000);
 close(reference.members.find(m=>m.id==='AC').force,reference.members.find(m=>m.id==='BC').force);
 assert.ok(reference.residual<1e-12 && reference.energyError<1e-12);
 const doubled=clone(fem.examples.triangle);doubled.nodes[2].fy=-40;
 const r2=fem.solve(doubled);
 close(r2.displacements[2].y,2*nodeC.y,1e-12);
 close(r2.members[1].stress,2*reference.members[1].stress);
});

test('stiffness and load invariant: doubling E halves displacement without changing member forces',()=>{
 const doubled=clone(fem.examples.triangle);doubled.members.forEach(m=>{m.E*=2;});
 const r=fem.solve(doubled),base=fem.solve(fem.examples.triangle);
 for(let i=0;i<3;i++){close(r.displacements[i].x,.5*base.displacements[i].x,1e-10);close(r.displacements[i].y,.5*base.displacements[i].y,1e-10);}
 for(let i=0;i<3;i++)close(r.members[i].force,base.members[i].force,1e-7);
});

test('rejects disconnected DOF, zero member length, negative area, nonfinite loads and duplicates',()=>{
 const invalid=clone(fem.examples.bar);invalid.nodes[1].fixY=false;
 assert.throws(()=>fem.solve(invalid),/Unstable|under-constrained/);
 invalid.nodes[1].fixY=true;invalid.nodes[1].x=0;
 assert.throws(()=>fem.solve(invalid),/zero\/invalid length/);
 invalid.nodes[1].x=2;invalid.members[0].area=-1;
 assert.throws(()=>fem.solve(invalid),/must be positive/);
 invalid.members[0].area=1000;invalid.nodes[1].fx='Infinity';
 assert.throws(()=>fem.solve(invalid),/finite/);
 invalid.nodes[1].fx=1;invalid.nodes[1].id='A';
 assert.throws(()=>fem.solve(invalid),/Duplicate node/);
});

test('rejects mechanisms with nonzero stiffness diagonals (two unbraced collinear bars)',()=>{
 const model={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:1,y:0,fixY:true},{id:'C',x:1,y:1,fx:1}],members:[{id:'AB',a:'A',b:'B',E:200,area:1000},{id:'BC',a:'B',b:'C',E:200,area:1000}]};
 assert.throws(()=>fem.solve(model),/Unstable|under-constrained|singular/);
});

test('scaled pivoting rejects a triangular mechanism with nonzero free-DOF stiffness diagonals',()=>{
 const model=clone(fem.examples.triangle);
 model.nodes[1].fixY=false;
 const parsed=fem.parseModel(model);
 const diagonal=new Array(parsed.nodes.length*2).fill(0);
 for(const member of parsed.members){
  const v=[-member.c,-member.s,member.c,member.s];
  const dof=[2*member.a,2*member.a+1,2*member.b,2*member.b+1];
  for(let i=0;i<4;i++) diagonal[dof[i]]+=member.stiffness*v[i]*v[i];
 }
 const free=parsed.nodes.flatMap((node,i)=>[
  ...(node.fixX?[]:[2*i]),...(node.fixY?[]:[2*i+1])
 ]);
 assert.equal(free.length,4);
 assert.ok(free.every(dof=>diagonal[dof]>0),'fixture must not be caught by a zero stiffness diagonal');
 const preview=fem.inspectJSON(JSON.stringify(model));
 assert.equal(preview.nodeCount,3);
 assert.equal(preview.memberCount,3);
 assert.equal(preview.connectedComponentCount,1);
 assert.throws(()=>fem.solve(model),/Unstable or under-constrained truss \(singular stiffness matrix\)/);
});

test('legacy SI model conversion preserves force and displacement, and rejects mixed units',()=>{
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},
   {id:'B',x:2,y:0,fixY:true,fx:1000}],
   members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 const converted=fem.fromLegacy(legacy);
 close(converted.nodes[1].fx,1);
 close(converted.members[0].E,200);
 close(converted.members[0].area,1000);
 const r=fem.solve(converted);
 close(r.displacements[1].x,1e-5,1e-13);
 close(r.reactions[0].rx,-1000);
 const mixed=clone(legacy);
 mixed.members.push({id:'BA',a:'B',b:'A',E:200,area:1000});
 assert.throws(()=>fem.fromLegacy(mixed),/Mixed legacy SI and current/);
 const both=clone(legacy);both.members[0].area=1000;
 assert.throws(()=>fem.fromLegacy(both),/Mixed legacy SI and current/);
 assert.throws(()=>fem.fromLegacy({nodes:null,members:legacy.members}),/Invalid legacy truss model/);
 assert.throws(()=>fem.fromLegacy({nodes:[null],members:legacy.members}),/Invalid legacy truss model/);
 const bad=clone(legacy);bad.nodes[1].fx='Infinity';
 assert.throws(()=>fem.fromLegacy(bad),/finite number/);
 assert.deepEqual(fem.fromLegacy(fem.examples.bar),fem.examples.bar);
});


test('current truss parser rejects malformed node and member entries with indexed diagnostics',()=>{
 const reference=fem.solve(fem.examples.bar);
 close(reference.displacements[1].x,1e-5,1e-13);
 for (const bad of [null,undefined,[],42,'bad']) {
   const nodes=clone(fem.examples.bar);nodes.nodes[1]=bad;
   assert.throws(()=>fem.solve(nodes),/Node 2 must be an object/);
   const members=clone(fem.examples.bar);members.members[0]=bad;
   assert.throws(()=>fem.solve(members),/Member 1 must be an object/);
 }
 assert.throws(()=>fem.parseModel({nodes:[fem.examples.bar.nodes[0],null],members:fem.examples.bar.members}),/Node 2 must be an object/);
 assert.throws(()=>fem.parseModel({nodes:fem.examples.bar.nodes,members:[null]}),/Member 1 must be an object/);
 assert.deepEqual(fem.fromLegacy(fem.examples.bar),fem.examples.bar);
});


test('numeric model fields reject arrays and objects rather than coercing them',()=>{
 for (const bad of [[],[1],{}, {valueOf:()=>1}]) {
   const node=clone(fem.examples.bar);node.nodes[1].fx=bad;
   assert.throws(()=>fem.solve(node),/finite number/);
   const member=clone(fem.examples.bar);member.members[0].area=bad;
   assert.throws(()=>fem.solve(member),/finite number/);
 }
 const good=fem.solve(fem.examples.bar);
 close(good.displacements[1].x,1e-5,1e-13);
});

test('rejects SI scaling overflow before assembling loads and stiffness',()=>{
 const reference=fem.solve(fem.examples.bar);
 close(reference.displacements[1].x,1e-5,1e-13);
 for (const field of ['fx','fy']) {
   const model=clone(fem.examples.bar);model.nodes[1][field]=1e308;
   assert.throws(()=>fem.parseModel(model),/exceeds the supported SI range/);
   assert.throws(()=>fem.solve(model),/exceeds the supported SI range/);
 }
 const stiff=clone(fem.examples.bar);stiff.members[0].E=1e308;
 assert.throws(()=>fem.parseModel(stiff),/exceeds the supported SI range/);
 const valid=clone(fem.examples.bar);valid.nodes[1].fx='1';
 close(fem.solve(valid).members[0].force,1000);
});


test('legacy area SI conversion rejects overflow and preserves valid axial-bar physics',()=>{
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true,fx:1000}],
   members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 const overflowing=clone(legacy);overflowing.members[0].A=1e308;
 assert.throws(()=>fem.fromLegacy(overflowing),/Legacy area.*exceeds the supported SI range/);
 assert.throws(()=>fem.solve(fem.fromLegacy(overflowing)),/Legacy area.*exceeds the supported SI range/);
 const converted=fem.fromLegacy(legacy);
 close(converted.members[0].area,1000);
 close(fem.solve(converted).displacements[1].x,1e-5,1e-13);
});


test('support constraints reject ambiguous flags and preserve explicit boolean/string settings',()=>{
 const base=clone(fem.examples.bar);
 for(const field of ['fixX','fixY']) for(const bad of [null,0,1,'TRUE','yes',[],{}]){
   const model=clone(base);model.nodes[0][field]=bad;
   assert.throws(()=>fem.parseModel(model),/must be true or false/);
   assert.throws(()=>fem.solve(model),/must be true or false/);
 }
 const strings=clone(base);
 strings.nodes[0].fixX='true';strings.nodes[0].fixY='true';
 strings.nodes[1].fixY='true';strings.nodes[1].fixX='false';
 close(fem.solve(strings).displacements[1].x,1e-5,1e-13);
 const omitted=clone(base);delete omitted.nodes[1].fixX;
 close(fem.solve(omitted).members[0].force,1000);
});


test('numeric input rejects whitespace-only values while preserving finite numeric strings',()=>{
 for(const blank of [' ', String.fromCharCode(9), String.fromCharCode(10), '  '+String.fromCharCode(9)+'  ']){
   const load=clone(fem.examples.bar);load.nodes[1].fx=blank;
   assert.throws(()=>fem.parseModel(load),/finite number/);
   assert.throws(()=>fem.solve(load),/finite number/);
   const area=clone(fem.examples.bar);area.members[0].area=blank;
   assert.throws(()=>fem.parseModel(area),/finite number/);
 }
 const valid=clone(fem.examples.bar);valid.nodes[1].fx=' 1 ';valid.members[0].area=' 1000 ';
 close(fem.solve(valid).displacements[1].x,1e-5,1e-13);
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true,fx:1000}],members:[{id:'AB',a:'A',b:'B',E:200e9,A:'   '}]};
 assert.throws(()=>fem.fromLegacy(legacy),/finite number/);
});


test('truss parser rejects positive properties whose assembled stiffness underflows to zero',()=>{
 const model=clone(fem.examples.bar);
 model.members[0].E=1e-300;
 model.members[0].area=1e-300;
 assert.throws(()=>fem.parseModel(model),/stiffness underflow/);
 assert.throws(()=>fem.solve(model),/stiffness underflow/);
 const reference=fem.solve(fem.examples.bar);
 close(reference.displacements[1].x,1e-5,1e-13);
});


test('member endpoints require string IDs; no array or object coercion',()=>{
 const reference=fem.solve(fem.examples.bar);
 close(reference.displacements[1].x,1e-5,1e-13);
 for(const field of ['a','b']) for(const bad of [null,undefined,0,1,['A'],['B'],{},true]){
   const model=clone(fem.examples.bar);model.members[0][field]=bad;
   assert.throws(()=>fem.parseModel(model),/end node IDs must be strings/);
   assert.throws(()=>fem.solve(model),/end node IDs must be strings/);
 }
 const trimmed=clone(fem.examples.bar);
 trimmed.members[0].a=' A ';trimmed.members[0].b=' B ';
 close(fem.solve(trimmed).displacements[1].x,1e-5,1e-13);
});

test('node and member identifiers reject coerced non-string IDs while retaining trimmed string IDs',()=>{
 const reference=fem.solve(fem.examples.bar);
 close(reference.displacements[1].x,1e-5,1e-13);
 for (const collection of ['nodes','members']) for (const bad of [null,undefined,0,1,['A'],['AB'],{},true]) {
   const model=clone(fem.examples.bar);model[collection][0].id=bad;
   assert.throws(()=>fem.parseModel(model),/ID must be a string/);
   assert.throws(()=>fem.solve(model),/ID must be a string/);
 }
 const valid=clone(fem.examples.bar);
 valid.nodes[0].id=' A ';valid.nodes[1].id=' B ';
 valid.members[0].id=' AB ';
 close(fem.solve(valid).displacements[1].x,1e-5,1e-13);
 assert.equal(fem.parseModel(valid).members[0].id,'AB');
});


test('numeric fields reject bigint and symbol without leaking native conversion errors',()=>{
 for(const bad of [1n, Symbol('bad')]) {
   const load=clone(fem.examples.bar);load.nodes[1].fx=bad;
   assert.throws(()=>fem.parseModel(load),/finite number/);
   assert.throws(()=>fem.solve(load),/finite number/);
   const area=clone(fem.examples.bar);area.members[0].area=bad;
   assert.throws(()=>fem.parseModel(area),/finite number/);
   const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true,fx:1000}],members:[{id:'AB',a:'A',b:'B',E:200e9,A:bad}]};
   assert.throws(()=>fem.fromLegacy(legacy),/finite number/);
 }
 const valid=clone(fem.examples.bar);valid.nodes[1].fx=' 1 ';
 close(fem.solve(valid).displacements[1].x,1e-5,1e-13);
});

test('truss JSON import preserves model data and rejects malformed or mixed units',()=>{
 for(const example of [fem.examples.bar,fem.examples.triangle]){
   const text=JSON.stringify(example), imported=fem.importJSON(text);
   assert.deepEqual(imported,example);
   assert.deepEqual(JSON.parse(JSON.stringify(imported)),example);
   close(fem.solve(imported).maxDisplacement.magnitude,fem.solve(example).maxDisplacement.magnitude,1e-12);
 }
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true,fx:1000}],
   members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 assert.deepEqual(fem.importJSON(JSON.stringify(legacy)),legacy);
 close(fem.solve(fem.fromLegacy(fem.importJSON(JSON.stringify(legacy)))).displacements[1].x,1e-5,1e-13);
 assert.throws(()=>fem.importJSON('{bad'),/Invalid truss JSON/);
 assert.throws(()=>fem.importJSON(null),/must be a string/);
 const mixed=clone(legacy);mixed.members[0].area=1000;
 assert.throws(()=>fem.importJSON(JSON.stringify(mixed)),/Mixed legacy SI and current/);
 const malformed=clone(fem.examples.bar);malformed.nodes[1].fixY=1;
 assert.throws(()=>fem.importJSON(JSON.stringify(malformed)),/must be true or false/);
});


test('truss JSON importer bounds input before parsing without rejecting normal models',()=>{
 const valid=JSON.stringify(fem.examples.bar);
 assert.deepEqual(fem.importJSON(valid),fem.examples.bar);
 assert.throws(()=>fem.importJSON(' '.repeat(1024*1024+1)),/1 MiB import limit/);
 assert.throws(()=>fem.importJSON(' '.repeat(1024*1024)+'x'),/1 MiB import limit/);
 assert.throws(()=>fem.importJSON('{bad'),/Invalid truss JSON/);
});


test('shared file-import byte validator enforces safe 1 MiB and exact byte-count boundaries',()=>{
 const limit=fem.MAX_IMPORT_BYTES;
 assert.equal(limit,1024*1024);
 for(const size of [0,1,limit]){
  assert.equal(fem.validateImportByteLength(size),size);
  assert.equal(fem.validateImportByteLength(size,size),size);
 }
 for(const size of [undefined,null,-1,1.5,NaN,Infinity,Number.MAX_SAFE_INTEGER+1]){
  assert.throws(()=>fem.validateImportByteLength(size),/Model JSON file size is invalid/);
 }
 assert.throws(()=>fem.validateImportByteLength(limit+1),/Model JSON exceeds 1 MiB/);
 for(const actual of [undefined,null,-1,1.5,NaN,Infinity,Number.MAX_SAFE_INTEGER+1]){
  assert.throws(()=>fem.validateImportByteLength(5,actual),/Model JSON read returned an invalid byte length/);
 }
 assert.throws(()=>fem.validateImportByteLength(5,limit+1),/Model JSON exceeds 1 MiB/);
 assert.throws(()=>fem.validateImportByteLength(17,16),/read returned fewer bytes than declared; expected 17 bytes, received 16 bytes/);
 assert.throws(()=>fem.validateImportByteLength(17,18),/read returned more bytes than declared; expected 17 bytes, received 18 bytes/);
 assert.equal(fem.validateImportByteLength(17,17),17);
});


test('file-byte decoder rejects malformed UTF-8 and preserves a counted BOM',()=>{
 const json=JSON.stringify(fem.examples.bar);
 const encoded=new TextEncoder().encode(json);
 assert.equal(fem.decodeImportBytes(encoded.buffer),json);
 const withBom=new Uint8Array(encoded.length+3);
 withBom.set([0xef,0xbb,0xbf]);
 withBom.set(encoded,3);
 const decoded=fem.decodeImportBytes(withBom);
 assert.equal(decoded.charCodeAt(0),0xfeff);
 assert.deepEqual(fem.importJSON(decoded).nodes,fem.examples.bar.nodes);
 for(const invalid of [[0xc3,0x28],[0xe2,0x82],[0xf0,0x28,0x8c,0x28]]){
  assert.throws(()=>fem.decodeImportBytes(new Uint8Array(invalid)),/Model JSON must be valid UTF-8/);
 }
 assert.throws(()=>fem.decodeImportBytes('not bytes'),/ArrayBuffer or typed array/);
 assert.throws(()=>fem.decodeImportBytes(new Uint8Array(fem.MAX_IMPORT_BYTES+1)),/Model JSON exceeds 1 MiB/);
});

test('truss JSON importer accepts an exact 1 MiB UTF-8 document',()=>{
 const limit=1024*1024;
 const prefix=JSON.stringify({...fem.examples.bar,note:'é'.repeat(100)});
 const padding=limit-new TextEncoder().encode(prefix).byteLength;
 assert.ok(padding>=0);
 const exact=prefix+' '.repeat(padding);
 assert.equal(new TextEncoder().encode(exact).byteLength,limit);
 assert.ok(exact.length<limit);
 assert.deepEqual(fem.importJSON(exact).nodes,fem.examples.bar.nodes);
 assert.throws(()=>fem.importJSON(exact+' '),/1 MiB import limit/);
});


test('JSON import enforces byte limit for multibyte Unicode rather than UTF-16 length',()=>{
 const valid=JSON.stringify({...fem.examples.bar,note:'é'.repeat(100)});
 assert.deepEqual(fem.importJSON(valid).nodes,fem.examples.bar.nodes);
 const oversized=JSON.stringify({...fem.examples.bar,note:'é'.repeat(530000)});
 assert.ok(oversized.length<1024*1024);
 assert.ok(new TextEncoder().encode(oversized).byteLength>1024*1024);
 assert.throws(()=>fem.importJSON(oversized),/1 MiB import limit/);
 close(fem.solve(fem.examples.bar).displacements[1].x,1e-5,1e-13);
});


test('truss JSON import accepts UTF-8 BOM from saved files without relaxing validation',()=>{
 const bar=JSON.stringify(fem.examples.bar);
 assert.deepEqual(fem.importJSON('\uFEFF'+bar),fem.examples.bar);
 close(fem.solve(fem.importJSON('\uFEFF'+bar)).displacements[1].x,1e-5,1e-13);
 assert.throws(()=>fem.importJSON('\uFEFF{bad'),/Invalid truss JSON/);
 assert.throws(()=>fem.importJSON('\uFEFF'.repeat(350000)+bar),/1 MiB import limit/);
});

test('validated truss JSON export round-trips current and legacy models',()=>{
 for(const example of [fem.examples.bar,fem.examples.triangle]){
   assert.deepEqual(fem.importJSON(fem.exportJSON(example)),example);
   close(fem.solve(fem.importJSON(fem.exportJSON(example))).maxDisplacement.magnitude,fem.solve(example).maxDisplacement.magnitude);
 }
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true,fx:1000}],
   members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 assert.deepEqual(fem.importJSON(fem.exportJSON(legacy)),legacy);
 close(fem.solve(fem.fromLegacy(fem.importJSON(fem.exportJSON(legacy)))).displacements[1].x,1e-5,1e-13);
 const invalid=clone(fem.examples.bar);invalid.nodes[1].fixY=1;
 assert.throws(()=>fem.exportJSON(invalid),/must be true or false/);
 const mixed=clone(legacy);mixed.members[0].area=1000;
 assert.throws(()=>fem.exportJSON(mixed),/Mixed legacy SI and current/);
 assert.throws(()=>fem.exportJSON(null),/Invalid legacy truss model/);
});


test('truss JSON export respects importer UTF-8 limit and round-trips valid Unicode',()=>{
 const valid={...clone(fem.examples.bar),note:'é'.repeat(100)};
 const json=fem.exportJSON(valid);
 assert.deepEqual(fem.importJSON(json),valid);
 close(fem.solve(fem.importJSON(json)).displacements[1].x,1e-5,1e-13);
 const tooLarge={...clone(fem.examples.bar),note:'é'.repeat(530000)};
 assert.throws(()=>fem.exportJSON(tooLarge),/1 MiB export limit/);
 assert.throws(()=>fem.importJSON(JSON.stringify(tooLarge)),/1 MiB import limit/);
});


test('JSON export validates serialized toJSON output rather than only original fields',()=>{
 const model=clone(fem.examples.bar);
 model.nodes[1].toJSON=function(){return {...this,fixY:1,toJSON:undefined};};
 assert.throws(()=>fem.exportJSON(model),/must be true or false/);
 const valid=clone(fem.examples.bar);
 assert.deepEqual(fem.importJSON(fem.exportJSON(valid)),valid);
 close(fem.solve(valid).displacements[1].x,1e-5,1e-13);
});


test('truss JSON export rejects missing or cyclic serialized documents with clear diagnostics',()=>{
 const missing=clone(fem.examples.bar);
 missing.toJSON=()=>undefined;
 assert.throws(()=>fem.exportJSON(missing),/must produce a document/);
 const cyclic=clone(fem.examples.bar);
 cyclic.extra=cyclic;
 assert.throws(()=>fem.exportJSON(cyclic),/could not serialize the model/);
 const valid=clone(fem.examples.bar);
 assert.deepEqual(fem.importJSON(fem.exportJSON(valid)),valid);
 close(fem.solve(valid).displacements[1].x,1e-5,1e-13);
});


test('truss JSON unit descriptors distinguish all core and optional properties without magnitude guessing',()=>{
 const studio=clone(fem.examples.bar);
 studio.members[0].density=0;studio.members[0].I=1e6;studio.members[0].K=1;
 const studioUnits={system:'studio',coordinates:'m',forces:'kN',modulus:'GPa',area:'mm²',
   density:'kg/m³',secondMoment:'mm⁴',effectiveLengthFactor:'dimensionless'};
 assert.deepEqual(fem.describeUnits(studio),studioUnits);
 assert.ok(Object.isFrozen(fem.describeUnits(studio)));
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true,fx:1000}],
   members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001,density:7850,I:1e-6,K:1}]};
 const legacyUnits={system:'legacy-si',coordinates:'m',forces:'N',modulus:'Pa',area:'m²',
   density:'kg/m³',secondMoment:'m⁴',effectiveLengthFactor:'dimensionless'};
 assert.deepEqual(fem.describeUnits(fem.importJSON(fem.exportJSON(legacy))),legacyUnits);
 close(fem.solve(fem.fromLegacy(legacy)).displacements[1].x,1e-5,1e-13);
 const mixed=clone(legacy);mixed.members[0].area=1000;
 assert.throws(()=>fem.describeUnits(mixed),/Mixed legacy SI and current/);
 const invalid=clone(studio);invalid.nodes[1].fixY=1;
 assert.throws(()=>fem.describeUnits(invalid),/must be true or false/);
});


test('solveDocument accepts current and legacy JSON while returning explicit input units and SI physics',()=>{
 const current=fem.importJSON(fem.exportJSON(fem.examples.bar));
 const modern=fem.solveDocument(current);
 close(modern.displacements[1].x,1e-5,1e-13);
 close(modern.members[0].force,1000);
 assert.deepEqual(modern.inputUnits,fem.describeUnits(current));
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true,fx:1000}],
  members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 const before=clone(legacy);
 const result=fem.solveDocument(fem.importJSON(fem.exportJSON(legacy)));
 close(result.displacements[1].x,modern.displacements[1].x,1e-13);
 close(result.members[0].force,modern.members[0].force);
 close(result.reactions[0].rx,-1000);
 assert.equal(result.inputUnits.system,'legacy-si');
 assert.ok(Object.isFrozen(result.inputUnits));
 assert.deepEqual(legacy,before);
 const mixed=clone(legacy);mixed.members[0].area=1000;
 assert.throws(()=>fem.solveDocument(mixed),/Mixed legacy SI and current/);
 const invalid=clone(current);invalid.nodes[1].fixY=1;
 assert.throws(()=>fem.solveDocument(invalid),/must be true or false/);
});


test('solveJSON validates imported Studio and SI documents and retains analytical physics',()=>{
 const studio=fem.solveJSON(fem.exportJSON(fem.examples.bar));
 close(studio.displacements[1].x,1e-5,1e-13);
 close(studio.members[0].force,1000);
 assert.equal(studio.inputUnits.system,'studio');
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true,fx:1000}],members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 const si=fem.solveJSON('\uFEFF'+fem.exportJSON(legacy));
 close(si.displacements[1].x,studio.displacements[1].x,1e-13);
 close(si.reactions[0].rx,-1000);
 assert.equal(si.inputUnits.system,'legacy-si');
 assert.throws(()=>fem.solveJSON('{bad'),/Invalid truss JSON/);
 assert.throws(()=>fem.solveJSON(' '.repeat(1024*1024+1)),/1 MiB import limit/);
 const invalid=clone(fem.examples.bar);invalid.nodes[1].fixY=1;
 assert.throws(()=>fem.solveJSON(JSON.stringify(invalid)),/must be true or false/);
});


test('inspectJSON previews Studio and legacy models, including unstable structures',()=>{
 const studio=fem.inspectJSON(fem.exportJSON(fem.examples.bar));
 assert.equal(studio.nodeCount,2);assert.equal(studio.memberCount,1);
 assert.equal(studio.inputUnits.system,'studio');
 assert.ok(Object.isFrozen(studio.inputUnits));
 assert.deepEqual(studio.model,fem.examples.bar);
 close(fem.solveDocument(studio.model).displacements[1].x,1e-5,1e-13);
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true,fx:1000}],members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 const preview=fem.inspectJSON('\uFEFF'+JSON.stringify(legacy));
 assert.equal(preview.inputUnits.system,'legacy-si');assert.equal(preview.inputUnits.forces,'N');
 assert.deepEqual(preview.model,legacy);
 assert.throws(()=>fem.inspectJSON(String.raw`\uFEFF`+JSON.stringify(legacy)),/Invalid truss JSON/);
 close(fem.solveDocument(preview.model).displacements[1].x,1e-5,1e-13);
 const unstable=clone(fem.examples.bar);unstable.nodes[1].fixY=false;
 assert.equal(fem.inspectJSON(JSON.stringify(unstable)).nodeCount,2);
 assert.throws(()=>fem.solveDocument(unstable),/Unstable|under-constrained/);
 assert.throws(()=>fem.inspectJSON('{bad'),/Invalid truss JSON/);
 assert.throws(()=>fem.inspectJSON(JSON.stringify({...fem.examples.bar,members:[]})),/members/);
});


test('inspectJSON reports constrained DOFs and loaded nodes without solving',()=>{
 const bar=fem.inspectJSON(fem.exportJSON(fem.examples.bar));
 assert.equal(bar.fixedDofCount,3);
 assert.equal(bar.loadedNodeCount,1);
 assert.equal(bar.nodeCount,2);
 close(fem.solveDocument(bar.model).displacements[1].x,1e-5,1e-13);
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true,fx:1000}],
   members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 const si=fem.inspectJSON(JSON.stringify(legacy));
 assert.equal(si.fixedDofCount,3);
 assert.equal(si.loadedNodeCount,1);
 assert.equal(si.inputUnits.system,'legacy-si');
 const unloaded=JSON.parse(JSON.stringify(fem.examples.bar));
 unloaded.nodes[1].fx=0;
 unloaded.nodes[1].fixY=false;
 const preview=fem.inspectJSON(JSON.stringify(unloaded));
 assert.equal(preview.fixedDofCount,2);
 assert.equal(preview.loadedNodeCount,0);
 assert.throws(()=>fem.solveDocument(preview.model),/Unstable|under-constrained/);
 const invalid=JSON.parse(JSON.stringify(fem.examples.bar));
 invalid.nodes[0].fixX=1;
 assert.throws(()=>fem.inspectJSON(JSON.stringify(invalid)),/must be true or false/);
});

test('inspectJSON computes immutable applied-force resultant in SI',()=>{
 const studio=JSON.parse(JSON.stringify(fem.examples.bar));
 studio.nodes[0].fx=-0.25; studio.nodes[0].fy=0.5;
 studio.nodes[1].fx=1.25; studio.nodes[1].fy=-0.25;
 const a=fem.inspectJSON(JSON.stringify(studio));
 close(a.appliedForce.x,1000);close(a.appliedForce.y,250);
 assert.ok(Object.isFrozen(a.appliedForce));
 assert.equal(a.loadedNodeCount,2);
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true,fx:-250,fy:500},
 {id:'B',x:2,y:0,fixY:true,fx:1250,fy:-250}],
 members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 assert.deepEqual(fem.inspectJSON(JSON.stringify(legacy)).appliedForce,a.appliedForce);
 const unloaded=JSON.parse(JSON.stringify(fem.examples.bar));
 unloaded.nodes.forEach(n=>{n.fx=0;n.fy=0;});unloaded.nodes[1].fixY=false;
 assert.deepEqual(fem.inspectJSON(JSON.stringify(unloaded)).appliedForce,{x:0,y:0});
 assert.throws(()=>fem.inspectJSON('{bad'),/Invalid truss JSON/);
 close(fem.solveDocument(fem.examples.bar).displacements[1].x,1e-5,1e-13);
});


test('inspectJSON reports signed applied moment about origin in SI N m',()=>{
 const studio=clone(fem.examples.bar);
 studio.nodes[0].fx=0;studio.nodes[0].fy=0;
 studio.nodes[1].fx=1;studio.nodes[1].fy=2;
 const p=fem.inspectJSON(JSON.stringify(studio));
 close(p.appliedMoment,4000);
 close(p.appliedForce.x,1000);close(p.appliedForce.y,2000);
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},
  {id:'B',x:2,y:0,fixY:true,fx:1000,fy:2000}],
  members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 close(fem.inspectJSON(JSON.stringify(legacy)).appliedMoment,4000);
 const translated=clone(studio);
 translated.nodes.forEach(n=>{n.y+=3;});
 close(fem.inspectJSON(JSON.stringify(translated)).appliedMoment,1000);
 const zero=clone(fem.examples.bar);zero.nodes.forEach(n=>{n.fx=0;n.fy=0;});
 zero.nodes[1].fixY=false;
 close(fem.inspectJSON(JSON.stringify(zero)).appliedMoment,0);
 close(fem.solveDocument(fem.examples.bar).displacements[1].x,1e-5,1e-13);
 assert.throws(()=>fem.inspectJSON('{broken'),/Invalid truss JSON/);
});


test('inspectJSON rejects nonfinite global moment instead of returning invalid preview physics',()=>{
 const huge=clone(fem.examples.bar);
 huge.nodes[0].x=1e200;huge.nodes[1].x=1e200+1e190;
 huge.nodes[1].fy=1e200;
 assert.throws(()=>fem.inspectJSON(JSON.stringify(huge)),/Applied moment.*finite number/);
 const normal=fem.inspectJSON(fem.exportJSON(fem.examples.bar));
 close(normal.appliedMoment,0);
 close(fem.solveDocument(normal.model).displacements[1].x,1e-5,1e-13);
 assert.throws(()=>fem.inspectJSON('{broken'),/Invalid truss JSON/);
});


test('inspectJSON rejects nonfinite resultant loads without weakening valid force and moment preview',()=>{
 const huge=clone(fem.examples.bar);
 huge.nodes[0].fx=1e305;huge.nodes[1].fx=1e305;
 assert.throws(()=>fem.inspectJSON(JSON.stringify(huge)),/Applied force x.*finite number/);
 const vertical=clone(fem.examples.bar);
 vertical.nodes[0].fy=1e305;vertical.nodes[1].fy=1e305;
 assert.throws(()=>fem.inspectJSON(JSON.stringify(vertical)),/Applied force y.*finite number/);
 const normal=fem.inspectJSON(fem.exportJSON(fem.examples.bar));
 close(normal.appliedForce.x,1000);close(normal.appliedForce.y,0);
 close(normal.appliedMoment,0);
 close(fem.solveDocument(normal.model).displacements[1].x,1e-5,1e-13);
 assert.throws(()=>fem.inspectJSON('{broken'),/Invalid truss JSON/);
});


test('inspectJSON returns immutable geometry bounds in metres without solving',()=>{
  const model=clone(fem.examples.bar);
  model.nodes[0].x=-3; model.nodes[0].y=4;
  model.nodes[1].x=2; model.nodes[1].y=-1;
  const p=fem.inspectJSON(JSON.stringify(model));
  assert.deepEqual(p.bounds,{minX:-3,maxX:2,minY:-1,maxY:4,width:5,height:5,diagonal:Math.hypot(5,5),centerX:-0.5,centerY:1.5});
  assert.ok(Object.isFrozen(p.bounds));
  const legacy={nodes:[{id:'A',x:-3,y:4,fixX:true,fixY:true},{id:'B',x:2,y:-1,fx:1000}],members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
  assert.deepEqual(fem.inspectJSON(JSON.stringify(legacy)).bounds,p.bounds);
  assert.throws(()=>fem.solveDocument(legacy),/Unstable|under-constrained/);
  close(fem.solveDocument(fem.examples.bar).displacements[1].x,1e-5,1e-13);
  assert.throws(()=>fem.inspectJSON('{broken'),/Invalid truss JSON/);
});


test('inspectJSON geometry spans reject overflow and support flat shapes',()=>{
 const flat=clone(fem.examples.bar);
 flat.nodes.forEach(n=>{n.y=0;});
 assert.equal(fem.inspectJSON(JSON.stringify(flat)).bounds.height,0);
 const huge=clone(fem.examples.bar);
 huge.nodes.push({id:'C',x:-1e308,y:0,fixX:true,fixY:true});
 huge.nodes.push({id:'D',x:1e308,y:0,fixX:true,fixY:true});
 // Keep member AB valid: the remote fixed nodes alone should overflow the bounds.
 assert.throws(()=>fem.inspectJSON(JSON.stringify(huge)),/Truss bounds width.*finite number/);
 close(fem.solveDocument(fem.examples.bar).displacements[1].x,1e-5,1e-13);
 assert.throws(()=>fem.inspectJSON('{broken'),/Invalid truss JSON/);
});


test('inspectJSON framing center is finite for extreme valid coordinates and flat models',()=>{
 const huge=clone(fem.examples.bar);
 huge.nodes.push({id:'C',x:-1e308,y:-1e307,fixX:true,fixY:true});
 huge.nodes.push({id:'D',x:1e307,y:1e307,fixX:true,fixY:true});
 const b=fem.inspectJSON(JSON.stringify(huge)).bounds;
 close(b.centerX,-4.5e307);close(b.centerY,0);
 assert.ok(Number.isFinite(b.centerX) && Number.isFinite(b.centerY));
 const flat=clone(fem.examples.bar);
 flat.nodes.forEach(n=>{n.y=7;});
 const f=fem.inspectJSON(JSON.stringify(flat)).bounds;
 assert.equal(f.centerY,7);assert.equal(f.height,0);
 assert.ok(Object.isFrozen(f));
 close(fem.solveDocument(fem.examples.bar).displacements[1].x,1e-5,1e-13);
 assert.throws(()=>fem.inspectJSON('{broken'),/Invalid truss JSON/);
});


test('inspectJSON framing diagonal is finite, zero for collapsed geometry, and rejects overflow',()=>{
 const normal=fem.inspectJSON(fem.exportJSON(fem.examples.bar)).bounds;
 close(normal.diagonal,2);
 const slanted=clone(fem.examples.bar);slanted.nodes[1].y=2;
 close(fem.inspectJSON(JSON.stringify(slanted)).bounds.diagonal,Math.sqrt(8));
 const huge=clone(fem.examples.bar);
 huge.nodes.push({id:'C',x:-1e308,y:-1e308,fixX:true,fixY:true});
 huge.nodes.push({id:'D',x:5e307,y:5e307,fixX:true,fixY:true});
 assert.throws(()=>fem.inspectJSON(JSON.stringify(huge)),/Truss bounds diagonal.*finite number/);
 assert.ok(Object.isFrozen(normal));
 close(fem.solveDocument(fem.examples.bar).displacements[1].x,1e-5,1e-13);
 assert.throws(()=>fem.inspectJSON('{broken'),/Invalid truss JSON/);
});


test('inspectJSON totals member centreline lengths in metres and rejects sum overflow',()=>{
 const bar=fem.inspectJSON(fem.exportJSON(fem.examples.bar));
 close(bar.totalMemberLength,2);
 const triangle=fem.inspectJSON(fem.exportJSON(fem.examples.triangle));
 close(triangle.totalMemberLength,4+2*Math.hypot(2,3));
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true,fx:1000}],members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 close(fem.inspectJSON(JSON.stringify(legacy)).totalMemberLength,2);
 const huge={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:1e308,y:0,fixX:true,fixY:true},{id:'C',x:0,y:1,fixX:true,fixY:true},{id:'D',x:1e308,y:1,fixX:true,fixY:true}],members:[{id:'AB',a:'A',b:'B',E:200,area:1000},{id:'CD',a:'C',b:'D',E:200,area:1000}]};
 assert.throws(()=>fem.inspectJSON(JSON.stringify(huge)),/Total member length.*finite number/);
 close(fem.solveDocument(fem.examples.bar).displacements[1].x,1e-5,1e-13);
 assert.throws(()=>fem.inspectJSON('{bad'),/Invalid truss JSON/);
});


test('inspectJSON totals SI member volume without solving and rejects overflow',()=>{
 const bar=fem.inspectJSON(fem.exportJSON(fem.examples.bar));
 close(bar.totalMemberVolume,0.002);
 const triangle=fem.inspectJSON(fem.exportJSON(fem.examples.triangle));
 close(triangle.totalMemberVolume,(4+2*Math.hypot(2,3))*0.0012);
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true,fx:1000}],members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 close(fem.inspectJSON(JSON.stringify(legacy)).totalMemberVolume,bar.totalMemberVolume);
 const unstable=clone(fem.examples.bar);unstable.nodes[1].fixY=false;
 close(fem.inspectJSON(JSON.stringify(unstable)).totalMemberVolume,0.002);
 const huge=clone(fem.examples.bar);huge.nodes[1].x=1e308;huge.members[0].area=1e12;
 // E*A/L stays finite and positive, but L*A exceeds the finite volume range.
 assert.ok(Number.isFinite(200e9*(1e12*1e-6)/1e308));
 assert.throws(()=>fem.inspectJSON(JSON.stringify(huge)),/Total member volume.*finite number/);
 close(fem.solveDocument(fem.examples.bar).displacements[1].x,1e-5,1e-13);
 assert.throws(()=>fem.inspectJSON('{bad'),/Invalid truss JSON/);
});


test('inspectJSON reports free and constrained translational DOFs without solving',()=>{
 const bar=fem.inspectJSON(fem.exportJSON(fem.examples.bar));
 assert.equal(bar.fixedDofCount,3);assert.equal(bar.freeDofCount,1);
 assert.equal(bar.fixedDofCount+bar.freeDofCount,2*bar.nodeCount);
 const unstable=clone(fem.examples.bar);unstable.nodes[1].fixY=false;
 const preview=fem.inspectJSON(JSON.stringify(unstable));
 assert.equal(preview.fixedDofCount,2);assert.equal(preview.freeDofCount,2);
 assert.throws(()=>fem.solveDocument(unstable),/Unstable|under-constrained/);
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true,fx:1000}],members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 assert.equal(fem.inspectJSON(JSON.stringify(legacy)).freeDofCount,1);
 close(fem.solveDocument(fem.examples.bar).displacements[1].x,1e-5,1e-13);
 assert.throws(()=>fem.inspectJSON('{bad'),/Invalid truss JSON/);
});


test('inspectJSON counts independently loaded translational components including restrained loads',()=>{
 const model=clone(fem.examples.bar);
 model.nodes[0].fx=-2;model.nodes[0].fy=3;
 model.nodes[1].fx=0;model.nodes[1].fy=-1;
 const preview=fem.inspectJSON(JSON.stringify(model));
 assert.equal(preview.loadedNodeCount,2);
 assert.equal(preview.loadedDofCount,3);
 assert.equal(preview.fixedDofCount,3);
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true,fx:-2000,fy:3000},{id:'B',x:2,y:0,fixY:true,fy:-1000}],members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 assert.equal(fem.inspectJSON(JSON.stringify(legacy)).loadedDofCount,3);
 const zero=clone(fem.examples.bar);zero.nodes.forEach(n=>{n.fx=0;n.fy=0;});
 zero.nodes[1].fixY=false;
 assert.equal(fem.inspectJSON(JSON.stringify(zero)).loadedDofCount,0);
 assert.throws(()=>fem.solveDocument(zero),/Unstable|under-constrained/);
 close(fem.solveDocument(fem.examples.bar).displacements[1].x,1e-5,1e-13);
 assert.throws(()=>fem.inspectJSON('{bad'),/Invalid truss JSON/);
});

test('inspectJSON counts disconnected truss components including isolated nodes without solving',()=>{
 const model=clone(fem.examples.bar);
 model.nodes.push({id:'C',x:4,y:0,fixX:true,fixY:true},
                  {id:'D',x:6,y:0,fixY:true},
                  {id:'E',x:8,y:2,fixX:true,fixY:true});
 model.members.push({id:'CD',a:'C',b:'D',E:200,area:1000});
 const preview=fem.inspectJSON(JSON.stringify(model));
 assert.equal(preview.nodeCount,5);
 assert.equal(preview.memberCount,2);
 assert.equal(preview.connectedComponentCount,3);
 assert.equal(fem.inspectJSON(JSON.stringify(fem.examples.bar)).connectedComponentCount,1);
 const legacy={nodes:model.nodes.map(n=>({...n,fx:(n.fx??0)*1000,fy:(n.fy??0)*1000})),
   members:model.members.map(m=>({id:m.id,a:m.a,b:m.b,E:m.E*1e9,A:m.area*1e-6}))};
 assert.equal(fem.inspectJSON(JSON.stringify(legacy)).connectedComponentCount,3);
 const connected=clone(model);
 connected.members.push({id:'BC',a:'B',b:'C',E:200,area:1000},
                        {id:'DE',a:'D',b:'E',E:200,area:1000});
 assert.equal(fem.inspectJSON(JSON.stringify(connected)).connectedComponentCount,1);
 assert.throws(()=>fem.inspectJSON('{bad'),/Invalid truss JSON/);
 close(fem.solve(fem.examples.bar).displacements[1].x,1e-5,1e-13);
});


test('inspectJSON exposes immutable per-member SI material metrics without solving',()=>{
 const triangle=fem.inspectJSON(fem.exportJSON(fem.examples.triangle));
 assert.deepEqual(triangle.memberMetrics.map(m=>[m.id,m.startNodeId,m.endNodeId]),
  [['AB','A','B'],['AC','A','C'],['BC','B','C']]);
 const lengths=[4,Math.hypot(2,3),Math.hypot(2,3)];
 triangle.memberMetrics.forEach((m,i)=>{
  close(m.length,lengths[i]);close(m.area,0.0012);close(m.volume,lengths[i]*0.0012);
  close(m.elasticModulus,210e9);close(m.axialStiffness,210e9*0.0012/lengths[i]);
  assert.ok(Object.isFrozen(m));
 });
 assert.ok(Object.isFrozen(triangle.memberMetrics));
 close(triangle.memberMetrics.reduce((sum,m)=>sum+m.length,0),triangle.totalMemberLength);
 close(triangle.memberMetrics.reduce((sum,m)=>sum+m.volume,0),triangle.totalMemberVolume);
 const legacy={nodes:fem.examples.triangle.nodes.map(n=>({...n,fx:n.fx*1000,fy:n.fy*1000})),
  members:fem.examples.triangle.members.map(m=>({id:m.id,a:m.a,b:m.b,E:m.E*1e9,A:m.area*1e-6}))};
 const imported=fem.inspectJSON(JSON.stringify(legacy));
 assert.equal(imported.inputUnits.system,'legacy-si');
 imported.memberMetrics.forEach((m,i)=>{
  close(m.length,triangle.memberMetrics[i].length);
  close(m.area,triangle.memberMetrics[i].area);
  close(m.volume,triangle.memberMetrics[i].volume);
  close(m.elasticModulus,triangle.memberMetrics[i].elasticModulus);
  close(m.axialStiffness,triangle.memberMetrics[i].axialStiffness);
 });
 assert.throws(()=>fem.inspectJSON('{bad'),/Invalid truss JSON/);
});

test('material schedule CSV exports validated per-member SI quantities without solving',()=>{
 const barCSV=fem.exportMaterialCSV(fem.examples.bar);
 const header='"Member ID","Start joint ID","End joint ID","Centreline length (m)","Cross-sectional area (m²)","Axial material volume (m³)","Elastic modulus (GPa)","Axial stiffness EA/L (kN/mm)","Density (kg/m³)","Member mass (kg)","Second moment of area I (mm⁴)","Effective length factor K (-)","Euler critical load Pcr (kN)"';
 assert.equal(barCSV,header+'\r\n"AB","A","B","2","0.001","0.002","200","100","","","","",""\r\n');
 assert.ok(barCSV.endsWith('\r\n'));
 assert.equal(barCSV.replace(/\r\n/g,'').includes('\n'),false);
 const triangleCSV=fem.exportMaterialCSV(fem.examples.triangle);
 const rows=triangleCSV.trimEnd().split('\r\n').map(line=>line.slice(1,-1).split('","'));
 assert.deepEqual(rows[0],['Member ID','Start joint ID','End joint ID','Centreline length (m)','Cross-sectional area (m²)','Axial material volume (m³)','Elastic modulus (GPa)','Axial stiffness EA/L (kN/mm)','Density (kg/m³)','Member mass (kg)','Second moment of area I (mm⁴)','Effective length factor K (-)','Euler critical load Pcr (kN)']);
 assert.equal(rows.length,4);
 const lengths=[4,Math.hypot(2,3),Math.hypot(2,3)];
 rows.slice(1).forEach((row,i)=>{
  close(Number(row[3]),lengths[i]);close(Number(row[4]),0.0012);close(Number(row[5]),lengths[i]*0.0012);
  close(Number(row[6]),210);close(Number(row[7]),210e9*0.0012/lengths[i]/1e6);
  assert.equal(row[8],'');assert.equal(row[9],'');
 });
 const legacy={nodes:fem.examples.bar.nodes.map(n=>({...n,fx:n.fx*1000,fy:n.fy*1000})),
  members:fem.examples.bar.members.map(m=>({id:m.id,a:m.a,b:m.b,E:m.E*1e9,A:m.area*1e-6}))};
 assert.equal(fem.exportMaterialCSV(legacy),barCSV,'legacy SI and Studio models must export identical physical schedules');
 const unstable=clone(fem.examples.bar);unstable.nodes[1].fixY=false;
 assert.equal(fem.exportMaterialCSV(unstable),barCSV,'a valid unstable model still has a material schedule');
 const invalid=clone(fem.examples.bar);invalid.members[0].area=0;
 assert.throws(()=>fem.exportMaterialCSV(invalid),/area must be positive/);
 assert.throws(()=>fem.exportMaterialCSV({nodes:[],members:[]}),/Use 2–80 nodes/);
});

test('optional member density produces SI mass estimates and rejects invalid or overflowing values',()=>{
 const bar=clone(fem.examples.bar);
 const unspecified=fem.inspectJSON(JSON.stringify(bar)).memberMetrics[0];
 assert.equal(unspecified.density,null);assert.equal(unspecified.mass,null);
 for(const blank of [undefined,null,'','   ']){
  const model=clone(bar);
  if(blank===undefined) delete model.members[0].density; else model.members[0].density=blank;
  const metric=fem.inspectJSON(JSON.stringify(model)).memberMetrics[0];
  assert.equal(metric.density,null);assert.equal(metric.mass,null);
 }
 const zero=clone(bar);zero.members[0].density=0;
 assert.equal(fem.inspectJSON(JSON.stringify(zero)).memberMetrics[0].mass,0);
 const dense=clone(bar);dense.members[0].density=7850;
 const preview=fem.inspectJSON(JSON.stringify(dense)),metric=preview.memberMetrics[0];
 close(metric.volume,0.002);close(metric.mass,15.7);assert.equal(metric.density,7850);
 assert.ok(Object.isFrozen(metric));assert.ok(Object.isFrozen(preview.memberMetrics));
 const triangle=clone(fem.examples.triangle);triangle.members.forEach(m=>m.density=7850);
 const trianglePreview=fem.inspectJSON(JSON.stringify(triangle));
 trianglePreview.memberMetrics.forEach(m=>close(m.mass,m.volume*7850));
 const legacy={nodes:bar.nodes.map(n=>({...n,fx:n.fx*1000,fy:n.fy*1000})),
  members:bar.members.map(m=>({id:m.id,a:m.a,b:m.b,E:m.E*1e9,A:m.area*1e-6,density:7850}))};
 const legacyMetric=fem.inspectJSON(JSON.stringify(legacy)).memberMetrics[0];
 close(legacyMetric.density,7850);close(legacyMetric.mass,metric.mass);
 const csvRows=fem.exportMaterialCSV(dense).trimEnd().split('\r\n').map(line=>line.slice(1,-1).split('\",\"'));
 assert.equal(csvRows[1][8],'7850');assert.equal(csvRows[1][9],'15.7');
 const blankRows=fem.exportMaterialCSV(bar).trimEnd().split('\r\n').map(line=>line.slice(1,-1).split('\",\"'));
 assert.equal(blankRows[1][8],'');assert.equal(blankRows[1][9],'');
 const unstable=clone(dense);unstable.nodes[1].fixY=false;
 close(fem.inspectJSON(JSON.stringify(unstable)).memberMetrics[0].mass,15.7);
 for(const invalid of [-1,NaN,Infinity,-Infinity,'not-a-number',true,{}]){
  const model=clone(bar);model.members[0].density=invalid;
  assert.throws(()=>fem.parseModel(model),invalid===-1?/density must be non-negative/:/finite number/);
 }
 const overflow=clone(bar);overflow.nodes[1].x=2000;overflow.members[0].density=Number.MAX_VALUE;
 assert.throws(()=>fem.parseModel(overflow),/mass.*finite number/);
 close(fem.solve(bar).displacements[1].x,1e-5,1e-13);
});

test('material CSV numeric cells avoid binary floating-point tails and retain sixteen significant digits',()=>{
 const dense=clone(fem.examples.bar);dense.members[0].density=7850;
 const csv=fem.exportMaterialCSV(dense);
 assert.ok(csv.includes(['"AB"','"A"','"B"','"2"','"0.001"','"0.002"','"200"','"100"','"7850"','"15.7"'].join(',')));
 const precise=clone(fem.examples.bar);precise.nodes[1].x=2/3;
 assert.ok(fem.exportMaterialCSV(precise).includes('"0.6666666666666666"'));
});

test('optional Euler buckling estimate uses SI units, validates I/K and remains independent of applied load',()=>{
 const bar=clone(fem.examples.bar);
 const baseline=fem.inspectJSON(JSON.stringify(bar)).memberMetrics[0];
 assert.equal(baseline.secondMoment,null);
 assert.equal(baseline.effectiveLengthFactor,null);
 assert.equal(baseline.eulerCriticalLoad,null);
 const pinned=clone(bar);pinned.members[0].I=1e6;pinned.members[0].K=1;
 const metric=fem.inspectJSON(JSON.stringify(pinned)).memberMetrics[0];
 const expected=Math.PI*Math.PI*200e9*1e-6/(2*2);
 close(metric.secondMoment,1e-6);assert.equal(metric.effectiveLengthFactor,1);
 close(metric.eulerCriticalLoad,expected,1e-12);
 assert.ok(Object.isFrozen(metric));
 const fixedEnd=clone(pinned);fixedEnd.members[0].K=2;
 close(fem.inspectJSON(JSON.stringify(fixedEnd)).memberMetrics[0].eulerCriticalLoad,expected/4,1e-12);
 const zeroLoad=clone(pinned);zeroLoad.nodes[1].fx=0;
 const tension=clone(pinned);tension.nodes[1].fx=1;
 close(fem.inspectJSON(JSON.stringify(zeroLoad)).memberMetrics[0].eulerCriticalLoad,expected,1e-12);
 close(fem.inspectJSON(JSON.stringify(tension)).memberMetrics[0].eulerCriticalLoad,expected,1e-12);
 const legacy={nodes:bar.nodes.map(n=>({...n,fx:n.fx*1000,fy:n.fy*1000})),
  members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001,I:1e-6,K:1}]};
 const legacyMetric=fem.inspectJSON(JSON.stringify(legacy)).memberMetrics[0];
 close(legacyMetric.secondMoment,1e-6);close(legacyMetric.eulerCriticalLoad,expected,1e-12);
 const rows=fem.exportMaterialCSV(pinned).trimEnd().split(String.fromCharCode(13)+String.fromCharCode(10)).map(line=>line.slice(1,-1).split('\",\"'));
 assert.deepEqual(rows[0].slice(-3),['Second moment of area I (mm⁴)','Effective length factor K (-)','Euler critical load Pcr (kN)']);
 assert.equal(rows[1][10],'1000000');assert.equal(rows[1][11],'1');
 close(Number(rows[1][12]),expected/1000,1e-12);
 for(const invalid of [0,-1,NaN,Infinity,-Infinity,'not-a-number',true,Number.MIN_VALUE]){
  const model=clone(pinned);model.members[0].I=invalid;
  assert.throws(()=>fem.parseModel(model),invalid===0||invalid===-1||invalid===Number.MIN_VALUE?/I must be positive/:/finite number/);
 }
 for(const invalid of [0,-1,NaN,Infinity,-Infinity,'not-a-number',true]){
  const model=clone(pinned);model.members[0].K=invalid;
  assert.throws(()=>fem.parseModel(model),invalid===0||invalid===-1?/K must be positive/:/finite number/);
 }
 const onlyI=clone(pinned);delete onlyI.members[0].K;
 const onlyIMetric=fem.inspectJSON(JSON.stringify(onlyI)).memberMetrics[0];
 close(onlyIMetric.secondMoment,1e-6);assert.equal(onlyIMetric.effectiveLengthFactor,null);assert.equal(onlyIMetric.eulerCriticalLoad,null);
 const onlyK=clone(pinned);delete onlyK.members[0].I;
 const onlyKMetric=fem.inspectJSON(JSON.stringify(onlyK)).memberMetrics[0];
 assert.equal(onlyKMetric.secondMoment,null);assert.equal(onlyKMetric.effectiveLengthFactor,1);assert.equal(onlyKMetric.eulerCriticalLoad,null);
 const overflow=clone(pinned);overflow.members[0].I=Number.MAX_VALUE;
 assert.throws(()=>fem.parseModel(overflow),/Euler buckling numerator.*finite number/);
 const shortK=clone(pinned);shortK.members[0].K=Number.MIN_VALUE;
 assert.throws(()=>fem.parseModel(shortK),/effective buckling length squared underflow/);
 close(fem.solve(bar).displacements[1].x,1e-5,1e-13);
});


test('post-solve Euler comparison reports compression-only utilization and load ratio',()=>{
 const bar=clone(fem.examples.bar);bar.members[0].I=1e6;bar.members[0].K=1;
 const pcr=Math.PI*Math.PI*200e9*1e-6/(2*2);
 const tension=fem.solve(bar).members[0];
 assert.equal(tension.type,'Tension');assert.equal(tension.compressionDemand,0);
 assert.equal(tension.eulerUtilization,null);assert.equal(tension.eulerLoadRatio,null);
 assert.equal(tension.eulerAssessment,'Tension — not applicable');
 const zero=clone(bar);zero.nodes[1].fx=0;
 const unloaded=fem.solve(zero).members[0];
 assert.equal(unloaded.type,'Zero');assert.equal(unloaded.compressionDemand,0);
 assert.equal(unloaded.eulerUtilization,null);assert.equal(unloaded.eulerLoadRatio,null);
 assert.equal(unloaded.eulerAssessment,'No compression demand');
 const compression=clone(bar);compression.nodes[1].fx=-1;
 const below=fem.solve(compression).members[0];
 close(below.force,-1000);close(below.compressionDemand,1000);
 close(below.eulerUtilization,1000/pcr,1e-12);close(below.eulerLoadRatio,pcr/1000,1e-12);
 assert.equal(below.eulerAssessment,'Below ideal Euler load');
 const above=clone(compression);above.nodes[1].fx=-600;
 const exceeded=fem.solve(above).members[0];
 assert.ok(exceeded.eulerUtilization>1);assert.ok(exceeded.eulerLoadRatio<1);
 assert.equal(exceeded.eulerAssessment,'At/above ideal Euler load');
 const noProperties=clone(compression);delete noProperties.members[0].I;delete noProperties.members[0].K;
 const unassessed=fem.solve(noProperties).members[0];
 assert.equal(unassessed.eulerUtilization,null);assert.equal(unassessed.eulerLoadRatio,null);
 assert.equal(unassessed.eulerAssessment,'Not assessed (I/K missing)');
 close(fem.solve(fem.examples.bar).displacements[1].x,1e-5,1e-13);
});


test('solid and concentric hollow section helpers return validated area and centroidal principal moments in mm units',()=>{
 const rectangle=fem.sectionProperties('rectangle',{width:'40',height:'60'});
 assert.deepEqual(rectangle.centroid,{x:20,y:30});
 assert.ok(Object.isFrozen(rectangle.centroid));
 assert.equal(rectangle.area,2400);
 assert.equal(rectangle.secondMoment,720000);
 assert.equal(rectangle.secondMomentPerpendicular,320000);
 assert.equal(rectangle.sectionModulusX,24000);
 assert.equal(rectangle.sectionModulusY,16000);
 assert.equal(rectangle.extremeFiberDistanceAboutX,30);
 assert.equal(rectangle.extremeFiberDistanceAboutY,20);
 close(rectangle.radiusOfGyrationX,Math.sqrt(300),1e-12);
 close(rectangle.radiusOfGyrationY,Math.sqrt(400/3),1e-12);
 assert.equal(rectangle.axis,'centroidal axis parallel to width');
 assert.equal(rectangle.perpendicularAxis,'centroidal axis parallel to depth');
 assert.ok(Object.isFrozen(rectangle));
 const circle=fem.sectionProperties('solid-circle',{diameter:40});
 assert.deepEqual(circle.centroid,{x:20,y:20});
 assert.ok(Object.isFrozen(circle.centroid));
 close(circle.area,400*Math.PI,1e-12);
 close(circle.secondMoment,40000*Math.PI,1e-12);
 assert.equal(circle.secondMomentPerpendicular,circle.secondMoment);
 close(circle.sectionModulusX,2000*Math.PI,1e-10);
 close(circle.sectionModulusY,2000*Math.PI,1e-10);
 assert.equal(circle.radiusOfGyrationX,10);
 assert.equal(circle.radiusOfGyrationY,10);
 assert.equal(circle.extremeFiberDistanceAboutX,20);
 assert.equal(circle.extremeFiberDistanceAboutY,20);
 assert.equal(circle.axis,'centroidal diameter axis');
 assert.ok(Object.isFrozen(circle));
 const hollowRectangle=fem.sectionProperties('hollow-rectangle',{width:100,height:80,innerWidth:80,innerHeight:60});
 assert.deepEqual(hollowRectangle.centroid,{x:50,y:40});
 assert.ok(Object.isFrozen(hollowRectangle.centroid));
 assert.equal(hollowRectangle.area,3200);
 close(hollowRectangle.secondMoment,2826666.6666666665,1e-7);
 close(hollowRectangle.secondMomentPerpendicular,4106666.666666667,1e-7);
 close(hollowRectangle.sectionModulusX,70666.66666666666,1e-8);
 close(hollowRectangle.sectionModulusY,82133.33333333333,1e-8);
 close(hollowRectangle.radiusOfGyrationX,29.720924166878344,1e-12);
 close(hollowRectangle.radiusOfGyrationY,35.823642100341125,1e-12);
 assert.equal(hollowRectangle.extremeFiberDistanceAboutX,40);
 assert.equal(hollowRectangle.extremeFiberDistanceAboutY,50);
 assert.ok(Object.isFrozen(hollowRectangle));
 const hollowCircle=fem.sectionProperties('hollow-circle',{diameter:100,innerDiameter:80});
 assert.deepEqual(hollowCircle.centroid,{x:50,y:50});
 assert.ok(Object.isFrozen(hollowCircle.centroid));
 close(hollowCircle.area,900*Math.PI,1e-10);
 close(hollowCircle.secondMoment,922500*Math.PI,1e-7);
 assert.equal(hollowCircle.secondMomentPerpendicular,hollowCircle.secondMoment);
 close(hollowCircle.sectionModulusX,18450*Math.PI,1e-8);
 close(hollowCircle.sectionModulusY,18450*Math.PI,1e-8);
 close(hollowCircle.radiusOfGyrationX,Math.sqrt(1025),1e-12);
 close(hollowCircle.radiusOfGyrationY,Math.sqrt(1025),1e-12);
 assert.equal(hollowCircle.extremeFiberDistanceAboutX,50);
 assert.equal(hollowCircle.extremeFiberDistanceAboutY,50);
 assert.ok(Object.isFrozen(hollowCircle));
 for(const properties of [rectangle,circle,hollowRectangle,hollowCircle]){
  for(const key of ['sectionModulusX','sectionModulusY','radiusOfGyrationX','radiusOfGyrationY','extremeFiberDistanceAboutX','extremeFiberDistanceAboutY']){
   assert.ok(Number.isFinite(properties[key])&&properties[key]>0,properties.shape+' '+key+' must be finite and positive');
  }
 }
 for(const invalid of [0,-1,NaN,Infinity,-Infinity,'not-a-number',true,{}]){
  assert.throws(()=>fem.sectionProperties('rectangle',{width:invalid,height:60}));
  assert.throws(()=>fem.sectionProperties('rectangle',{width:40,height:invalid}));
  assert.throws(()=>fem.sectionProperties('solid-circle',{diameter:invalid}));
  assert.throws(()=>fem.sectionProperties('hollow-rectangle',{width:100,height:80,innerWidth:invalid,innerHeight:60}));
  assert.throws(()=>fem.sectionProperties('hollow-circle',{diameter:100,innerDiameter:invalid}));
 }
 for(const dimensions of [
  {width:100,height:80,innerWidth:0,innerHeight:60},
  {width:100,height:80,innerWidth:100,innerHeight:60},
  {width:100,height:80,innerWidth:80,innerHeight:80},
  {width:100,height:80,innerWidth:80,innerHeight:90},
  {width:100,height:80,innerWidth:80,innerHeight:-1}
 ]) assert.throws(()=>fem.sectionProperties('hollow-rectangle',dimensions));
 for(const dimensions of [
  {diameter:100,innerDiameter:0},
  {diameter:100,innerDiameter:100},
  {diameter:100,innerDiameter:101},
  {diameter:100,innerDiameter:-1}
 ]) assert.throws(()=>fem.sectionProperties('hollow-circle',dimensions));
 assert.throws(()=>fem.sectionProperties('rectangle',{width:1e-200,height:1e-200}),/area underflow/);
 assert.throws(()=>fem.sectionProperties('rectangle',{width:1e308,height:2}),/finite number/);
 assert.throws(()=>fem.sectionProperties('solid-circle',{diameter:1e100}),/finite number/);
 assert.throws(()=>fem.sectionProperties('solid-circle',{diameter:1e-100}),/second moment underflow/);
 assert.throws(()=>fem.sectionProperties('hollow-rectangle',{width:1e308,height:2,innerWidth:1,innerHeight:1}),/finite number/);
 assert.throws(()=>fem.sectionProperties('hollow-rectangle',{width:1e-200,height:1e-200,innerWidth:5e-201,innerHeight:5e-201}),/underflow/);
 assert.throws(()=>fem.sectionProperties('hollow-circle',{diameter:1e100,innerDiameter:1}),/finite number/);
 assert.throws(()=>fem.sectionProperties('hollow-circle',{diameter:1e-100,innerDiameter:5e-101}),/underflow/);
 assert.throws(()=>fem.sectionProperties('hollow-square',{width:100,height:80,innerWidth:80,innerHeight:60}),/Section shape/);
 assert.throws(()=>fem.sectionProperties('rectangle',[]),/dimensions must be an object/);
 close(fem.solve(fem.examples.bar).displacements[1].x,1e-5,1e-13);
});

test('open channel and I sections use composite rectangles and the parallel-axis theorem',()=>{
 const channel=fem.sectionProperties('channel',{width:100,height:80,webThickness:10,flangeThickness:8});
 close(channel.area,2240,1e-12);
 close(channel.centroid.x,37.142857142857146,1e-12);
 close(channel.centroid.y,40,1e-12);
 close(channel.secondMoment,2300586.6666666665,1e-7);
 close(channel.secondMomentPerpendicular,2264380.9523809524,1e-7);
 close(channel.sectionModulusX,57514.666666666664,1e-8);
 close(channel.sectionModulusY,36024.242424242424,1e-8);
 close(channel.radiusOfGyrationX,32.04758366940664,1e-12);
 close(channel.radiusOfGyrationY,31.794407585949713,1e-12);
 assert.equal(channel.extremeFiberDistanceAboutX,40);
 close(channel.extremeFiberDistanceAboutY,62.857142857142854,1e-12);
 const iSection=fem.sectionProperties('i-section',{width:100,height:80,webThickness:10,flangeThickness:8});
 close(iSection.area,2240,1e-12);
 close(iSection.centroid.x,50,1e-12);
 close(iSection.centroid.y,40,1e-12);
 close(iSection.secondMoment,2300586.6666666665,1e-7);
 close(iSection.secondMomentPerpendicular,1338666.6666666665,1e-7);
 close(iSection.sectionModulusX,57514.666666666664,1e-8);
 close(iSection.sectionModulusY,26773.33333333333,1e-8);
 close(iSection.radiusOfGyrationX,32.04758366940664,1e-12);
 close(iSection.radiusOfGyrationY,24.44624812970382,1e-12);
 assert.equal(iSection.extremeFiberDistanceAboutX,40);
 assert.equal(iSection.extremeFiberDistanceAboutY,50);
 for(const properties of [channel,iSection]){
  for(const key of ['sectionModulusX','sectionModulusY','radiusOfGyrationX','radiusOfGyrationY','extremeFiberDistanceAboutX','extremeFiberDistanceAboutY']){
   assert.ok(Number.isFinite(properties[key])&&properties[key]>0,properties.shape+' '+key+' must be finite and positive');
  }
 }
 assert.ok(Object.isFrozen(channel));assert.ok(Object.isFrozen(channel.centroid));
 assert.ok(Object.isFrozen(iSection));assert.ok(Object.isFrozen(iSection.centroid));
 for(const invalid of [
  {width:0,height:80,webThickness:10,flangeThickness:8},
  {width:100,height:0,webThickness:10,flangeThickness:8},
  {width:100,height:80,webThickness:0,flangeThickness:8},
  {width:100,height:80,webThickness:100,flangeThickness:8},
  {width:100,height:80,webThickness:10,flangeThickness:0},
  {width:100,height:80,webThickness:10,flangeThickness:40},
  {width:100,height:80,webThickness:10,flangeThickness:41},
  {width:100,height:80,webThickness:-1,flangeThickness:8}
 ]) {
  assert.throws(()=>fem.sectionProperties('channel',invalid));
  assert.throws(()=>fem.sectionProperties('i-section',invalid));
 }
 for(const invalid of [NaN,Infinity,-Infinity,'bad',true,{}]) {
  assert.throws(()=>fem.sectionProperties('channel',{width:100,height:80,webThickness:invalid,flangeThickness:8}));
  assert.throws(()=>fem.sectionProperties('i-section',{width:100,height:80,webThickness:10,flangeThickness:invalid}));
 }
 assert.throws(()=>fem.sectionProperties('channel',{width:1e308,height:2,webThickness:1,flangeThickness:0.1}),/finite number/);
 assert.throws(()=>fem.sectionProperties('i-section',{width:1e-200,height:1e-200,webThickness:5e-201,flangeThickness:1e-201}),/underflow/);
 assert.throws(()=>fem.sectionProperties('channel',[]),/dimensions must be an object/);
 close(fem.solve(fem.examples.bar).displacements[1].x,1e-5,1e-13);
});


test('L-angle section returns centroidal and principal properties with validated dimensions',()=>{
 const angle=fem.sectionProperties('l-angle',{width:100,height:80,thickness:10});
 close(angle.area,1700,1e-12);
 close(angle.centroid.x,31.470588235294116,1e-12);
 close(angle.centroid.y,21.470588235294116,1e-12);
 close(angle.secondMoment,952990.1960784313,1e-7);
 close(angle.secondMomentPerpendicular,1672990.1960784313,1e-7);
 close(angle.productOfInertia,-741176.4705882354,1e-7);
 close(angle.principalMomentMajor,2136969.904902401,1e-7);
 close(angle.principalMomentMinor,489010.48725446186,1e-7);
 close(angle.principalAxisAngleDegrees,57.953253999757194,1e-10);
 close(angle.principalMomentMajor+angle.principalMomentMinor,angle.secondMoment+angle.secondMomentPerpendicular,1e-7);
 const theta=angle.principalAxisAngleDegrees*Math.PI/180;
 close(angle.productOfInertia*Math.cos(2*theta)+(angle.secondMoment-angle.secondMomentPerpendicular)*Math.sin(2*theta)/2,0,1e-7);
 for(const key of ['sectionModulusX','sectionModulusY','radiusOfGyrationX','radiusOfGyrationY','extremeFiberDistanceAboutX','extremeFiberDistanceAboutY'])
  assert.ok(Number.isFinite(angle[key])&&angle[key]>0,'L-angle '+key+' must be finite and positive');
 assert.ok(Object.isFrozen(angle));assert.ok(Object.isFrozen(angle.centroid));
 for(const invalid of [
  {width:0,height:80,thickness:10},{width:100,height:0,thickness:10},{width:100,height:80,thickness:0},
  {width:100,height:80,thickness:100},{width:100,height:80,thickness:80},{width:100,height:80,thickness:-1}
 ]) assert.throws(()=>fem.sectionProperties('l-angle',invalid));
 for(const invalid of [NaN,Infinity,-Infinity,'bad',true,{}])
  assert.throws(()=>fem.sectionProperties('l-angle',{width:100,height:80,thickness:invalid}));
 assert.throws(()=>fem.sectionProperties('l-angle',{width:1e308,height:80,thickness:10}),/finite number/);
 assert.throws(()=>fem.sectionProperties('l-angle',{width:1e-200,height:1e-200,thickness:5e-201}),/underflow/);
 assert.throws(()=>fem.sectionProperties('l-angle',[]),/dimensions must be an object/);
});


test('L-angle asymmetric and near-limit valid references preserve principal invariants',()=>{
 const references=[
  {dimensions:{width:120,height:70,thickness:12},expected:{area:2136,cx:42.40449438202247,cy:17.40449438202247,ixx:787178.5168539326,iyy:3104578.5168539323,ixy:-886813.4831460675,i1:3404996.004888964,i2:486761.02881890116,angle:71.2856436104474}},
  {dimensions:{width:120,height:70,thickness:69.9},expected:{area:8394.99,cx:59.97914238134888,cy:34.97914238134888,ixx:3423876.6161414036,iyy:10072828.691141404,ixy:-6123.379683596653,i1:10072834.330488255,i2:3423870.976794552,angle:89.94723327653608}}
 ];
 for(const {dimensions,expected} of references){
  const section=fem.sectionProperties('l-angle',dimensions);
  close(section.area,expected.area,1e-8); close(section.centroid.x,expected.cx,1e-9); close(section.centroid.y,expected.cy,1e-9);
  close(section.secondMoment,expected.ixx,1e-6); close(section.secondMomentPerpendicular,expected.iyy,1e-6);
  close(section.productOfInertia,expected.ixy,1e-6); close(section.principalMomentMajor,expected.i1,1e-6);
  close(section.principalMomentMinor,expected.i2,1e-6); close(section.principalAxisAngleDegrees,expected.angle,1e-9);
  close(section.principalMomentMajor+section.principalMomentMinor,section.secondMoment+section.secondMomentPerpendicular,1e-6);
  const theta=section.principalAxisAngleDegrees*Math.PI/180;
  close(section.productOfInertia*Math.cos(2*theta)+(section.secondMoment-section.secondMomentPerpendicular)*Math.sin(2*theta)/2,0,1e-6);
  const determinantScale=Math.max(1,Math.abs(section.secondMoment*section.secondMomentPerpendicular));
  assert.ok(Math.abs(section.principalMomentMajor*section.principalMomentMinor-(section.secondMoment*section.secondMomentPerpendicular-section.productOfInertia**2))<=1e-12*determinantScale);
  assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
 }
 assert.throws(()=>fem.sectionProperties('l-angle',{width:120,height:70,thickness:70}),/t < min\(B,H\)/);
});

test('legacy TrussStudio.solve retains its original member result shape',()=>{
 const result=globalThis.TrussStudio.solve(globalThis.TrussStudio.example);
 assert.deepEqual(Object.keys(result.members[0]).sort(),['force','id','strain','stress']);
 assert.ok(result.members.every(m=>Number.isFinite(m.force)&&Number.isFinite(m.stress)&&Number.isFinite(m.strain)));
});


test('legacy SI JSON import preserves optional density, second moment and effective-length factor',()=>{
 const legacy=globalThis.TrussStudio.example;
 for(const member of legacy.members){member.density=7850;member.I=1e-6;member.K=1;}
 const json=JSON.stringify(legacy);
 const imported=fem.importJSON(json);
 assert.equal(fem.describeUnits(imported).system,'legacy-si');
 const normalized=fem.fromLegacy(imported);
 assert.equal(normalized.members[0].E,200);
 assert.equal(normalized.members[0].area,1000);
 assert.equal(normalized.members[0].density,7850);
 assert.equal(normalized.members[0].I,1000000);
 assert.equal(normalized.members[0].K,1);
 const first=fem.inspectJSON(json).memberMetrics[0];
 close(first.mass,15.7,1e-12);
 close(first.secondMoment,1e-6,1e-12);
 close(first.effectiveLengthFactor,1,1e-12);
 close(first.eulerCriticalLoad,493480.22005446785,1e-12);
 const result=fem.solve(normalized);
 assert.ok(result.residual<1e-12);
 assert.ok(Number.isFinite(result.energyError));
});
 
test('legacy SI optional properties normalize null and blank values while retaining zero density and independent I/K',()=>{
 const template=globalThis.TrussStudio.example;
 const absent=[null,'',' \t '];
 for(const value of absent){
  const legacy=clone(template);
  for(const member of legacy.members){member.density=value;member.I=value;member.K=value;}
  const json=JSON.stringify(legacy);
  const normalized=fem.fromLegacy(fem.importJSON(json));
  for(const member of normalized.members){
   assert.equal(Object.prototype.hasOwnProperty.call(member,'density'),false);
   assert.equal(Object.prototype.hasOwnProperty.call(member,'I'),false);
   assert.equal(Object.prototype.hasOwnProperty.call(member,'K'),false);
  }
  for(const metric of fem.inspectJSON(json).memberMetrics){
   assert.equal(metric.density,null);assert.equal(metric.mass,null);
   assert.equal(metric.secondMoment,null);assert.equal(metric.effectiveLengthFactor,null);
   assert.equal(metric.eulerCriticalLoad,null);
  }
 }
 const zero=clone(template);
 for(const member of zero.members)member.density=0;
 const normalizedZero=fem.fromLegacy(fem.importJSON(JSON.stringify(zero)));
 assert.equal(normalizedZero.members[0].density,0);
 assert.equal(fem.inspectJSON(JSON.stringify(zero)).memberMetrics[0].mass,0);
 const onlyI=clone(template);
 for(const member of onlyI.members){member.density=' ';member.I=1e-6;member.K=' \t ';}
 const normalizedI=fem.fromLegacy(fem.importJSON(JSON.stringify(onlyI)));
 assert.equal(normalizedI.members[0].I,1000000);
 assert.equal(Object.prototype.hasOwnProperty.call(normalizedI.members[0],'K'),false);
 const metricI=fem.inspectJSON(JSON.stringify(onlyI)).memberMetrics[0];
 assert.equal(metricI.secondMoment,1e-6);assert.equal(metricI.effectiveLengthFactor,null);
 assert.equal(metricI.eulerCriticalLoad,null);assert.equal(metricI.mass,null);
 const onlyK=clone(template);
 for(const member of onlyK.members){member.density=null;member.I=null;member.K=1;}
 const normalizedK=fem.fromLegacy(fem.importJSON(JSON.stringify(onlyK)));
 assert.equal(Object.prototype.hasOwnProperty.call(normalizedK.members[0],'I'),false);
 assert.equal(normalizedK.members[0].K,1);
 const metricK=fem.inspectJSON(JSON.stringify(onlyK)).memberMetrics[0];
 assert.equal(metricK.secondMoment,null);assert.equal(metricK.effectiveLengthFactor,1);
 assert.equal(metricK.eulerCriticalLoad,null);assert.equal(metricK.mass,null);
});

