/* Standalone, accessible truss FEM editor and SVG result viewer. UI stays separate from FEM kernel. */
(() => {
  'use strict';
  const fem = window.ProMathTrussFEM;
  if (!fem) return;
  const $ = id => document.getElementById(id);
  const SVG = 'http://www.w3.org/2000/svg';
  let latest = null, latestModel = null;
  // Latest file selection wins even when an earlier byte read resolves later.
  let importRequest = 0;
  let importPending = false;
  let importCancelledNotice = false;
  const IMPORT_CANCELLED_STATUS = 'Pending import cancelled because the model was edited.';
  const MAX_IMPORT_BYTES = 1024 * 1024;
  const fmt = (x, digits=5) => Number(x).toPrecision(digits).replace(/(\.\d*?)0+(e|$)/,'$1$2').replace(/\.(e|$)/,'$1');
  const fmtAngle = x => Number(x).toFixed(3);
  // Keep whole-number section properties readable; retain compact precision for fractional values.
  const fmtSectionMoment = value => Number.isSafeInteger(value) ? String(value) : fmt(value,4);
  function status(message, error=false, busy=false) {
    if(message===IMPORT_CANCELLED_STATUS) importCancelledNotice=true;
    else if(importCancelledNotice && typeof message==='string' && message.startsWith('Preview ready')) message=IMPORT_CANCELLED_STATUS;
    else if(importCancelledNotice && typeof message==='string' && message.startsWith('Preview unavailable:')) message+=' · '+IMPORT_CANCELLED_STATUS;
    else importCancelledNotice=false;
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
  function updateSectionSketch() {
    const control=$('section-sketch-control'),svg=$('section-sketch'),caption=$('section-sketch-caption'),shape=$('section-shape').value;
    const channel=shape==='channel',iSection=shape==='i-section',composite=channel||iSection,angle=shape==='l-angle',hollowRectangle=shape==='hollow-rectangle',rectangle=shape==='rectangle'||hollowRectangle,circle=shape==='solid-circle'||shape==='hollow-circle',hollowCircle=shape==='hollow-circle';
    if(!control||(!composite&&!angle&&!rectangle&&!circle)) return;
    svg.replaceChildren();
    const titleText=composite?(channel?'Open channel cross-section preview':'I-section cross-section preview'):angle?'L-angle cross-section preview':hollowRectangle?'Hollow rectangle cross-section preview':hollowCircle?'Hollow circle cross-section preview':circle?'Solid circle cross-section preview':'Solid rectangle cross-section preview';
    const description=composite?(channel?'Dimensioned open-channel outline with the web on the left, flanges extending right, B/H/tw/tf dimensions, offset centroid and perpendicular centroidal axes.':'Dimensioned symmetric I-section outline with a centered web, equal flanges, B/H/tw/tf dimensions, centroid and perpendicular centroidal axes.')
      :angle?'Dimensioned L-angle outline with centroid and perpendicular major (I₁) and minor (I₂) principal axes.'
      :hollowRectangle?'Dimensioned hollow-rectangle outline with a centered void, B/H/bi/hi dimensions, centroid and perpendicular centroidal axes.'
      :hollowCircle?'Dimensioned concentric hollow-circle outline with outer and inner diameters, centroid and perpendicular centroidal axes.'
      :circle?'Dimensioned solid circle outline with diameter, centroid and perpendicular centroidal diameter axes.'
      :'Dimensioned solid rectangle outline with centroid and horizontal and vertical centroidal axes.';
    svg.append(svgNode('title',{id:'section-sketch-title'},titleText),svgNode('desc',{id:'section-sketch-desc'},description));
    const width=Number($('section-width').value),height=Number($('section-height').value),diameter=Number($('section-diameter').value);
    const innerDiameter=Number($('section-inner-diameter').value);
    const innerWidth=Number($('section-inner-width').value),innerHeight=Number($('section-inner-height').value);
    const webThickness=composite?Number($('section-web-thickness').value):null,flangeThickness=composite?Number($('section-flange-thickness').value):null;
    const thickness=angle?Number($('section-angle-thickness').value):null;
    const unavailable=message=>{
      // aria-labelledby references this description, so keep the SVG's accessible
      // description in sync with the live caption whenever geometry is unavailable.
      const descriptionNode=svg.querySelector('#section-sketch-desc');
      if(descriptionNode) descriptionNode.textContent=message;
      svg.append(svgNode('text',{x:180,y:126,'text-anchor':'middle','font-size':12,fill:'currentColor'},message));
      caption.textContent=message;svg.setAttribute('aria-label',message);
    };
    if(circle&&(!Number.isFinite(diameter)||!(diameter>0))){
      unavailable('Preview unavailable: enter a positive finite outer diameter D.');return;
    }
    if(hollowCircle&&(!Number.isFinite(innerDiameter)||!(innerDiameter>0)||!(innerDiameter<diameter))){
      unavailable('Preview unavailable: inner diameter Di must be positive and smaller than outer diameter Do.');return;
    }
    if(hollowRectangle&&(!Number.isFinite(innerWidth)||!Number.isFinite(innerHeight)||!(innerWidth>0)||!(innerHeight>0)||!(innerWidth<width)||!(innerHeight<height))){
      unavailable('Preview unavailable: inner width bi and inner depth hi must be positive and smaller than B and H.');return;
    }
    if(composite&&(!Number.isFinite(webThickness)||!(webThickness>0)||!(webThickness<width)||!Number.isFinite(flangeThickness)||!(flangeThickness>0)||!(2*flangeThickness<height))){
      unavailable(channel?'Preview unavailable: channel web thickness tw and flange thickness tf must be positive, with tw < B and 2·tf < H.'
        :'Preview unavailable: I-section web thickness tw and flange thickness tf must be positive, with tw < B and 2·tf < H.');return;
    }
    if(!circle&&(!Number.isFinite(width)||!Number.isFinite(height)||!(width>0)||!(height>0)||
       (angle&&(!Number.isFinite(thickness)||!(thickness>0)||!(thickness<Math.min(width,height)))))){
      unavailable(angle?'Preview unavailable: enter positive B, H and t with t smaller than B and H.'
        :'Preview unavailable: enter positive finite B and H dimensions.');return;
    }
    let properties;
    try{properties=fem.sectionProperties(shape,circle?{diameter,...(hollowCircle?{innerDiameter}:{})}:composite?{width,height,webThickness,flangeThickness}:angle?{width,height,thickness}:{width,height,...(hollowRectangle?{innerWidth,innerHeight}:{})});}
    catch(error){unavailable('Preview unavailable: '+error.message);return;}
    const scale=circle?Math.min(190/diameter,155/diameter):Math.min(190/width,155/height);
    const x=86,y=24,w=circle?diameter*scale:width*scale,h=circle?w:height*scale;
    const cx=x+properties.centroid.x*scale,cy=y+h-properties.centroid.y*scale;
    const outlineMetadata={'data-section-width-mm':circle?diameter:width,'data-section-height-mm':circle?diameter:height,'data-section-area-mm2':properties.area,'data-section-centroid-x-mm':properties.centroid.x,'data-section-centroid-y-mm':properties.centroid.y};
    const centroidMetadata={'data-centroid-x-mm':properties.centroid.x,'data-centroid-y-mm':properties.centroid.y};
    if(circle){
      const radius=w/2,innerRadius=hollowCircle?innerDiameter*scale/2:0,axisHalf=radius*(hollowCircle?0.92:0.78);
      svg.append(svgNode('circle',{cx,cy,r:radius,fill:'#b8cbe2',stroke:'#355578','stroke-width':2,'data-section-outline':hollowCircle?'hollow-circle-outer':'solid-circle',...outlineMetadata,'data-section-diameter-mm':diameter,...(hollowCircle?{'data-section-inner-diameter-mm':innerDiameter}:{})}));
      if(hollowCircle) svg.append(svgNode('circle',{cx,cy,r:innerRadius,fill:'rgba(127,127,127,.05)',stroke:'#355578','stroke-width':2,'data-section-outline':'hollow-circle-inner'}));
      svg.append(svgNode('line',{x1:cx-axisHalf,y1:cy,x2:cx+axisHalf,y2:cy,stroke:'#c47b19','stroke-width':2,'stroke-dasharray':'6 4','data-centroid-axis':'horizontal',...centroidMetadata}));
      svg.append(svgNode('line',{x1:cx,y1:cy-axisHalf,x2:cx,y2:cy+axisHalf,stroke:'#2b7a65','stroke-width':2,'stroke-dasharray':'6 4','data-centroid-axis':'vertical',...centroidMetadata}));
      svg.append(svgNode('text',{x:cx+radius*0.48,y:cy-6,fill:'#c47b19','font-size':10,'font-weight':'600',role:'text','aria-label':'Horizontal centroidal axis Ixx'},'Ixx'));
      svg.append(svgNode('text',{x:cx+6,y:cy-radius*0.5,fill:'#2b7a65','font-size':10,'font-weight':'600',role:'text','aria-label':'Vertical centroidal axis Iyy'},'Iyy'));
    }else if(channel){
      const tw=webThickness*scale,tf=flangeThickness*scale;
      const path='M '+x+' '+y+' H '+(x+w)+' V '+(y+tf)+' H '+(x+tw)+' V '+(y+h-tf)+' H '+(x+w)+' V '+(y+h)+' H '+x+' Z';
      svg.append(svgNode('path',{d:path,fill:'#b8cbe2',stroke:'#355578','stroke-width':2,'data-section-outline':'channel',...outlineMetadata,'data-channel-opening':'right','data-web-thickness-mm':webThickness,'data-flange-thickness-mm':flangeThickness}));
      const padX=Math.min(8,w*0.15),padY=Math.min(8,h*0.15);
      svg.append(svgNode('line',{x1:x+padX,y1:cy,x2:x+w-padX,y2:cy,stroke:'#c47b19','stroke-width':2,'stroke-dasharray':'6 4','data-centroid-axis':'horizontal',...centroidMetadata}));
      svg.append(svgNode('line',{x1:cx,y1:y+padY,x2:cx,y2:y+h-padY,stroke:'#2b7a65','stroke-width':2,'stroke-dasharray':'6 4','data-centroid-axis':'vertical',...centroidMetadata}));
      svg.append(svgNode('text',{x:x+w-30,y:cy-6,fill:'#c47b19','font-size':10,'font-weight':'600',role:'text','aria-label':'Horizontal centroidal axis Ixx'},'Ixx'));
      svg.append(svgNode('text',{x:cx+5,y:y+flangeThickness*scale+13,fill:'#2b7a65','font-size':10,'font-weight':'600',role:'text','aria-label':'Vertical centroidal axis Iyy'},'Iyy'));
    }else if(iSection){
      const tw=webThickness*scale,tf=flangeThickness*scale,webLeft=(w-tw)/2,webRight=webLeft+tw;
      const path='M '+x+' '+y+' H '+(x+w)+' V '+(y+tf)+' H '+(x+webRight)+' V '+(y+h-tf)+' H '+(x+w)+' V '+(y+h)+' H '+x+' V '+(y+h-tf)+' H '+(x+webLeft)+' V '+(y+tf)+' H '+x+' Z';
      svg.append(svgNode('path',{d:path,fill:'#b8cbe2',stroke:'#355578','stroke-width':2,'data-section-outline':'i-section',...outlineMetadata,'data-web-thickness-mm':webThickness,'data-flange-thickness-mm':flangeThickness}));
      const padX=Math.min(8,w*0.15),padY=Math.min(8,h*0.15);
      svg.append(svgNode('line',{x1:x+padX,y1:cy,x2:x+w-padX,y2:cy,stroke:'#c47b19','stroke-width':2,'stroke-dasharray':'6 4','data-centroid-axis':'horizontal',...centroidMetadata}));
      svg.append(svgNode('line',{x1:cx,y1:y+padY,x2:cx,y2:y+h-padY,stroke:'#2b7a65','stroke-width':2,'stroke-dasharray':'6 4','data-centroid-axis':'vertical',...centroidMetadata}));
      svg.append(svgNode('text',{x:x+w-30,y:cy-6,fill:'#c47b19','font-size':10,'font-weight':'600',role:'text','aria-label':'Horizontal centroidal axis Ixx'},'Ixx'));
      svg.append(svgNode('text',{x:cx+5,y:y+flangeThickness*scale+13,fill:'#2b7a65','font-size':10,'font-weight':'600',role:'text','aria-label':'Vertical centroidal axis Iyy'},'Iyy'));
    }else if(angle){
      const t=thickness*scale,theta=properties.principalAxisAngleDegrees*Math.PI/180,axisLength=Math.max(18,Math.min(78,Math.hypot(w,h)*0.45));
      svg.append(svgNode('path',{d:'M '+x+' '+y+' H '+(x+t)+' V '+(y+h-t)+' H '+(x+w)+' V '+(y+h)+' H '+x+' Z',fill:'#b8cbe2',stroke:'#355578','stroke-width':2,'data-section-outline':'l-angle',...outlineMetadata,'data-section-thickness-mm':thickness}));
      [
        {name:'major',label:'I₁',angle:theta,color:'#c47b19'},
        {name:'minor',label:'I₂',angle:theta+Math.PI/2,color:'#2b7a65'}
      ].forEach(axis=>{
        const x1=cx-axisLength*Math.cos(axis.angle),y1=cy+axisLength*Math.sin(axis.angle);
        const x2=cx+axisLength*Math.cos(axis.angle),y2=cy-axisLength*Math.sin(axis.angle);
        svg.append(svgNode('line',{x1,y1,x2,y2,stroke:axis.color,'stroke-width':2.2,'stroke-dasharray':'6 4','data-principal-axis':axis.name,'data-axis-angle-deg':axis.angle*180/Math.PI,'data-centroid-x-mm':properties.centroid.x,'data-centroid-y-mm':properties.centroid.y}));
        svg.append(svgNode('text',{x:x2+5,y:y2-5,fill:axis.color,'font-size':11,'font-weight':'600','data-principal-axis-label':axis.name,role:'text','aria-label':axis.name==='major'?'Major principal axis I1':'Minor principal axis I2','data-axis-angle-deg':axis.angle*180/Math.PI},axis.label));
      });
      svg.append(dimensionLabel('t',thickness,{x:x+w-62,y:y+h-t/2+4,fill:'#20364f','font-size':10,'font-weight':'600'}));
    }else{
      const innerW=hollowRectangle?innerWidth*scale:0,innerH=hollowRectangle?innerHeight*scale:0;
      const innerX=x+(w-innerW)/2,innerY=y+(h-innerH)/2;
      svg.append(svgNode('path',{d:'M '+x+' '+y+' H '+(x+w)+' V '+(y+h)+' H '+x+' Z',fill:'#b8cbe2',stroke:'#355578','stroke-width':2,'data-section-outline':hollowRectangle?'hollow-rectangle-outer':'rectangle',...outlineMetadata,...(hollowRectangle?{'data-section-inner-width-mm':innerWidth,'data-section-inner-height-mm':innerHeight}:{})}));
      if(hollowRectangle) svg.append(svgNode('path',{d:'M '+innerX+' '+innerY+' H '+(innerX+innerW)+' V '+(innerY+innerH)+' H '+innerX+' Z',fill:'rgba(127,127,127,.05)',stroke:'#355578','stroke-width':2,'data-section-outline':'hollow-rectangle-inner','data-inner-width-mm':innerWidth,'data-inner-height-mm':innerHeight}));
      const padX=Math.min(8,w*0.15),padY=Math.min(8,h*0.15);
      svg.append(svgNode('line',{x1:x+padX,y1:cy,x2:x+w-padX,y2:cy,stroke:'#c47b19','stroke-width':2,'stroke-dasharray':'6 4','data-centroid-axis':'horizontal',...centroidMetadata}));
      svg.append(svgNode('line',{x1:cx,y1:y+padY,x2:cx,y2:y+h-padY,stroke:'#2b7a65','stroke-width':2,'stroke-dasharray':'6 4','data-centroid-axis':'vertical',...centroidMetadata}));
      svg.append(svgNode('text',{x:x+w-30,y:cy-6,fill:'#c47b19','font-size':10,'font-weight':'600',role:'text','aria-label':'Horizontal centroidal axis Ixx'},'Ixx'));
      svg.append(svgNode('text',{x:cx+5,y:y+12,fill:'#2b7a65','font-size':10,'font-weight':'600',role:'text','aria-label':'Vertical centroidal axis Iyy'},'Iyy'));
    }
    svg.append(svgNode('circle',{cx,cy,r:4,fill:'#b42318',stroke:'#fff','stroke-width':1.4,'data-centroid':'true','data-centroid-x-mm':properties.centroid.x,'data-centroid-y-mm':properties.centroid.y}));
    svg.append(svgNode('text',{x:cx+7,y:cy-7,fill:'#b42318','font-size':11,'font-weight':'600'},'C'));
    if(circle){
      const dimensionY=y+h+18,outerLabel=hollowCircle?'Do':'D';
      svg.append(svgNode('line',{x1:x,y1:dimensionY,x2:x+w,y2:dimensionY,stroke:'currentColor','stroke-width':1,'data-dimension':outerLabel}));
      svg.append(dimensionLabel(outerLabel,diameter,{x:cx,y:dimensionY+14,'text-anchor':'middle',fill:'currentColor','font-size':11}));
      if(hollowCircle){
        const innerX1=x+(diameter-innerDiameter)*scale/2,innerX2=x+(diameter+innerDiameter)*scale/2,innerY=dimensionY+22;
        svg.append(svgNode('line',{x1:innerX1,y1:innerY,x2:innerX2,y2:innerY,stroke:'currentColor','stroke-width':1,'stroke-dasharray':'3 2','data-dimension':'Di'}));
        svg.append(dimensionLabel('Di',innerDiameter,{x:(innerX1+innerX2)/2,y:innerY+14,'text-anchor':'middle',fill:'currentColor','font-size':11}));
      }
    }else{
      const dimensionY=y+h+18,dimensionX=x-20;
      svg.append(svgNode('line',{x1:x,y1:dimensionY,x2:x+w,y2:dimensionY,stroke:'currentColor','stroke-width':1,'data-dimension':'B'}));
      svg.append(dimensionLabel('B',width,{x:x+w/2,y:dimensionY+15,'text-anchor':'middle',fill:'currentColor','font-size':11}));
      svg.append(svgNode('line',{x1:dimensionX,y1:y,x2:dimensionX,y2:y+h,stroke:'currentColor','stroke-width':1,'data-dimension':'H'}));
      svg.append(dimensionLabel('H',height,{x:dimensionX-7,y:y+h/2,transform:'rotate(-90 '+(dimensionX-7)+' '+(y+h/2)+')','text-anchor':'middle',fill:'currentColor','font-size':11}));
      if(composite){
        const tw=webThickness*scale,tf=flangeThickness*scale;
        if(channel){
          const twY=y+h-tf-Math.min(8,tf*0.4),tfX=x+tw+Math.min(20,(w-tw)*0.25);
          svg.append(svgNode('line',{x1:x,y1:twY,x2:x+tw,y2:twY,stroke:'currentColor','stroke-width':1,'stroke-dasharray':'3 2','data-dimension':'tw'}));
          svg.append(dimensionLabel('tw',webThickness,{x:x+tw+5,y:twY-4,fill:'currentColor','font-size':10}));
          svg.append(svgNode('line',{x1:tfX,y1:y,x2:tfX,y2:y+tf,stroke:'currentColor','stroke-width':1,'stroke-dasharray':'3 2','data-dimension':'tf'}));
          svg.append(dimensionLabel('tf',flangeThickness,{x:tfX+5,y:y+tf+11,fill:'currentColor','font-size':10}));
        }else{
          const webLeft=x+(width-webThickness)*scale/2,webRight=webLeft+tw;
          const twY=cy+Math.min(12,tf*0.55),tfX=x+w-Math.min(16,w*0.12);
          svg.append(svgNode('line',{x1:webLeft,y1:twY,x2:webRight,y2:twY,stroke:'currentColor','stroke-width':1,'stroke-dasharray':'3 2','data-dimension':'tw'}));
          svg.append(dimensionLabel('tw',webThickness,{x:webRight+5,y:twY-4,fill:'currentColor','font-size':10}));
          svg.append(svgNode('line',{x1:tfX,y1:y,x2:tfX,y2:y+tf,stroke:'currentColor','stroke-width':1,'stroke-dasharray':'3 2','data-dimension':'tf'}));
          svg.append(dimensionLabel('tf',flangeThickness,{x:tfX+5,y:y+tf+11,fill:'currentColor','font-size':10}));
        }
      }
      if(hollowRectangle){
        const innerW=innerWidth*scale,innerH=innerHeight*scale;
        const innerX=x+(w-innerW)/2,innerY=y+(h-innerH)/2;
        const biY=cy+Math.min(7,innerH*0.12),hiX=cx+Math.min(7,innerW*0.12);
        svg.append(svgNode('line',{x1:innerX,y1:biY,x2:innerX+innerW,y2:biY,stroke:'currentColor','stroke-width':1,'stroke-dasharray':'3 2','data-dimension':'bi'}));
        svg.append(svgNode('line',{x1:hiX,y1:innerY,x2:hiX,y2:innerY+innerH,stroke:'currentColor','stroke-width':1,'stroke-dasharray':'3 2','data-dimension':'hi'}));
        svg.append(dimensionLabel('bi',innerWidth,{x:cx-40,y:dimensionY+32,'text-anchor':'middle',fill:'currentColor','font-size':10}));
        svg.append(dimensionLabel('hi',innerHeight,{x:cx+44,y:dimensionY+32,'text-anchor':'middle',fill:'currentColor','font-size':10}));
      }
    }
    const summary=channel
      ?'Open channel B='+fmt(width,4)+' mm, H='+fmt(height,4)+' mm, tw='+fmt(webThickness,4)+' mm, tf='+fmt(flangeThickness,4)+' mm; centroid x '+fmt(properties.centroid.x,5)+' mm, y '+fmt(properties.centroid.y,5)+' mm; horizontal Ixx and vertical Iyy centroidal axes; web on left, flanges extend right.'
      :iSection
        ?'I-section B='+fmt(width,4)+' mm, H='+fmt(height,4)+' mm, tw='+fmt(webThickness,4)+' mm, tf='+fmt(flangeThickness,4)+' mm; centroid x '+fmt(properties.centroid.x,5)+' mm, y '+fmt(properties.centroid.y,5)+' mm; horizontal Ixx and vertical Iyy centroidal axes; centered web and equal-width flanges.'
      :circle
      ?(hollowCircle
        ?'Hollow circle Do='+fmt(diameter,4)+' mm, Di='+fmt(innerDiameter,4)+' mm; centroid x '+fmt(properties.centroid.x,5)+' mm, y '+fmt(properties.centroid.y,5)+' mm; horizontal and vertical centroidal diameter axes Ixx and Iyy.'
        :'Solid circle D='+fmt(diameter,4)+' mm; centroid x '+fmt(properties.centroid.x,5)+' mm, y '+fmt(properties.centroid.y,5)+' mm; horizontal and vertical centroidal diameter axes Ixx and Iyy.')
      :angle
        ?'L-angle B='+fmt(width,4)+' mm, H='+fmt(height,4)+' mm, t='+fmt(thickness,4)+' mm; centroid x '+fmt(properties.centroid.x,5)+' mm, y '+fmt(properties.centroid.y,5)+' mm; major principal axis '+fmtAngle(properties.principalAxisAngleDegrees)+'° counter-clockwise from +x; minor principal axis '+fmtAngle(properties.principalAxisAngleDegrees+90)+'° counter-clockwise from +x.'
        :hollowRectangle
          ?'Hollow rectangle B='+fmt(width,4)+' mm, H='+fmt(height,4)+' mm, bi='+fmt(innerWidth,4)+' mm, hi='+fmt(innerHeight,4)+' mm; centroid x '+fmt(properties.centroid.x,5)+' mm, y '+fmt(properties.centroid.y,5)+' mm; horizontal Ixx and vertical Iyy centroidal axes.'
          :'Solid rectangle B='+fmt(width,4)+' mm, H='+fmt(height,4)+' mm; centroid x '+fmt(properties.centroid.x,5)+' mm, y '+fmt(properties.centroid.y,5)+' mm; horizontal Ixx and vertical Iyy centroidal axes.';
    caption.textContent=summary;svg.setAttribute('aria-label',summary);
  }
  function updateSectionShape() {
    const shape=$('section-shape').value;
    const composite=shape==='channel'||shape==='i-section';
    const angle=shape==='l-angle';
    const sketch=shape==='rectangle'||shape==='hollow-rectangle'||angle||shape==='solid-circle'||shape==='hollow-circle'||shape==='channel'||shape==='i-section';
    const rectangle=shape==='rectangle'||shape==='hollow-rectangle'||composite||angle;
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
    $('section-angle-thickness-control').hidden=!angle;
    $('section-axis-control').hidden=!rectangle;
    $('section-sketch-control').hidden=!sketch;
    $('section-axis').querySelectorAll('[data-angle-axis]').forEach(option=>option.hidden=!angle);
    if(angle) $('section-axis').value='principal-major';
    else if($('section-axis').value.startsWith('principal-')) $('section-axis').value='width';
    updateSectionSketch();
  }
  function applySectionProperties() {
    try {
      const memberId=$('section-member').value;
      const row=Array.from($('members').querySelectorAll('tr')).find(tr=>tr.querySelector('input[data-field="id"]')?.value.trim()===memberId);
      if(!row) throw Error('Choose an existing member.');
      const shape=$('section-shape').value;
      const composite=shape==='channel'||shape==='i-section';
      const angle=shape==='l-angle';
      const rectangle=shape==='rectangle'||shape==='hollow-rectangle'||composite||angle;
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
        if(angle) dimensions.thickness=$('section-angle-thickness').value;
      } else {
        dimensions={diameter:$('section-diameter').value};
        if(hollowCircle) dimensions.innerDiameter=$('section-inner-diameter').value;
      }
      const properties=fem.sectionProperties(shape,dimensions);
      const axis=$('section-axis').value;
      let appliedI=properties.secondMoment, axisName='Ixx';
      if(angle&&axis==='principal-major') {appliedI=properties.principalMomentMajor;axisName='I1 (major principal)';}
      else if(angle&&axis==='principal-minor') {appliedI=properties.principalMomentMinor;axisName='I2 (minor principal)';}
      else if(rectangle&&axis==='depth') {appliedI=properties.secondMomentPerpendicular;axisName='Iyy';}
      else if(!rectangle) axisName='I';
      row.querySelector('input[data-field="area"]').value=String(properties.area);
      row.querySelector('input[data-field="I"]').value=String(appliedI);
      invalidate();
      const shapeName=shape==='rectangle'?'Solid rectangle':shape==='hollow-rectangle'?'Hollow rectangle':shape==='solid-circle'?'Solid circle':shape==='hollow-circle'?'Hollow circle':shape==='channel'?'Open channel (web left)':shape==='i-section'?'I-section':'L-angle (web left, bottom leg right)';
      const centroidText=properties.centroid
        ? '; centroid x '+fmt(properties.centroid.x,5)+' mm, y '+fmt(properties.centroid.y,5)+' mm'
        : '';
      const moments=rectangle
        ? '; Ixx '+fmtSectionMoment(properties.secondMoment)+' mm⁴; Iyy '+fmtSectionMoment(properties.secondMomentPerpendicular)+' mm⁴; applied '+axisName+' '+fmtSectionMoment(appliedI)+' mm⁴'+centroidText
        : '; I '+fmtSectionMoment(properties.secondMoment)+' mm⁴ about any centroidal diameter';
      const principalMetrics=angle
        ? '; Ixy '+fmtSectionMoment(properties.productOfInertia)+' mm⁴; principal I1 '+fmtSectionMoment(properties.principalMomentMajor)+' mm⁴; principal I2 '+fmtSectionMoment(properties.principalMomentMinor)+' mm⁴; I1 axis '+fmt(properties.principalAxisAngleDegrees,5)+'° counter-clockwise from +x'
        : '';
      const sectionMetrics='; Sx '+fmt(properties.sectionModulusX,5)+' mm³; Sy '+fmt(properties.sectionModulusY,5)+' mm³; rx '+fmt(properties.radiusOfGyrationX,5)+' mm; ry '+fmt(properties.radiusOfGyrationY,5)+' mm; cX '+fmt(properties.extremeFiberDistanceAboutX,5)+' mm; cY '+fmt(properties.extremeFiberDistanceAboutY,5)+' mm';
      $('section-result').textContent=shapeName+': area '+fmt(properties.area,5)+' mm²'+moments+principalMetrics+sectionMetrics+', applied to member '+memberId+'.';
    } catch(error) {
      $('section-result').textContent='Not applied: '+error.message;
    }
  }
  function cancelPendingImport(){if(!importPending)return;importRequest++;importPending=false;status(IMPORT_CANCELLED_STATUS);}
  function invalidate(){cancelPendingImport();latest=null;latestModel=null;$('disp-card').textContent='—';$('stress-card').textContent='—';$('res-card').textContent='—';$('member-results').replaceChildren(el('tr',null)); $('member-results').firstChild.append(el('td','Run analysis to see results.',{colspan:7}));$('joint-results').replaceChildren();$('reactions').replaceChildren();$('verification').textContent='';updatePreview();}
  function svgNode(tag,attrs,text){const e=document.createElementNS(SVG,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,String(v)));if(text!=null)e.textContent=String(text);return e;}
  function dimensionLabel(name,value,attrs){const formatted=fmt(value,4);return svgNode('text',{...attrs,'data-dimension-label':name,role:'text','aria-label':'Section dimension '+name+': '+formatted+' millimetres'},name+'='+formatted+' mm');}
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
    const g=svgNode('g',{}),line=(a,b,color,width=2,dash='',metadata={})=>g.append(svgNode('line',{x1:a[0],y1:a[1],x2:b[0],y2:b[1],stroke:color,'stroke-width':width,'stroke-linecap':'round',...(dash?{'stroke-dasharray':dash}:{}),...metadata}));
    m.members.forEach(member=>{const a=p(...xy.get(String(member.a))),b=p(...xy.get(String(member.b)));line(a,b,'#7083a4',2,'5 6',{'data-geometry-role':'original-member','data-member-id':member.id});});
    d.members.forEach(member=>{
      const a0=xy.get(member.a),b0=xy.get(member.b),ua=us.get(member.a),ub=us.get(member.b);
      const a=p(a0[0]+amp*ua[0],a0[1]+amp*ua[1]),b=p(b0[0]+amp*ub[0],b0[1]+amp*ub[1]);
      const forceState=member.force>1e-8?'tension':member.force< -1e-8?'compression':'neutral';
      const color=forceState==='tension'?'#46e5b4':forceState==='compression'?'#ffb36e':'#b5c7e2';
      line(a,b,color,4,'',{'data-geometry-role':'deformed-member','data-member-id':member.id,'data-force-state':forceState,'data-axial-force-n':member.force});
      if($('show-labels').value==='all')g.append(svgNode('text',{x:(a[0]+b[0])/2+5,y:(a[1]+b[1])/2-8,'font-size':12},member.id));
    });
    m.nodes.forEach(node=>{
      const [x,y]=xy.get(String(node.id)),pt=p(x,y);
      if(node.fixX||node.fixY)g.append(svgNode('rect',{x:pt[0]-9,y:pt[1]-9,width:18,height:18,rx:3,fill:'#30507e',stroke:'#a8c0e2','stroke-width':1}));
      g.append(svgNode('circle',{cx:pt[0],cy:pt[1],r:4,fill:'#e5f3ff'}));
      if($('show-labels').value!=='none')g.append(svgNode('text',{x:pt[0]+9,y:pt[1]-11},node.id));
      const fx=Number(node.fx),fy=Number(node.fy);
      if(Math.hypot(fx,fy)>1e-12){const length=30,angle=Math.atan2(-fy,fx),start=[pt[0]-length*Math.cos(angle),pt[1]-length*Math.sin(angle)];line(start,pt,'#ffe173',2.6,'',{'data-geometry-role':'applied-load','data-node-id':node.id,'data-force-x-kN':fx,'data-force-y-kN':fy});const a1=angle+Math.PI*0.82,a2=angle-Math.PI*0.82;line(pt,[pt[0]+9*Math.cos(a1),pt[1]+9*Math.sin(a1)],'#ffe173',2.6,'',{'data-geometry-role':'load-arrowhead','data-node-id':node.id,'data-arrowhead-index':1});line(pt,[pt[0]+9*Math.cos(a2),pt[1]+9*Math.sin(a2)],'#ffe173',2.6,'',{'data-geometry-role':'load-arrowhead','data-node-id':node.id,'data-arrowhead-index':2});}
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
  function analyze(successNotice=''){cancelPendingImport();try{const model=readModel();showResult(fem.solve(model),model);if(typeof successNotice==='string'&&successNotice)status($('status').textContent+' · '+successNotice);}catch(error){invalidate();status(error.message,true);}}
  function download(name,content,mime){const link=el('a',null);const url=URL.createObjectURL(new Blob([content],{type:mime}));link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),3000);}
  function downloadCsv(name,content,mime){
    // Canonicalize records to CRLF, terminate non-empty CSV with CRLF, and emit one leading UTF-8 BOM.
    const body=String(content).replace(/^\uFEFF+/,'').replace(/\r\n|\r|\n/g,'\r\n');
    const records=body && !body.endsWith('\r\n') ? body+'\r\n' : body;
    download(name,'\uFEFF'+records,mime||'text/csv;charset=utf-8');
  }
  function csv(){if(!latest){status('Run analysis before exporting results.',true);return;}const rows=[['Member','Axial force (kN)','Stress (MPa)','Strain','Euler utilization (%)','Euler load ratio Pcr/Pcomp (-)','Euler assessment'],...latest.members.map(m=>[m.id,m.force/1000,m.stress/1e6,m.strain,m.eulerUtilization===null?'':m.eulerUtilization*100,m.eulerLoadRatio===null?'':m.eulerLoadRatio,m.eulerAssessment]),[],['Joint','Ux (mm)','Uy (mm)'],...latest.displacements.map(n=>[n.id,n.x*1000,n.y*1000]),[],['Support','Rx (kN)','Ry (kN)'],...latest.reactions.map(r=>[r.id,r.rx/1000,r.ry/1000])];downloadCsv('promath-truss-results.csv',rows.map(row=>row.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(',')).join('\r\n')+'\r\n','text/csv;charset=utf-8');}
  function materialCsv(){try{downloadCsv('promath-truss-material-schedule.csv',fem.exportMaterialCSV(readModel()),'text/csv;charset=utf-8');status('Validated member material schedule exported.');}catch(error){status('Material schedule export failed: '+error.message,true);}}
  $('section-shape').addEventListener('change',updateSectionShape);
  ['section-width','section-height','section-inner-width','section-inner-height','section-web-thickness','section-flange-thickness','section-angle-thickness','section-diameter','section-inner-diameter'].forEach(id=>$(id).addEventListener('input',updateSectionSketch));
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
    // Snapshot immutable File metadata before crossing the asynchronous read boundary.
    const declaredSize=file.size;
    const request=++importRequest;
    importPending=true;
    status('Importing model…',false,true);
    try {
      if(!Number.isSafeInteger(declaredSize)||declaredSize<0||declaredSize>MAX_IMPORT_BYTES)throw Error('Model JSON exceeds 1 MiB.');
      const bytes=await file.arrayBuffer();
      // A newer selection supersedes a slower earlier read; stale data/errors must not win.
      if(request!==importRequest)return;
      // Enforce the same budget against the actual payload, not only File.size metadata.
      if(!Number.isSafeInteger(bytes?.byteLength)||bytes.byteLength>MAX_IMPORT_BYTES)throw Error('Model JSON exceeds 1 MiB.');
      if(bytes.byteLength!==declaredSize)throw Error(`Model JSON file size does not match the bytes read. (expected ${declaredSize} bytes, received ${bytes.byteLength}).`);
      let text;
      try {
        // File.text() replaces malformed UTF-8, which can silently corrupt imported IDs.
        text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(bytes);
      } catch (_) {
        throw Error('Model JSON must be valid UTF-8.');
      }
      if(request!==importRequest)return;
      const imported=fem.importJSON(text);
      const inputUnits=fem.describeUnits(imported);
      const model=fem.fromLegacy(imported);
      importPending=false;
      renderModel(model);
      const unitNotice=inputUnits.system==='legacy-si'
        ? 'Legacy SI input converted to Studio units.'
        : 'Studio units retained from file.';
      const optionalUnitsNotice='Optional property units in file: density '+inputUnits.density+
        ', I '+inputUnits.secondMoment+', K '+inputUnits.effectiveLengthFactor+'.';
      analyze(unitNotice+' '+optionalUnitsNotice);
    } catch(err) {
      if(request!==importRequest)return;
      importPending=false;
      status('Import failed: '+err.message,true);
    }
  });
  $('export-csv').addEventListener('click',csv);$('export-material-csv').addEventListener('click',materialCsv);
  $('export-svg').addEventListener('click',()=>{if(!latest){status('Analyze before exporting SVG.',true);return;}const svg=$('plot').cloneNode(true);svg.setAttribute('xmlns',SVG);svg.setAttribute('width','1240');svg.setAttribute('height','760');svg.setAttribute('preserveAspectRatio','xMidYMid meet');svg.setAttribute('role','img');svg.setAttribute('aria-labelledby','truss-export-title truss-export-description');svg.removeAttribute('aria-label');const title=svgNode('title',{id:'truss-export-title'},'ProMathStudio truss deformation analysis');const description=svgNode('desc',{id:'truss-export-description'},'The original truss members are shown as dotted lines. The solved deformation is colored by tension or compression and amplified for visibility.');svg.insertBefore(title,svg.firstChild);svg.insertBefore(description,title.nextSibling);const background=svgNode('rect',{x:0,y:0,width:620,height:380,fill:'#09152a'});svg.insertBefore(background,description.nextSibling);download('promath-truss-deformation.svg',new XMLSerializer().serializeToString(svg),'image/svg+xml;charset=utf-8');});
  updateSectionShape();
  renderModel(fem.examples.triangle);analyze();
})();
