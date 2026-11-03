(function(){
'use strict';
const root=document.getElementById('complex-graph-workbench');
if(!root)return;
const get=id=>document.getElementById(id);
const canvas=get('complex-canvas'),ctx=canvas.getContext('2d');
const calc=(a,b,kind)=>{
 if(kind==='square')return [a*a-b*b,2*a*b];
 if(kind==='inverse'){const d=a*a+b*b;return d>1e-16?[a/d,-b/d]:[NaN,NaN];}
 if(kind==='exp'){const m=Math.exp(a);return [m*Math.cos(b),m*Math.sin(b)];}
 return [a,b];
};
const valid=(a,b)=>Number.isFinite(a)&&Number.isFinite(b);
function render(){
 const a=Number(get('complex-real').value),b=Number(get('complex-imag').value);
 if(!get('complex-real').value.trim()||!get('complex-imag').value.trim()||!valid(a,b)||Math.abs(a)>1e6||Math.abs(b)>1e6){
 get('complex-status').textContent='Enter finite real and imaginary values (absolute value ≤ 1,000,000).';return;
 }
 const kind=get('complex-function').value,mode=get('complex-view').value;
 const result=calc(a,b,kind);
 if(!valid(...result)){get('complex-status').textContent='Function undefined or overflows at this point.';return;}
 const w=canvas.width,h=canvas.height;
 ctx.clearRect(0,0,w,h);ctx.fillStyle='#ffffff';ctx.fillRect(0,0,w,h);
 ctx.font='15px system-ui,sans-serif';ctx.lineWidth=1;
 if(mode==='2d'){
 const bound=Math.max(4,Math.abs(a)*1.25,Math.abs(b)*1.25,Math.abs(result[0])*1.25,Math.abs(result[1])*1.25);
 const scale=Math.min((w-110)/(bound*2),(h-80)/(bound*2)),cx=w/2,cy=h/2;
 ctx.strokeStyle='#e6eef0';
 for(let t=-4;t<=4;t++){const v=t*bound/4;ctx.beginPath();ctx.moveTo(cx+v*scale,20);ctx.lineTo(cx+v*scale,h-20);ctx.moveTo(30,cy-v*scale);ctx.lineTo(w-30,cy-v*scale);ctx.stroke();}
 ctx.strokeStyle='#597b82';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(30,cy);ctx.lineTo(w-25,cy);ctx.moveTo(cx,20);ctx.lineTo(cx,h-25);ctx.stroke();
 ctx.fillStyle='#385d66';ctx.fillText('Re',w-50,cy-12);ctx.fillText('Im',cx+12,24);
 const x=cx+result[0]*scale,y=cy-result[1]*scale;
 ctx.strokeStyle='#188b81';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(x,y);ctx.stroke();
 ctx.fillStyle='#ec824f';ctx.beginPath();ctx.arc(x,y,7,0,Math.PI*2);ctx.fill();
 ctx.fillStyle='#27444b';ctx.fillText('f(z)',Math.min(w-50,x+12),Math.max(20,y-12));
 }else{
 const range=3,steps=26,mag=(x,y)=>{const v=calc(x,y,kind);return valid(...v)?Math.min(8,Math.hypot(...v)):NaN;};
 const project=(x,y,v)=>[w/2+(x-y)*52,h*.68+(x+y)*21-v*26];
 ctx.lineWidth=1;ctx.strokeStyle='#8ebfb8';
 for(let axis=0;axis<2;axis++)for(let i=0;i<=steps;i++){
 const fixed=-range+2*range*i/steps;ctx.beginPath();let started=false;
 for(let j=0;j<=steps;j++){const variable=-range+2*range*j/steps;const x=axis?variable:fixed,y=axis?fixed:variable;const m=mag(x,y);
 if(!Number.isFinite(m)){started=false;continue;}const [px,py]=project(x,y,m);
 if(!started){ctx.moveTo(px,py);started=true;}else ctx.lineTo(px,py);}
 ctx.stroke();
 }
 const [px,py]=project(a,b,Math.min(8,Math.hypot(...result)));
 if(Math.abs(a)<=range&&Math.abs(b)<=range){ctx.fillStyle='#e77843';ctx.beginPath();ctx.arc(px,py,6,0,Math.PI*2);ctx.fill();}
 ctx.fillStyle='#27444b';ctx.fillText('Re(z) →',w*.72,h*.86);ctx.fillText('Im(z) →',w*.22,h*.86);ctx.fillText('|f(z)| ↑',w*.51,30);
 }
 const fmt=n=>Number(n.toPrecision(6));
 get('complex-status').textContent='Plotted '+(mode==='2d'?'Argand point':'magnitude surface')+'.';
 get('complex-detail').textContent='z = '+fmt(a)+(b<0?' − ':' + ')+fmt(Math.abs(b))+'i; f(z) = '+fmt(result[0])+(result[1]<0?' − ':' + ')+fmt(Math.abs(result[1]))+'i; |f(z)| = '+fmt(Math.hypot(...result))+'. 3D surface domain: Re, Im ∈ [−3, 3]; height clipped to 8.';
}
get('complex-plot').addEventListener('click',render);
get('complex-view').addEventListener('change',render);
get('complex-function').addEventListener('change',render);
root.addEventListener('toggle',()=>{if(root.open)render();});
window.ProMathComplexGraph={evaluate:calc,render};
})();
