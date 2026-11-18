/* ProMathStudio · structural-truss-fem-2d
   Small-displacement, pin-jointed, axial-only linear 2D truss FEM. SI internally.
   No external dependencies; callable from Node and the browser. MIT licensed. */
(function (root, make) {
  'use strict';
  const api = make();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) {
    root.ProMathTrussFEM = api;
    // Preserve the prior TrussStudio.solve SI-unit API for external consumers.
    root.TrussStudio = {
      example: {nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true},{id:'B',x:2,y:0,fixY:true},{id:'C',x:1,y:1,fy:-10000}],
        members:[{id:'AB',a:'A',b:'B',E:200e9,A:0.001},{id:'AC',a:'A',b:'C',E:200e9,A:0.001},{id:'BC',a:'B',b:'C',E:200e9,A:0.001}]},
      solve: model => {
        const result=api.solve(api.fromLegacy(model));
        return {nodes:result.nodes.map((n,i)=>({...model.nodes[i],ux:result.displacements[i].x,uy:result.displacements[i].y,
          rx:result.reactions.find(r=>r.id===n.id)?.rx??0,ry:result.reactions.find(r=>r.id===n.id)?.ry??0})),
          members:result.members.map(m=>({id:m.id,force:m.force,stress:m.stress,strain:m.strain})),
          residual:result.residual,maxDisplacement:result.maxDisplacement.magnitude};
      }
    };
  }
})(typeof window !== 'undefined' ? window : globalThis, function () {
  'use strict';
  const MAX_NODES = 80, MAX_MEMBERS = 240;
  const finite = (v, name) => {
    if (v === null || v === undefined || v === '' || typeof v === 'boolean' || typeof v === 'object' || typeof v === 'function') throw Error(name + ' must be a finite number.');
    const n = Number(v);
    if (!Number.isFinite(n)) throw Error(name + ' must be a finite number.');
    return n;
  };
  const requiredId = (v, name) => {
    const id = String(v ?? '').trim();
    if (!/^[A-Za-z0-9_-]{1,24}$/.test(id)) throw Error(name + ' needs a unique 1–24 character ID (letters, digits, - or _).');
    return id;
  };
  function parseModel(model) {
    if (!model || typeof model !== 'object' || !Array.isArray(model.nodes) || !Array.isArray(model.members)) {
      throw Error('Provide a model with nodes and members arrays.');
    }
    if (model.nodes.length < 2 || model.nodes.length > MAX_NODES || model.members.length < 1 || model.members.length > MAX_MEMBERS) {
      throw Error('Use 2–'+MAX_NODES+' nodes and 1–'+MAX_MEMBERS+' members.');
    }
    const ids = new Set();
    const nodes = model.nodes.map((row, i) => {
      if (!row || typeof row !== 'object' || Array.isArray(row)) throw Error('Node ' + (i + 1) + ' must be an object.');
      const id = requiredId(row.id, 'Node ' + (i + 1));
      if (ids.has(id)) throw Error('Duplicate node ID: ' + id + '.');
      ids.add(id);
      return {id, x: finite(row.x, id + ' x (m)'), y: finite(row.y, id + ' y (m)'),
        fixX: row.fixX === true || row.fixX === 'true',
        fixY: row.fixY === true || row.fixY === 'true',
        fx: finite(row.fx ?? 0, id + ' Fx (kN)') * 1000,
        fy: finite(row.fy ?? 0, id + ' Fy (kN)') * 1000};
    });
    const ix = new Map(nodes.map((n, i) => [n.id, i]));
    const members = model.members.map((row, i) => {
      if (!row || typeof row !== 'object' || Array.isArray(row)) throw Error('Member ' + (i + 1) + ' must be an object.');
      const id = requiredId(row.id, 'Member ' + (i + 1));
      const a = ix.get(String(row.a).trim()), b = ix.get(String(row.b).trim());
      if (a === undefined || b === undefined) throw Error('Member ' + id + ': end nodes must exist.');
      if (a === b) throw Error('Member ' + id + ': both ends cannot be the same node.');
      const E = finite(row.E, id + ' E (GPa)') * 1e9;
      const A = finite(row.area, id + ' area (mm²)') * 1e-6;
      if (E <= 0 || A <= 0) throw Error('Member ' + id + ': E and area must be positive.');
      const dx = nodes[b].x - nodes[a].x, dy = nodes[b].y - nodes[a].y;
      const L = Math.hypot(dx, dy);
      if (!Number.isFinite(L) || L <= 1e-12) throw Error('Member ' + id + ': zero/invalid length.');
      const EAbyL = E * A / L;
      if (!Number.isFinite(EAbyL)) throw Error('Member ' + id + ': stiffness overflow.');
      return {id, a, b, E, A, L, c: dx / L, s: dy / L, stiffness: EAbyL};
    });
    if (new Set(members.map(m => m.id)).size !== members.length) throw Error('Member IDs must be unique.');
    return {nodes, members};
  }
  function linearSolve(A, rhs) {
    // Scaled pivoting: reject near-mechanisms instead of dividing by tiny pivots.
    const n = rhs.length, m = A.map((row, i) => row.concat(rhs[i]));
    for (let k = 0; k < n; k++) {
      let piv = k, pivScore = -1;
      for (let i = k; i < n; i++) {
        const scale = Math.max(...m[i].slice(k, n).map(Math.abs));
        const score = scale ? Math.abs(m[i][k]) / scale : 0;
        if (score > pivScore) { pivScore = score; piv = i; }
      }
      // Compare to original row stiffness scale, which is kept outside elimination.
      if (!(pivScore > 1e-12) || !Number.isFinite(pivScore)) throw Error('Unstable or under-constrained truss (singular stiffness matrix).');
      [m[k], m[piv]] = [m[piv], m[k]];
      for (let i = k + 1; i < n; i++) {
        const q = m[i][k] / m[k][k];
        m[i][k] = 0;
        for (let j = k + 1; j <= n; j++) m[i][j] -= q * m[k][j];
      }
    }
    const x = new Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) {
      let s = m[i][n];
      for (let j = i + 1; j < n; j++) s -= m[i][j] * x[j];
      x[i] = s / m[i][i];
      if (!Number.isFinite(x[i])) throw Error('Numerical overflow in truss solution.');
    }
    return x;
  }
  function solve(input) {
    const {nodes, members} = parseModel(input), n = nodes.length, N = n * 2;
    const K = Array.from({length: N}, () => new Float64Array(N));
    const F = new Float64Array(N), fixed = new Set();
    nodes.forEach((node, i) => {
      F[2 * i] = node.fx; F[2 * i + 1] = node.fy;
      if (node.fixX) fixed.add(2 * i);
      if (node.fixY) fixed.add(2 * i + 1);
    });
    for (const m of members) {
      const v = [-m.c, -m.s, m.c, m.s], dof = [2*m.a, 2*m.a+1, 2*m.b, 2*m.b+1];
      for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) K[dof[i]][dof[j]] += m.stiffness*v[i]*v[j];
    }
    const free = Array.from({length: N}, (_, i) => i).filter(i => !fixed.has(i));
    if (!free.length) throw Error('At least one displacement DOF must remain free.');
    if (free.length > 150) throw Error('Model exceeds supported free DOFs.');
    const A = free.map(i => free.map(j => K[i][j]));
    // Normalize DOFs by diagonal scales: avoids rejecting valid structures when E/A vary.
    const diag = free.map(i => Math.sqrt(Math.max(K[i][i], 0)));
    if (diag.some(d => !(d > 0))) throw Error('Unstable or under-constrained truss (unconnected/free DOF).');
    const scaled = A.map((row, i) => row.map((v, j) => v / diag[i] / diag[j]));
    const ys = linearSolve(scaled, free.map((i, r) => F[i] / diag[r]));
    const u = new Float64Array(N);
    free.forEach((dof, i) => {u[dof] = ys[i] / diag[i];});
    const r = Array.from({length: N}, (_, i) => K[i].reduce((sum, v, j) => sum + v*u[j], -F[i]));
    const loadScale = Math.max(1, ...F.map(Math.abs));
    const residual = Math.max(0, ...free.map(i => Math.abs(r[i]))) / loadScale;
    if (!Number.isFinite(residual) || residual > 1e-6) throw Error('Numerical equilibrium residual too large; check member stiffness contrast or mechanism.');
    const displacements = nodes.map((node, i) => ({id: node.id, x: u[i*2], y: u[i*2+1], magnitude: Math.hypot(u[i*2], u[i*2+1])}));
    const results = members.map(m => {
      const extension = m.c*(u[2*m.b]-u[2*m.a]) + m.s*(u[2*m.b+1]-u[2*m.a+1]);
      const force = m.stiffness * extension;
      return {id: m.id, a: nodes[m.a].id, b: nodes[m.b].id, length: m.L, extension, force, stress: force/m.A,
        strain: extension/m.L, type: force > 1e-8 ? 'Tension' : force < -1e-8 ? 'Compression' : 'Zero'};
    });
    const reactions = nodes.map((node, i) => ({id: node.id, rx: node.fixX ? r[2*i] : 0, ry: node.fixY ? r[2*i+1] : 0}))
      .filter(q => nodes.find(n => n.id === q.id).fixX || nodes.find(n => n.id === q.id).fixY);
    const forceSum = nodes.reduce((a, b) => [a[0]+b.fx, a[1]+b.fy], [0, 0]);
    const reactionSum = reactions.reduce((a, b) => [a[0]+b.rx, a[1]+b.ry], [0, 0]);
    const externalWork = free.reduce((sum, i) => sum + F[i] * u[i], 0);
    const elasticEnergy = results.reduce((sum, m) => sum + m.force*m.extension/2, 0);
    const energyError = Math.abs(2*elasticEnergy-externalWork)/Math.max(1, Math.abs(externalWork));
    if (!Number.isFinite(energyError) || energyError > 1e-6) throw Error('Numerical energy verification failed.');
    const maxDisplacement = displacements.reduce((a,b)=>b.magnitude>a.magnitude?b:a,displacements[0]);
    const maxStress = results.reduce((a,b)=>Math.abs(b.stress)>Math.abs(a.stress)?b:a,results[0]);
    return {id:'structural-truss-fem-2d',nodes,members:results,displacements,reactions,maxDisplacement,maxStress,
      residual,energyError,elasticEnergy,forceBalance:{x:forceSum[0]+reactionSum[0],y:forceSum[1]+reactionSum[1]},
      assumptions:'2D pin-connected truss; linear elastic axial bars; small deformation; static loads; supported DOFs fixed at zero. No member buckling, plasticity, geometric nonlinearity, thermal effects, safety factors or design-code certification.'};
  }
  const examples = {
    triangle: {nodes:[
      {id:'A',x:0,y:0,fixX:true,fixY:true,fx:0,fy:0},
      {id:'B',x:4,y:0,fixX:false,fixY:true,fx:0,fy:0},
      {id:'C',x:2,y:3,fixX:false,fixY:false,fx:0,fy:-20}],
      members:[{id:'AB',a:'A',b:'B',E:210,area:1200},{id:'AC',a:'A',b:'C',E:210,area:1200},{id:'BC',a:'B',b:'C',E:210,area:1200}]},
    bar: {nodes:[{id:'A',x:0,y:0,fixX:true,fixY:true,fx:0,fy:0},
        {id:'B',x:2,y:0,fixX:false,fixY:true,fx:1,fy:0}],
      members:[{id:'AB',a:'A',b:'B',E:200,area:1000}]}
  };
  function fromLegacy(model) {
    if (!model || !Array.isArray(model.nodes) || !Array.isArray(model.members) ||
        model.nodes.some(n => !n || typeof n !== 'object' || Array.isArray(n)) ||
        model.members.some(m => !m || typeof m !== 'object' || Array.isArray(m))) {
      throw Error('Invalid legacy truss model: nodes and members must contain objects.');
    }
    const legacyCount = model.members.filter(m => m.A !== undefined).length;
    if (!legacyCount) return model;
    if (legacyCount !== model.members.length || model.members.some(m => m.area !== undefined)) {
      throw Error('Mixed legacy SI and current truss member units are not supported.');
    }
    return {nodes: model.nodes.map(n => ({...n, fx: finite(n.fx ?? 0, 'Legacy Fx (N)') / 1000,
      fy: finite(n.fy ?? 0, 'Legacy Fy (N)') / 1000})),
      members: model.members.map(m => ({id: m.id, a: m.a, b: m.b,
        E: finite(m.E, 'Legacy E (Pa)') / 1e9, area: finite(m.A, 'Legacy area (m²)') * 1e6}))};
  }
  return Object.freeze({solve, parseModel, fromLegacy, examples, id:'structural-truss-fem-2d'});
});
