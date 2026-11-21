/* Offline project backup validation and version migration. SPDX-License-Identifier: MIT. */
(() => {
  'use strict';
  const record = value => value !== null && typeof value === 'object' && !Array.isArray(value);
  const fail = message => { throw Error('Invalid project: ' + message); };
  const short = (value, limit, label) => {
    if (typeof value !== 'string' || value.length > limit) fail(label + ' must be a bounded string.');
  };
  const optionalRecord = (value, label) => {
    if (value !== undefined && value !== null && !record(value)) fail(label + ' must be an object.');
  };
  function migrate(data) {
    if (!record(data) || data.format !== 'mathstudio-project' || ![1, 2].includes(data.version))
      fail('unsupported format or version (supported: 1 and 2).');
    if (!Array.isArray(data.notebook) || data.notebook.length > 300) fail('notebook exceeds 300 entries or is missing.');
    for (const item of data.notebook) {
      if (!record(item)) fail('notebook entry is not an object.');
      short(item.raw, 12000, 'notebook expression');
      if (item.sympy !== undefined && item.sympy !== null) {
        if (!record(item.sympy)) fail('symbolic notebook result is invalid.');
        for (const key of ['mathml', 'latex', 'plain'])
          if (item.sympy[key] !== undefined) short(item.sympy[key], 100000, 'symbolic ' + key);
      }
    }
    if (data.working !== undefined) short(data.working, 12000, 'working expression');
    if (data.origin !== undefined) short(data.origin, 80, 'expression origin');
    if (data.recent !== undefined) {
      if (!Array.isArray(data.recent) || data.recent.length > 14) fail('recent expression list exceeds 14 entries.');
      for (const item of data.recent) {
        if (!record(item)) fail('recent expression is invalid.');
        short(item.raw, 12000, 'recent expression');
      }
    }
    for (const key of ['calculator', 'solver', 'graph', 'tables', 'fit']) optionalRecord(data[key], key);
    if (data.calculator?.history !== undefined) {
      if (!Array.isArray(data.calculator.history) || data.calculator.history.length > 40) fail('calculator history exceeds 40 entries.');
      for (const item of data.calculator.history) {
        if (!record(item)) fail('calculator history entry is invalid.');
        short(item.expr, 12000, 'calculator history expression');
        short(item.result, 12000, 'calculator history result');
      }
    }
    if (data.solver) for (const key of ['expression', 'variable', 'operation', 'engine', 'limitPoint', 'limitDirection'])
      if (data.solver[key] !== undefined) short(data.solver[key], 12000, 'solver ' + key);
    if (data.solver?.odeInitialCondition !== undefined) short(data.solver.odeInitialCondition, 160, 'ODE initial condition');
    if (data.solver?.assumptions !== undefined) {
      const flags=data.solver.assumptions;
      if (!record(flags) || Object.keys(flags).some(k=>!['real','positive','negative','integer'].includes(k)||typeof flags[k]!=='boolean') ||
          (flags.positive===true && flags.negative===true)) fail('solver assumptions are invalid or contradictory.');
    }
    if (data.graph?.functions !== undefined) short(data.graph.functions, 12000, 'graph functions');
    if (data.graph?.dataset !== undefined && data.graph.dataset !== null) {
      const set = data.graph.dataset;
      if (!record(set) || !Array.isArray(set.headers) || !Array.isArray(set.rows) ||
          set.headers.length < 1 || set.headers.length > 32 || set.rows.length > 6000)
        fail('graph dataset dimensions exceed limits.');
      // Column selectors require unambiguous names in restored graph datasets.
      if (set.headers.every(h => typeof h === 'string')) {
        const identities = set.headers.map(h => h.trim().toLowerCase());
        if (identities.some(h => !h)) fail('graph dataset has blank column names.');
        if (new Set(identities).size !== identities.length)
          fail('graph dataset has duplicate column names.');
      }
      if (set.headers.some(h => typeof h !== 'string' || h.length > 8000) ||
          set.rows.some(row => !Array.isArray(row) || row.length !== set.headers.length ||
            row.some(cell => (cell !== null && !['string', 'number', 'boolean'].includes(typeof cell)) ||
              (typeof cell === 'number' && !Number.isFinite(cell)) || String(cell ?? '').length > 8000)))
        fail('graph dataset has invalid cells.');
    }
    // Main-graph curve overlays (implicit/parametric/polar definitions). Legacy projects omit
    // the field; present definitions must match the exact shape the exporter writes.
    if (data.graph?.curves !== undefined && data.graph.curves !== null) {
      const curves = data.graph.curves;
      if (!Array.isArray(curves) || curves.length > 8) fail('graph curve overlays must be a list of at most 8.');
      const shapes = {implicit: {expression: 'text', grid: 'grid'},
        parametric: {x: 'text', y: 'text', t0: 'bound', t1: 'bound', samples: 'samples'},
        polar: {r: 'text', theta0: 'bound', theta1: 'bound', samples: 'samples'}};
      const seen = new Set();
      for (const curve of curves) {
        if (!record(curve) || !Object.prototype.hasOwnProperty.call(shapes, curve.type)) fail('graph curve overlay type is invalid.');
        const shape = shapes[curve.type], keys = Object.keys(curve).filter(k => k !== 'type');
        if (keys.length !== Object.keys(shape).length || keys.some(k => !Object.prototype.hasOwnProperty.call(shape, k)))
          fail('graph curve overlay fields are invalid.');
        for (const [key, kind] of Object.entries(shape)) {
          const value = curve[key];
          const ok = kind === 'text' ? typeof value === 'string' && value.trim() !== '' && value.length <= 1500 :
            kind === 'bound' ? typeof value === 'number' && Number.isFinite(value) && Math.abs(value) <= 1e12 :
            kind === 'grid' ? Number.isInteger(value) && value >= 4 && value <= 300 :
            Number.isInteger(value) && value >= 2 && value <= 20000;
          if (!ok) fail('graph curve overlay ' + key + ' is invalid.');
        }
        if (curve.type === 'implicit' && (curve.expression.split('=').length > 2 || /==|<=|>=|!=/.test(curve.expression)))
          fail('graph curve overlay implicit equation must use at most one "=".');
        if (curve.type === 'parametric' && !(curve.t1 > curve.t0)) fail('graph curve overlay t range is empty.');
        if (curve.type === 'polar' && !(curve.theta1 > curve.theta0)) fail('graph curve overlay θ range is empty.');
        const identity = JSON.stringify(Object.keys(shape).map(k => curve[k]).concat(curve.type));
        if (seen.has(identity)) fail('duplicate graph curve overlays.');
        seen.add(identity);
      }
    }
    if (data.engineering !== undefined && data.engineering !== null) {
      const eng = data.engineering;
      if (!record(eng) || typeof eng.discipline !== 'string' || !/^[a-z-]{0,32}$/.test(eng.discipline) ||
          typeof eng.query !== 'string' || eng.query.length > 200)
        fail('saved Engineering filter is invalid.');
    }
    if (data.matrix !== undefined && data.matrix !== null) {
      const matrix = data.matrix;
      if (!record(matrix) || !['rows','cols','bRows','bCols'].every(key => [2,3].includes(matrix[key])))
        fail('saved Matrix dimensions must be 2 or 3.');
      const numericDraft = value => typeof value === 'string' && value.length <= 80 &&
        (value === '' || (/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(value) &&
          Number.isFinite(Number(value)) && Math.abs(Number(value)) <= 1e12));
      for (const [key, size] of [['a',matrix.rows*matrix.cols],['b',matrix.bRows*matrix.bCols],
        ['rhs',matrix.rows],['weights',matrix.rows]]) {
        if (!Array.isArray(matrix[key]) || matrix[key].length !== size || !matrix[key].every(numericDraft))
          fail('saved Matrix ' + key + ' entries are invalid.');
      }
    }
    // Validate saved custom functions as strictly as the editor: restore would otherwise
    // silently drop ambiguous duplicates or argument-less entries after other state changed.
    if (data.customFunctions !== undefined) {
      const list = data.customFunctions, identifier = /^[A-Za-z][A-Za-z0-9_]*$/, seen = new Set();
      if (!Array.isArray(list) || list.length > 60) fail('custom function limit is 60.');
      for (const item of list) {
        if (!record(item) || typeof item.name !== 'string' || item.name.length > 64 || !identifier.test(item.name))
          fail('custom function name is invalid.');
        const key = item.name.toLowerCase();
        if (seen.has(key)) fail('duplicate custom function names.');
        seen.add(key);
        if (!Array.isArray(item.params) || item.params.length < 1 || item.params.length > 6 ||
            item.params.some(param => typeof param !== 'string' || param.length > 64 || !identifier.test(param)) ||
            new Set(item.params).size !== item.params.length)
          fail('custom function arguments are invalid.');
        short(item.expression, 12000, 'custom function expression');
        if (item.source !== undefined) short(item.source, 12000, 'custom function source');
        if (item.type !== undefined && !['formula', 'python'].includes(item.type)) fail('custom function type is invalid.');
      }
    }
    if (data.tables) {
      if (!Array.isArray(data.tables.tables) || data.tables.tables.length > 20) fail('table count exceeds 20.');
      // A stored selection must name a real table; otherwise restore would silently
      // fall back to another sheet. Exports always write an existing id.
      if (data.tables.selected !== undefined &&
          (typeof data.tables.selected !== 'string' ||
           !data.tables.tables.some(t => record(t) && t.id === data.tables.selected)))
        fail('selected table does not exist.');
      const names = new Set();
      const ids = new Set();
      for (const table of data.tables.tables) {
        if (!record(table) || !Array.isArray(table.columns) || !Array.isArray(table.rows) ||
            table.columns.length < 1 || table.columns.length > 32 || table.rows.length > 6000)
          fail('table dimensions exceed limits.');
        // Legacy projects may omit ids; present ids must uniquely identify a sheet.
        if (table.id !== undefined) {
          if (typeof table.id !== 'string' || !table.id.trim() || table.id.length > 120)
            fail('table id is invalid.');
          if (ids.has(table.id)) fail('duplicate table ids.');
          ids.add(table.id);
        }
        short(table.name, 48, 'table name');
        // Trim only for identity checks: preserve the user's original display name.
        const name = table.name.trim().toLowerCase();
        if (!name) fail('table name must not be blank.');
        if (names.has(name)) fail('duplicate table names.');
        names.add(name);
        if (table.columns.some(col => typeof col !== 'string' || !col.trim() || col.length > 80) ||
            new Set(table.columns.map(col => typeof col === 'string' ? col.trim().toLowerCase() : col)).size !== table.columns.length ||
            table.rows.some(row => !Array.isArray(row) || row.length !== table.columns.length ||
              row.some(cell => (cell !== null && !['string', 'number', 'boolean'].includes(typeof cell)) ||
                (typeof cell === 'number' && !Number.isFinite(cell)) || String(cell ?? '').length > 8000)))
          fail('table contains invalid rows or cells.');
      }
    }
    // Version 1 is the established legacy format. Upgrade only metadata;
    // retain every supported workbook, graph, formula and notebook field.
    return {...data, version: 2};
  }
  window.MathStudio.projectSchema = {migrate};
})();
