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
      if (set.headers.some(h => typeof h !== 'string' || h.length > 8000) ||
          set.rows.some(row => !Array.isArray(row) || row.length !== set.headers.length ||
            row.some(cell => (cell !== null && !['string', 'number', 'boolean'].includes(typeof cell)) ||
              (typeof cell === 'number' && !Number.isFinite(cell)) || String(cell ?? '').length > 8000)))
        fail('graph dataset has invalid cells.');
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
    if (data.customFunctions !== undefined) {
      if (!Array.isArray(data.customFunctions) || data.customFunctions.length > 60) fail('custom function limit is 60.');
      for (const fn of data.customFunctions) {
        if (!record(fn) || typeof fn.name !== 'string' || !/^[A-Za-z][A-Za-z0-9_]*$/.test(fn.name) ||
            !Array.isArray(fn.params) || fn.params.length > 6) fail('custom function definition is invalid.');
        short(fn.expression, 12000, 'custom function expression');
        for (const param of fn.params) if (typeof param !== 'string' || !/^[A-Za-z][A-Za-z0-9_]*$/.test(param))
          fail('custom function parameter is invalid.');
      }
    }
    if (data.tables) {
      if (!Array.isArray(data.tables.tables) || data.tables.tables.length > 20) fail('table count exceeds 20.');
      const names = new Set();
      for (const table of data.tables.tables) {
        if (!record(table) || !Array.isArray(table.columns) || !Array.isArray(table.rows) ||
            table.columns.length < 1 || table.columns.length > 32 || table.rows.length > 6000)
          fail('table dimensions exceed limits.');
        short(table.name, 48, 'table name');
        const name = table.name.toLowerCase();
        if (names.has(name)) fail('duplicate table names.');
        names.add(name);
        if (table.columns.some(col => typeof col !== 'string' || col.length > 80) ||
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
