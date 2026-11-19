/* Analytical reference, equilibrium, energy and invalid-mechanism regressions. */
'use strict';
const assert = require('node:assert/strict');
const test = require('node:test');
const fem = require('../tools/truss-fem.js');
const close = (got,want,rel=1e-9) => assert.ok(Math.abs(got-want)<=rel*Math.max(1,Math.abs(want)),String(got)+' != '+String(want));
const clone = data => JSON.parse(JSON.stringify(data));

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
