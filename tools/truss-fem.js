/* ProMathStudio · structural-truss-fem-2d
   Small-displacement, pin-jointed, axial-only linear 2D truss FEM. SI internally.
   No external dependencies; callable from Node and the browser. MIT licensed. */
(function (root, make) {
  'use strict';
  // Keep the legacy SI reference private; each public read receives an editable copy.
  const legacyExample = Object.freeze({
    nodes:Object.freeze([
      Object.freeze({id:'A',x:0,y:0,fixX:true,fixY:true}),
      Object.freeze({id:'B',x:2,y:0,fixY:true}),
      Object.freeze({id:'C',x:1,y:1,fy:-10000})
    ]),
    members:Object.freeze([
      Object.freeze({id:'AB',a:'A',b:'B',E:200e9,A:0.001}),
      Object.freeze({id:'AC',a:'A',b:'C',E:200e9,A:0.001}),
      Object.freeze({id:'BC',a:'B',b:'C',E:200e9,A:0.001})
    ])
  });
  const api = make();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) {
    root.ProMathTrussFEM = api;
    // Preserve the prior TrussStudio.solve SI-unit API for external consumers.
    root.TrussStudio = {
      get example() { return JSON.parse(JSON.stringify(legacyExample)); },
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
  const MAX_NODES = 80, MAX_MEMBERS = 240, MAX_IMPORT_BYTES = 1024 * 1024;
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
  // Correctly round the exact sum of finite binary64 inputs without an overflowing partial sum.
  // Each finite double is an integer multiple of 2^-1074; BigInt accumulates that integer exactly.
  // The final conversion rounds once to nearest, ties-to-even, and still returns a binary64 Number.
  function exactFiniteBinarySum(terms, name) {
    if (typeof BigInt !== 'function' || typeof DataView !== 'function') return null;
    const zero=BigInt(0), one=BigInt(1), shift32=BigInt(32), shift52=BigInt(52), shift63=BigInt(63);
    const signMask=one<<shift63, exponentMask=BigInt(2047), fractionMask=(one<<shift52)-one;
    const view=new DataView(new ArrayBuffer(8));
    let total=zero;
    for (const term of terms) {
      view.setFloat64(0,term,false);
      const bits=(BigInt(view.getUint32(0,false))<<shift32)|BigInt(view.getUint32(4,false));
      const negative=(bits&signMask)!==zero;
      const exponent=Number((bits>>shift52)&exponentMask);
      const fraction=bits&fractionMask;
      if (exponent===0 && fraction===zero) continue;
      const significand=exponent===0?fraction:(one<<shift52)|fraction;
      const shift=exponent===0?0:exponent-1;
      const magnitude=significand<<BigInt(shift);
      total+=negative?-magnitude:magnitude;
    }
    if (total===zero) return 0;
    const negative=total<zero;
    const magnitude=negative?-total:total;
    const bitLength=magnitude.toString(2).length;
    let result;
    if (bitLength<=53) {
      result=Number(magnitude)*Number.MIN_VALUE;
    } else {
      let shift=bitLength-53;
      let significand=magnitude>>BigInt(shift);
      const remainder=magnitude-(significand<<BigInt(shift));
      const halfway=one<<BigInt(shift-1);
      if (remainder>halfway || (remainder===halfway && (significand&one)!==zero)) significand+=one;
      if (significand===(one<<BigInt(53))) {significand>>=one;shift++;}
      const exponent=shift-1074;
      result=exponent>971?Infinity:Number(significand)*Math.pow(2,exponent);
    }
    return finite(negative?-result:result,name);
  }
  // Sum signed finite terms without overflowing intermediate partial sums.
  // Normalize by the largest magnitude, compensate rounding, and retain terms
  // whose normalized quotient underflows in a separately compensated residual.
  function finiteSignedSum(values, name) {
    const terms = Array.from(values, value => finite(value, name));
    const scale = Math.max(0, ...terms.map(value => Math.abs(value)));
    if (scale === 0) return 0;
    const hasPositive=terms.some(value=>value>0),hasNegative=terms.some(value=>value<0);
    if (hasPositive&&hasNegative) {
      const exact=exactFiniteBinarySum(terms,name);
      if (exact!==null) return exact;
    }
    const normalized = {sum:0, correction:0};
    const residual = {sum:0, correction:0};
    const add = (state, value) => {
      const next = state.sum + value;
      state.correction += Math.abs(state.sum) >= Math.abs(value)
        ? (state.sum - next) + value
        : (value - next) + state.sum;
      state.sum = next;
    };
    for (const term of terms) {
      const scaled = term / scale;
      if (Math.abs(scaled) < 2.2250738585072014e-308 && term !== 0) add(residual, term);
      else add(normalized, scaled);
    }
    const restored = (normalized.sum + normalized.correction) * scale;
    const smallResidual = residual.sum + residual.correction;
    return finite(restored + smallResidual, name);
  }
  // Preserve a representable EA/L when the intermediate E*A overflows or underflows.
  // Keep the direct expression for ordinary products so established results stay bit-identical.
  function positiveProductQuotient(a, b, c) {
    const product = a * b;
    const direct = product / c;
    const minNormal = 2.2250738585072014e-308;
    if (Number.isFinite(product) && product >= minNormal && Number.isFinite(direct) && direct > 0) {
      return direct;
    }
    const binaryParts = value => {
      let exponent = Math.floor(Math.log2(value));
      exponent = Math.max(-1074, Math.min(1023, exponent));
      let mantissa = value / (2 ** exponent);
      if (mantissa < 1) { mantissa *= 2; exponent--; }
      else if (mantissa >= 2) { mantissa /= 2; exponent++; }
      return {mantissa, exponent};
    };
    const left = binaryParts(a), right = binaryParts(b), divisor = binaryParts(c);
    let mantissa = left.mantissa * right.mantissa / divisor.mantissa;
    let exponent = left.exponent + right.exponent - divisor.exponent;
    if (mantissa >= 2) { mantissa /= 2; exponent++; }
    else if (mantissa < 1) { mantissa *= 2; exponent--; }
    if (exponent > 1023) return Infinity;
    if (exponent >= -1022) return mantissa * (2 ** exponent);
    if (exponent >= -1075) return (mantissa * (2 ** (exponent + 1022))) * minNormal;
    return 0;
  }
  // Preserve a representable L*A*density result when the intermediate volume overflows or underflows.
  // Keep the direct left-to-right product when both intermediate and final values are normal.
  function positiveProduct(a, b, c) {
    const product = a * b;
    const direct = product * c;
    const minNormal = 2.2250738585072014e-308;
    if (a === 0 || b === 0 || c === 0) return 0;
    if (Number.isFinite(product) && product >= minNormal &&
        Number.isFinite(direct) && direct >= minNormal) return direct;
    const binaryParts = value => {
      let exponent = Math.floor(Math.log2(value));
      exponent = Math.max(-1074, Math.min(1023, exponent));
      let mantissa = value / (2 ** exponent);
      if (mantissa < 1) { mantissa *= 2; exponent--; }
      else if (mantissa >= 2) { mantissa /= 2; exponent++; }
      return {mantissa, exponent};
    };
    const factors = [a, b, c].map(binaryParts);
    let mantissa = 1, exponent = 0;
    for (const part of factors) {
      mantissa *= part.mantissa;
      exponent += part.exponent;
      if (mantissa >= 2) { mantissa /= 2; exponent++; }
      else if (mantissa < 1) { mantissa *= 2; exponent--; }
    }
    if (exponent > 1023) return Infinity;
    if (exponent >= -1022) return mantissa * (2 ** exponent);
    if (exponent >= -1075) return (mantissa * (2 ** (exponent + 1022))) * minNormal;
    return 0;
  }
  // Preserve a representable product of positive factors divided by positive factors.
  // The caller supplies the old direct intermediates so ordinary calculations retain their exact order.
  function positiveProductQuotientFactors(numerators, denominators, directNumerator, directDenominator) {
    const minNormal = 2.2250738585072014e-308;
    const direct = directNumerator / directDenominator;
    if (Number.isFinite(directNumerator) && directNumerator >= minNormal &&
        Number.isFinite(directDenominator) && directDenominator >= minNormal &&
        Number.isFinite(direct) && direct > 0) return direct;
    const binaryParts = value => {
      let exponent = Math.floor(Math.log2(value));
      exponent = Math.max(-1074, Math.min(1023, exponent));
      let mantissa = value / (2 ** exponent);
      if (mantissa < 1) { mantissa *= 2; exponent--; }
      else if (mantissa >= 2) { mantissa /= 2; exponent++; }
      return {mantissa, exponent};
    };
    let mantissa = 1, exponent = 0;
    const accumulate = (value, direction) => {
      const part = binaryParts(value);
      mantissa = direction > 0 ? mantissa * part.mantissa : mantissa / part.mantissa;
      exponent += direction * part.exponent;
      const adjustment = Math.floor(Math.log2(mantissa));
      mantissa /= 2 ** adjustment;
      exponent += adjustment;
    };
    for (const value of numerators) accumulate(value, 1);
    for (const value of denominators) accumulate(value, -1);
    if (exponent > 1023) return Infinity;
    if (exponent >= -1022) return mantissa * (2 ** exponent);
    if (exponent >= -1075) return (mantissa * (2 ** (exponent + 1022))) * minNormal;
    return 0;
  }
  // Null and whitespace-only optional properties mean "not supplied"; numeric zero remains present.
  const hasOptionalValue = value => value !== undefined && value !== null &&
    !(typeof value === 'string' && !value.trim());
  // Share the File.size / ArrayBuffer.byteLength contract between the browser UI and tests.
  function validateImportByteLength(declaredSize, actualByteLength) {
    const safeLength = value => Number.isSafeInteger(value) && value >= 0;
    if (!safeLength(declaredSize)) throw Error('Model JSON file size is invalid.');
    if (declaredSize > MAX_IMPORT_BYTES) throw Error('Model JSON exceeds 1 MiB.');
    if (arguments.length > 1) {
      // Distinguish a broken/invalid read result from a legitimate file over the size budget.
      if (!safeLength(actualByteLength)) {
        throw Error('Model JSON read returned an invalid byte length.');
      }
      if (actualByteLength > MAX_IMPORT_BYTES) throw Error('Model JSON exceeds 1 MiB.');
      if (actualByteLength !== declaredSize) {
        const direction = actualByteLength < declaredSize ? 'fewer' : 'more';
        throw Error(`Model JSON file size does not match the bytes read. (read returned ${direction} bytes than declared; expected ${declaredSize} bytes, received ${actualByteLength} bytes).`);
      }
    }
    return declaredSize;
  }
  // Decode actual uploaded bytes strictly; preserve a counted BOM for importJSON to strip.
  function decodeImportBytes(bytes) {
    const view = bytes instanceof ArrayBuffer
      ? new Uint8Array(bytes)
      : ArrayBuffer.isView(bytes)
        ? new Uint8Array(bytes.buffer, bytes.byteOffset, bytes.byteLength)
        : null;
    if (!view) throw Error('Model JSON bytes must be an ArrayBuffer or typed array.');
    validateImportByteLength(view.byteLength);
    try {
      return new TextDecoder('utf-8', {fatal:true, ignoreBOM:true}).decode(view);
    } catch (_) {
      throw Error('Model JSON must be valid UTF-8.');
    }
  }
  // Solid, concentric hollow, open-channel and I-section properties in mm units.
  // Returns centroidal Ixx/Iyy, section moduli and radii of gyration for both axes.
  // Composite open sections use non-overlapping rectangles and the parallel-axis theorem.
  function sectionProperties(shape, dimensions) {
    // Divide before the final multiplication: b*h^3/12 can be finite even when b*h^3 overflows.
    const rectangleIxx = (piece, label, factor = 1) => {
      const scaledHeight = piece.height * Math.sqrt(factor);
      return finite(piece.width*piece.height*(scaledHeight/12)*scaledHeight, label);
    };
    const rectangleIyy = (piece, label, factor = 1) => {
      const scaledWidth = piece.width * Math.sqrt(factor);
      return finite(piece.height*piece.width*(scaledWidth/12)*scaledWidth, label);
    };
    const rectangular = shape === 'rectangle' || shape === 'hollow-rectangle';
    const MIN_NORMAL = 2.2250738585072014e-308;
    // Restore products of extreme geometry scales without overflowing intermediate powers.
    const scaleProduct = (...values) => {
      let sign=1, mantissa=1, exponent=0;
      for (const value of values) {
        if (value === 0) return 0;
        if (!Number.isFinite(value)) return value;
        if (value < 0) sign=-sign;
        const absolute=Math.abs(value);
        let power=Math.floor(Math.log2(absolute));
        let unit=Math.pow(2,power);
        if (!Number.isFinite(unit)) { power=1023; unit=Math.pow(2,1023); }
        else if (unit === 0) { power=-1074; unit=Number.MIN_VALUE; }
        let part=absolute/unit;
        if (part >= 2) { part/=2; power++; }
        else if (part < 1) { part*=2; power--; }
        mantissa*=part;
        exponent+=power;
        const adjustment=Math.floor(Math.log2(mantissa));
        mantissa/=Math.pow(2,adjustment);
        exponent+=adjustment;
      }
      if (exponent < -1075) return sign*0;
      const magnitude=exponent < -1022
        ? mantissa*Math.pow(2,exponent+1022)*MIN_NORMAL
        : mantissa*Math.pow(2,exponent);
      return sign*magnitude;
    };
    const circular = shape === 'solid-circle' || shape === 'hollow-circle';
    const composite = shape === 'channel' || shape === 'i-section';
    const angle = shape === 'l-angle';
    if (!rectangular && !circular && !composite && !angle) throw Error('Section shape must be rectangle, hollow-rectangle, solid-circle, hollow-circle, channel, i-section or l-angle.');
    if (!dimensions || typeof dimensions !== 'object' || Array.isArray(dimensions)) throw Error('Section dimensions must be an object.');
    let area, secondMoment, secondMomentPerpendicular, axis, perpendicularAxis, centroid = null;
    let analyticRadiusOfGyrationX = null, analyticRadiusOfGyrationY = null;
    let analyticSectionModulusX = null, analyticSectionModulusY = null;
    let productOfInertia = null, principalMomentMajor = null, principalMomentMinor = null, principalAxisAngleDegrees = null;
    let boundsWidth, boundsHeight, centroidX, centroidY;
    if (angle) {
      const width = finite(dimensions.width, 'L-angle outer width B (mm)');
      const depth = finite(dimensions.height, 'L-angle outer depth H (mm)');
      const thickness = finite(dimensions.thickness, 'L-angle leg thickness t (mm)');
      if (!(width > 0) || !(depth > 0) || !(thickness > 0) || !(thickness < width) || !(thickness < depth)) {
        throw Error('L-angle B, H and t must be positive, with t < min(B,H).');
      }
      boundsWidth = width; boundsHeight = depth;
      const pieces = [
        {x:0,y:0,width:thickness,height:depth},
        {x:thickness,y:0,width:width-thickness,height:thickness}
      ];
      const pieceMetrics = pieces.map((piece,index) => {
        const pieceArea = finite(piece.width*piece.height, 'L-angle rectangle '+(index+1)+' area (mm²)');
        if (!(pieceArea > 0)) throw Error('L-angle rectangle area underflow; increase dimensions.');
        return {...piece,area:pieceArea,
          cx:finite(piece.x+piece.width/2, 'L-angle rectangle centroid x (mm)'),
          cy:finite(piece.y+piece.height/2, 'L-angle rectangle centroid y (mm)')};
      });
      // Preserve combined sub-ulp rectangle contributions when their total changes the rounded area.
      area = finiteSignedSum(pieceMetrics.map(piece=>piece.area), 'L-angle area (mm²)');
      if (!(area > 0)) throw Error('L-angle area underflow; increase dimensions.');
      centroidX = finite(pieceMetrics.reduce((sum,piece)=>sum+piece.area*piece.cx,0)/area, 'L-angle centroid x (mm)');
      centroidY = finite(pieceMetrics.reduce((sum,piece)=>sum+piece.area*piece.cy,0)/area, 'L-angle centroid y (mm)');
      secondMoment = finite(pieceMetrics.reduce((sum,piece)=>{
        const local = rectangleIxx(piece, 'L-angle local Ixx (mm⁴)');
        const offset = finite(piece.area*(piece.cy-centroidY)*(piece.cy-centroidY), 'L-angle Ixx offset (mm⁴)');
        return sum+local+offset;
      },0), 'L-angle Ixx (mm⁴)');
      secondMomentPerpendicular = finite(pieceMetrics.reduce((sum,piece)=>{
        const local = rectangleIyy(piece, 'L-angle local Iyy (mm⁴)');
        const offset = finite(piece.area*(piece.cx-centroidX)*(piece.cx-centroidX), 'L-angle Iyy offset (mm⁴)');
        return sum+local+offset;
      },0), 'L-angle Iyy (mm⁴)');
      productOfInertia = finite(pieceMetrics.reduce((sum,piece)=>sum+piece.area*(piece.cx-centroidX)*(piece.cy-centroidY),0),
        'L-angle product of inertia Ixy (mm⁴)');
      // A subnormal tensor or an underflowed Ixy can lose orientation information
      // even when the diagonal moments are representable. Re-evaluate the
      // two-rectangle geometry at unit scale, then restore physical units once.
      const physicalMomentScale = Math.max(secondMoment,secondMomentPerpendicular,Math.abs(productOfInertia));
      let normalizedLowExponentResolved = false;
      if (physicalMomentScale < MIN_NORMAL || productOfInertia === 0) {
        const lengthScale = Math.max(width,depth);
        const lengthScaleSquared = lengthScale*lengthScale;
        if (Number.isFinite(lengthScaleSquared) && lengthScaleSquared >= MIN_NORMAL) {
          const normalizedWidth = width/lengthScale;
          const normalizedDepth = depth/lengthScale;
          const normalizedThickness = thickness/lengthScale;
          const normalizedPieces = [
            {x:0,y:0,width:normalizedThickness,height:normalizedDepth},
            {x:normalizedThickness,y:0,width:normalizedWidth-normalizedThickness,height:normalizedThickness}
          ];
          const normalizedMetrics = normalizedPieces.map(piece => {
            const pieceArea = piece.width*piece.height;
            return {...piece,area:pieceArea,cx:piece.x+piece.width/2,cy:piece.y+piece.height/2};
          });
          const normalizedArea = normalizedMetrics.reduce((sum,piece)=>sum+piece.area,0);
          const normalizedCentroidX = normalizedMetrics.reduce((sum,piece)=>sum+piece.area*piece.cx,0)/normalizedArea;
          const normalizedCentroidY = normalizedMetrics.reduce((sum,piece)=>sum+piece.area*piece.cy,0)/normalizedArea;
          const normalizedIxx = normalizedMetrics.reduce((sum,piece)=>
            sum+piece.width*piece.height*piece.height*piece.height/12+
              piece.area*(piece.cy-normalizedCentroidY)*(piece.cy-normalizedCentroidY),0);
          const normalizedIyy = normalizedMetrics.reduce((sum,piece)=>
            sum+piece.height*piece.width*piece.width*piece.width/12+
              piece.area*(piece.cx-normalizedCentroidX)*(piece.cx-normalizedCentroidX),0);
          const normalizedIxy = normalizedMetrics.reduce((sum,piece)=>
            sum+piece.area*(piece.cx-normalizedCentroidX)*(piece.cy-normalizedCentroidY),0);
          const normalizedMean = (normalizedIxx+normalizedIyy)/2;
          const normalizedRadius = Math.hypot((normalizedIxx-normalizedIyy)/2,normalizedIxy);
          const normalizedMajor = normalizedMean+normalizedRadius;
          const normalizedDeterminant = normalizedIxx*normalizedIyy-normalizedIxy*normalizedIxy;
          const normalizedMinor = normalizedDeterminant/normalizedMajor;
          const normalizedExtremeX = Math.max(normalizedCentroidY,normalizedDepth-normalizedCentroidY);
          const normalizedExtremeY = Math.max(normalizedCentroidX,normalizedWidth-normalizedCentroidX);
          const candidate = {
            centroidX:normalizedCentroidX*lengthScale,
            centroidY:normalizedCentroidY*lengthScale,
            ixx:(normalizedIxx*lengthScaleSquared)*lengthScaleSquared,
            iyy:(normalizedIyy*lengthScaleSquared)*lengthScaleSquared,
            ixy:(normalizedIxy*lengthScaleSquared)*lengthScaleSquared,
            major:(normalizedMajor*lengthScaleSquared)*lengthScaleSquared,
            minor:(normalizedMinor*lengthScaleSquared)*lengthScaleSquared,
            sx:((normalizedIxx/normalizedExtremeX)*lengthScaleSquared)*lengthScale,
            sy:((normalizedIyy/normalizedExtremeY)*lengthScaleSquared)*lengthScale,
            rx:lengthScale*Math.sqrt(normalizedIxx/normalizedArea),
            ry:lengthScale*Math.sqrt(normalizedIyy/normalizedArea),
            angle:0.5*Math.atan2(-2*normalizedIxy,normalizedIxx-normalizedIyy)*180/Math.PI
          };
          if (normalizedArea>0 && normalizedIxx>0 && normalizedIyy>0 &&
              normalizedDeterminant>0 && normalizedMajor>0 && normalizedMinor>0 &&
              normalizedExtremeX>0 && normalizedExtremeY>0 &&
              Object.values(candidate).every(Number.isFinite) &&
              candidate.ixx>0 && candidate.iyy>0 &&
              candidate.major>0 && candidate.minor>0 && candidate.sx>0 && candidate.sy>0 &&
              candidate.rx>0 && candidate.ry>0) {
            centroidX = candidate.centroidX;
            centroidY = candidate.centroidY;
            secondMoment = candidate.ixx;
            secondMomentPerpendicular = candidate.iyy;
            // The normalized tensor retains Ixy's sign for the principal-axis angle.
            // Canonicalize dimensional underflowed zero so UI/export never emits -0.
            productOfInertia = candidate.ixy === 0 ? 0 : candidate.ixy;
            principalMomentMajor = candidate.major;
            principalMomentMinor = candidate.minor;
            analyticSectionModulusX = candidate.sx;
            analyticSectionModulusY = candidate.sy;
            analyticRadiusOfGyrationX = candidate.rx;
            analyticRadiusOfGyrationY = candidate.ry;
            principalAxisAngleDegrees = candidate.angle;
            normalizedLowExponentResolved = true;
          }
        }
      }
      // If only one L-angle axis is subnormal, max-dimension normalization can
      // erase that axis. Normalize x and y independently for its geometric S and r.
      if (!normalizedLowExponentResolved &&
          (secondMoment < MIN_NORMAL || secondMomentPerpendicular < MIN_NORMAL)) {
        const axisNormalizedMetrics = pieces.map(piece => {
          const normalizedPiece = {
            x:piece.x/width, y:piece.y/depth,
            width:piece.width/width, height:piece.height/depth
          };
          return {...normalizedPiece,
            area:normalizedPiece.width*normalizedPiece.height,
            cx:normalizedPiece.x+normalizedPiece.width/2,
            cy:normalizedPiece.y+normalizedPiece.height/2};
        });
        const axisNormalizedArea = axisNormalizedMetrics.reduce((sum,piece)=>sum+piece.area,0);
        if (axisNormalizedArea > 0 && Number.isFinite(axisNormalizedArea)) {
          const axisNormalizedCentroidX = axisNormalizedMetrics.reduce((sum,piece)=>sum+piece.area*piece.cx,0)/axisNormalizedArea;
          const axisNormalizedCentroidY = axisNormalizedMetrics.reduce((sum,piece)=>sum+piece.area*piece.cy,0)/axisNormalizedArea;
          const axisNormalizedIxx = axisNormalizedMetrics.reduce((sum,piece)=>{
            const dy=piece.cy-axisNormalizedCentroidY;
            return sum+piece.area*(piece.height*piece.height/12+dy*dy);
          },0);
          const axisNormalizedIyy = axisNormalizedMetrics.reduce((sum,piece)=>{
            const dx=piece.cx-axisNormalizedCentroidX;
            return sum+piece.area*(piece.width*piece.width/12+dx*dx);
          },0);
          const axisExtremeY = Math.max(axisNormalizedCentroidY,1-axisNormalizedCentroidY);
          const axisExtremeX = Math.max(axisNormalizedCentroidX,1-axisNormalizedCentroidX);
          if (axisNormalizedIxx > 0 && Number.isFinite(axisNormalizedIxx) &&
              axisNormalizedIyy > 0 && Number.isFinite(axisNormalizedIyy) &&
              axisExtremeY > 0 && axisExtremeX > 0) {
            const normalizedRadius = (moment,dimensionScale) => {
              const ratio=moment/axisNormalizedArea;
              const root=Number.isFinite(ratio) && ratio>0
                ? Math.sqrt(ratio) : Math.sqrt(moment)/Math.sqrt(axisNormalizedArea);
              return scaleProduct(dimensionScale,root);
            };
            if (secondMoment < MIN_NORMAL) {
              const radius=normalizedRadius(axisNormalizedIxx,depth);
              const modulus=scaleProduct(width,depth,depth,axisNormalizedIxx,1/axisExtremeY);
              if (radius>0 && Number.isFinite(radius)) analyticRadiusOfGyrationX=radius;
              if (modulus>0 && Number.isFinite(modulus)) analyticSectionModulusX=modulus;
            }
            if (secondMomentPerpendicular < MIN_NORMAL) {
              const radius=normalizedRadius(axisNormalizedIyy,width);
              const modulus=scaleProduct(width,width,depth,axisNormalizedIyy,1/axisExtremeX);
              if (radius>0 && Number.isFinite(radius)) analyticRadiusOfGyrationY=radius;
              if (modulus>0 && Number.isFinite(modulus)) analyticSectionModulusY=modulus;
            }
          }
        }
      }
      if (!normalizedLowExponentResolved) {
        // Normalize the inertia tensor before diagonalizing it. Subtracting the
        // nearly equal mean and radius loses the minor eigenvalue for slender angles.
        const momentScale = physicalMomentScale;
        const scaledIxx = secondMoment/momentScale;
        const scaledIyy = secondMomentPerpendicular/momentScale;
        const scaledIxy = productOfInertia/momentScale;
        const meanMoment = (scaledIxx+scaledIyy)/2;
        const principalRadius = Math.hypot((scaledIxx-scaledIyy)/2,scaledIxy);
        const majorNormalized = meanMoment+principalRadius;
        const determinantNormalized = scaledIxx*scaledIyy-scaledIxy*scaledIxy;
        if (!(majorNormalized > 0)) {
          throw Error('L-angle principal second moment underflow; increase dimensions.');
        }
        principalMomentMajor = finite(momentScale*majorNormalized, 'L-angle major principal moment I1 (mm⁴)');
        // For a positive-definite 2×2 inertia tensor, λmin = det(I)/λmax.
        // Usually the normalized determinant is safest; at extreme aspect ratios it
        // can underflow even when the minor eigenvalue is still representable.
        let minorMoment = momentScale*(determinantNormalized/majorNormalized);
        if (!(minorMoment > 0) || !Number.isFinite(minorMoment)) {
          // Recover only when the unscaled determinant itself remains finite and positive.
          // Otherwise retain the explicit underflow rejection rather than inventing a value.
          const determinant = secondMoment*secondMomentPerpendicular-productOfInertia*productOfInertia;
          if (!(determinant > 0) || !Number.isFinite(determinant)) {
            throw Error('L-angle principal second moment underflow; increase dimensions.');
          }
          minorMoment = determinant/principalMomentMajor;
        }
        principalMomentMinor = finite(minorMoment, 'L-angle minor principal moment I2 (mm⁴)');
        if (!(principalMomentMajor > 0) || !(principalMomentMinor > 0)) throw Error('L-angle principal second moment underflow; increase dimensions.');
        principalAxisAngleDegrees = finite(0.5*Math.atan2(-2*scaledIxy,scaledIxx-scaledIyy)*180/Math.PI,
          'L-angle principal-axis angle (degrees)');
      }
      centroid = {x:centroidX,y:centroidY};
      axis = 'centroidal horizontal axis (Ixx)';
      perpendicularAxis = 'centroidal vertical axis (Iyy)';
    } else if (composite) {
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
      const lengthScale = Math.max(width, depth);
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
        // A centered I-section web has no parallel-axis contribution. A channel web
        // is off-axis, so omit it only when exponent-scaled upper bounds prove that
        // its area, first moments and every local/offset inertia round to zero.
        const negligibleCenteredIWeb = shape === 'i-section' && index === 1 &&
          pieceArea === 0 && piece.width < 1 && piece.height < 1 &&
          piece.x + piece.width/2 === width/2 && piece.y + piece.height/2 === depth/2;
        const negligibleChannelWeb = shape === 'channel' && index === 0 && pieceArea === 0 &&
          scaleProduct(2,piece.width,piece.height) === 0 &&
          scaleProduct(2,piece.width,piece.height,width) === 0 &&
          scaleProduct(2,piece.width,piece.height,depth) === 0 &&
          scaleProduct(2,piece.width,piece.height,depth,depth) === 0 &&
          scaleProduct(2,piece.width,piece.height,piece.height,piece.height,1/12) === 0 &&
          scaleProduct(2,piece.height,piece.width,width,width) === 0 &&
          scaleProduct(2,piece.height,piece.width,piece.width,piece.width,1/12) === 0 &&
          scaleProduct(2,piece.width,piece.height,width,depth) === 0 &&
          scaleProduct(2,piece.width/lengthScale,piece.height/lengthScale) === 0 &&
          scaleProduct(2,piece.width/width,piece.height/depth) === 0;
        if (!(pieceArea > 0) && !negligibleCenteredIWeb && !negligibleChannelWeb) {
          throw Error('Composite section area underflow; increase dimensions.');
        }
        return {...piece,area:pieceArea,
          cx:finite(piece.x + piece.width/2, 'Composite section rectangle centroid x (mm)'),
          cy:finite(piece.y + piece.height/2, 'Composite section rectangle centroid y (mm)')};
      });
      const omittedChannelWeb = shape === 'channel' && pieceMetrics[0].area === 0;
      // Two small flange areas can each be below half an ulp of the web area while their sum is representable.
      area = finiteSignedSum(pieceMetrics.map(piece=>piece.area), 'Composite section area (mm²)');
      const firstMomentX = finite(pieceMetrics.reduce((sum,piece)=>sum+piece.area*piece.cx,0), 'Composite section first moment x (mm³)');
      const firstMomentY = finite(pieceMetrics.reduce((sum,piece)=>sum+piece.area*piece.cy,0), 'Composite section first moment y (mm³)');
      if (omittedChannelWeb && (area < MIN_NORMAL || firstMomentX < MIN_NORMAL || firstMomentY < MIN_NORMAL)) {
        throw Error('Composite section area underflow; increase dimensions.');
      }
      if (!(area > 0)) throw Error('Composite section area underflow; increase dimensions.');
      centroidX = finite(firstMomentX/area, 'Composite section centroid x (mm)');
      centroidY = finite(firstMomentY/area, 'Composite section centroid y (mm)');
      secondMoment = finite(pieceMetrics.reduce((sum,piece)=>{
        const local = rectangleIxx(piece, 'Composite rectangle local Ixx (mm⁴)');
        const offset = finite(piece.area*(piece.cy-centroidY)*(piece.cy-centroidY), 'Composite rectangle Ixx offset (mm⁴)');
        return sum+local+offset;
      },0), 'Composite section Ixx (mm⁴)');
      secondMomentPerpendicular = finite(pieceMetrics.reduce((sum,piece)=>{
        const local = rectangleIyy(piece, 'Composite rectangle local Iyy (mm⁴)');
        const offset = finite(piece.area*(piece.cx-centroidX)*(piece.cx-centroidX), 'Composite rectangle Iyy offset (mm⁴)');
        return sum+local+offset;
      },0), 'Composite section Iyy (mm⁴)');
      // The omitted web bounds are below half an ulp; require normal aggregate
      // area, first moments and inertias so they cannot change rounded outputs.
      if (omittedChannelWeb &&
          (secondMoment < MIN_NORMAL || secondMomentPerpendicular < MIN_NORMAL)) {
        throw Error('Composite section area underflow; increase dimensions.');
      }
      // Physical composite inertias can be subnormal even when the section radii are
      // representable. Recompute I/A in coordinates normalized by the largest length,
      // then restore that length once; keep the reported dimensional area and inertias intact.
      const normalizedMetrics = pieces.map(piece => {
        const normalizedPiece = {
          x:piece.x/lengthScale, y:piece.y/lengthScale,
          width:piece.width/lengthScale, height:piece.height/lengthScale
        };
        return {...normalizedPiece,
          area:normalizedPiece.width*normalizedPiece.height,
          cx:normalizedPiece.x+normalizedPiece.width/2,
          cy:normalizedPiece.y+normalizedPiece.height/2};
      });
      const normalizedArea = normalizedMetrics.reduce((sum,piece)=>sum+piece.area,0);
      let commonScaleResolved = false;
      if (normalizedArea > 0 && Number.isFinite(normalizedArea)) {
        const normalizedCentroidX = normalizedMetrics.reduce((sum,piece)=>sum+piece.area*piece.cx,0)/normalizedArea;
        const normalizedCentroidY = normalizedMetrics.reduce((sum,piece)=>sum+piece.area*piece.cy,0)/normalizedArea;
        const normalizedIxx = normalizedMetrics.reduce((sum,piece)=>{
          const local = rectangleIxx(piece, 'Normalized composite rectangle local Ixx');
          const offset = piece.area*(piece.cy-normalizedCentroidY)*(piece.cy-normalizedCentroidY);
          return sum+local+offset;
        },0);
        const normalizedIyy = normalizedMetrics.reduce((sum,piece)=>{
          const local = rectangleIyy(piece, 'Normalized composite rectangle local Iyy');
          const offset = piece.area*(piece.cx-normalizedCentroidX)*(piece.cx-normalizedCentroidX);
          return sum+local+offset;
        },0);
        commonScaleResolved = normalizedArea >= MIN_NORMAL &&
          normalizedIxx >= MIN_NORMAL && Number.isFinite(normalizedIxx) &&
          normalizedIyy >= MIN_NORMAL && Number.isFinite(normalizedIyy);
        if (normalizedIxx > 0 && Number.isFinite(normalizedIxx)) {
          analyticRadiusOfGyrationX = finite(lengthScale*Math.sqrt(normalizedIxx/normalizedArea),
            'Radius of gyration rx (mm)');
        }
        if (normalizedIyy > 0 && Number.isFinite(normalizedIyy)) {
          analyticRadiusOfGyrationY = finite(lengthScale*Math.sqrt(normalizedIyy/normalizedArea),
            'Radius of gyration ry (mm)');
        }
        // A subnormal dimensional inertia is too coarsely quantized for I/c.
        // Reuse the normalized tensor and extreme-fibre distance, then restore L³.
        const normalizedBoundsWidth = width/lengthScale;
        const normalizedBoundsHeight = depth/lengthScale;
        const normalizedExtremeFiberDistanceAboutX =
          Math.max(normalizedCentroidY, normalizedBoundsHeight-normalizedCentroidY);
        const normalizedExtremeFiberDistanceAboutY =
          Math.max(normalizedCentroidX, normalizedBoundsWidth-normalizedCentroidX);
        if (secondMoment < 2.2250738585072014e-308 &&
            normalizedIxx > 0 && normalizedExtremeFiberDistanceAboutX > 0) {
          const normalizedModulus = normalizedIxx/normalizedExtremeFiberDistanceAboutX;
          const candidate = lengthScale*(lengthScale*(lengthScale*normalizedModulus));
          if (candidate > 0 && Number.isFinite(candidate)) analyticSectionModulusX = candidate;
        }
        if (secondMomentPerpendicular < 2.2250738585072014e-308 &&
            normalizedIyy > 0 && normalizedExtremeFiberDistanceAboutY > 0) {
          const normalizedModulus = normalizedIyy/normalizedExtremeFiberDistanceAboutY;
          const candidate = lengthScale*(lengthScale*(lengthScale*normalizedModulus));
          if (candidate > 0 && Number.isFinite(candidate)) analyticSectionModulusY = candidate;
        }
      }
      // A single max-dimension scale can underflow one normalized inertia for an
      // extreme aspect ratio. Normalize each coordinate by its own section
      // dimension so both axis tensors remain well-scaled before restoring units.
      if (!commonScaleResolved) {
        const axisNormalizedMetrics = pieces.map(piece => {
          const normalizedPiece = {
            x:piece.x/width, y:piece.y/depth,
            width:piece.width/width, height:piece.height/depth
          };
          return {...normalizedPiece,
            area:normalizedPiece.width*normalizedPiece.height,
            cx:normalizedPiece.x+normalizedPiece.width/2,
            cy:normalizedPiece.y+normalizedPiece.height/2};
        });
        const axisNormalizedArea = axisNormalizedMetrics.reduce((sum,piece)=>sum+piece.area,0);
        if (axisNormalizedArea > 0 && Number.isFinite(axisNormalizedArea)) {
          const axisNormalizedCentroidX = axisNormalizedMetrics.reduce((sum,piece)=>sum+piece.area*piece.cx,0)/axisNormalizedArea;
          const axisNormalizedCentroidY = axisNormalizedMetrics.reduce((sum,piece)=>sum+piece.area*piece.cy,0)/axisNormalizedArea;
          const axisNormalizedIxx = axisNormalizedMetrics.reduce((sum,piece)=>{
            const dy=piece.cy-axisNormalizedCentroidY;
            return sum+piece.area*(piece.height*piece.height/12+dy*dy);
          },0);
          const axisNormalizedIyy = axisNormalizedMetrics.reduce((sum,piece)=>{
            const dx=piece.cx-axisNormalizedCentroidX;
            return sum+piece.area*(piece.width*piece.width/12+dx*dx);
          },0);
          const axisExtremeY = Math.max(axisNormalizedCentroidY,1-axisNormalizedCentroidY);
          const axisExtremeX = Math.max(axisNormalizedCentroidX,1-axisNormalizedCentroidX);
          if (axisNormalizedIxx > 0 && Number.isFinite(axisNormalizedIxx)) {
            const radius=depth*Math.sqrt(axisNormalizedIxx/axisNormalizedArea);
            if (radius > 0 && Number.isFinite(radius)) analyticRadiusOfGyrationX=radius;
            if (secondMoment < MIN_NORMAL && axisExtremeY > 0) {
              const candidate=scaleProduct(width,depth,depth,axisNormalizedIxx/axisExtremeY);
              if (candidate > 0 && Number.isFinite(candidate)) analyticSectionModulusX=candidate;
            }
          }
          if (axisNormalizedIyy > 0 && Number.isFinite(axisNormalizedIyy)) {
            const radius=width*Math.sqrt(axisNormalizedIyy/axisNormalizedArea);
            if (radius > 0 && Number.isFinite(radius)) analyticRadiusOfGyrationY=radius;
            if (secondMomentPerpendicular < MIN_NORMAL && axisExtremeX > 0) {
              const candidate=scaleProduct(width,width,depth,axisNormalizedIyy/axisExtremeX);
              if (candidate > 0 && Number.isFinite(candidate)) analyticSectionModulusY=candidate;
            }
          }
        }
      }
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
      centroid = {x:centroidX,y:centroidY};
      const hollow = shape === 'hollow-rectangle';
      const innerWidth = hollow ? finite(dimensions.innerWidth, 'Hollow rectangle inner width bi (mm)') : 0;
      const innerHeight = hollow ? finite(dimensions.innerHeight, 'Hollow rectangle inner depth hi (mm)') : 0;
      if (hollow && (!(innerWidth > 0) || !(innerWidth < width) || !(innerHeight > 0) || !(innerHeight < depth))) {
        throw Error('Hollow rectangle inner width and depth must be positive and smaller than the outer dimensions.');
      }
      const outerArea = finite(width * depth, 'Rectangle outer area (mm²)');
      // Do not form innerWidth*innerHeight as a validity check: the cavity area may
      // underflow even when the net section area and both centroidal inertias remain
      // representable. Positive, strictly contained dimensions above validate the
      // geometry; the factored dimensionless ratios below determine its contribution.
      // Factor the outer-minus-inner expressions into dimensionless wall gaps.
      // Direct subtraction loses significant digits when a valid hollow section has very thin walls.
      const widthRatio = hollow ? innerWidth / width : 0;
      const heightRatio = hollow ? innerHeight / depth : 0;
      const widthGap = hollow ? (width - innerWidth) / width : 1;
      const heightGap = hollow ? (depth - innerHeight) / depth : 1;
      const netAreaFactor = hollow ? widthGap + widthRatio * heightGap : 1;
      area = finite(outerArea * netAreaFactor, 'Rectangle net area (mm²)');
      const ixxFactor = hollow
        ? widthGap + widthRatio * heightGap * (1 + heightRatio + heightRatio * heightRatio)
        : 1;
      // Split the dimensionless hollow-section factor between the two depth
      // factors. This keeps a finite thin-wall Ixx even when the full outer
      // and inner solid-rectangle fourth-power intermediates would overflow.
      secondMoment = rectangleIxx({width,height:depth}, 'Rectangle Ixx (mm⁴)', ixxFactor);
      const iyyFactor = hollow
        ? heightGap + heightRatio * widthGap * (1 + widthRatio + widthRatio * widthRatio)
        : 1;
      secondMomentPerpendicular = rectangleIyy({width,height:depth}, 'Rectangle Iyy (mm⁴)', iyyFactor);
      // Compute rectangular radii from dimensionless geometry rather than rounded I/A.
      // A representable subnormal inertia can be quantized enough to corrupt sqrt(I/A).
      analyticRadiusOfGyrationX = finite(depth*Math.sqrt(ixxFactor/netAreaFactor/12), 'Radius of gyration rx (mm)');
      analyticRadiusOfGyrationY = finite(width*Math.sqrt(iyyFactor/netAreaFactor/12), 'Radius of gyration ry (mm)');
      // Preserve section-modulus precision only when the corresponding inertia is subnormal.
      // Sx=b*h²*fx/6 and Sy=h*b²*fy/6 avoid dividing a quantized Ixx/Iyy by c.
      if (secondMoment < 2.2250738585072014e-308) {
        analyticSectionModulusX = finite(outerArea * (depth * (ixxFactor / 6)), 'Section modulus Sx (mm³)');
      }
      if (secondMomentPerpendicular < 2.2250738585072014e-308) {
        analyticSectionModulusY = finite(outerArea * (width * (iyyFactor / 6)), 'Section modulus Sy (mm³)');
      }
      axis = 'centroidal axis parallel to width';
      perpendicularAxis = 'centroidal axis parallel to depth';
    } else {
      const diameter = finite(dimensions.diameter, 'Circle outer diameter Do (mm)');
      if (!(diameter > 0)) throw Error('Circle outer diameter must be positive.');
      boundsWidth = diameter;
      boundsHeight = diameter;
      centroidX = diameter/2;
      centroidY = diameter/2;
      centroid = {x:centroidX,y:centroidY};
      const hollow = shape === 'hollow-circle';
      let inertiaFactor = 1;
      const innerDiameter = hollow ? finite(dimensions.innerDiameter, 'Hollow circle inner diameter Di (mm)') : 0;
      if (hollow && (!(innerDiameter > 0) || !(innerDiameter < diameter))) {
        throw Error('Hollow circle inner diameter must be positive and smaller than the outer diameter.');
      }
      const outerSquare = finite(diameter * diameter, 'Circle outer diameter squared (mm²)');
      // Avoid squaring the inner diameter solely for validation. Its square may
      // underflow while the annulus area, inertia and section modulus are finite;
      // positive containment is validated above and the ratios below are sufficient.
      if (hollow) {
        // Factor the concentric annulus differences to preserve thin-wall precision.
        // Do not form Do^4 or Di^4: either can overflow while the thin-annulus
        // inertia is still representable. Keep the small factor between Do² terms.
        const innerRatio = finite(innerDiameter / diameter, 'Hollow circle inner/outer diameter ratio');
        const radialGap = finite((diameter - innerDiameter) / diameter, 'Hollow circle relative radial wall thickness');
        const areaFactor = finite(radialGap * (1 + innerRatio), 'Hollow circle net area factor');
        inertiaFactor = finite(areaFactor * (1 + innerRatio * innerRatio), 'Hollow circle inertia factor');
        area = finite((Math.PI / 4) * outerSquare * areaFactor, 'Circle net area (mm²)');
        secondMoment = finite((Math.PI / 64) * outerSquare * inertiaFactor * outerSquare, 'Circle centroidal second moment I (mm⁴)');
        // The annulus identity is I/A = Do²·(1 + (Di/Do)²)/16.
        // Evaluate its radius directly so a subnormal rounded I/A cannot corrupt it.
        const circularRadius = diameter * (Math.sqrt(1 + innerRatio * innerRatio) / 4);
        analyticRadiusOfGyrationX = finite(circularRadius, 'Radius of gyration rx (mm)');
        analyticRadiusOfGyrationY = finite(circularRadius, 'Radius of gyration ry (mm)');
      } else {
        area = finite(Math.PI * outerSquare / 4, 'Circle net area (mm²)');
        // Apply the coefficient before the final square: Do^4 may overflow even
        // when the physical solid-circle inertia (pi/64)*Do^4 is representable.
        secondMoment = finite((Math.PI / 64) * outerSquare * outerSquare, 'Circle centroidal second moment I (mm⁴)');
        // For a solid circle, I/A = Do²/16; avoid a rounded subnormal quotient.
        analyticRadiusOfGyrationX = finite(diameter / 4, 'Radius of gyration rx (mm)');
        analyticRadiusOfGyrationY = finite(diameter / 4, 'Radius of gyration ry (mm)');
      }
      // Subnormal inertia values are too coarsely quantized for I/c, even when S remains normal.
      // The circular identity S = (pi/32)·Do³·(1 - (Di/Do)^4) uses the
      // same factored annulus term and avoids dividing a rounded subnormal I.
      if (secondMoment < 2.2250738585072014e-308) {
        const circularSectionModulus = finite((Math.PI / 32) * outerSquare * diameter * inertiaFactor,
          'Circular section modulus (mm³)');
        analyticSectionModulusX = circularSectionModulus;
        analyticSectionModulusY = circularSectionModulus;
      }
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
    const sectionModulusX = analyticSectionModulusX === null
      ? finite(secondMoment/extremeFiberDistanceAboutX, 'Section modulus Sx (mm³)')
      : finite(analyticSectionModulusX, 'Section modulus Sx (mm³)');
    const sectionModulusY = analyticSectionModulusY === null
      ? finite(secondMomentPerpendicular/extremeFiberDistanceAboutY, 'Section modulus Sy (mm³)')
      : finite(analyticSectionModulusY, 'Section modulus Sy (mm³)');
    // Use the canonical I/area quotient when representable; it avoids the extra
    // rounding of two square roots. If the quotient over/underflows, split the
    // square roots so a representable physical radius is not lost to the ratio.
    const radiusOfGyration = (moment, label) => {
      const ratio = moment / area;
      const value = Number.isFinite(ratio) && ratio > 0
        ? Math.sqrt(ratio)
        : Math.sqrt(moment) / Math.sqrt(area);
      return finite(value, label);
    };
    const radiusOfGyrationX = analyticRadiusOfGyrationX === null
      ? radiusOfGyration(secondMoment, 'Radius of gyration rx (mm)') : analyticRadiusOfGyrationX;
    const radiusOfGyrationY = analyticRadiusOfGyrationY === null
      ? radiusOfGyration(secondMomentPerpendicular, 'Radius of gyration ry (mm)') : analyticRadiusOfGyrationY;
    if (!(sectionModulusX > 0) || !(sectionModulusY > 0)) throw Error('Section modulus underflow; increase the section dimensions or wall thickness.');
    if (!(radiusOfGyrationX > 0) || !(radiusOfGyrationY > 0)) throw Error('Radius of gyration underflow; increase the section dimensions.');
    return Object.freeze({shape, area, secondMoment, secondMomentPerpendicular, axis, perpendicularAxis,
      sectionModulusX, sectionModulusY, radiusOfGyrationX, radiusOfGyrationY,
      extremeFiberDistanceAboutX, extremeFiberDistanceAboutY,
      ...(centroid ? {centroid:Object.freeze(centroid)} : {}),
      ...(angle ? {productOfInertia,principalMomentMajor,principalMomentMinor,principalAxisAngleDegrees} : {})});
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
      const EAbyL = positiveProductQuotient(E, A, L);
      if (!Number.isFinite(EAbyL)) throw Error('Member ' + id + ': stiffness overflow.');
      if (!(EAbyL > 0)) throw Error('Member ' + id + ': stiffness underflow; increase E or area.');
      // Density is an optional SI quantity shared by Studio and legacy imports.
      // Blank/null means unknown; zero is valid, while negative/non-finite values are not.
      const density = hasOptionalValue(row.density) ? finite(row.density, id + ' density (kg/m³)') : null;
      if (density !== null && density < 0) throw Error('Member ' + id + ': density must be non-negative.');
      let mass = null;
      if (density !== null) {
        const calculatedMass = positiveProduct(L, A, density);
        if (density > 0 && !(calculatedMass > 0)) {
          throw Error('Member ' + id + ': mass underflow; increase dimensions or density.');
        }
        mass = finite(calculatedMass, 'Member ' + id + ' mass (kg)');
      }
      // I and K are independent member properties; the Euler estimate is available only when both are supplied.
      const hasI = hasOptionalValue(row.I);
      const hasK = hasOptionalValue(row.K);
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
        // Keep the established direct numerator / (K·L)² operation order for ordinary inputs.
        // If any intermediate loses range, evaluate π²·E·I / (K·L·K·L) by binary exponents.
        const numerator = Math.PI * Math.PI * E * secondMoment;
        const effectiveLength = effectiveLengthFactor * L;
        const denominator = effectiveLength * effectiveLength;
        eulerCriticalLoad = finite(positiveProductQuotientFactors(
          [Math.PI,Math.PI,E,secondMoment],
          [effectiveLengthFactor,L,effectiveLengthFactor,L],
          numerator,denominator), id + ' Euler critical load (N)');
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
    // Combine external loads and support reactions before summing: separately reducing
    // either group can overflow even when the final equilibrium residual is finite.
    const forceBalance = {
      x: finiteSignedSum([...nodes.map(node => node.fx), ...reactions.map(reaction => reaction.rx)], 'Force balance x (N)'),
      y: finiteSignedSum([...nodes.map(node => node.fy), ...reactions.map(reaction => reaction.ry)], 'Force balance y (N)')
    };
    const externalWork = free.reduce((sum, i) => sum + F[i] * u[i], 0);
    const elasticEnergy = results.reduce((sum, m) => sum + m.force*m.extension/2, 0);
    const energyError = Math.abs(2*elasticEnergy-externalWork)/Math.max(1, Math.abs(externalWork));
    if (!Number.isFinite(energyError) || energyError > 1e-6) throw Error('Numerical energy verification failed.');
    const maxDisplacement = displacements.reduce((a,b)=>b.magnitude>a.magnitude?b:a,displacements[0]);
    const maxStress = results.reduce((a,b)=>Math.abs(b.stress)>Math.abs(a.stress)?b:a,results[0]);
    return {id:'structural-truss-fem-2d',nodes,members:results,displacements,reactions,maxDisplacement,maxStress,
      residual,energyError,elasticEnergy,forceBalance,
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
  // Keep canonical reference examples immutable; callers receive independent editable copies.
  function freezeExampleTree(value) {
    if (!value || typeof value !== 'object' || Object.isFrozen(value)) return value;
    Object.values(value).forEach(freezeExampleTree);
    return Object.freeze(value);
  }
  freezeExampleTree(examples);
  function getExample(name) {
    if (typeof name !== 'string' || !Object.prototype.hasOwnProperty.call(examples, name)) {
      throw Error('Unknown truss example. Choose triangle or bar.');
    }
    return JSON.parse(JSON.stringify(examples[name]));
  }
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
        ...(hasOptionalValue(m.density) ? {density: m.density} : {}),
        ...(hasOptionalValue(m.I) ? {I: finiteScaled(m.I, 'Legacy I (m⁴)', 1e12)} : {}),
        ...(hasOptionalValue(m.K) ? {K: m.K} : {})}))};
  }
  // Import JSON as a model, retaining the original public-unit values and IDs.
  // Validation is performed on a converted copy, not on the returned document.
  function importJSON(text) {
    if (typeof text !== 'string') throw Error('Truss JSON input must be a string.');
    // Bound UTF-8 bytes (not UTF-16 code units) before parsing oversized imports.
    if (new TextEncoder().encode(text).byteLength > MAX_IMPORT_BYTES) throw Error('Truss JSON document exceeds the 1 MiB import limit.');
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
    if (new TextEncoder().encode(document).byteLength > MAX_IMPORT_BYTES) throw Error('Truss JSON document exceeds the 1 MiB export limit.');
    // JSON.stringify invokes toJSON hooks; validate the actual serialized model too.
    parseModel(fromLegacy(JSON.parse(document)));
    return document;
  }
  // Public unit metadata for JSON file workflows; never infer units from magnitudes.
  function describeUnits(model) {
    parseModel(fromLegacy(model));
    const legacy = model.members.some(m => m.A !== undefined);
    return Object.freeze(legacy
      ? {system:'legacy-si',coordinates:'m',forces:'N',modulus:'Pa',area:'m²',
        density:'kg/m³',secondMoment:'m⁴',effectiveLengthFactor:'dimensionless'}
      : {system:'studio',coordinates:'m',forces:'kN',modulus:'GPa',area:'mm²',
        density:'kg/m³',secondMoment:'mm⁴',effectiveLengthFactor:'dimensionless'});
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
    // Positive member geometry must not silently appear as zero when L*A underflows.
    const memberVolumes = normalized.members.map(member => {
      const volume = member.L * member.A;
      if (!Number.isFinite(volume)) throw Error('Total member volume (m³) must be a finite number.');
      if (!(volume > 0)) throw Error('Member ' + member.id + ' material volume underflow; increase dimensions.');
      return volume;
    });
    const totalMemberVolume = finite(memberVolumes.reduce((sum, volume) => sum + volume, 0), 'Total member volume (m³)');
    const appliedForce = Object.freeze({
      x: finiteSignedSum(normalized.nodes.map(node => node.fx), 'Applied force x (N)'),
      y: finiteSignedSum(normalized.nodes.map(node => node.fy), 'Applied force y (N)')
    });
    // Keep each moment product finite-checked, then sum signed terms without
    // overflowing a partial resultant when later nodes cancel it.
    const appliedMomentTerms = [];
    for (const node of normalized.nodes) {
      appliedMomentTerms.push(finite(node.x * node.fy, 'Applied moment term (N·m)'));
      appliedMomentTerms.push(finite(-node.y * node.fx, 'Applied moment term (N·m)'));
    }
    const appliedMoment = finiteSignedSum(appliedMomentTerms, 'Applied moment (N·m)');
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
      totalMemberVolume,
      // Per-member quantities stay in SI and are available even when the structure is unstable.
      memberMetrics: Object.freeze(normalized.members.map((member, index) => Object.freeze({
        id: member.id,
        startNodeId: normalized.nodes[member.a].id,
        endNodeId: normalized.nodes[member.b].id,
        length: member.L,
        area: member.A,
        elasticModulus: member.E,
        // EA/L is axial stiffness in N/m; the existing validated FEM stiffness is reused.
        axialStiffness: member.stiffness,
        volume: memberVolumes[index],
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
      appliedForce,
      appliedMoment};
  }
  // Export a validated per-member material schedule in explicit SI units without solving.
  function exportMaterialCSV(model) {
    const preview = inspectJSON(exportJSON(model));
    const rows = [
      ['Member ID', 'Start joint ID', 'End joint ID', 'Centreline length (m)', 'Cross-sectional area (m²)', 'Axial material volume (m³)', 'Elastic modulus (GPa)', 'Axial stiffness EA/L (kN/mm)', 'Density (kg/m³)', 'Member mass (kg)', 'Second moment of area I (mm⁴)', 'Effective length factor K (-)', 'Euler critical load Pcr (kN)'],
      ...preview.memberMetrics.map(member => {
        const eulerCriticalLoadKN = member.eulerCriticalLoad === null ? '' : member.eulerCriticalLoad / 1000;
        if (member.eulerCriticalLoad !== null && member.eulerCriticalLoad > 0 && !(eulerCriticalLoadKN > 0)) {
          throw Error('Member ' + member.id + ': Euler critical load underflows in kN CSV export.');
        }
        return [member.id, member.startNodeId, member.endNodeId,
          member.length, member.area, member.volume, member.elasticModulus / 1e9, member.axialStiffness / 1e6,
          member.density ?? '', member.mass ?? '',
          member.secondMoment === null ? '' : member.secondMoment * 1e12,
          member.effectiveLengthFactor ?? '',
          eulerCriticalLoadKN];
      })
    ];
    // Use the shortest decimal that round-trips to the original binary64 value.
    // Fixed 16-digit formatting can silently change valid engineering data.
    const quote = value => {
      let text;
      if (typeof value === 'number') {
        if (!Number.isFinite(value)) throw Error('Material CSV cannot export a non-finite numeric value.');
        text = Object.is(value, -0) ? '-0' : value.toString();
        if (!Object.is(Number(text), value)) throw Error('Material CSV numeric value did not round-trip.');
      } else {
        text = String(value);
      }
      return '"' + text.replace(/"/g, '""') + '"';
    };
    return rows.map(row => row.map(quote).join(',')).join('\r\n') + '\r\n';
  }
  function solveJSON(text) {
    return solveDocument(importJSON(text));
  }
  return Object.freeze({solve, solveDocument, solveJSON, inspectJSON, exportMaterialCSV, sectionProperties, parseModel, fromLegacy, importJSON, exportJSON, validateImportByteLength, decodeImportBytes, MAX_IMPORT_BYTES, describeUnits, getExample, examples, id:'structural-truss-fem-2d'});
});
