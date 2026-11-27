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

test('numeric strings accept decimal/scientific syntax but reject JavaScript radix coercion',()=>{
 const valid=clone(fem.examples.bar);
 valid.nodes[1].fx=' 1e3 ';
 valid.members[0].area='1.0e3';
 close(fem.solve(valid).displacements[1].x,0.01,1e-13);
 for(const invalid of ['0x10','0b10','0o10']){
  assert.ok(Number.isFinite(Number(invalid)),invalid+' must reproduce JavaScript radix coercion');
  const model=clone(fem.examples.bar);
  model.nodes[1].fx=invalid;
  assert.throws(()=>fem.parseModel(model),/finite number/);
  assert.throws(()=>fem.solve(model),/finite number/);
  assert.throws(()=>fem.sectionProperties('rectangle',{width:invalid,height:2}),/finite number/);
 }
 for(const decimal of ['+1','.5','1.','1e3','1E-3',' 2.5e+2 ']){
  const section=fem.sectionProperties('rectangle',{width:decimal,height:'2'});
  assert.ok(Number.isFinite(section.area)&&section.area>0,decimal+' must remain a valid decimal string');
 }
 const boundaryPaddedDecimal=' '.repeat(255)+'1';
 const boundaryModel=clone(fem.examples.bar);boundaryModel.nodes[1].fx=boundaryPaddedDecimal;
 assert.equal(boundaryPaddedDecimal.length,256);
 assert.equal(Number(boundaryPaddedDecimal),1);
 assert.doesNotThrow(()=>fem.parseModel(boundaryModel));
 assert.ok(fem.solve(boundaryModel).displacements[1].x>0);
 assert.ok(fem.sectionProperties('rectangle',{width:boundaryPaddedDecimal,height:2}).area>0);
 for(const oversized of ['0'.repeat(256)+'1',' '.repeat(256)+'1']){
  const oversizedModel=clone(fem.examples.bar);oversizedModel.nodes[1].fx=oversized;
  assert.equal(oversized.length,257);
  assert.equal(Number(oversized),1,'fixture must otherwise coerce to a finite Number');
  assert.throws(()=>fem.parseModel(oversizedModel),/finite number/);
  assert.throws(()=>fem.solve(oversizedModel),/finite number/);
  assert.throws(()=>fem.sectionProperties('rectangle',{width:oversized,height:2}),/finite number/);
 }
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


test('axial stiffness preserves representable EA/L when the intermediate product overflows or underflows',()=>{
 // Synthetic binary64 range fixtures, not physical engineering design dimensions.
 const overflowModel={nodes:[{id:'A',x:0,y:0},{id:'B',x:1e308,y:0}],
  members:[{id:'AB',a:'A',b:'B',E:1e299,area:1e308}]};
 const overflowE=1e299*1e9,overflowA=1e308*1e-6;
 assert.equal(overflowE*overflowA,Infinity,'the former E*A intermediate must overflow');
 const overflowExpected=Number('9.99999999999999885958866505692717215321468788319296420214711529659623043742459952401017773115158026984853220263372612120e301');
 const overflowMember=fem.parseModel(overflowModel).members[0];
 assert.equal(overflowMember.stiffness,overflowExpected,'EA/L must match the exact-binary64 Decimal reference');
 assert.equal(overflowMember.L,1e308);
 const underflowModel={nodes:[{id:'A',x:0,y:0},{id:'B',x:2e-12,y:0}],
  members:[{id:'AB',a:'A',b:'B',E:1e-16,area:5e-315}]};
 const underflowE=1e-16*1e9,underflowA=5e-315*1e-6;
 assert.equal(underflowE*underflowA,0,'the former E*A intermediate must underflow to zero');
 const underflowExpected=Number('2.49997216795670745068779824030659627302515457676733811374660615827877680162392969010589166580326478124861920201213291582e-316');
 const underflowMember=fem.parseModel(underflowModel).members[0];
 assert.equal(underflowMember.stiffness,underflowExpected,'EA/L must retain the representable subnormal result');
 assert.ok(underflowMember.stiffness>0&&Number.isFinite(underflowMember.stiffness));
 const trulyOverflowing={...overflowModel,nodes:[overflowModel.nodes[0],{...overflowModel.nodes[1],x:2e-12}]};
 assert.throws(()=>fem.parseModel(trulyOverflowing),/stiffness overflow/);
 assert.equal(fem.parseModel(fem.examples.bar).members[0].stiffness,1e8,
  'ordinary member stiffness must retain the existing direct calculation');
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


test('inspectJSON preserves finite signed resultants after overflowing intermediate sums',()=>{
 const horizontal=clone(fem.examples.bar);
 horizontal.nodes.forEach(n=>{n.fx=0;n.fy=0;});
 horizontal.nodes.push({id:'C',x:1,y:0,fixX:true,fixY:true});
 horizontal.nodes[0].fx=1e305;horizontal.nodes[1].fx=1e305;horizontal.nodes[2].fx=-1e305;
 assert.equal((1e308+1e308)-1e308,Infinity);
 const horizontalPreview=fem.inspectJSON(JSON.stringify(horizontal));
 assert.equal(horizontalPreview.appliedForce.x,1e308);
 assert.equal(horizontalPreview.appliedForce.y,0);

 const vertical=clone(fem.examples.bar);
 vertical.nodes.forEach(n=>{n.fx=0;n.fy=0;});
 vertical.nodes[1].x=0;vertical.nodes[1].y=2;
 vertical.nodes.push({id:'C',x:0,y:1,fixX:true,fixY:true});
 vertical.nodes[0].fy=1e305;vertical.nodes[1].fy=1e305;vertical.nodes[2].fy=-1e305;
 const verticalPreview=fem.inspectJSON(JSON.stringify(vertical));
 assert.equal(verticalPreview.appliedForce.y,1e308);
 assert.equal(verticalPreview.appliedMoment,0);

 const residual=clone(fem.examples.bar);
 residual.nodes.forEach(n=>{n.fx=0;n.fy=0;});
 residual.nodes.push({id:'C',x:1,y:0,fixX:true,fixY:true});
 residual.nodes[0].fx=1e305;residual.nodes[1].fx=Number.MIN_VALUE;residual.nodes[2].fx=-1e305;
 assert.equal((1e308+(Number.MIN_VALUE*1000))-1e308,0);
 assert.equal(fem.inspectJSON(JSON.stringify(residual)).appliedForce.x,Number.MIN_VALUE*1000);

 const subnormalRatio=clone(fem.examples.bar);
 subnormalRatio.nodes.forEach(n=>{n.fx=0;n.fy=0;});
 subnormalRatio.nodes.push({id:'C',x:1,y:0,fixX:true,fixY:true});
 subnormalRatio.nodes[0].fx=1e305;
 subnormalRatio.nodes[1].fx=1e-13;
 subnormalRatio.nodes[2].fx=-1e305;
 assert.equal((1e308+1e-10)-1e308,0);
 assert.equal(fem.inspectJSON(JSON.stringify(subnormalRatio)).appliedForce.x,1e-10);

 const moment=clone(fem.examples.bar);
 moment.nodes.forEach(n=>{n.fx=0;n.fy=0;});
 moment.nodes[0].y=1;moment.nodes[0].fx=-1e305;moment.nodes[1].fy=5e304;
 moment.nodes.push({id:'C',x:1,y:0,fixX:true,fixY:true,fx:0,fy:-1e305});
 const naiveMoment=moment.nodes.reduce((sum,n)=>sum+n.x*(n.fy*1000)-n.y*(n.fx*1000),0);
 assert.equal(naiveMoment,Infinity);
 const momentPreview=fem.inspectJSON(JSON.stringify(moment));
 assert.equal(momentPreview.appliedMoment,1e308);
 assert.equal(momentPreview.appliedForce.x,-1e308);
 assert.equal(momentPreview.appliedForce.y,-5e307);

 const overflow=clone(fem.examples.bar);
 overflow.nodes[0].fx=1e305;overflow.nodes[1].fx=1e305;
 assert.throws(()=>fem.inspectJSON(JSON.stringify(overflow)),/Applied force x.*finite number/);
});

test('solve force-balance diagnostic preserves finite equilibrium after overflowing partial sums',()=>{
 const model=clone(fem.examples.triangle);
 model.nodes.forEach(n=>{n.fx=0;n.fy=0;n.fixX=true;n.fixY=true;});
 model.nodes[2].fixY=false;
 model.nodes[0].fx=1e305;
 model.nodes[1].fx=1e305;
 model.nodes[2].fx=-1e305;
 const result=fem.solve(model);
 const naiveApplied=model.nodes.reduce((sum,node)=>sum+node.fx*1000,0);
 const naiveReactions=result.reactions.reduce((sum,reaction)=>sum+reaction.rx,0);
 assert.equal(Number.isFinite(naiveApplied),false);
 assert.equal(Number.isFinite(naiveReactions),false);
 assert.ok(Number.isNaN(naiveApplied+naiveReactions));
 assert.deepEqual(result.forceBalance,{x:0,y:0});
});


test('support reactions retain a small residual between large cancelling member forces',()=>{
 // Synthetic binary64 stress fixture, not a physical design model.
 const model={
  nodes:[
   {id:'A',x:0,y:0,fixX:true,fixY:true},
   {id:'B',x:1,y:0,fixY:true,fx:0.001},
   {id:'C',x:1,y:0,fixY:true,fx:1e13},
   {id:'D',x:1,y:0,fixY:true,fx:-1e13}
  ],
  members:[
   {id:'AB',a:'A',b:'B',E:1e14,area:1000},
   {id:'AC',a:'A',b:'C',E:1e14,area:1000},
   {id:'AD',a:'A',b:'D',E:1e14,area:1000}
  ]
 };
 const result=fem.solve(model);
 const stiffness=fem.parseModel(model).members[0].stiffness;
 const ux=id=>result.displacements.find(node=>node.id===id).x;
 const naiveReaction=['B','C','D'].reduce((sum,id)=>sum-stiffness*ux(id),0);
 assert.equal(stiffness,1e20);
 assert.equal(naiveReaction,0,'the fixture must reproduce order-dependent cancellation');
 assert.equal(result.reactions.find(reaction=>reaction.id==='A').rx,-1);
 assert.equal(result.forceBalance.x,0);
 assert.ok(result.residual<1e-12);
 assert.ok(result.energyError<1e-12);
});

test('mixed-sign resultants retain exact binary64 precision across scale groups',()=>{
 const model=clone(fem.examples.bar);
 const nodes=[
  {id:'A',x:0,y:1,fixX:true,fixY:true,fx:1e305,fy:0},
  {id:'B',x:2,y:1,fixX:true,fixY:true,fx:-1e305,fy:0},
  ...Array.from({length:35},(_,i)=>({id:'P'+i,x:0,y:1,fx:0.0023,fy:0})),
  ...Array.from({length:40},(_,i)=>({id:'N'+i,x:0,y:1,fx:-0.002,fy:0})),
  {id:'C',x:0,y:1,fx:-0.0005,fy:0},
  {id:'D',x:0,y:1,fx:1e-13,fy:0}
 ];
 model.nodes=nodes;
 const preview=fem.inspectJSON(JSON.stringify(model));
 const expected=9.99937827510621e-11;
 const naive=nodes.reduce((sum,node)=>sum+node.fx*1000,0);
 assert.equal(nodes.length,79);
 assert.equal(preview.appliedForce.x,expected);
 assert.equal(preview.appliedMoment,-expected);
 assert.ok(Math.abs(naive-expected)>1e-14,
  'the sequential binary64 reduction must reproduce the lost mixed-scale residual');
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



test('inspectJSON retains sub-ULP contributions in aggregate member length and volume',()=>{
 const nodes=[
  {id:'L0',x:0,y:0,fixX:true,fixY:true},
  {id:'L1',x:1e16,y:0,fixX:true,fixY:true}
 ];
 const members=[{id:'LONG',a:'L0',b:'L1',E:200,area:1}];
 for(let i=0;i<20;i++){
  const a='S'+i+'A',b='S'+i+'B',y=10+i*2;
  nodes.push({id:a,x:0,y,fixX:true,fixY:true},{id:b,x:1,y,fixX:true,fixY:true});
  members.push({id:'M'+i,a,b,E:200,area:1});
 }
 const byId=new Map(nodes.map(node=>[node.id,node]));
 const lengths=members.map(member=>{
  const a=byId.get(member.a),b=byId.get(member.b);
  return Math.hypot(b.x-a.x,b.y-a.y);
 });
 const naiveLength=lengths.reduce((sum,length)=>sum+length,0);
 const naiveVolume=lengths.reduce((sum,length)=>sum+length*1e-6,0);
 const preview=fem.inspectJSON(JSON.stringify({nodes,members}));
 assert.notEqual(naiveLength,1e16+20,'fixture must expose lost small member lengths');
 assert.notEqual(naiveVolume,1e10+20e-6,'fixture must expose distorted small member volumes');
 assert.equal(preview.totalMemberLength,1e16+20);
 assert.equal(preview.totalMemberVolume,1e10+20e-6);
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
 assert.equal(csvRows[1][8],String(metric.density));assert.equal(Number(csvRows[1][8]),metric.density);
 assert.equal(csvRows[1][9],String(metric.mass));assert.equal(Number(csvRows[1][9]),metric.mass);
 assert.equal(csvRows[1][9],'15.700000000000001');
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

test('material CSV numeric cells use shortest round-trip binary64 values',()=>{
 const dense=clone(fem.examples.bar);dense.members[0].density=7850;
 const csv=fem.exportMaterialCSV(dense);
 assert.ok(csv.includes(['"AB"','"A"','"B"','"2"','"0.001"','"0.002"','"200"','"100"','"7850"','"15.700000000000001"'].join(',')));
 const precise=clone(fem.examples.bar);precise.nodes[1].x=2/3;
 assert.ok(fem.exportMaterialCSV(precise).includes('"0.6666666666666666"'));
 const exact=clone(fem.examples.bar);exact.members[0].density=0.10000000000000002;
 const metric=fem.inspectJSON(JSON.stringify(exact)).memberMetrics[0];
 const exactRow=fem.exportMaterialCSV(exact).trimEnd().split('\r\n')[1].slice(1,-1).split('","');
 assert.equal(exactRow[8],'0.10000000000000002');
 assert.equal(Number(exactRow[8]),metric.density);
 assert.equal(exactRow[9],String(metric.mass));
 assert.equal(Number(exactRow[9]),metric.mass);
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
 const eulerCriticalLoadKN=metric.eulerCriticalLoad/1000;
 assert.equal(rows[1][12],String(eulerCriticalLoadKN),'Euler CSV must preserve the shortest round-trip kN value');
 assert.equal(Number(rows[1][12]),eulerCriticalLoadKN);
 close(eulerCriticalLoadKN,expected/1000,1e-12);
 const tinyCSV=clone(bar);
 tinyCSV.members[0].E=1e-170;tinyCSV.members[0].area=1e-155;
 tinyCSV.members[0].I=1e-149;tinyCSV.members[0].K=1;
 const tinyMetric=fem.inspectJSON(JSON.stringify(tinyCSV)).memberMetrics[0];
 assert.ok(Number.isFinite(tinyMetric.eulerCriticalLoad)&&tinyMetric.eulerCriticalLoad>0);
 assert.equal(tinyMetric.eulerCriticalLoad/1000,0,'positive N value is not representable in kN');
 assert.throws(()=>fem.exportMaterialCSV(tinyCSV),/Euler critical load underflows in kN CSV export/);
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
 const overflowMember=fem.parseModel(overflow).members[0];
 assert.equal(Math.PI*Math.PI*overflowMember.E*overflowMember.secondMoment,Infinity,
  'the direct Euler numerator must overflow while the final load remains representable');
 assert.ok(Math.abs(overflowMember.eulerCriticalLoad/8.871260037822617e307-1)<=5e-15,
  'scale-safe Euler load must match the exact-binary64 Decimal reference');
 const hugeEuler=fem.parseModel({
  nodes:[{id:'A',x:0,y:0},{id:'B',x:1e200,y:0}],
  members:[{id:'AB',a:'A',b:'B',E:1e291,area:1e-100,I:1e308,K:1e200}]
 }).members[0];
 assert.equal(Math.PI*Math.PI*hugeEuler.E*hugeEuler.secondMoment,Infinity);
 assert.equal(hugeEuler.effectiveLengthFactor*hugeEuler.L,Infinity);
 assert.equal((hugeEuler.effectiveLengthFactor*hugeEuler.L)**2,Infinity);
 assert.ok(Math.abs(hugeEuler.eulerCriticalLoad/9.869604401089358e-204-1)<=5e-15,
  'Euler load must survive overflowing numerator, effective length and denominator');
 const tinyEuler=fem.parseModel({
  nodes:[{id:'A',x:0,y:0},{id:'B',x:2e-12,y:0}],
  members:[{id:'AB',a:'A',b:'B',E:1e-318,area:1e300,I:1e-310,K:5e-151}]
 }).members[0];
 assert.equal(Math.PI*Math.PI*tinyEuler.E*tinyEuler.secondMoment,0,
  'the direct Euler numerator must underflow');
 assert.equal((tinyEuler.effectiveLengthFactor*tinyEuler.L)**2,0,
  'the direct effective-length square must underflow');
 assert.ok(tinyEuler.eulerCriticalLoad>0&&Number.isFinite(tinyEuler.eulerCriticalLoad));
 assert.ok(Math.abs(tinyEuler.eulerCriticalLoad/9.752452739990855e-307-1)<=5e-15,
  'Euler load must survive simultaneous numerator and denominator underflow');
 const shortK=clone(pinned);shortK.members[0].K=Number.MIN_VALUE;
 assert.throws(()=>fem.parseModel(shortK),/Euler critical load.*finite number/,
  'a genuinely overflowing final Euler load must still be rejected');
 const finalUnderflow={
  nodes:[{id:'A',x:0,y:0},{id:'B',x:1e308,y:0}],
  members:[{id:'AB',a:'A',b:'B',E:1e-318,area:1e300,I:1e-310,K:1}]
 };
 assert.throws(()=>fem.parseModel(finalUnderflow),/Euler critical load underflow/,
  'a genuinely underflowing final Euler load must still be rejected');
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


test('radius of gyration uses a finite quotient and a range-safe split-root fallback',()=>{
 const circle=fem.sectionProperties('solid-circle',{diameter:40});
 assert.equal(circle.secondMoment/circle.area,100);
 assert.equal(circle.radiusOfGyrationX,10);
 assert.equal(circle.radiusOfGyrationY,10);
 const slender=fem.sectionProperties('l-angle',{width:1e200,height:1e100,thickness:1e-293});
 assert.equal(Number.isFinite(slender.secondMomentPerpendicular/slender.area),false);
 close(slender.radiusOfGyrationY,2.8867513459481287e199,5e-13);
});

test('rectangular radii use geometry factors when subnormal inertias lose relative precision',()=>{
 const relative=(got,want,label)=>assert.ok(Number.isFinite(got)&&want>0&&Math.abs(got/want-1)<=2e-15,
  label+' '+got+' != '+want);
 const solidDimensions={width:1e-6,height:3.5e-106};
 const solid=fem.sectionProperties('rectangle',solidDimensions);
 assert.equal(solid.secondMoment,Number.MIN_VALUE);
 const solidExpectedX=solidDimensions.height/Math.sqrt(12);
 assert.ok(Math.abs(Math.sqrt(solid.secondMoment/solid.area)/solidExpectedX-1)>0.1,
  'rounded subnormal Ixx/A must expose the previous radius precision loss');
 relative(solid.radiusOfGyrationX,solidExpectedX,'solid rectangle rx');
 relative(solid.radiusOfGyrationY,solidDimensions.width/Math.sqrt(12),'solid rectangle ry');

 const hollowDimensions={width:1e-6,height:3.5e-106,innerWidth:5e-7,innerHeight:1.75e-106};
 const hollow=fem.sectionProperties('hollow-rectangle',hollowDimensions);
 assert.equal(hollow.secondMoment,Number.MIN_VALUE);
 const widthRatio=hollowDimensions.innerWidth/hollowDimensions.width;
 const heightRatio=hollowDimensions.innerHeight/hollowDimensions.height;
 const widthGap=(hollowDimensions.width-hollowDimensions.innerWidth)/hollowDimensions.width;
 const heightGap=(hollowDimensions.height-hollowDimensions.innerHeight)/hollowDimensions.height;
 const areaFactor=widthGap+widthRatio*heightGap;
 const ixxFactor=widthGap+widthRatio*heightGap*(1+heightRatio+heightRatio*heightRatio);
 const iyyFactor=heightGap+heightRatio*widthGap*(1+widthRatio+widthRatio*widthRatio);
 const hollowExpectedX=hollowDimensions.height*Math.sqrt(ixxFactor/areaFactor/12);
 const hollowExpectedY=hollowDimensions.width*Math.sqrt(iyyFactor/areaFactor/12);
 assert.ok(Math.abs(Math.sqrt(hollow.secondMoment/hollow.area)/hollowExpectedX-1)>0.1,
  'rounded hollow Ixx/A must expose the previous radius precision loss');
 relative(hollow.radiusOfGyrationX,hollowExpectedX,'hollow rectangle rx');
 relative(hollow.radiusOfGyrationY,hollowExpectedY,'hollow rectangle ry');
});

test('circular radii use geometry factors when subnormal inertias lose relative precision',()=>{
 const relative=(got,want,label)=>assert.ok(Number.isFinite(got)&&want>0&&Math.abs(got/want-1)<=2e-15,
  label+' '+got+' != '+want);
 const solidDiameter=3e-81;
 const solid=fem.sectionProperties('solid-circle',{diameter:solidDiameter});
 assert.equal(solid.secondMoment,Number.MIN_VALUE);
 const solidExpected=solidDiameter/4;
 assert.ok(Math.abs(Math.sqrt(solid.secondMoment/solid.area)/solidExpected-1)>0.1,
  'rounded subnormal solid-circle I/A must expose the previous radius precision loss');
 relative(solid.radiusOfGyrationX,solidExpected,'solid circle rx');
 relative(solid.radiusOfGyrationY,solidExpected,'solid circle ry');

 const hollowDimensions={diameter:3e-81,innerDiameter:1.5e-81};
 const hollow=fem.sectionProperties('hollow-circle',hollowDimensions);
 assert.equal(hollow.secondMoment,Number.MIN_VALUE);
 const ratio=hollowDimensions.innerDiameter/hollowDimensions.diameter;
 const hollowExpected=(hollowDimensions.diameter/4)*Math.sqrt(1+ratio*ratio);
 assert.ok(Math.abs(Math.sqrt(hollow.secondMoment/hollow.area)/hollowExpected-1)>0.1,
  'rounded subnormal hollow-circle I/A must expose the previous radius precision loss');
 relative(hollow.radiusOfGyrationX,hollowExpected,'hollow circle rx');
 relative(hollow.radiusOfGyrationY,hollowExpected,'hollow circle ry');
});

test('channel and I-section radii use normalized geometry when physical inertias are subnormal',()=>{
 const scale=10**-82.2;
 const references=[
  {shape:'channel',expected:{rx:2.0220658289055487e-81,ry:2.0060914979751612e-81}},
  {shape:'i-section',expected:{rx:2.0220658289055487e-81,ry:1.5424539802421713e-81}}
 ];
 const relative=(actual,want,label)=>assert.ok(Number.isFinite(actual)&&want>0&&
  Math.abs(actual/want-1)<=5e-13,label+' '+actual+' must match '+want);
 for(const {shape,expected} of references){
  const dimensions={width:100*scale,height:80*scale,webThickness:10*scale,flangeThickness:8*scale};
  const original={...dimensions};
  const section=fem.sectionProperties(shape,dimensions);
  assert.ok(section.area>0&&Number.isFinite(section.area),shape+' area must remain representable');
  assert.ok(section.secondMoment>0&&section.secondMoment<16*Number.MIN_VALUE,
   shape+' Ixx must be positive and subnormal');
  assert.ok(section.secondMomentPerpendicular>0&&section.secondMomentPerpendicular<16*Number.MIN_VALUE,
   shape+' Iyy must be positive and subnormal');
  assert.ok(Math.abs(Math.sqrt(section.secondMoment/section.area)/expected.rx-1)>0.01,
   shape+' rounded Ixx/A must reproduce the previous rx precision loss');
  assert.ok(Math.abs(Math.sqrt(section.secondMomentPerpendicular/section.area)/expected.ry-1)>0.01,
   shape+' rounded Iyy/A must reproduce the previous ry precision loss');
  relative(section.radiusOfGyrationX,expected.rx,shape+' rx');
  relative(section.radiusOfGyrationY,expected.ry,shape+' ry');
  assert.deepEqual(dimensions,original);
  assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
 }
});

test('channel and I-section section moduli use normalized geometry when physical inertias are subnormal',()=>{
 const scale=10**-82.2;
 const references=[
  {shape:'channel',sx:1.444703108127935e-242,sy:9.048880575086456e-243},
  {shape:'i-section',sx:1.444703108127935e-242,sy:6.725157272628184e-243}
 ];
 for(const expected of references){
  const dimensions={width:100*scale,height:80*scale,webThickness:10*scale,flangeThickness:8*scale};
  const original={...dimensions};
  const section=fem.sectionProperties(expected.shape,dimensions);
  assert.ok(Number.isFinite(section.area)&&section.area>0,expected.shape+' area must remain representable');
  assert.ok(section.secondMoment>0&&section.secondMoment<16*Number.MIN_VALUE,
   expected.shape+' Ixx must remain positive and subnormal');
  assert.ok(section.secondMomentPerpendicular>0&&section.secondMomentPerpendicular<16*Number.MIN_VALUE,
   expected.shape+' Iyy must remain positive and subnormal');
  const oldSx=section.secondMoment/section.extremeFiberDistanceAboutX;
  const oldSy=section.secondMomentPerpendicular/section.extremeFiberDistanceAboutY;
  assert.ok(Math.abs(oldSx/expected.sx-1)>0.04,
   expected.shape+' rounded Ixx/c must reproduce the previous section-modulus error');
  assert.ok(Math.abs(oldSy/expected.sy-1)>0.04,
   expected.shape+' rounded Iyy/c must reproduce the previous section-modulus error');
  assert.ok(Math.abs(section.sectionModulusX/expected.sx-1)<=5e-13,
   expected.shape+' Sx '+section.sectionModulusX+' must match the exact-binary64 Decimal reference '+expected.sx);
  assert.ok(Math.abs(section.sectionModulusY/expected.sy-1)<=5e-13,
   expected.shape+' Sy '+section.sectionModulusY+' must match the exact-binary64 Decimal reference '+expected.sy);
  assert.deepEqual(dimensions,original);
  assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
 }
});

test('channel and I-section use axis-separated normalization at extreme aspect ratios',()=>{
 const minNormal=2.2250738585072014e-308;
 const references=[
  {shape:'channel',rx:2.9160475533388224e-155,ry:2.8867513459481288e149,
   sx:1.6666533333333332e-159,sy:1.6333333333333333e145},
  {shape:'i-section',rx:2.9160475533388224e-155,ry:2.8867513459481288e149,
   sx:1.6666533333333332e-159,sy:1.6333333333333333e145}
 ];
 const relative=(actual,want,label)=>assert.ok(Number.isFinite(actual)&&want>0&&
  Math.abs(actual/want-1)<=5e-13,label+' '+actual+' must match '+want);
 for(const expected of references){
  const dimensions={width:1e150,height:1e-154,webThickness:1e-154,flangeThickness:4.9e-155};
  const original={...dimensions};
  const section=fem.sectionProperties(expected.shape,dimensions);
  assert.ok(Number.isFinite(section.area)&&section.area>0,expected.shape+' area must remain representable');
  assert.ok(section.secondMoment>0&&section.secondMoment<minNormal,
   expected.shape+' Ixx must remain positive and subnormal');
  assert.ok(section.secondMomentPerpendicular>minNormal,
   expected.shape+' Iyy must remain in the normal range');
  const oldRx=Math.sqrt(section.secondMoment/section.area);
  const oldSx=section.secondMoment/section.extremeFiberDistanceAboutX;
  assert.ok(Math.abs(oldRx/expected.rx-1)>1e-11,
   expected.shape+' rounded Ixx/A must reproduce the previous extreme-aspect radius error');
  assert.ok(Math.abs(oldSx/expected.sx-1)>1e-11,
   expected.shape+' rounded Ixx/c must reproduce the previous extreme-aspect modulus error');
  relative(section.radiusOfGyrationX,expected.rx,expected.shape+' rx');
  relative(section.radiusOfGyrationY,expected.ry,expected.shape+' ry');
  relative(section.sectionModulusX,expected.sx,expected.shape+' Sx');
  relative(section.sectionModulusY,expected.sy,expected.shape+' Sy');
  assert.deepEqual(dimensions,original);
  assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
 }
 const ordinary=fem.sectionProperties('channel',{width:100,height:80,webThickness:10,flangeThickness:8});
 assert.equal(ordinary.sectionModulusX,ordinary.secondMoment/ordinary.extremeFiberDistanceAboutX,
  'ordinary channel sections retain the dimensional I/c path');
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

test('hollow cavity area may underflow when all net section properties remain representable',()=>{
 const rectangleDimensions={width:1e100,height:1e-100,innerWidth:1e-162,innerHeight:1e-162};
 const originalRectangle={...rectangleDimensions};
 assert.equal(rectangleDimensions.innerWidth*rectangleDimensions.innerHeight,0,
  'the synthetic cavity area must underflow to zero');
 const hollowRectangle=fem.sectionProperties('hollow-rectangle',rectangleDimensions);
 const solidRectangle=fem.sectionProperties('rectangle',{width:rectangleDimensions.width,height:rectangleDimensions.height});
 for(const key of ['area','secondMoment','secondMomentPerpendicular','sectionModulusX','sectionModulusY',
                   'radiusOfGyrationX','radiusOfGyrationY']){
  assert.ok(Number.isFinite(hollowRectangle[key])&&hollowRectangle[key]>0,key+' must remain finite and positive');
  assert.equal(hollowRectangle[key],solidRectangle[key],key+' must match the numerically indistinguishable solid envelope');
 }
 assert.deepEqual(hollowRectangle.centroid,solidRectangle.centroid);
 assert.deepEqual(rectangleDimensions,originalRectangle);
 assert.ok(Object.isFrozen(hollowRectangle)&&Object.isFrozen(hollowRectangle.centroid));

 const circleDimensions={diameter:1e-50,innerDiameter:1e-200};
 const originalCircle={...circleDimensions};
 assert.equal(circleDimensions.innerDiameter*circleDimensions.innerDiameter,0,
  'the synthetic inner-diameter square must underflow to zero');
 const hollowCircle=fem.sectionProperties('hollow-circle',circleDimensions);
 const solidCircle=fem.sectionProperties('solid-circle',{diameter:circleDimensions.diameter});
 for(const key of ['area','secondMoment','secondMomentPerpendicular','sectionModulusX','sectionModulusY',
                   'radiusOfGyrationX','radiusOfGyrationY']){
  assert.ok(Number.isFinite(hollowCircle[key])&&hollowCircle[key]>0,key+' must remain finite and positive');
  assert.equal(hollowCircle[key],solidCircle[key],key+' must match the numerically indistinguishable solid envelope');
 }
 assert.deepEqual(hollowCircle.centroid,solidCircle.centroid);
 assert.deepEqual(circleDimensions,originalCircle);
 assert.ok(Object.isFrozen(hollowCircle)&&Object.isFrozen(hollowCircle.centroid));
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


test('I-section accepts a centered web whose area is below binary64 range when flange properties remain representable',()=>{
 const dimensions={width:1e100,height:1e-100,webThickness:Number.MIN_VALUE,flangeThickness:1e-101};
 const original={...dimensions};
 const webHeight=dimensions.height-2*dimensions.flangeThickness;
 assert.equal(dimensions.webThickness*webHeight,0,
  'the positive centered-web area must underflow to zero in binary64');
 assert.equal((dimensions.width-dimensions.webThickness)/2+dimensions.webThickness/2,
  dimensions.width/2,'the web must be centered on the I-section vertical axis');
 assert.equal(dimensions.flangeThickness+webHeight/2,dimensions.height/2,
  'the web must be centered on the I-section horizontal axis');
 const section=fem.sectionProperties('i-section',dimensions);
 const expected={
  area:0.2,
  ixx:4.066666666666667e-202,
  iyy:1.6666666666666667e198,
  sx:8.133333333333335e-102,
  sy:3.333333333333333e98,
  rx:4.509249752822894e-101,
  ry:2.8867513459481287e99
 };
 const relative=(actual,want,label)=>assert.ok(Number.isFinite(actual)&&want>0&&
  Math.abs(actual/want-1)<=5e-13,label+' '+actual+' must match the 120-digit exact-binary64 Decimal reference '+want);
 relative(section.area,expected.area,'I-section area');
 relative(section.secondMoment,expected.ixx,'I-section Ixx');
 relative(section.secondMomentPerpendicular,expected.iyy,'I-section Iyy');
 relative(section.sectionModulusX,expected.sx,'I-section Sx');
 relative(section.sectionModulusY,expected.sy,'I-section Sy');
 relative(section.radiusOfGyrationX,expected.rx,'I-section rx');
 relative(section.radiusOfGyrationY,expected.ry,'I-section ry');
 assert.deepEqual(section.centroid,{x:5e99,y:5e-101});
 assert.equal(section.extremeFiberDistanceAboutX,5e-101);
 assert.equal(section.extremeFiberDistanceAboutY,5e99);
 assert.throws(()=>fem.sectionProperties('channel',dimensions),/Composite section area underflow/,
  'the exception is limited to the exactly centered I-section web');
 assert.deepEqual(dimensions,original);
 assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
});



test('channel omits an underflowed web only when every contribution is below binary64 significance',()=>{
 const dimensions={width:1e40,height:1e-100,webThickness:Number.MIN_VALUE,flangeThickness:2e-101};
 const original={...dimensions};
 assert.equal(dimensions.webThickness*dimensions.height,0,
  'the positive off-axis web area must underflow to zero in binary64');
 const section=fem.sectionProperties('channel',dimensions);
 const expected={
  area:4e-61,centroidX:5e39,centroidY:5e-101,
  ixx:6.533333333333334e-262,iyy:3.333333333333334e18,
  sx:1.306666666666667e-161,sy:6.666666666666667e-22,
  rx:4.041451884327381e-101,ry:2.886751345948129e39
 };
 const actual={
  area:section.area,centroidX:section.centroid.x,centroidY:section.centroid.y,
  ixx:section.secondMoment,iyy:section.secondMomentPerpendicular,
  sx:section.sectionModulusX,sy:section.sectionModulusY,
  rx:section.radiusOfGyrationX,ry:section.radiusOfGyrationY
 };
 for(const [key,want] of Object.entries(expected)){
  const got=actual[key];
  assert.ok(Number.isFinite(got)&&Math.abs(got/want-1)<=5e-13,
   key+' '+got+' must match the 200-digit exact-binary64 Decimal reference '+want);
 }
 assert.equal(section.extremeFiberDistanceAboutX,5e-101);
 assert.equal(section.extremeFiberDistanceAboutY,5e39);
 assert.deepEqual(dimensions,original);
 assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
 const nonNegligible={width:1e100,height:1e-100,webThickness:Number.MIN_VALUE,flangeThickness:1e-101};
 assert.throws(()=>fem.sectionProperties('channel',nonNegligible),/Composite section area underflow/,
  'an underflowed off-axis web with a representable first moment must still be rejected');
});

test('composite section local inertias avoid intermediate overflow when final properties are finite',()=>{
 // Synthetic floating-range stress cases (dimensions in mm), not physical design examples.
 // The old left-to-right b*h*h*h/12 expression overflows before division although Ixx is finite.
 assert.equal(1e74*2e78*2e78*2e78/12,Infinity);
 assert.equal(2.25e73*2e78*2e78*2e78/12,Infinity);
 const cases=[
  {shape:'channel',dimensions:{width:5e78,height:2e78,webThickness:1e74,flangeThickness:1e71},
   expected:{area:2.0099998e152,cx:1.2487563426623227e76,cy:1e78,ixx:6.766664656666867e307,iyy:8.301990215811596e306}},
  {shape:'i-section',dimensions:{width:5e78,height:2e78,webThickness:1e74,flangeThickness:1e71},
   expected:{area:2.0099998e152,cx:2.5e78,cy:1e78,ixx:6.766664656666867e307,iyy:2.0833335e306}},
  {shape:'l-angle',dimensions:{width:1e78,height:2e78,thickness:2.25e73},
   expected:{area:6.749949375e151,cx:1.6667541664791653e77,cy:6.6667541664791653e77,
    ixx:2.999943750622263e307,iyy:5.624817191824194e306,
    major:3.212217891384522e307,minor:3.502075784201607e306}}
 ];
 const closeRelative=(got,want,label)=>{
  assert.ok(Number.isFinite(got)&&Math.abs(got-want)<=Math.abs(want)*2e-13,
   label+' '+got+' must match '+want);
 };
 for(const {shape,dimensions,expected} of cases){
  const section=fem.sectionProperties(shape,dimensions);
  closeRelative(section.area,expected.area,shape+' area');
  closeRelative(section.centroid.x,expected.cx,shape+' centroid x');
  closeRelative(section.centroid.y,expected.cy,shape+' centroid y');
  closeRelative(section.secondMoment,expected.ixx,shape+' Ixx');
  closeRelative(section.secondMomentPerpendicular,expected.iyy,shape+' Iyy');
  for(const key of ['sectionModulusX','sectionModulusY','radiusOfGyrationX','radiusOfGyrationY'])
   assert.ok(Number.isFinite(section[key])&&section[key]>0,shape+' '+key+' must remain finite and positive');
  if(shape==='l-angle'){
   closeRelative(section.principalMomentMajor,expected.major,'L-angle I1');
   closeRelative(section.principalMomentMinor,expected.minor,'L-angle I2');
  }
  assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
 }
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


test('legacy SI conversion rejects nonzero forces and modulus that underflow in current units',()=>{
 const template=globalThis.TrussStudio.example;
 for(const field of ['fx','fy']){
  for(const value of [Number.MIN_VALUE,-Number.MIN_VALUE]){
   const legacy=clone(template);
   legacy.nodes[2][field]=value;
   assert.throws(()=>fem.fromLegacy(legacy),/Legacy (Fx|Fy) \(N\) underflows the supported SI range\./);
  }
 }
 const tinyModulus=clone(template);
 tinyModulus.members[0].E=Number.MIN_VALUE;
 assert.throws(()=>fem.fromLegacy(tinyModulus),/Legacy E \(Pa\) underflows the supported SI range\./);
 const zero=clone(template);
 zero.nodes[2].fx=0;zero.nodes[2].fy=0;
 const normalizedZero=fem.fromLegacy(zero);
 assert.equal(normalizedZero.nodes[2].fx,0);
 assert.equal(normalizedZero.nodes[2].fy,0);
 const normalized=fem.fromLegacy(template);
 assert.equal(normalized.nodes[2].fy,-10);
 assert.equal(normalized.members[0].E,200);
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



test('L-angle principal minor remains resolvable for an extreme aspect-ratio section',()=>{
 const section=fem.sectionProperties('l-angle',{width:1e6,height:1,thickness:1e-3});
 const referenceMinor=4.161659185863228e-4; // 80-digit Decimal composite-rectangle reference, mm^4.
 assert.ok(Number.isFinite(section.principalMomentMajor)&&section.principalMomentMajor>0);
 assert.ok(Number.isFinite(section.principalMomentMinor)&&section.principalMomentMinor>0);
 assert.ok(Math.abs(section.principalMomentMinor-referenceMinor)<=referenceMinor*1e-10,
  'minor principal moment '+section.principalMomentMinor+' must match '+referenceMinor);
 close(section.principalMomentMajor,83333583083083.333,1e-12);
 close(section.principalAxisAngleDegrees,89.99999999982829,1e-12);
 close(section.principalMomentMajor+section.principalMomentMinor,
  section.secondMoment+section.secondMomentPerpendicular,1e-12);
 assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
});

test('thin-walled hollow rectangle retains net properties without subtractive cancellation',()=>{
 const dimensions={width:1e6,height:1e6,innerWidth:999999.9999999,innerHeight:999999.9999999};
 const original={...dimensions};
 const section=fem.sectionProperties('hollow-rectangle',dimensions);
 // 80-digit Decimal references evaluated from the exact binary64 input dimensions.
 const expectedArea=0.20000152289866402;
 const expectedMoment=33333587149.774002;
 const closeRelative=(actual,expected,label)=>{
  assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=expected*1e-12,
   label+' '+actual+' must match '+expected);
 };
 closeRelative(section.area,expectedArea,'net area');
 closeRelative(section.secondMoment,expectedMoment,'Ixx');
 closeRelative(section.secondMomentPerpendicular,expectedMoment,'Iyy');
 closeRelative(section.sectionModulusX,expectedMoment/500000,'Sx');
 closeRelative(section.sectionModulusY,expectedMoment/500000,'Sy');
 closeRelative(section.radiusOfGyrationX,Math.sqrt(expectedMoment/expectedArea),'rx');
 closeRelative(section.radiusOfGyrationY,Math.sqrt(expectedMoment/expectedArea),'ry');
 assert.ok(section.area>0&&section.secondMoment>0&&section.secondMomentPerpendicular>0);
 assert.deepEqual(dimensions,original);
 assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
 assert.throws(()=>fem.sectionProperties('hollow-rectangle',{
  width:1e6,height:1e6,innerWidth:1e6,innerHeight:999999
 }),/inner width and depth must be positive and smaller/);
});


test('hollow rectangle retains finite thin-wall inertias when outer and inner fourth-power intermediates overflow',()=>{
 const dimensions={width:1e-10,height:1e110,innerWidth:9.999999999999998e-11,innerHeight:9.999999999999999e109};
 const original={...dimensions};
 assert.equal(dimensions.width*dimensions.height*dimensions.height*dimensions.height/12,Infinity);
 assert.equal(dimensions.innerWidth*dimensions.innerHeight*dimensions.innerHeight*dimensions.innerHeight/12,Infinity);
 const section=fem.sectionProperties('hollow-rectangle',dimensions);
 // 100-digit Decimal references evaluated from the exact binary64 input dimensions.
 const expected={
  area:4.253679286041422e84,
  secondMoment:6.325965858056535e303,
  secondMomentPerpendicular:7.852965095414868e63,
  sectionModulusX:1.2651931716113071e194,
  sectionModulusY:1.5705930190829738e74,
  radiusOfGyrationX:3.856390911208362e109,
  radiusOfGyrationY:4.296694365821575e-11
 };
 const closeRelative=(actual,want,label)=>{
  assert.ok(Number.isFinite(actual)&&Math.abs(actual-want)<=Math.abs(want)*5e-13,label+' '+actual+' must match '+want);
 };
 for(const [key,want] of Object.entries(expected)) closeRelative(section[key],want,key);
 assert.deepEqual(section.centroid,{x:dimensions.width/2,y:dimensions.height/2});
 assert.equal(section.extremeFiberDistanceAboutX,dimensions.height/2);
 assert.equal(section.extremeFiberDistanceAboutY,dimensions.width/2);
 assert.deepEqual(dimensions,original);
 assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
});

test('thin-walled hollow circle retains area and inertia without subtractive cancellation',()=>{
 const dimensions={diameter:1e6,innerDiameter:999999.9999999};
 const original={...dimensions};
 const section=fem.sectionProperties('hollow-circle',dimensions);
 // 100-digit reference evaluated from the exact binary64 input dimensions.
 const expectedArea=0.15708082876130342;
 const expectedMoment=19635103595.160965;
 const closeRelative=(actual,expected,label)=>{
  assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=Math.abs(expected)*1e-12,
   label+' '+actual+' must match '+expected);
 };
 closeRelative(section.area,expectedArea,'annulus area');
 closeRelative(section.secondMoment,expectedMoment,'Ixx');
 closeRelative(section.secondMomentPerpendicular,expectedMoment,'Iyy');
 closeRelative(section.sectionModulusX,expectedMoment/500000,'Sx');
 closeRelative(section.sectionModulusY,expectedMoment/500000,'Sy');
 closeRelative(section.radiusOfGyrationX,Math.sqrt(expectedMoment/expectedArea),'rx');
 closeRelative(section.radiusOfGyrationY,Math.sqrt(expectedMoment/expectedArea),'ry');
 assert.deepEqual(section.centroid,{x:500000,y:500000});
 assert.equal(section.secondMomentPerpendicular,section.secondMoment);
 const outerSquare=dimensions.diameter*dimensions.diameter;
 const innerSquare=dimensions.innerDiameter*dimensions.innerDiameter;
 const naiveArea=Math.PI*(outerSquare-innerSquare)/4;
 const naiveMoment=Math.PI*(outerSquare*outerSquare-innerSquare*innerSquare)/64;
 assert.ok(Math.abs(naiveArea-expectedArea)/expectedArea>1e-4,
  'reference geometry must expose direct area-subtraction cancellation');
 assert.ok(Math.abs(naiveMoment-expectedMoment)/expectedMoment>1e-5,
  'reference geometry must expose direct inertia-subtraction cancellation');
 assert.deepEqual(dimensions,original);
 assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
});


test('hollow-circle uses direct differences while cavity area remains well-conditioned',()=>{
 const ratio=0.5000000000000001;
 const dimensions={diameter:1,innerDiameter:ratio};
 const original={...dimensions};
 const previousAreaFactor=(1-ratio)*(1+ratio);
 const previousInertiaFactor=previousAreaFactor*(1+ratio*ratio);
 const previousArea=(Math.PI/4)*previousAreaFactor;
 const previousMoment=(Math.PI/64)*previousInertiaFactor;
 const section=fem.sectionProperties('hollow-circle',dimensions);
 assert.ok(ratio*ratio<=0.5,'cavity occupies no more than half of the envelope area');
 assert.equal(previousArea,0.589048622548086,'former factored area path reproduces its one-ulp loss');
 assert.equal(previousMoment,0.046019423636569225,'former factored inertia path reproduces its one-ulp loss');
 assert.equal(section.area,0.5890486225480861,'direct area difference matches the correctly rounded reference');
 assert.equal(section.secondMoment,0.04601942363656923,'direct inertia difference matches the correctly rounded reference');
 assert.equal(section.secondMomentPerpendicular,section.secondMoment);
 assert.equal(section.sectionModulusX,0.09203884727313846);
 assert.equal(section.sectionModulusY,section.sectionModulusX);
 assert.equal(section.radiusOfGyrationX,0.2795084971874737);
 assert.equal(section.radiusOfGyrationY,section.radiusOfGyrationX);
 assert.notEqual(section.area,previousArea);
 assert.notEqual(section.secondMoment,previousMoment);
 assert.deepEqual(section.centroid,{x:0.5,y:0.5});
 assert.deepEqual(dimensions,original);
 assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
});

test('small-cavity hollow circle matches solid-envelope rounding below half an ulp',()=>{
 const dimensions={diameter:1,innerDiameter:9.313225746154786e-14};
 const original={...dimensions};
 const ratio=dimensions.innerDiameter/dimensions.diameter;
 const previousAreaFactor=((dimensions.diameter-dimensions.innerDiameter)/dimensions.diameter)*(1+ratio);
 const previousInertiaFactor=previousAreaFactor*(1+ratio*ratio);
 const outerSquare=dimensions.diameter*dimensions.diameter;
 const previousArea=(Math.PI/4)*outerSquare*previousAreaFactor;
 const previousMoment=(Math.PI/64)*outerSquare*previousInertiaFactor*outerSquare;
 const solid=fem.sectionProperties('solid-circle',{diameter:dimensions.diameter});
 const hollow=fem.sectionProperties('hollow-circle',dimensions);
 // Exact-binary64 100-digit reference: q² is about 8.67e-27, far below half an ulp.
 assert.equal(previousAreaFactor,0.9999999999999999);
 assert.equal(previousInertiaFactor,0.9999999999999999);
 assert.notEqual(previousArea,solid.area,'the former factored path must reproduce the one-ulp area loss');
 assert.notEqual(previousMoment,solid.secondMoment,'the former factored path must reproduce the one-ulp inertia loss');
 for(const key of ['area','secondMoment','secondMomentPerpendicular','sectionModulusX','sectionModulusY',
  'radiusOfGyrationX','radiusOfGyrationY']){
  assert.equal(hollow[key],solid[key],key+' must round to the solid envelope below half an ulp');
 }
 assert.deepEqual(hollow.centroid,solid.centroid);
 assert.deepEqual(dimensions,original);
 assert.ok(Object.isFrozen(hollow)&&Object.isFrozen(hollow.centroid));
});


test('extreme thin hollow circle remains representable when both fourth powers overflow',()=>{
 const dimensions={diameter:1e78,innerDiameter:9.999999999999998e77};
 const outerSquare=dimensions.diameter*dimensions.diameter;
 const innerSquare=dimensions.innerDiameter*dimensions.innerDiameter;
 assert.ok(Number.isFinite(outerSquare)&&Number.isFinite(innerSquare));
 assert.equal(Number.isFinite(outerSquare*outerSquare),false,
  'the outer fourth power must overflow to exercise the former rejection');
 assert.equal(Number.isFinite(innerSquare*innerSquare),false,
  'the inner fourth power must also overflow for this boundary case');
 const original={...dimensions};
 const section=fem.sectionProperties('hollow-circle',dimensions);
 // 120-digit Decimal references evaluated from the exact binary64 input dimensions.
 const expectedArea=3.230940642955516e140;
 const expectedMoment=4.038675803694394e295;
 const closeRelative=(actual,expected,label)=>{
  assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=Math.abs(expected)*5e-13,
   label+' '+actual+' must match '+expected);
 };
 closeRelative(section.area,expectedArea,'annulus area');
 closeRelative(section.secondMoment,expectedMoment,'Ixx');
 closeRelative(section.secondMomentPerpendicular,expectedMoment,'Iyy');
 closeRelative(section.sectionModulusX,expectedMoment/(dimensions.diameter/2),'Sx');
 closeRelative(section.sectionModulusY,expectedMoment/(dimensions.diameter/2),'Sy');
 closeRelative(section.radiusOfGyrationX,Math.sqrt(expectedMoment/expectedArea),'rx');
 closeRelative(section.radiusOfGyrationY,Math.sqrt(expectedMoment/expectedArea),'ry');
 assert.deepEqual(section.centroid,{x:5e77,y:5e77});
 assert.equal(section.secondMomentPerpendicular,section.secondMoment);
 assert.deepEqual(dimensions,original);
 assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
});


test('L-angle minor principal moment survives normalized determinant underflow',()=>{
 const dimensions={width:1e100,height:1e-139,thickness:1e-140};
 const original={...dimensions};
 const section=fem.sectionProperties('l-angle',dimensions);
 const momentScale=Math.max(section.secondMoment,section.secondMomentPerpendicular,Math.abs(section.productOfInertia));
 const scaledIxx=section.secondMoment/momentScale;
 const scaledIyy=section.secondMomentPerpendicular/momentScale;
 const scaledIxy=section.productOfInertia/momentScale;
 const normalizedDeterminant=scaledIxx*scaledIyy-scaledIxy*scaledIxy;
 assert.equal(normalizedDeterminant,0,
  'the normalized determinant must underflow for this representable minor-moment case');
 // 100-digit Decimal determinant/eigenvalue reference from the exact binary64 input dimensions.
 const expectedMinor=Number('8.333333333333333047120026461242959511255978638690079422571566289435343033091377208870550837651415192e-322');
 assert.equal(section.principalMomentMinor,expectedMinor,
  'minor principal moment must retain the representable subnormal reference');
 assert.equal(section.principalMomentMinor,section.secondMoment);
 assert.ok(Number.isFinite(section.principalMomentMajor)&&section.principalMomentMajor>0);
 assert.ok(Number.isFinite(section.sectionModulusX)&&section.sectionModulusX>0);
 assert.ok(Number.isFinite(section.sectionModulusY)&&section.sectionModulusY>0);
 assert.ok(Number.isFinite(section.radiusOfGyrationX)&&section.radiusOfGyrationX>0);
 assert.ok(Number.isFinite(section.radiusOfGyrationY)&&section.radiusOfGyrationY>0);
 assert.ok(Number.isFinite(section.principalAxisAngleDegrees));
 assert.notEqual(section.productOfInertia,0);
 assert.deepEqual(dimensions,original);
 assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
});

 
test('solid circle retains finite inertia when the unscaled diameter fourth power overflows',()=>{
 const dimensions={diameter:2.45e77};
 const original={...dimensions};
 const outerSquare=dimensions.diameter*dimensions.diameter;
 assert.ok(Number.isFinite(outerSquare));
 assert.equal(Number.isFinite(outerSquare*outerSquare),false,
  'the unscaled diameter fourth power must overflow to exercise the former rejection');
 const section=fem.sectionProperties('solid-circle',dimensions);
 // 120-digit Decimal references evaluated from the exact binary64 diameter.
 const expected={
  area:4.714352475793184e154,
  secondMoment:1.768618795996787e308,
  sectionModulus:1.4437704457116628e231,
  radiusOfGyration:6.125e76
 };
 const closeRelative=(actual,want,label)=>{
  assert.ok(Number.isFinite(actual)&&Math.abs(actual-want)<=Math.abs(want)*5e-13,
   label+' '+actual+' must match '+want);
 };
 closeRelative(section.area,expected.area,'solid-circle area');
 closeRelative(section.secondMoment,expected.secondMoment,'solid-circle I');
 closeRelative(section.secondMomentPerpendicular,expected.secondMoment,'solid-circle Iyy');
 closeRelative(section.sectionModulusX,expected.sectionModulus,'solid-circle Sx');
 closeRelative(section.sectionModulusY,expected.sectionModulus,'solid-circle Sy');
 closeRelative(section.radiusOfGyrationX,expected.radiusOfGyration,'solid-circle rx');
 closeRelative(section.radiusOfGyrationY,expected.radiusOfGyration,'solid-circle ry');
 assert.deepEqual(section.centroid,{x:dimensions.diameter/2,y:dimensions.diameter/2});
 assert.equal(section.extremeFiberDistanceAboutX,dimensions.diameter/2);
 assert.equal(section.extremeFiberDistanceAboutY,dimensions.diameter/2);
 assert.equal(section.secondMomentPerpendicular,section.secondMoment);
 assert.deepEqual(dimensions,original);
 assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
});

test('L-angle radius of gyration remains finite when I/area overflows but sqrt(I/area) is representable',()=>{
 const dimensions={width:1e200,height:1e100,thickness:1e-293};
 const original={...dimensions};
 // The direct ratio overflows although the physical radius is about 2.89e199 mm.
 const section=fem.sectionProperties('l-angle',dimensions);
 assert.equal(Number.isFinite(section.secondMomentPerpendicular/section.area),false,
  'the unscaled Iyy/area intermediate must overflow for this boundary case');
 const expected={
  area:1.0000000000000001e-93,
  secondMoment:3333333.3333333335,
  secondMomentPerpendicular:8.333333333333333e305,
  radiusOfGyrationX:5.773502691896258e49,
  radiusOfGyrationY:2.8867513459481287e199
 };
 for(const [key,want] of Object.entries(expected)){
  const actual=section[key];
  assert.ok(Number.isFinite(actual)&&Math.abs(actual-want)<=Math.abs(want)*5e-13,
   key+' '+actual+' must match the 120-digit Decimal reference '+want);
 }
 assert.ok(section.radiusOfGyrationY>0);
 assert.deepEqual(dimensions,original);
 assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
});

test('L-angle mixed-scale subnormal axis retains geometric section modulus and radius precision',()=>{
 const dimensions={width:1e-60,height:1e60,thickness:1e-140};
 const original={...dimensions};
 const section=fem.sectionProperties('l-angle',dimensions);
 const expected={
  iyy:Number('3.33333333333333298183631920421949584405656150194446080197909255407398642909353764315625757002364921539649631612465441774e-321'),
  sy:Number('3.33333333333333308039143949377197100135385266166081762303295114348390848263158407192863184947726846704610772530023857252e-261'),
  ry:Number('5.77350269189625753514452957713086083520760935289477550500278383336899368867504169740982398221061503994525925291050145305e-121')
 };
 const closeRelative=(actual,want,label)=>assert.ok(Number.isFinite(actual)&&
  Math.abs(actual/want-1)<=5e-13,label+' '+actual+' must match the 160-digit exact-binary64 Decimal reference '+want);
 assert.ok(section.secondMomentPerpendicular>0&&section.secondMomentPerpendicular<2.2250738585072014e-308,
  'the minor-axis inertia must remain representable but subnormal');
 assert.equal(section.secondMomentPerpendicular,expected.iyy,
  'the reported dimensional inertia must retain its correctly rounded binary64 value');
 closeRelative(section.sectionModulusY,expected.sy,'L-angle Sy');
 closeRelative(section.radiusOfGyrationY,expected.ry,'L-angle ry');
 const oldSy=section.secondMomentPerpendicular/section.extremeFiberDistanceAboutY;
 const oldRy=Math.sqrt(section.secondMomentPerpendicular/section.area);
 assert.ok(Math.abs(oldSy/expected.sy-1)>1e-4,'the former I/c path must reproduce the mixed-axis subnormal error');
 assert.ok(Math.abs(oldRy/expected.ry-1)>1e-4,'the former sqrt(I/A) path must reproduce the mixed-axis subnormal error');
 assert.deepEqual(dimensions,original);
 assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
});

test('L-angle retains principal properties when dimensional product of inertia underflows',()=>{
 const dimensions={width:1e-75,height:1e-75,thickness:1e-75*(1-1e-14)};
 const original={...dimensions};
 const section=fem.sectionProperties('l-angle',dimensions);
 const expected={
  area:9.999999999999999e-151,
  ixx:8.333333333333331e-302,
  iyy:8.333333333333331e-302,
  ixy:0,
  major:8.333333333333331e-302,
  minor:8.333333333333331e-302,
  sx:1.6666666666666664e-226,
  sy:1.6666666666666664e-226,
  rx:2.886751345948129e-76,
  ry:2.886751345948129e-76
 };
 const relative=(actual,want,label)=>assert.ok(Number.isFinite(actual)&&want>0&&
  Math.abs(actual/want-1)<=5e-13,label+' '+actual+' must match the exact-binary64 Decimal reference '+want);
 relative(section.area,expected.area,'L-angle area');
 relative(section.secondMoment,expected.ixx,'L-angle Ixx');
 relative(section.secondMomentPerpendicular,expected.iyy,'L-angle Iyy');
 assert.ok(Object.is(section.productOfInertia,0),
  'the underflowed dimensional Ixy is canonical positive zero; normalized Ixy retains its sign for the 45-degree principal axis');
 relative(section.principalMomentMajor,expected.major,'L-angle major principal moment');
 relative(section.principalMomentMinor,expected.minor,'L-angle minor principal moment');
 relative(section.sectionModulusX,expected.sx,'L-angle Sx');
 relative(section.sectionModulusY,expected.sy,'L-angle Sy');
 relative(section.radiusOfGyrationX,expected.rx,'L-angle rx');
 relative(section.radiusOfGyrationY,expected.ry,'L-angle ry');
 assert.ok(Math.abs(section.principalAxisAngleDegrees-45)<=1e-12,
  'normalized Ixy must retain the 45-degree principal axis after dimensional Ixy underflows');
 assert.deepEqual(section.centroid,{x:5e-76,y:5e-76});
 assert.deepEqual(dimensions,original);
 assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
});


test('L-angle subnormal inertia tensor is recomputed from normalized geometry',()=>{
 const dimensions={width:1e-80,height:8e-81,thickness:1e-81};
 const original={...dimensions};
 const section=fem.sectionProperties('l-angle',dimensions);
 const expected={
  area:1.7e-161,
  cx:3.1470588235294115e-81,
  cy:2.1470588235294115e-81,
  ixx:Number('9.52990196078431225503842701523049063955259240565224190364284583596076919536930220340547140677992483958724978455638912481e-323'),
  iyy:Number('1.67299019607843111440875714007922131082398244026801792052583038699400798245336615863394544335163857234850701042706138800e-322'),
  ixy:Number('-7.41176470588235179755058980866647901188391529105817075166297150556693741237507583537321782164047443930657974088229018912e-323'),
  major:Number('2.13696990490240033485848025461171882260390032664760984885065784831439903362470541950069389676999098048873387796463550738e-322'),
  minor:Number('4.89010487254462005054119586990551552175341354185632262039457122275685868365590959473798687259640075818498110918064793104e-323'),
  sx:1.62822445561139e-242,
  sy:2.4412732474964233e-242,
  rx:2.3676622822552844e-81,
  ry:3.1370557534830907e-81,
  angle:57.953253999757194
 };
 const closeRelative=(actual,want,label)=>{
  assert.ok(Number.isFinite(actual)&&Math.abs(actual-want)<=Math.abs(want)*5e-13,
   label+' '+actual+' must match the exact-binary64 Decimal reference '+want);
 };
 closeRelative(section.area,expected.area,'area');
 closeRelative(section.centroid.x,expected.cx,'centroid x');
 closeRelative(section.centroid.y,expected.cy,'centroid y');
 closeRelative(section.sectionModulusX,expected.sx,'Sx');
 closeRelative(section.sectionModulusY,expected.sy,'Sy');
 closeRelative(section.radiusOfGyrationX,expected.rx,'rx');
 closeRelative(section.radiusOfGyrationY,expected.ry,'ry');
 closeRelative(section.principalAxisAngleDegrees,expected.angle,'principal axis angle');
 assert.equal(section.secondMoment,expected.ixx);
 assert.equal(section.secondMomentPerpendicular,expected.iyy);
 assert.equal(section.productOfInertia,expected.ixy);
 assert.equal(section.principalMomentMajor,expected.major);
 assert.equal(section.principalMomentMinor,expected.minor);
 assert.equal(section.principalMomentMajor+section.principalMomentMinor,
  section.secondMoment+section.secondMomentPerpendicular);
 const oldArea=1.7000000000000001e-161,oldIxx=1e-322,oldIyy=1.63e-322,oldIxy=-7.4e-323;
 const oldRx=Math.sqrt(oldIxx/oldArea),oldRy=Math.sqrt(oldIyy/oldArea);
 const oldAngle=0.5*Math.atan2(-2*oldIxy,oldIxx-oldIyy)*180/Math.PI;
 assert.ok(Math.abs(oldRx-expected.rx)>expected.rx*0.01,'the former dimensional radius path must reproduce >1% error');
 assert.ok(Math.abs(oldRy-expected.ry)>expected.ry*0.01,'the former dimensional radius path must reproduce >1% error');
 assert.ok(Math.abs(oldAngle-expected.angle)>1,'the former dimensional principal angle must reproduce >1 degree error');
 assert.ok(section.secondMoment>0&&section.secondMoment<2.2250738585072014e-308);
 assert.ok(section.secondMomentPerpendicular>0&&section.secondMomentPerpendicular<2.2250738585072014e-308);
 assert.deepEqual(dimensions,original);
 assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
});



test('rectangular section moduli use geometry factors when subnormal inertias lose precision',()=>{
 const minNormal=2.2250738585072014e-308;
 const cases=[
  {shape:'rectangle',dimensions:{width:4.5e-81,height:6e-81},sx:2.7e-242,sy:2.025e-242},
  {shape:'hollow-rectangle',dimensions:{width:4.5e-81,height:6e-81,innerWidth:2.25e-81,innerHeight:3e-81},
   sx:2.53125e-242,sy:1.8984375e-242}
 ];
 const relative=(actual,want,label)=>assert.ok(Number.isFinite(actual)&&want>0&&
  Math.abs(actual/want-1)<=5e-13,label+' '+actual+' must match '+want);
 for(const item of cases){
  const original={...item.dimensions};
  const section=fem.sectionProperties(item.shape,item.dimensions);
  assert.ok(section.secondMoment>0&&section.secondMoment<minNormal,item.shape+' Ixx must remain subnormal');
  assert.ok(section.secondMomentPerpendicular>0&&section.secondMomentPerpendicular<minNormal,
   item.shape+' Iyy must remain subnormal');
  const oldSx=section.secondMoment/section.extremeFiberDistanceAboutX;
  const oldSy=section.secondMomentPerpendicular/section.extremeFiberDistanceAboutY;
  assert.ok(Math.abs(oldSx/item.sx-1)>0.02,item.shape+' rounded Ixx/cX must reproduce the previous section-modulus error');
  assert.ok(Math.abs(oldSy/item.sy-1)>0.02,item.shape+' rounded Iyy/cY must reproduce the previous section-modulus error');
  relative(section.sectionModulusX,item.sx,item.shape+' Sx');
  relative(section.sectionModulusY,item.sy,item.shape+' Sy');
  assert.deepEqual(item.dimensions,original);
  assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
 }
});

 
test('circular section moduli avoid subnormal inertia quantization',()=>{
 const minNormal=2.2250738585072014e-308;
 const cases=[
  {shape:'solid-circle',dimensions:{diameter:3e-81},sx:2.6507188014663876e-243},
  {shape:'hollow-circle',dimensions:{diameter:3e-81,innerDiameter:1.5e-81},sx:2.4850488763747383e-243}
 ];
 for(const item of cases){
  const original={...item.dimensions};
  const section=fem.sectionProperties(item.shape,item.dimensions);
  assert.ok(section.secondMoment>0&&section.secondMoment<minNormal,
   item.shape+' Ixx must remain positive and subnormal');
  assert.equal(section.secondMomentPerpendicular,section.secondMoment);
  const oldSx=section.secondMoment/section.extremeFiberDistanceAboutX;
  assert.ok(Math.abs(oldSx/item.sx-1)>0.2,
   item.shape+' rounded I/c must reproduce the previous >20% section-modulus error');
  for(const [axis,value] of [['Sx',section.sectionModulusX],['Sy',section.sectionModulusY]]){
   assert.ok(Number.isFinite(value)&&Math.abs(value/item.sx-1)<=5e-13,
    item.shape+' '+axis+' '+value+' must match the 120-digit Decimal reference '+item.sx);
  }
  assert.deepEqual(item.dimensions,original);
  assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
 }
 const ordinary=fem.sectionProperties('solid-circle',{diameter:40});
 assert.equal(ordinary.sectionModulusX,ordinary.secondMoment/ordinary.extremeFiberDistanceAboutX,
  'ordinary solid circles retain the existing I/c path');
});

 
test('optional member mass preserves finite L*A*density when intermediate volume overflows or underflows',()=>{
 const model=(length,E,area,density)=>({
  nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:length,y:0,fixY:true}],
  members:[{id:'AB',a:'A',b:'B',E,area,density}]
 });
 const thin=fem.parseModel(model(2e-12,1e299,4.940656458412465e-318,1e308)).members[0];
 assert.equal(thin.A,Number.MIN_VALUE);
 assert.equal(thin.L*thin.A,0,'the old intermediate member volume must underflow to zero');
 assert.ok(Number.isFinite(thin.stiffness)&&thin.stiffness>0);
 assert.ok(Math.abs(thin.mass/9.88131291682493e-28-1)<=5e-15,
  'mass must match the exact-binary64 Decimal reference after volume underflow');
 const huge=fem.parseModel(model(1e308,1e-308,1e308,1e-310)).members[0];
 assert.equal(huge.L*huge.A,Infinity,'the old intermediate member volume must overflow');
 assert.ok(Number.isFinite(huge.stiffness)&&huge.stiffness>0);
 assert.ok(Number.isFinite(huge.mass));
 assert.ok(Math.abs(huge.mass/9.999999999999968e299-1)<=5e-15,
  'mass must match the exact-binary64 Decimal reference after volume overflow');
 const zeroDensity=fem.parseModel(model(1e308,1e-308,1e308,0)).members[0];
 assert.equal(zeroDensity.mass,0,'zero density remains a valid zero mass even when volume is unrepresentable');
 assert.throws(()=>fem.parseModel(model(1e308,1e-308,1e308,1e308)),
  /mass.*must be a finite number/,
  'a genuinely unrepresentable final mass must still be rejected');
});

test('inspectJSON and material CSV reject positive member volume that underflows to zero',()=>{
 const model={
  nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2e-12,y:0,fixY:true}],
  members:[{id:'AB',a:'A',b:'B',E:1e299,area:4.940656458412465e-318,density:1e308}]
 };
 const member=fem.parseModel(model).members[0];
 assert.equal(member.L*member.A,0,'the positive physical member volume must underflow in binary64');
 assert.ok(Number.isFinite(member.mass)&&member.mass>0,
  'the independently scale-safe member mass remains representable');
 assert.throws(()=>fem.inspectJSON(JSON.stringify(model)),
  /Member AB material volume underflow; increase dimensions/,
  'the preview must not publish a false zero material volume');
 assert.throws(()=>fem.exportMaterialCSV(model),
  /Member AB material volume underflow; increase dimensions/,
  'the material schedule must not export a false zero material volume');
 const huge={
  nodes:[{id:'A',x:0,y:0},{id:'B',x:1e308,y:0}],
  members:[{id:'AB',a:'A',b:'B',E:1e-308,area:1e308,density:1e-310}]
 };
 assert.throws(()=>fem.inspectJSON(JSON.stringify(huge)),
  /Total member volume \(m³\) must be a finite number/,
  'the existing material-volume overflow rejection remains intact');
});


test('positive optional member mass rejects final underflow while preserving zero density',()=>{
 const model=density=>({
  nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2e-12,y:0,fixY:true}],
  members:[{id:'AB',a:'A',b:'B',E:200,area:5e-318,density}]
 });
 const underflow=model(1e-300);
 const areaSI=underflow.members[0].area*1e-6;
 assert.equal(areaSI,Number.MIN_VALUE,'the SI area must remain representable');
 assert.ok((200*1e9*areaSI)/2e-12>0,'the same member retains positive finite axial stiffness');
 assert.equal((2e-12*areaSI)*1e-300,0,'the final positive mass is below binary64 range');
 assert.throws(()=>fem.parseModel(underflow),
  /Member AB: mass underflow; increase dimensions or density/,
  'positive density must not silently produce a zero mass');
 assert.throws(()=>fem.solve(underflow),/Member AB: mass underflow/);
 assert.throws(()=>fem.inspectJSON(JSON.stringify(underflow)),/Member AB: mass underflow/);
 assert.throws(()=>fem.exportMaterialCSV(underflow),/Member AB: mass underflow/);
 const zeroDensity=fem.parseModel(model(0)).members[0];
 assert.equal(zeroDensity.mass,0,'explicit zero density remains a valid zero mass');
 const retained=fem.parseModel(model(1e308)).members[0];
 assert.equal(retained.mass,9.88131291682493e-28,
  'a positive mass remains accepted when only the intermediate volume underflows');
});

test('channel and I-section areas retain combined sub-ulp flange contributions',()=>{
 // Synthetic binary64 summation boundary, not a physical engineering design.
 const dimensions={width:1e154,height:1e154,webThickness:1e-154,flangeThickness:6.661338147750939e-171};
 const webArea=dimensions.webThickness*dimensions.height;
 const flangeArea=(dimensions.width-dimensions.webThickness)*dimensions.flangeThickness;
 assert.equal(webArea,1);
 assert.ok(flangeArea>0&&flangeArea<Number.EPSILON/2,
  'each flange area must be individually below half an ulp of the dominant web area');
 assert.equal(webArea+flangeArea+flangeArea,1,
  'naive left-to-right addition loses both individually sub-ulp flange contributions');
 for(const shape of ['channel','i-section']){
  const original={...dimensions};
  const section=fem.sectionProperties(shape,dimensions);
  assert.equal(section.area,1.0000000000000002,
   shape+' area must be the correctly rounded sum of the web and both flanges');
  for(const key of ['secondMoment','secondMomentPerpendicular','sectionModulusX','sectionModulusY',
                    'radiusOfGyrationX','radiusOfGyrationY']){
   assert.ok(Number.isFinite(section[key])&&section[key]>0,shape+' '+key+' must remain finite and positive');
  }
  assert.deepEqual(dimensions,original);
  assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
 }
});

 
test('channel and I-section centroid and inertias retain sub-ulp rectangle contributions',()=>{
 // Synthetic binary64 boundary fixture, not a physical engineering design.
 const dimensions={width:2,height:1,webThickness:1,flangeThickness:2e-17};
 // The naive channel first-moment and Ixx reductions lose two individually small terms.
 assert.equal(0.5+3e-17+3e-17,0.5);
 assert.equal(1/12+5e-18+5e-18,1/12);
 // In the I-section, adding the top-flange offset before the web rounds one ulp too high.
 const naiveISectionIxx=1.3333333333333336e-51+1e-17+1/12+1e-17;
 assert.equal(naiveISectionIxx,0.08333333333333336);
 const expected={
  channel:{x:0.5000000000000001,y:0.5,ixx:0.08333333333333334,iyy:0.08333333333333337},
  'i-section':{x:1,y:0.5,ixx:0.08333333333333334,iyy:0.08333333333333336}
 };
 for(const [shape,reference] of Object.entries(expected)){
  const original={...dimensions};
  const section=fem.sectionProperties(shape,dimensions);
  assert.equal(section.centroid.x,reference.x,shape+' centroid x must retain the correctly rounded first moment');
  assert.equal(section.centroid.y,reference.y,shape+' centroid y must retain the correctly rounded first moment');
  assert.equal(section.secondMoment,reference.ixx,shape+' Ixx must sum local and parallel-axis terms before rounding');
  assert.equal(section.secondMomentPerpendicular,reference.iyy,shape+' Iyy must sum local and parallel-axis terms before rounding');
  for(const key of ['sectionModulusX','sectionModulusY','radiusOfGyrationX','radiusOfGyrationY']){
   assert.ok(Number.isFinite(section[key])&&section[key]>0,shape+' '+key+' must remain finite and positive');
  }
  assert.deepEqual(dimensions,original);
  assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
 }
});


test('L-angle area and inertia sums round their binary64 rectangle contributions once',()=>{
 const cases=[
  {dimensions:{width:8605413.972369973,height:4.292204701476468,thickness:2.136125318978258e-5},
   expected:{area:183.82251835310274,x:4302704.840094387,y:1.1751052746539924e-5,ixx:0.0005630523010274837,iyy:1134387503114039.5},
   previousArea:183.8225183531027,naiveProperty:'ixx',naiveValue:0.0005630523010274838},
  {dimensions:{width:1.1143751945503119e-20,height:4.305111224234166e-16,thickness:2.015788401705846e-21},
   expected:{area:8.678377274295314e-37,x:1.0080123367146022e-21,y:2.1525099734807228e-16,ixx:1.3404309505588713e-68,iyy:2.9455728539715605e-79},
   naiveProperty:'iyy',naiveValue:2.94557285397156e-79}
 ];
 const previousScaledPositiveSum=values=>{
  const scale=Math.max(0,...values.map(Math.abs));if(scale===0)return 0;
  let sum=0,correction=0;
  for(const value of values){const scaled=value/scale,next=sum+scaled;
   correction+=Math.abs(sum)>=Math.abs(scaled)?(sum-next)+scaled:(scaled-next)+sum;sum=next;}
  return (sum+correction)*scale;
 };
 const naiveMoments=(dimensions,centroid)=>{
  const {width,height,thickness}=dimensions;
  const pieces=[
   {x:0,y:0,width:thickness,height},
   {x:thickness,y:0,width:width-thickness,height:thickness}
  ].map(piece=>({...piece,area:piece.width*piece.height,cx:piece.x+piece.width/2,cy:piece.y+piece.height/2}));
  const ixx=pieces.reduce((sum,piece)=>{
   const local=piece.width*piece.height*(piece.height/12)*piece.height;
   const offset=piece.area*(piece.cy-centroid.y)*(piece.cy-centroid.y);return sum+local+offset;
  },0);
  const iyy=pieces.reduce((sum,piece)=>{
   const local=piece.height*piece.width*(piece.width/12)*piece.width;
   const offset=piece.area*(piece.cx-centroid.x)*(piece.cx-centroid.x);return sum+local+offset;
  },0);
  return {ixx,iyy};
 };
 for(const item of cases){
  const original={...item.dimensions},section=fem.sectionProperties('l-angle',item.dimensions);
  const naive=naiveMoments(item.dimensions,section.centroid);
  if(item.previousArea!==undefined){
   const {width,height,thickness}=item.dimensions;
   const previous=previousScaledPositiveSum([thickness*height,(width-thickness)*thickness]);
   assert.equal(previous,item.previousArea,'former scaled area reduction reproduces its one-ulp error');
   assert.notEqual(previous,item.expected.area);
  }
  assert.equal(naive[item.naiveProperty],item.naiveValue,'previous left-to-right inertia reduction reproduces its rounding error');
  assert.notEqual(naive[item.naiveProperty],item.expected[item.naiveProperty]);
  assert.equal(section.area,item.expected.area,'L-angle area must be correctly rounded');
  assert.equal(section.centroid.x,item.expected.x,'L-angle centroid x must use the correctly rounded area and first moment');
  assert.equal(section.centroid.y,item.expected.y,'L-angle centroid y must use the correctly rounded area and first moment');
  assert.equal(section.secondMoment,item.expected.ixx,'L-angle Ixx must round local and offset terms once');
  assert.equal(section.secondMomentPerpendicular,item.expected.iyy,'L-angle Iyy must round local and offset terms once');
  for(const key of ['principalMomentMajor','principalMomentMinor','sectionModulusX','sectionModulusY','radiusOfGyrationX','radiusOfGyrationY'])
   assert.ok(Number.isFinite(section[key])&&section[key]>0,'L-angle '+key+' must remain finite and positive');
  assert.ok(Number.isFinite(section.productOfInertia));
  assert.deepEqual(item.dimensions,original);
  assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
 }
});

test('section-property compatibility fallback preserves same-sign contributions without BigInt',()=>{
 const originalBigInt=globalThis.BigInt;
 try{
  globalThis.BigInt=undefined;
  const first=fem.sectionProperties('l-angle',{width:8605413.972369973,height:4.292204701476468,thickness:2.136125318978258e-5});
  assert.equal(first.area,183.82251835310274);
  assert.equal(first.centroid.x,4302704.840094387);
  assert.equal(first.centroid.y,1.1751052746539924e-5);
  assert.equal(first.secondMoment,0.0005630523010274837);
  assert.equal(first.secondMomentPerpendicular,1134387503114039.5);
  const second=fem.sectionProperties('l-angle',{width:1.1143751945503119e-20,height:4.305111224234166e-16,thickness:2.015788401705846e-21});
  assert.equal(second.area,8.678377274295314e-37);
  assert.equal(second.centroid.x,1.0080123367146022e-21);
  assert.equal(second.centroid.y,2.1525099734807228e-16);
  assert.equal(second.secondMoment,1.3404309505588713e-68);
  assert.equal(second.secondMomentPerpendicular,2.9455728539715605e-79);
  const thinFlanges={width:1e154,height:1e154,webThickness:1e-154,flangeThickness:6.661338147750939e-171};
  for(const shape of ['channel','i-section']){
   const section=fem.sectionProperties(shape,thinFlanges);
   assert.equal(section.area,1.0000000000000002,shape+' must retain both sub-ulp flange areas');
  }
  const channel=fem.sectionProperties('channel',{width:2,height:1,webThickness:1,flangeThickness:2e-17});
  assert.equal(channel.centroid.x,0.5000000000000001);
  assert.equal(channel.secondMoment,0.08333333333333334);
  assert.equal(channel.secondMomentPerpendicular,0.08333333333333337);
  const iSection=fem.sectionProperties('i-section',{width:2,height:1,webThickness:1,flangeThickness:2e-17});
  assert.equal(iSection.secondMoment,0.08333333333333334);
  assert.equal(iSection.secondMomentPerpendicular,0.08333333333333336);
 }finally{globalThis.BigInt=originalBigInt;}
});

test('hollow rectangles preserve small-cavity area, inertia and radius rounding',()=>{
 const dimensions={width:1,height:1,innerWidth:1.2e-16,innerHeight:0.5};
 const original={...dimensions};
 const section=fem.sectionProperties('hollow-rectangle',dimensions);
 assert.equal(section.area,0.9999999999999999,'small cavity area must not round up to the solid envelope');
 assert.equal(section.centroid.x,0.5);
 assert.equal(section.centroid.y,0.5);
 assert.equal(section.secondMoment,0.08333333333333333);
 assert.equal(section.secondMomentPerpendicular,0.08333333333333333);
 assert.equal(section.radiusOfGyrationX,0.28867513459481287);
 assert.equal(section.radiusOfGyrationY,0.28867513459481287);
 assert.deepEqual(dimensions,original);
 assert.ok(Object.isFrozen(section)&&Object.isFrozen(section.centroid));
 const tinyCavity=fem.sectionProperties('hollow-rectangle',{
  width:1,height:1,innerWidth:1.2e-16,innerHeight:0.25
 });
 assert.equal(tinyCavity.area,1,'a cavity below half an area ulp must still round away');
 const thinCavity=fem.sectionProperties('hollow-rectangle',{
  width:1,height:1,innerWidth:1.1e-16,innerHeight:0.51
 });
 assert.equal(thinCavity.secondMomentPerpendicular,0.08333333333333333,
  'small-cavity Iyy must not lose an ulp while combining the wall-gap terms');
 const originalBigInt=globalThis.BigInt;
 try {
  globalThis.BigInt=undefined;
  const fallback=fem.sectionProperties('hollow-rectangle',dimensions);
  assert.equal(fallback.area,0.9999999999999999);
  assert.equal(fallback.secondMoment,0.08333333333333333);
  assert.equal(fallback.secondMomentPerpendicular,0.08333333333333333);
 } finally { globalThis.BigInt=originalBigInt; }
});

test('global stiffness assembly retains combined sub-ulp parallel-member contributions',()=>{
 const model={
  nodes:[
   {id:'A',x:0,y:0,fixX:true,fixY:true,fx:0,fy:0},
   {id:'B',x:1,y:0,fixX:false,fixY:true,fx:1e13,fy:0}
  ],
  members:[
   {id:'large',a:'A',b:'B',E:1e13,area:1},
   ...Array.from({length:20},(_,i)=>({id:'small-'+i,a:'A',b:'B',E:1e-6,area:1000}))
  ]
 };
 const original=clone(model);
 const naiveStiffness=[1e16,...Array(20).fill(1)].reduce((sum,value)=>sum+value,0);
 assert.equal(naiveStiffness,1e16,'naive sequential assembly loses all twenty 1 N/m members');
 const expected=1e16/(1e16+20);
 const result=fem.solve(model);
 const displacement=result.displacements.find(node=>node.id==='B').x;
 assert.ok(Math.abs(displacement-expected)<=2e-16,
  'diagonal-scaled FEM displacement must reflect the compensated 1e16+20 N/m stiffness: '+displacement);
 assert.ok(displacement<1-1e-15,'the old naive assembly incorrectly returns exactly 1 m');
 assert.ok(result.residual<1e-6,'free-DOF equilibrium residual remains within the solver contract');
 assert.ok(result.energyError<1e-6,'strain-energy verification remains within the solver contract');
 assert.equal(result.members.length,21);
 assert.deepEqual(model,original,'FEM solve must not mutate the source model');
});

test('global stiffness assembly scales before direction-cosine products near the subnormal limit',()=>{
 const model={
  nodes:[
   {id:'A',x:0,y:0,fixX:true,fixY:true,fx:0,fy:0},
   {id:'B',x:2e-12,y:2e-12,fixX:false,fixY:true,fx:Number.MIN_VALUE,fy:0}
  ],
  members:Array.from({length:20},(_,i)=>({id:'S'+i,a:'A',b:'B',E:1e-323,area:1e-15}))
 };
 const original=clone(model);
 const parsed=fem.parseModel(model), member=parsed.members[0];
 assert.equal(member.stiffness,Number.MIN_VALUE,'the member stiffness must remain the minimum positive subnormal');
 assert.equal(member.stiffness*member.c*member.c,Number.MIN_VALUE,
  'left-to-right multiplication double-rounds each subnormal contribution upward');
 assert.equal(member.stiffness*(member.c*member.c),0,
  'rounding the direction-cosine product first shows the individual exact product is below half a subnormal ulp');
 const force=Number.MIN_VALUE*1000;
 const expectedCoefficient=Number.MIN_VALUE*10;
 const naiveCoefficient=Number.MIN_VALUE*20;
 assert.equal(force/expectedCoefficient,100);
 assert.equal(force/naiveCoefficient,50,'the previous sequential product path doubles the assembled coefficient');
 const result=fem.solve(model);
 const displacement=result.displacements.find(node=>node.id==='B').x;
 assert.equal(displacement,100,'scale-first assembly must retain the correctly rounded sum of twenty subnormal products');
 assert.equal(result.residual,0);
 assert.ok(result.energyError<1e-6);
 assert.equal(result.forceBalance.x,0);
 assert.equal(result.members.length,20);
 assert.deepEqual(model,original,'FEM solve must not mutate the source model');
});
