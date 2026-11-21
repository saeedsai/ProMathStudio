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
    if (v === null || v === undefined || (typeof v === 'string' && !v.trim()) || typeof v === 'boolean' || typeof v === 'bigint' || typeof v === 'symbol' || typeof v === 'object' || typeof v === 'function') throw Error(name + ' must be a finite number.');
    const n = Number(v);
    if (!Number.isFinite(n)) throw Error(name + ' must be a finite number.');
    return n;
  };
  const finiteScaled = (v, name, scale) => {
    const result = finite(v, name) * scale;
    if (!Number.isFinite(result)) throw Error(name + ' exceeds the supported SI range.');
    return result;
  };
  // Solid, concentric hollow, open-channel and I-section properties in mm units.
  // Returns centroidal Ixx/Iyy, section moduli and radii of gyration for both axes.
  // Composite open sections use non-overlapping rectangles and the parallel-axis theorem.
  function sectionProperties(shape, dimensions) {
    const rectangular = shape === 'rectangle' || shape === 'hollow-rectangle';
    const circular = shape === 'solid-circle' || shape === 'hollow-circle';
    const composite = shape === 'channel' || shape === 'i-section';
    if (!rectangular && !circular && !composite) throw Error('Section shape must be rectangle, hollow-rectangle, solid-circle, hollow-circle, channel or i-section.');
    if (!dimensions || typeof dimensions !== 'object' || Array.isArray(dimensions)) throw Error('Section dimensions must be an object.');
    let area, secondMoment, secondMomentPerpendicular, axis, perpendicularAxis, centroid = null;
    let boundsWidth, boundsHeight, centroidX, centroidY;
    if (composite) {
      const width = finite(dimensions.width, 'Section outer width B (mm)');
      const depth = finite(dimensions.height, 'Section outer depth H (mm)');
      const webThickness = finite(dimensions.webThickness, 'Section web thickness tw (mm)');
      const flangeThickness = finite(dimensions.flangeThickness, 'Section flange thickness tf (mm)');
      if (!(width > 0) || !(depth > 0) || !(webThickness > 0) || !(webThickness < width) ||
          !(flangeThickness > 0) || !(2 * flangeThickness < depth)) {
        throw Error('Section B, H, tw and tf must be positive, with tw < B and 2·tf < H.');
      }
      boundsWidth = width;
      boundsHeight = depth;
      // Channel web is on the left and both flanges extend right.
      // The I-section web is centered between equal-width top and bottom flanges.
      const pieces = shape === 'channel'
        ? [
            {x:0,y:0,width:webThickness,height:depth},
            {x:webThickness,y:0,width:width-webThickness,height:flangeThickness},
            {x:webThickness,y:depth-flangeThickness,width:width-webThickness,height:flangeThickness}
          ]
        : [
            {x:0,y:0,width,height:flangeThickness},
            {x:(width-webThickness)/2,y:flangeThickness,width:webThickness,height:depth-2*flangeThickness},
            {x:0,y:depth-flangeThickness,width,height:flangeThickness}
          ];
      const pieceMetrics = pieces.map((piece,index) => {
        const pieceArea = finite(piece.width * piece.height, 'Composite section rectangle '+(index+1)+' area (mm²)');
        if (!(pieceArea > 0)) throw Error('Composite section area underflow; increase dimensions.');
        return {...piece,area:pieceArea,
          cx:finite(piece.x + piece.width/2, 'Composite section rectangle centroid x (mm)'),
          cy:finite(piece.y + piece.height/2, 'Composite section rectangle centroid y (mm)')};
      });
      area = finite(pieceMetrics.reduce((sum,piece)=>sum+piece.area,0), 'Composite section area (mm²)');
      if (!(area > 0)) throw Error('Composite section area underflow; increase dimensions.');
      centroidX = finite(pieceMetrics.reduce((sum,piece)=>sum+piece.area*piece.cx,0)/area, 'Composite section centroid x (mm)');
      centroidY = finite(pieceMetrics.reduce((sum,piece)=>sum+piece.area*piece.cy,0)/area, 'Composite section centroid y (mm)');
      secondMoment = finite(pieceMetrics.reduce((sum,piece)=>{
        const local = finite(piece.width*piece.height*piece.height*piece.height/12, 'Composite rectangle local Ixx (mm⁴)');
        const offset = finite(piece.area*(piece.cy-centroidY)*(piece.cy-centroidY), 'Composite rectangle Ixx offset (mm⁴)');
        return sum+local+offset;
      },0), 'Composite section Ixx (mm⁴)');
      secondMomentPerpendicular = finite(pieceMetrics.reduce((sum,piece)=>{
        const local = finite(piece.height*piece.width*piece.width*piece.width/12, 'Composite rectangle local Iyy (mm⁴)');
        const offset = finite(piece.area*(piece.cx-centroidX)*(piece.cx-centroidX), 'Composite rectangle Iyy offset (mm⁴)');
        return sum+local+offset;
      },0), 'Composite section Iyy (mm⁴)');
      centroid = {x:centroidX,y:centroidY};
      axis = 'centroidal horizontal axis (Ixx)';
      perpendicularAxis = 'centroidal vertical axis (Iyy)';
    } else if (rectangular) {
      const width = finite(dimensions.width, 'Rectangle width b (mm)');
      const depth = finite(dimensions.height, 'Rectangle depth h (mm)');
      if (!(width > 0) || !(depth > 0)) throw Error('Rectangle width and depth must be positive.');
      boundsWidth = width;
      boundsHeight = depth;
      centroidX = width/2;
      centroidY = depth/2;
      const hollow = shape === 'hollow-rectangle';
      const innerWidth = hollow ? finite(dimensions.innerWidth, 'Hollow rectangle inner width bi (mm)') : 0;
      const innerHeight = hollow ? finite(dimensions.innerHeight, 'Hollow rectangle inner depth hi (mm)') : 0;
      if (hollow && (!(innerWidth > 0) || !(innerWidth < width) || !(innerHeight > 0) || !(innerHeight < depth))) {
        throw Error('Hollow rectangle inner width and depth must be positive and smaller than the outer dimensions.');
      }
      const outerArea = finite(width * depth, 'Rectangle outer area (mm²)');
      const innerArea = hollow ? finite(innerWidth * innerHeight, 'Hollow rectangle inner area (mm²)') : 0;
      if (hollow && !(innerArea > 0)) throw Error('Hollow rectangle inner area underflow; increase the inner dimensions.');
      area = finite(outerArea - innerArea, 'Rectangle net area (mm²)');
      const outerIxx = finite(width * depth * depth * depth / 12, 'Rectangle outer Ixx (mm⁴)');
      const innerIxx = hollow ? finite(innerWidth * innerHeight * innerHeight * innerHeight / 12, 'Hollow rectangle inner Ixx (mm⁴)') : 0;
      secondMoment = finite(outerIxx - innerIxx, 'Rectangle Ixx (mm⁴)');
      const outerIyy = finite(depth * width * width * width / 12, 'Rectangle outer Iyy (mm⁴)');
      const innerIyy = hollow ? finite(innerHeight * innerWidth * innerWidth * innerWidth / 12, 'Hollow rectangle inner Iyy (mm⁴)') : 0;
      secondMomentPerpendicular = finite(outerIyy - innerIyy, 'Rectangle Iyy (mm⁴)');
      axis = 'centroidal axis parallel to width';
      perpendicularAxis = 'centroidal axis parallel to depth';
    } else {
      const diameter = finite(dimensions.diameter, 'Circle outer diameter Do (mm)');
      if (!(diameter > 0)) throw Error('Circle outer diameter must be positive.');
      boundsWidth = diameter;
      boundsHeight = diameter;
      centroidX = diameter/2;
      centroidY = diameter/2;
      const hollow = shape === 'hollow-circle';
      const innerDiameter = hollow ? finite(dimensions.innerDiameter, 'Hollow circle inner diameter Di (mm)') : 0;
      if (hollow && (!(innerDiameter > 0) || !(innerDiameter < diameter))) {
        throw Error('Hollow circle inner diameter must be positive and smaller than the outer diameter.');
      }
      const outerSquare = finite(diameter * diameter, 'Circle outer diameter squared (mm²)');
      const innerSquare = hollow ? finite(innerDiameter * innerDiameter, 'Hollow circle inner diameter squared (mm²)') : 0;
      if (hollow && !(innerSquare > 0)) throw Error('Hollow circle inner area underflow; increase the inner diameter.');
      area = finite(Math.PI * (outerSquare - innerSquare) / 4, 'Circle net area (mm²)');
      const outerFourth = finite(outerSquare * outerSquare, 'Circle outer diameter to fourth power (mm⁴)');
      const innerFourth = hollow ? finite(innerSquare * innerSquare, 'Hollow circle inner diameter to fourth power (mm⁴)') : 0;
      secondMoment = finite(Math.PI * (outerFourth - innerFourth) / 64, 'Circle centroidal second moment I (mm⁴)');
      secondMomentPerpendicular = secondMoment;
      axis = 'centroidal diameter axis';
      perpendicularAxis = 'centroidal diameter axis';
    }
    if (!(area > 0)) throw Error('Section area underflow; increase the dimensions or use a resolvable wall thickness.');
    if (!(secondMoment > 0)) throw Error('Section second moment underflow (Ixx); increase the dimensions or use a resolvable wall thickness.');
    if (!(secondMomentPerpendicular > 0)) throw Error('Section second moment underflow (Iyy); increase the dimensions or use a resolvable wall thickness.');
    const extremeFiberDistanceAboutX = finite(Math.max(centroidY, boundsHeight-centroidY), 'Extreme-fibre distance about X (mm)');
    const extremeFiberDistanceAboutY = finite(Math.max(centroidX, boundsWidth-centroidX), 'Extreme-fibre distance about Y (mm)');
    if (!(extremeFiberDistanceAboutX > 0) || !(extremeFiberDistanceAboutY > 0)) throw Error('Section extreme-fibre distance underflow.');
    const sectionModulusX = finite(secondMoment/extremeFiberDistanceAboutX, 'Section modulus Sx (mm³)');
    const sectionModulusY = finite(secondMomentPerpendicular/extremeFiberDistanceAboutY, 'Section modulus Sy (mm³)');
    const radiusOfGyrationX = finite(Math.sqrt(secondMoment/area), 'Radius of gyration rx (mm)');
    const radiusOfGyrationY = finite(Math.sqrt(secondMomentPerpendicular/area), 'Radius of gyration ry (mm)');
    if (!(sectionModulusX > 0) || !(sectionModulusY > 0)) throw Error('Section modulus underflow; increase the section dimensions or wall thickness.');
    if (!(radiusOfGyrationX > 0) || !(radiusOfGyrationY > 0)) throw Error('Radius of gyration underflow; increase the section dimensions.');
    return Object.freeze({shape, area, secondMoment, secondMomentPerpendicular, axis, perpendicularAxis,
      sectionModulusX, sectionModulusY, radiusOfGyrationX, radiusOfGyrationY,
      extremeFiberDistanceAboutX, extremeFiberDistanceAboutY,
      ...(centroid ? {centroid:Object.freeze(centroid)} : {})});
  }
  const supportFlag = (value, name) => {
    if (value === undefined || value === false || value === 'false') return false;
    if (value === true || value === 'true') return true;
    throw Error(name + ' must be true or false.');
  };
  const requiredId = (v, name) => {
    if (typeof v !== 'string') throw Error(name + ' ID must be a string.');
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
        fixX: supportFlag(row.fixX, id + ' fixX'),
        fixY: supportFlag(row.fixY, id + ' fixY'),
        fx: finiteScaled(row.fx ?? 0, id + ' Fx (kN)', 1000),
        fy: finiteScaled(row.fy ?? 0, id + ' Fy (kN)', 1000)};
    });
    const ix = new Map(nodes.map((n, i) => [n.id, i]));
    const members = model.members.map((row, i) => {
      if (!row || typeof row !== 'object' || Array.isArray(row)) throw Error('Member ' + (i + 1) + ' must be an object.');
      const id = requiredId(row.id, 'Member ' + (i + 1));
      if (typeof row.a !== 'string' || typeof row.b !== 'string') throw Error('Member ' + id + ': end node IDs must be strings.');
      const a = ix.get(row.a.trim()), b = ix.get(row.b.trim());
      if (a === undefined || b === undefined) throw Error('Member ' + id + ': end nodes must exist.');
      if (a === b) throw Error('Member ' + id + ': both ends cannot be the same node.');
      const E = finiteScaled(row.E, id + ' E (GPa)', 1e9);
      const A = finite(row.area, id + ' area (mm²)') * 1e-6;
      if (E <= 0 || A <= 0) throw Error('Member ' + id + ': E and area must be positive.');
      const dx = nodes[b].x - nodes[a].x, dy = nodes[b].y - nodes[a].y;
      const L = Math.hypot(dx, dy);
      if (!Number.isFinite(L) || L <= 1e-12) throw Error('Member ' + id + ': zero/invalid length.');
      const EAbyL = E * A / L;
      if (!Number.isFinite(EAbyL)) throw Error('Member ' + id + ': stiffness overflow.');
      if (!(EAbyL > 0)) throw Error('Member ' + id + ': stiffness underflow; increase E or area.');
      // Density is an optional SI quantity shared by Studio and legacy imports.
      // Blank/null means unknown; zero is valid, while negative/non-finite values are not.
      const density = row.density === undefined || row.density === null ||
        (typeof row.density === 'string' && !row.density.trim()) ? null : finite(row.density, id + ' density (kg/m³)');
      if (density !== null && density < 0) throw Error('Member ' + id + ': density must be non-negative.');
      const mass = density === null ? null : finite(finite(L * A, 'Member ' + id + ' material volume (m³)') * density, 'Member ' + id + ' mass (kg)');
      // I and K are independent member properties; the Euler estimate is available only when both are supplied.
      const hasI = row.I !== undefined && row.I !== null && !(typeof row.I === 'string' && !row.I.trim());
      const hasK = row.K !== undefined && row.K !== null && !(typeof row.K === 'string' && !row.K.trim());
      let secondMoment = null, effectiveLengthFactor = null, eulerCriticalLoad = null;
      if (hasI) {
        secondMoment = finiteScaled(row.I, id + ' I (mm⁴)', 1e-12);
        if (!(secondMoment > 0)) throw Error('Member ' + id + ': I must be positive.');
      }
      if (hasK) {
        effectiveLengthFactor = finite(row.K, id + ' K (dimensionless)');
        if (!(effectiveLengthFactor > 0)) throw Error('Member ' + id + ': K must be positive.');
      }
      if (hasI && hasK) {
        const effectiveLength = finite(effectiveLengthFactor * L, id + ' effective buckling length (m)');
        if (!(effectiveLength > 0)) throw Error('Member ' + id + ': effective buckling length underflow.');
        const numerator = finite(Math.PI * Math.PI * E * secondMoment, id + ' Euler buckling numerator');
        const denominator = finite(effectiveLength * effectiveLength, id + ' effective buckling length squared');
        if (!(denominator > 0)) throw Error('Member ' + id + ': effective buckling length squared underflow.');
        eulerCriticalLoad = finite(numerator / denominator, id + ' Euler critical load (N)');
        if (!(eulerCriticalLoad > 0)) throw Error('Member ' + id + ': Euler critical load underflow; increase I or E, or reduce K·L.');
      }
      return {id, a, b, E, A, L, c: dx / L, s: dy / L, stiffness: EAbyL,
        density, mass, secondMoment, effectiveLengthFactor, eulerCriticalLoad};
    });
    if (new Set(members.map(m => m.id)).size !== members.length) throw Error('Member IDs must be unique.');
    return {nodes, members};
  }
  function linearSolve(A, rhs) {
    // Scaled partial pivoting must retain each original row scale. Re-scaling by
    // the shrinking trailing row can make a tiny singular pivot score as one.
    const n = rhs.length, m = A.map((row, i) => row.concat(rhs[i]));
    const rowScales = A.map(row => Math.max(...row.map(Math.abs)));
    for (let k = 0; k < n; k++) {
      let piv = k, pivScore = -1;
      for (let i = k; i < n; i++) {
        const score = rowScales[i] ? Math.abs(m[i][k]) / rowScales[i] : 0;
        if (score > pivScore) { pivScore = score; piv = i; }
      }
      if (!(pivScore > 1e-12) || !Number.isFinite(pivScore)) throw Error('Unstable or under-constrained truss (singular stiffness matrix).');
      [m[k], m[piv]] = [m[piv], m[k]];
      [rowScales[k], rowScales[piv]] = [rowScales[piv], rowScales[k]];
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
      const compressionDemand = force < -1e-8 ? -force : 0;
      // Only compression has an Euler demand. Tension and zero force deliberately avoid division.
      const eulerUtilization = m.eulerCriticalLoad !== null && compressionDemand > 0
        ? finite(compressionDemand / m.eulerCriticalLoad, 'Member ' + m.id + ' Euler utilization') : null;
      const eulerLoadRatio = m.eulerCriticalLoad !== null && compressionDemand > 0
        ? finite(m.eulerCriticalLoad / compressionDemand, 'Member ' + m.id + ' Euler load ratio') : null;
      const eulerAssessment = m.eulerCriticalLoad === null ? 'Not assessed (I/K missing)' :
        compressionDemand > 0 ? (eulerUtilization >= 1 ? 'At/above ideal Euler load' : 'Below ideal Euler load') :
        force > 1e-8 ? 'Tension — not applicable' : 'No compression demand';
      return {id: m.id, a: nodes[m.a].id, b: nodes[m.b].id, length: m.L, extension, force, stress: force/m.A,
        strain: extension/m.L, type: force > 1e-8 ? 'Tension' : force < -1e-8 ? 'Compression' : 'Zero',
        compressionDemand,eulerCriticalLoad:m.eulerCriticalLoad,eulerUtilization,eulerLoadRatio,eulerAssessment};
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
      assumptions:'2D pin-connected truss; linear elastic axial bars; small deformation; static loads; supported DOFs fixed at zero. Optional post-solve Euler comparison is an ideal elastic compression-only screen when I/K are supplied; no geometric buckling, imperfections, yielding, code resistance factors or design-code certification.'};
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
        E: finite(m.E, 'Legacy E (Pa)') / 1e9, area: finiteScaled(m.A, 'Legacy area (m²)', 1e6),
        ...(m.density === undefined ? {} : {density: m.density}),
        ...(m.I === undefined || m.I === null || (typeof m.I === 'string' && !m.I.trim()) ? {} : {I: finiteScaled(m.I, 'Legacy I (m⁴)', 1e12)}),
        ...(m.K === undefined ? {} : {K: m.K})}))};
  }
  // Import JSON as a model, retaining the original public-unit values and IDs.
  // Validation is performed on a converted copy, not on the returned document.
  function importJSON(text) {
    if (typeof text !== 'string') throw Error('Truss JSON input must be a string.');
    // Bound UTF-8 bytes (not UTF-16 code units) before parsing oversized imports.
    if (new TextEncoder().encode(text).byteLength > 1024 * 1024) throw Error('Truss JSON document exceeds the 1 MiB import limit.');
    let model;
    // Accept a single UTF-8 BOM from imported text files; count it toward the byte limit.
    try { model = JSON.parse(text.charCodeAt(0) === 0xFEFF ? text.slice(1) : text); } catch (_) { throw Error('Invalid truss JSON document.'); }
    parseModel(fromLegacy(model));
    return model;
  }
  // Export only validated models, retaining original current or legacy public units.
  function exportJSON(model) {
    parseModel(fromLegacy(model));
    let document;
    try { document = JSON.stringify(model, null, 2); }
    catch (_) { throw Error('Truss JSON export could not serialize the model.'); }
    if (typeof document !== 'string') throw Error('Truss JSON export must produce a document.');
    // Keep exports importable under the same UTF-8 byte budget.
    if (new TextEncoder().encode(document).byteLength > 1024 * 1024) throw Error('Truss JSON document exceeds the 1 MiB export limit.');
    // JSON.stringify invokes toJSON hooks; validate the actual serialized model too.
    parseModel(fromLegacy(JSON.parse(document)));
    return document;
  }
  // Public unit metadata for JSON file workflows; never infer units from magnitudes.
  function describeUnits(model) {
    parseModel(fromLegacy(model));
    const legacy = model.members.some(m => m.A !== undefined);
    return Object.freeze(legacy
      ? {system:'legacy-si',coordinates:'m',forces:'N',modulus:'Pa',area:'m²'}
      : {system:'studio',coordinates:'m',forces:'kN',modulus:'GPa',area:'mm²'});
  }
  // Solve a validated imported document in either public unit system. Results remain SI.
  function solveDocument(model) {
    const inputUnits = describeUnits(model);
    return {...solve(fromLegacy(model)), inputUnits};
  }
  // One-step file-to-solution entry point, preserving import validation and public unit labels.
  // Preview valid truss files without requiring structural stability.
  function inspectJSON(text) {
    const model = importJSON(text);
    const normalized = parseModel(fromLegacy(model));
    return {model, inputUnits: describeUnits(model), nodeCount: model.nodes.length,
      memberCount: model.members.length,
      // Topological components include isolated nodes; this is not a stability certificate.
      connectedComponentCount: (() => {
        const parent = normalized.nodes.map((_, i) => i);
        const rootOf = i => {
          while (parent[i] !== i) i = parent[i];
          return i;
        };
        for (const member of normalized.members) {
          const a = rootOf(member.a), b = rootOf(member.b);
          if (a !== b) parent[b] = a;
        }
        return new Set(parent.map((_, i) => rootOf(i))).size;
      })(),
      // Nodes without any incident member remain isolated even when other members form a component.
      isolatedNodeCount: (() => {
        const incident = new Set();
        for (const member of normalized.members) {
          incident.add(member.a);
          incident.add(member.b);
        }
        return normalized.nodes.length - incident.size;
      })(),
      // Sum member centreline lengths for material estimates; do not silently overflow.
      totalMemberLength: finite(normalized.members.reduce((sum, m) => sum + m.L, 0), 'Total member length (m)'),
      // Sum physical axial-bar volumes in m³; reject overflow before UI/material estimates.
      totalMemberVolume: finite(normalized.members.reduce((sum, m) => sum + finite(m.L * m.A, 'Total member volume (m³)'), 0), 'Total member volume (m³)'),
      // Per-member quantities stay in SI and are available even when the structure is unstable.
      memberMetrics: Object.freeze(normalized.members.map(member => Object.freeze({
        id: member.id,
        startNodeId: normalized.nodes[member.a].id,
        endNodeId: normalized.nodes[member.b].id,
        length: member.L,
        area: member.A,
        elasticModulus: member.E,
        // EA/L is axial stiffness in N/m; the existing validated FEM stiffness is reused.
        axialStiffness: member.stiffness,
        volume: finite(member.L * member.A, 'Member ' + member.id + ' material volume (m³)'),
        density: member.density,
        mass: member.mass,
        secondMoment: member.secondMoment,
        effectiveLengthFactor: member.effectiveLengthFactor,
        eulerCriticalLoad: member.eulerCriticalLoad
      }))),
      // Immutable geometry bounds in metres, including unconnected nodes of otherwise valid imports.
      bounds: Object.freeze((() => {
        const xs = normalized.nodes.map(n => n.x), ys = normalized.nodes.map(n => n.y);
        const minX = Math.min(...xs), maxX = Math.max(...xs);
        const minY = Math.min(...ys), maxY = Math.max(...ys);
        const width = finite(maxX - minX, 'Truss bounds width (m)');
        const height = finite(maxY - minY, 'Truss bounds height (m)');
        // The diagonal supports viewport fit; reject finite spans whose combined extent overflows.
        const diagonal = finite(Math.hypot(width, height), 'Truss bounds diagonal (m)');
        return {minX, maxX, minY, maxY, width, height, diagonal,
          centerX: minX + width / 2, centerY: minY + height / 2};
      })()),
      fixedDofCount: normalized.nodes.reduce((sum, n) => sum + Number(n.fixX) + Number(n.fixY), 0),
      // Count free x/y translations independently of structural stability.
      freeDofCount: normalized.nodes.reduce((sum, n) => sum + Number(!n.fixX) + Number(!n.fixY), 0),
      loadedNodeCount: normalized.nodes.filter(n => n.fx !== 0 || n.fy !== 0).length,
      // Count independently loaded translation components, including loads at supports.
      loadedDofCount: normalized.nodes.reduce((sum, n) => sum + Number(n.fx !== 0) + Number(n.fy !== 0), 0),
      // Loads at constrained translations produce reactions, not free displacement forcing.
      restrainedLoadedDofCount: normalized.nodes.reduce((sum, n) => sum + Number(n.fixX && n.fx !== 0) + Number(n.fixY && n.fy !== 0), 0),
      // Nonzero applied loads on unconstrained translations, excluding support reactions.
      freeLoadedDofCount: normalized.nodes.reduce((sum, n) => sum + Number(!n.fixX && n.fx !== 0) + Number(!n.fixY && n.fy !== 0), 0),
      appliedForce: Object.freeze((() => {
        const total = normalized.nodes.reduce((sum, n) => ({
          x: sum.x + n.fx, y: sum.y + n.fy
        }), {x: 0, y: 0});
        return {x: finite(total.x, 'Applied force x (N)'), y: finite(total.y, 'Applied force y (N)')};
      })()),
      // Signed z-axis moment about the global origin, in SI N·m.
      appliedMoment: finite(normalized.nodes.reduce((sum, n) => sum + n.x*n.fy - n.y*n.fx, 0), 'Applied moment (N·m)')};
  }
  // Export a validated per-member material schedule in explicit SI units without solving.
  function exportMaterialCSV(model) {
    const preview = inspectJSON(exportJSON(model));
    const rows = [
      ['Member ID', 'Start joint ID', 'End joint ID', 'Centreline length (m)', 'Cross-sectional area (m²)', 'Axial material volume (m³)', 'Elastic modulus (GPa)', 'Axial stiffness EA/L (kN/mm)', 'Density (kg/m³)', 'Member mass (kg)', 'Second moment of area I (mm⁴)', 'Effective length factor K (-)', 'Euler critical load Pcr (kN)'],
      ...preview.memberMetrics.map(member => [member.id, member.startNodeId, member.endNodeId,
        member.length, member.area, member.volume, member.elasticModulus / 1e9, member.axialStiffness / 1e6,
        member.density ?? '', member.mass ?? '',
        member.secondMoment === null ? '' : member.secondMoment * 1e12,
        member.effectiveLengthFactor ?? '',
        member.eulerCriticalLoad === null ? '' : member.eulerCriticalLoad / 1000])
    ];
    // Keep CSV numeric cells readable without exposing binary floating-point tails.
    // Sixteen significant digits retain near-double precision for engineering exports.
    const quote = value => {
      const text = typeof value === 'number' && Number.isFinite(value)
        ? String(Number(value.toPrecision(16))) : String(value);
      return '"' + text.replace(/"/g, '""') + '"';
    };
    return rows.map(row => row.map(quote).join(',')).join('\r\n') + '\r\n';
  }
  function solveJSON(text) {
    return solveDocument(importJSON(text));
  }
  return Object.freeze({solve, solveDocument, solveJSON, inspectJSON, exportMaterialCSV, sectionProperties, parseModel, fromLegacy, importJSON, exportJSON, describeUnits, examples, id:'structural-truss-fem-2d'});
});
