/* Standalone, accessible truss FEM editor and SVG result viewer. UI stays separate from FEM kernel. */
(() => {
  'use strict';
  const fem = window.ProMathTrussFEM;
  if (!fem) return;
  const $ = id => document.getElementById(id);
  const SVG = 'http://www.w3.org/2000/svg';
  let latest = null, latestModel = null;
  // Latest file selection wins even when an earlier File.text() resolves later.
  let importRequest = 0;
  const fmt = (x, digits=5) => Number(x).toPrecision(digits).replace(/(\.\d*?)0+(e|$)/,'$1$2').replace(/\.(e|$)/,'$1');
  // Keep whole-number section properties readable; retain compact precision for fractional values.
  const fmtSectionMoment = value => Number.isSafeInteger(value) ? String(value) : fmt(value,4);
  function status(message, error=false, busy=false) {
    const target = $('status');
    target.textContent = message;
    target.classList.toggle('error', error);
    target.setAttribute('aria-busy', String(busy));
  }
  const el = (tag, text, attrs={}) => {
    const node = document.createElement(tag);
    if (text !== null) node.textContent = String(text);
    Object.entries(attrs).forEach(([key,val])=>node.setAttribute(key,String(val)));
    return node;
  };
  function rowInput(row,key,type='text') {
    const td = el('td',null), input = el('input',null,{'aria-label':key, 'data-field':key});
    input.type = type;
    if (type==='checkbox') input.checked = Boolean(row[key]);
    else { input.value = row[key] ?? ''; if(type==='number') {input.step='any'; input.inputMode='decimal';} }
    td.append(input);return td;
  }
  function appendRow(kind, row) {
    const tbody = $(kind), tr = el('tr',null);
    const fields = kind === 'nodes' ? ['id','x','y','fixX','fixY','fx','fy'] : ['id','a','b','E','area','density','I','K'];
    fields.forEach(key=>tr.append(rowInput(row,key,['fixX','fixY'].includes(key)?'checkbox':(['id','a','b'].includes(key)?'text':'number'))));
    const td=el('td',null), btn=el('button','×',{'type':'button','class':'remove','aria-label':'Remove '+kind.slice(0,-1)+' '+(row.id||'row')});
    btn.addEventListener('click',()=>{tr.remove(); if(kind==='members')syncSectionMembers(); invalidate();});td.append(btn);tr.append(td);tbody.append(tr);
  }
  function renderModel(model) {
    $('nodes').replaceChildren();$('members').replaceChildren();
    model.nodes.forEach(node=>appendRow('nodes',node));
    model.members.forEach(m=>appendRow('members',m));
    syncSectionMembers();
    invalidate();
  }
  function readRows(kind) {
    return Array.from($(kind).querySelectorAll('tr')).map(tr=>{
      const record={};
      tr.querySelectorAll('input').forEach(input=>{record[input.dataset.field] = input.type==='checkbox' ? input.checked : input.value;});
      return record;
    });
  }
  function readModel() {return {nodes:readRows('nodes'),members:readRows('members')};}
  function syncSectionMembers() {
    const select=$('section-member'), previous=select.value;
    const ids=readRows('members').map(member=>String(member.id??'').trim()).filter(Boolean);
    select.replaceChildren(...ids.map(id=>el('option',id,{value:id})));
    if(ids.includes(previous)) select.value=previous;
    else if(ids.length) select.value=ids[0];
  }
  function updateSectionShape() {
    const shape=$('section-shape').value;
    const composite=shape==='channel'||shape==='i-section';
    const rectangle=shape==='rectangle'||shape==='hollow-rectangle'||composite;
    const hollowRectangle=shape==='hollow-rectangle';
    const circle=shape==='solid-circle'||shape==='hollow-circle';
    const hollowCircle=shape==='hollow-circle';
    $('section-width-control').hidden=!rectangle;
    $('section-height-control').hidden=!rectangle;
    $('section-inner-width-control').hidden=!hollowRectangle;
    $('section-inner-height-control').hidden=!hollowRectangle;
    $('section-diameter-control').hidden=!circle;
    $('section-inner-diameter-control').hidden=!hollowCircle;
    $('section-web-thickness-control').hidden=!composite;
    $('section-flange-thickness-control').hidden=!composite;
    $('section-axis-control').hidden=!rectangle;
  }
  function applySectionProperties() {
    try {
      const memberId=$('section-member').value;
      const row=Array.from($('members').querySelectorAll('tr')).find(tr=>tr.querySelector('input[data-field="id"]')?.value.trim()===memberId);
      if(!row) throw Error('Choose an existing member.');
      const shape=$('section-shape').value;
      const composite=shape==='channel'||shape==='i-section';
      const rectangle=shape==='rectangle'||shape==='hollow-rectangle'||composite;
      const hollowRectangle=shape==='hollow-rectangle';
      const hollowCircle=shape==='hollow-circle';
      let dimensions;
      if(rectangle) {
        dimensions={width:$('section-width').value,height:$('section-height').value};
        if(hollowRectangle) {
          dimensions.innerWidth=$('section-inner-width').value;
          dimensions.innerHeight=$('section-inner-height').value;
        }
        if(composite) {
          dimensions.webThickness=$('section-web-thickness').value;
          dimensions.flangeThickness=$('section-flange-thickness').value;
        }
      } else {
        dimensions={diameter:$('section-diameter').value};
        if(hollowCircle) dimensions.innerDiameter=$('section-inner-diameter').value;
      }
      const properties=fem.sectionProperties(shape,dimensions);
      const axis=rectangle&&$('section-axis').value==='depth'?'depth':'width';
      const appliedI=rectangle&&axis==='depth'?properties.secondMomentPerpendicular:properties.secondMoment;
      const axisName=rectangle?(axis==='depth'?'Iyy':'Ixx'):'I';
      row.querySelector('input[data-field="area"]').value=String(properties.area);
      row.querySelector('input[data-field="I"]').value=String(appliedI);
      invalidate();
      const shapeName=shape==='rectangle'?'Solid rectangle':shape==='hollow-rectangle'?'Hollow rectangle':shape==='solid-circle'?'Solid circle':shape==='hollow-circle'?'Hollow circle':shape==='channel'?'Open channel (web left)':'I-section';
      const centroidText=properties.centroid
        ? '; centroid x '+fmt(properties.centroid.x,5)+' mm, y '+fmt(properties.centroid.y,5)+' mm'
        : '';
      const moments=rectangle
        ? '; Ixx '+fmtSectionMoment(properties.secondMoment)+' mm⁴; Iyy '+fmtSectionMoment(properties.secondMomentPerpendicular)+' mm⁴; applied '+axisName+' '+fmtSectionMoment(appliedI)+' mm⁴'+centroidText
        : '; I '+fmtSectionMoment(properties.secondMoment)+' mm⁴ about any centroidal diameter';
      const sectionMetrics='; Sx '+fmt(properties.sectionModulusX,5)+' mm³; Sy '+fmt(properties.sectionModulusY,5)+' mm³; rx '+fmt(properties.radiusOfGyrationX,5)+' mm; ry '+fmt(properties.radiusOfGyrationY,5)+' mm; cX '+fmt(properties.extremeFiberDistanceAboutX,5)+' mm; cY '+fmt(properties.extremeFiberDistanceAboutY,5)+' mm';
      $('section-result').textContent=shapeName+': area '+fmt(properties.area,5)+' mm²'+moments+sectionMetrics+', applied to member '+memberId+'.';
    } catch(error) {
      $('section-result').textContent='Not applied: '+error.message;
    }
  }
  function invalidate(){latest=null;latestModel=null;$('disp-card').textContent='—';$('stress-card').textContent='—';$('res-card').textContent='—';$('member-results').replaceChildren(el('tr',null)); $('member-results').firstChild.append(el('td','Run analysis to see results.',{colspan:7}));$('joint-results').replaceChildren();$('reactions').replaceChildren();$('verification').textContent='';updatePreview();}
  function svgNode(tag,attrs,text){const e=document.createElementNS(SVG,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,String(v)));if(text!=null)e.textContent=String(text);return e;}
  function updatePreview() {
    try {
      const info=fem.inspectJSON(fem.exportJSON(readModel()));
      const model=info.model,bounds=info.bounds,scale=500/Math.max(bounds.width,bounds.height,0.1);
      const point=(x,y)=>[310+(Number(x)-bounds.centerX)*scale,190-(Number(y)-bounds.centerY)*scale];
      const group=svgNode('g',{}),nodeById=new Map(model.nodes.map(node=>[String(node.id).trim(),node]));
      const line=(a,b,attrs={})=>group.append(svgNode('line',{x1:a[0],y1:a[1],x2:b[0],y2:b[1],...attrs}));
      model.members.forEach(member=>{
        const a=nodeById.get(String(member.a).trim()),b=nodeById.get(String(member.b).trim());
        const pa=point(a.x,a.y),pb=point(b.x,b.y);
        line(pa,pb,{stroke:'#78d7ff','stroke-width':3,'stroke-linecap':'round','data-member-id':member.id});
        if($('show-labels').value==='all')group.append(svgNode('text',{x:(pa[0]+pb[0])/2+5,y:(pa[1]+pb[1])/2-8},member.id));
      });
      model.nodes.forEach(node=>{
        const pt=point(node.x,node.y);
        if(node.fixX||node.fixY)group.append(svgNode('rect',{x:pt[0]-9,y:pt[1]-9,width:18,height:18,rx:3,fill:'#30507e',stroke:'#a8c0e2','stroke-width':1}));
        group.append(svgNode('circle',{cx:pt[0],cy:pt[1],r:4,fill:'#e5f3ff','data-node-id':node.id}));
        if($('show-labels').value!=='none')group.append(svgNode('text',{x:pt[0]+9,y:pt[1]-11},node.id));
        const fx=Number(node.fx),fy=Number(node.fy);
        if(Math.hypot(fx,fy)>1e-12){
          const length=30,angle=Math.atan2(-fy,fx),start=[pt[0]-length*Math.cos(angle),pt[1]-length*Math.sin(angle)];
          line(start,pt,{stroke:'#ffe173','stroke-width':2.6});
          const a1=angle+Math.PI*0.82,a2=angle-Math.PI*0.82;
          line(pt,[pt[0]+9*Math.cos(a1),pt[1]+9*Math.sin(a1)],{stroke:'#ffe173','stroke-width':2.6});
          line(pt,[pt[0]+9*Math.cos(a2),pt[1]+9*Math.sin(a2)],{stroke:'#ffe173','stroke-width':2.6});
        }
      });
      group.append(svgNode('text',{x:15,y:362,'font-size':12},'Pre-solve geometry · not to scale'));
      $('plot').replaceChildren(group);
      $('plot').setAttribute('aria-label',`Pre-solve truss geometry preview with ${info.nodeCount} joints and ${info.memberCount} members. Supports and applied loads are shown. Topology does not certify stability.`);
      addResultRows('member-metrics',info.memberMetrics,m=>[m.id,m.startNodeId,m.endNodeId,fmt(m.length,4),fmt(m.area*1e6,4),fmt(m.volume,4),fmt(m.elasticModulus/1e9,4),fmt(m.axialStiffness/1e6,4),m.density===null?'—':fmt(m.density,4),m.mass===null?'—':fmt(m.mass,4),m.secondMoment===null?'—':fmtSectionMoment(m.secondMoment*1e12),m.effectiveLengthFactor===null?'—':fmt(m.effectiveLengthFactor,4),m.eulerCriticalLoad===null?'—':fmt(m.eulerCriticalLoad/1000,5)]);
      const unit=info.inputUnits.forces,divisor=unit==='N'?1:1000;
      const components=info.connectedComponentCount===1?'connected component':'connected components';
      const isolated=info.isolatedNodeCount===1?'isolated joint':'isolated joints';
      $('preview-summary').textContent=`Model overview · ${info.nodeCount} joints · ${info.memberCount} members · ${info.connectedComponentCount} ${components} · ${info.isolatedNodeCount} ${isolated} · total member length ${fmt(info.totalMemberLength,4)} m · axial member volume Σ(L·A) ${fmt(info.totalMemberVolume,4)} m³ · bounds ${fmt(bounds.width,4)} × ${fmt(bounds.height,4)} m · applied load ΣFx ${fmt(info.appliedForce.x/divisor,4)} ${unit}, ΣFy ${fmt(info.appliedForce.y/divisor,4)} ${unit} (${info.loadedDofCount} loaded DOFs). Topology is not a stability check.`;
      const hasIncompleteEulerInputs=info.memberMetrics.some(metric =>
        (metric.secondMoment===null)!==(metric.effectiveLengthFactor===null));
      status(hasIncompleteEulerInputs
        ? 'Preview ready · Euler estimate requires both I and K.'
        : 'Preview ready · analyze to check structural stability.',false);
    } catch(error) {
      $('preview-summary').textContent='Preview unavailable: '+error.message;
      const empty=el('tr',null);empty.append(el('td','Correct model inputs to see member metrics.',{colspan:13,class:'empty'}));$('member-metrics').replaceChildren(empty);
      $('plot').replaceChildren(svgNode('text',{x:310,y:190,'text-anchor':'middle'},'Correct model inputs to preview'));
      $('plot').setAttribute('aria-label','Truss preview unavailable because model inputs are invalid.');
      status('Preview unavailable: '+error.message,true);
    }
  }
  function draw() {
    if(!latest||!latestModel) return;
    const svg=$('plot'), m=latestModel, d=latest, xy=new Map(m.nodes.map(node=>[String(node.id),[Number(node.x),Number(node.y)]]));
    const us=new Map(d.displacements.map(z=>[z.id,[z.x,z.y]]));
    const amp=Number($('scale').value);if(!Number.isFinite(amp)||amp<0||amp>100000){status('Deformation amplification must be 0–100000.',true);return;}
    const all=[...xy.values(),...m.nodes.map(node=>{const [x,y]=xy.get(String(node.id)),[ux,uy]=us.get(String(node.id));return [x+amp*ux,y+amp*uy];})];
    const xs=all.map(a=>a[0]),ys=all.map(a=>a[1]);const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
    const spread=Math.max(maxX-minX,maxY-minY,0.1),size=300/spread,centerX=(minX+maxX)/2,centerY=(minY+maxY)/2;
    const p=(x,y)=>[310+(x-centerX)*size,190-(y-centerY)*size];
    const g=svgNode('g',{}),line=(a,b,color,width=2,dash='')=>g.append(svgNode('line',{x1:a[0],y1:a[1],x2:b[0],y2:b[1],stroke:color,'stroke-width':width,'stroke-linecap':'round',...(dash?{'stroke-dasharray':dash}:{})}));
    m.members.forEach(member=>{const a=p(...xy.get(String(member.a))),b=p(...xy.get(String(member.b)));line(a,b,'#7083a4',2,'5 6');});
    d.members.forEach(member=>{
      const a0=xy.get(member.a),b0=xy.get(member.b),ua=us.get(member.a),ub=us.get(member.b);
      const a=p(a0[0]+amp*ua[0],a0[1]+amp*ua[1]),b=p(b0[0]+amp*ub[0],b0[1]+amp*ub[1]);
      const color=member.force>1e-8?'#46e5b4':member.force< -1e-8?'#ffb36e':'#b5c7e2';line(a,b,color,4);
      if($('show-labels').value==='all')g.append(svgNode('text',{x:(a[0]+b[0])/2+5,y:(a[1]+b[1])/2-8,'font-size':12},member.id));
    });
    m.nodes.forEach(node=>{
      const [x,y]=xy.get(String(node.id)),pt=p(x,y);
      if(node.fixX||node.fixY)g.append(svgNode('rect',{x:pt[0]-9,y:pt[1]-9,width:18,height:18,rx:3,fill:'#30507e',stroke:'#a8c0e2','stroke-width':1}));
      g.append(svgNode('circle',{cx:pt[0],cy:pt[1],r:4,fill:'#e5f3ff'}));
      if($('show-labels').value!=='none')g.append(svgNode('text',{x:pt[0]+9,y:pt[1]-11},node.id));
      const fx=Number(node.fx),fy=Number(node.fy);
      if(Math.hypot(fx,fy)>1e-12){const length=30,angle=Math.atan2(-fy,fx),start=[pt[0]-length*Math.cos(angle),pt[1]-length*Math.sin(angle)];line(start,pt,'#ffe173',2.6);const a1=angle+Math.PI*0.82,a2=angle-Math.PI*0.82;line(pt,[pt[0]+9*Math.cos(a1),pt[1]+9*Math.sin(a1)],'#ffe173',2.6);line(pt,[pt[0]+9*Math.cos(a2),pt[1]+9*Math.sin(a2)],'#ffe173',2.6);}
    });
    g.append(svgNode('text',{x:15,y:362,fill:'#a5c1dc'},'Deformation ×'+fmt(amp,4)+' · Geometry not to scale'));svg.replaceChildren(g);svg.setAttribute('aria-label','Solved truss deformation with original geometry, member force colors and applied loads.');
  }
  function addResultRows(target, data, formatter) {
    const rows=data.map(item=>{const tr=el('tr',null);formatter(item).forEach(value=>tr.append(el('td',value)));return tr;});
    $(target).replaceChildren(...rows);
  }
  function showResult(result,model){
    latest=result;latestModel=model;
    $('disp-card').textContent=fmt(result.maxDisplacement.magnitude*1000)+' mm · '+result.maxDisplacement.id;
    $('stress-card').textContent=fmt(Math.abs(result.maxStress.stress)/1e6)+' MPa · '+result.maxStress.id;
    $('res-card').textContent=result.residual.toExponential(2);
    addResultRows('member-results',result.members,m=>[m.id,fmt(m.force/1000),fmt(m.stress/1e6),m.type,
      m.eulerUtilization===null?'—':fmt(m.eulerUtilization*100)+'%',
      m.eulerLoadRatio===null?'—':fmt(m.eulerLoadRatio),m.eulerAssessment]);
    addResultRows('joint-results',result.displacements,n=>[n.id,fmt(n.x*1000),fmt(n.y*1000),fmt(n.magnitude*1000)]);
    addResultRows('reactions',result.reactions,r=>[r.id,fmt(r.rx/1000),fmt(r.ry/1000)]);
    $('verification').textContent='Force balance: ΣFx = '+fmt(result.forceBalance.x)+' N, ΣFy = '+fmt(result.forceBalance.y)+' N. Max free DOF residual / load scale = '+result.residual.toExponential(3)+'. Elastic strain energy = '+fmt(result.elasticEnergy)+' J. Normalized energy identity error = '+result.energyError.toExponential(3)+'.';
    draw();status('Analysis complete · '+result.nodes.length+' joints, '+result.members.length+' members.');
  }
  function analyze(){try{const model=readModel();showResult(fem.solve(model),model);}catch(error){invalidate();status(error.message,true);}}
  function download(name,content,mime){const link=el('a',null);const url=URL.createObjectURL(new Blob([content],{type:mime}));link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),3000);}
  function csv(){if(!latest){status('Run analysis before exporting results.',true);return;}const rows=[['Member','Axial force (kN)','Stress (MPa)','Strain','Euler utilization (%)','Euler load ratio Pcr/Pcomp (-)','Euler assessment'],...latest.members.map(m=>[m.id,m.force/1000,m.stress/1e6,m.strain,m.eulerUtilization===null?'':m.eulerUtilization*100,m.eulerLoadRatio===null?'':m.eulerLoadRatio,m.eulerAssessment]),[],['Joint','Ux (mm)','Uy (mm)'],...latest.displacements.map(n=>[n.id,n.x*1000,n.y*1000]),[],['Support','Rx (kN)','Ry (kN)'],...latest.reactions.map(r=>[r.id,r.rx/1000,r.ry/1000])];download('promath-truss-results.csv',rows.map(row=>row.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(',')).join('\r\n')+'\r\n','text/csv;charset=utf-8');}
  function materialCsv(){try{download('promath-truss-material-schedule.csv',fem.exportMaterialCSV(readModel()),'text/csv;charset=utf-8');status('Validated member material schedule exported.');}catch(error){status('Material schedule export failed: '+error.message,true);}}
  $('section-shape').addEventListener('change',updateSectionShape);
  $('section-properties-apply').addEventListener('click',applySectionProperties);
  $('members').addEventListener('change',()=>{syncSectionMembers();invalidate();});
  $('load-example').addEventListener('click',()=>{renderModel(fem.examples[$('example').value]);analyze();});
  $('reset').addEventListener('click',()=>{renderModel(fem.examples[$('example').value]);analyze();});
  $('add-node').addEventListener('click',()=>{appendRow('nodes',{id:'N'+($('nodes').children.length+1),x:0,y:0,fixX:false,fixY:false,fx:0,fy:0});invalidate();});
  $('add-member').addEventListener('click',()=>{const nodes=readRows('nodes');appendRow('members',{id:'M'+($('members').children.length+1),a:nodes[0]?.id||'',b:nodes[1]?.id||'',E:210,area:1000,density:'',I:'',K:''});syncSectionMembers();invalidate();});
  $('nodes').addEventListener('input',invalidate);$('members').addEventListener('input',invalidate);$('nodes').addEventListener('change',invalidate);$('members').addEventListener('change',invalidate);
  $('solve').addEventListener('click',analyze);$('scale').addEventListener('change',draw);$('show-labels').addEventListener('change',draw);
  $('export-model').addEventListener('click',()=>{try{download('promath-truss-model.json',fem.exportJSON(readModel()),'application/json;charset=utf-8');status('Validated model JSON exported.');}catch(err){status('Export failed: '+err.message,true);}});
  $('import-model').addEventListener('change',async event=>{
    const file=event.target.files?.[0];event.target.value='';if(!file)return;
    const request=++importRequest;
    status('Importing model…',false,true);
    try {
      if(file.size>1024*1024)throw Error('Model JSON exceeds 1 MiB.');
      const text=await file.text();
      // A newer selection supersedes a slower earlier read; stale data/errors must not win.
      if(request!==importRequest)return;
      const model=fem.fromLegacy(fem.importJSON(text));
      renderModel(model);analyze();
    } catch(err) {
      if(request!==importRequest)return;
      status('Import failed: '+err.message,true);
    }
  });
  $('export-csv').addEventListener('click',csv);$('export-material-csv').addEventListener('click',materialCsv);
  $('export-svg').addEventListener('click',()=>{if(!latest){status('Analyze before exporting SVG.',true);return;}const svg=$('plot').cloneNode(true);svg.setAttribute('xmlns',SVG);svg.setAttribute('width','1240');svg.setAttribute('height','760');const background=svgNode('rect',{x:0,y:0,width:620,height:380,fill:'#09152a'});svg.insertBefore(background,svg.firstChild);download('promath-truss-deformation.svg',new XMLSerializer().serializeToString(svg),'image/svg+xml;charset=utf-8');});
  updateSectionShape();
  renderModel(fem.examples.triangle);analyze();
})();
