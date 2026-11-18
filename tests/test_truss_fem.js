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
