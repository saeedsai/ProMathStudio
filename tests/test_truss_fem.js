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


test('truss JSON unit descriptors distinguish Studio and legacy SI without magnitude guessing',()=>{
 const studio=clone(fem.examples.bar);
 assert.deepEqual(fem.describeUnits(studio),{system:'studio',coordinates:'m',forces:'kN',modulus:'GPa',area:'mm²'});
 assert.ok(Object.isFrozen(fem.describeUnits(studio)));
 const legacy={nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true,fx:1000}],members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001}]};
 assert.deepEqual(fem.describeUnits(fem.importJSON(fem.exportJSON(legacy))),{system:'legacy-si',coordinates:'m',forces:'N',modulus:'Pa',area:'m²'});
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
