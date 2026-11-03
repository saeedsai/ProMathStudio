/* ProMathStudio: unit conversion and dimensional analysis over the 7 SI base dimensions (offline, no eval). */
(()=>{'use strict';
const M=window.MathStudio;
if(!M)return;
/* Dimension vector order: m, kg, s, A, K, mol, cd. Exponents are exact rationals [numerator, denominator]. */
const BASE=['m','kg','s','A','K','mol','cd'];
const DIM_SYMBOL=['L','M','T','I','Θ','N','J'];
const DISPLAY_ORDER=[1,0,2,3,4,5,6];
const MAX_EXPR=200,MAX_EXP=24;
function gcd(a,b){a=Math.abs(a);b=Math.abs(b);while(b){[a,b]=[b,a%b];}return a||1;}
function rat(n,d=1){if(d<0){n=-n;d=-d;}const g=gcd(n,d);return [n/g,d/g];}
function radd(a,b){return rat(a[0]*b[1]+b[0]*a[1],a[1]*b[1]);}
function rmul(a,b){return rat(a[0]*b[0],a[1]*b[1]);}
function rval(r){return r[0]/r[1];}
const ZERO_DIM=()=>BASE.map(()=>rat(0));
function dimOf(ints){return ints.map(n=>rat(n));}
function sameDim(a,b){return a.every((r,i)=>r[0]===b[i][0]&&r[1]===b[i][1]);}
function expText(r){return r[1]===1?(r[0]===1?'':'^'+r[0]):'^('+r[0]+'/'+r[1]+')';}
function dimensionText(dim){
 const parts=DISPLAY_ORDER.filter(i=>dim[i][0]!==0).map(i=>DIM_SYMBOL[i]+expText(dim[i]));
 return parts.length?parts.join(' '):'1 (dimensionless)';
}
function vectorText(dim){return '('+dim.map(r=>r[1]===1?String(r[0]):r[0]+'/'+r[1]).join(', ')+')';}
function siText(dim){
 const parts=DISPLAY_ORDER.filter(i=>dim[i][0]!==0).map(i=>BASE[i]+expText(dim[i]));
 return parts.length?parts.join('·'):'1';
}

/* SI prefixes as exact powers of ten. 'u' is the ASCII alias of micro. */
const PREFIX={q:-30,r:-27,y:-24,z:-21,a:-18,f:-15,p:-12,n:-9,'µ':-6,'μ':-6,u:-6,m:-3,c:-2,d:-1,da:1,h:2,k:3,M:6,G:9,T:12,P:15,E:18,Z:21,Y:24,R:27,Q:30};
/* Each unit: factor = m × 10^p (in SI base units), dim = integer base exponents, pre = accepts SI prefixes,
   zero = offset to absolute zero in the unit's own scale (non-zero only for affine °C/°F), ice = reading at 0 °C. */
const UNITS=Object.create(null);
function def(names,m,p,dim,pre=false,extra={}){
 const unit=Object.freeze({name:names[0],m,p,dim:dimOf(dim),pre,temp:!!extra.temp,zero:extra.zero||0,ice:extra.ice||0,note:extra.note||''});
 for(const n of names){if(UNITS[n])throw Error('Duplicate unit symbol '+n);UNITS[n]=unit;}
}
//     m  kg  s  A  K mol cd
def(['m'],1,0,[1,0,0,0,0,0,0],true);
def(['g'],1,-3,[0,1,0,0,0,0,0],true);
def(['s'],1,0,[0,0,1,0,0,0,0],true);
def(['A'],1,0,[0,0,0,1,0,0,0],true);
def(['K'],1,0,[0,0,0,0,1,0,0],true,{temp:true,ice:273.15});
def(['mol'],1,0,[0,0,0,0,0,1,0],true);
def(['cd'],1,0,[0,0,0,0,0,0,1],true);
def(['N'],1,0,[1,1,-2,0,0,0,0],true);
def(['J'],1,0,[2,1,-2,0,0,0,0],true);
def(['W'],1,0,[2,1,-3,0,0,0,0],true);
def(['Pa'],1,0,[-1,1,-2,0,0,0,0],true);
def(['Hz'],1,0,[0,0,-1,0,0,0,0],true);
def(['C'],1,0,[0,0,1,1,0,0,0],true);
def(['V'],1,0,[2,1,-3,-1,0,0,0],true);
def(['Ω','\u2126','ohm'],1,0,[2,1,-3,-2,0,0,0],true);
def(['F'],1,0,[-2,-1,4,2,0,0,0],true);
def(['H'],1,0,[2,1,-2,-2,0,0,0],true);
def(['S'],1,0,[-2,-1,3,2,0,0,0],true);
def(['Wb'],1,0,[2,1,-2,-1,0,0,0],true);
def(['T'],1,0,[0,1,-2,-1,0,0,0],true);
def(['L','l'],1,-3,[3,0,0,0,0,0,0],true);
def(['rad'],1,0,[0,0,0,0,0,0,0],true);
def(['sr'],1,0,[0,0,0,0,0,0,0]);
def(['deg','°'],Math.PI/180,0,[0,0,0,0,0,0,0]);
def(['min'],60,0,[0,0,1,0,0,0,0]);
def(['h'],3600,0,[0,0,1,0,0,0,0]);
def(['day'],86400,0,[0,0,1,0,0,0,0]);
def(['eV'],1.602176634,-19,[2,1,-2,0,0,0,0],true);
def(['cal'],4.184,0,[2,1,-2,0,0,0,0],true,{note:'thermochemical calorie'});
def(['Wh'],3600,0,[2,1,-2,0,0,0,0],true);
def(['bar'],1,5,[-1,1,-2,0,0,0,0],true);
def(['atm'],101325,0,[-1,1,-2,0,0,0,0]);
def(['degC','°C','℃'],1,0,[0,0,0,0,1,0,0],false,{temp:true,zero:273.15,ice:0});
def(['degF','°F','℉'],5/9,0,[0,0,0,0,1,0,0],false,{temp:true,zero:459.67,ice:32});
def(['R','degR','°R'],5/9,0,[0,0,0,0,1,0,0],false,{temp:true,ice:491.67});
/* US customary / imperial (exact NIST SP 811 definitions). */
def(['in'],2.54,-2,[1,0,0,0,0,0,0]);
def(['ft'],0.3048,0,[1,0,0,0,0,0,0]);
def(['yd'],0.9144,0,[1,0,0,0,0,0,0]);
def(['mi'],1609.344,0,[1,0,0,0,0,0,0]);
def(['lb','lbm'],0.45359237,0,[0,1,0,0,0,0,0]);
def(['lbf'],4.4482216152605,0,[1,1,-2,0,0,0,0]);
def(['psi'],4.4482216152605/0.00064516,0,[-1,1,-2,0,0,0,0]);
def(['ksi'],4.4482216152605/0.00064516,3,[-1,1,-2,0,0,0,0]);
def(['gal'],3.785411784,-3,[3,0,0,0,0,0,0],false,{note:'US liquid gallon'});
def(['mph'],1609.344/3600,0,[1,0,-1,0,0,0,0]);
def(['hp'],745.69987158227022,0,[2,1,-3,0,0,0,0],false,{note:'mechanical horsepower'});
def(['BTU','Btu'],1055.05585262,0,[2,1,-2,0,0,0,0],false,{note:'International Table BTU'});
/* Names deliberately rejected because they denote several different quantities. */
const AMBIGUOUS={
 ton:'"ton" is ambiguous (short ton, long ton or metric tonne); write the mass in lb or kg.',
 oz:'"oz" is ambiguous (avoirdupois mass ounce or US fluid ounce) and is not supported.',
 Cal:'"Cal" (food Calorie) is easily confused with "cal"; write kcal.',
 gallon:'"gallon" is ambiguous (US or imperial); "gal" means the US liquid gallon.',
 mil:'"mil" is ambiguous (thousandth of an inch or milliradian) and is not supported.'
};
const NAMED=['N','J','W','Pa','Hz','C','V','Ω','F','H','S','Wb','T'].map(n=>UNITS[n]);

function decompositions(token){
 const out=[];
 for(const [prefix,power] of Object.entries(PREFIX)){
  if(token.length>prefix.length&&token.startsWith(prefix)){
   const unit=UNITS[token.slice(prefix.length)];
   if(unit&&unit.pre)out.push({prefix,power,unit});
  }
 }
 return out;
}
function suggest(token){
 const lower=token.toLowerCase(),names=Object.keys(UNITS).filter(n=>n.toLowerCase()===lower);
 for(const [prefix] of Object.entries(PREFIX)){
  const rest=token.slice(prefix.length);
  if(token.startsWith(prefix)&&UNITS[rest]&&!UNITS[rest].pre)return ' SI prefix "'+prefix+'" cannot be applied to "'+rest+'".';
 }
 return names.length?' Did you mean '+names.map(n=>'"'+n+'"').join(' or ')+'? Unit symbols are case-sensitive.':'';
}
/* Exact symbols win only when no prefixed reading also exists; otherwise the token is rejected as ambiguous. */
function resolveUnit(token,pos){
 if(Object.prototype.hasOwnProperty.call(AMBIGUOUS,token))throw Error('Ambiguous unit at position '+(pos+1)+': '+AMBIGUOUS[token]);
 const exact=UNITS[token],split=decompositions(token);
 if(exact&&!split.length)return {unit:exact,power:0};
 if(split.length+(exact?1:0)>1){
  const readings=(exact?['"'+token+'" ('+exact.name+')']:[]).concat(split.map(s=>'"'+s.prefix+'" + "'+s.unit.name+'"'));
  throw Error('Ambiguous unit "'+token+'" at position '+(pos+1)+': it reads as '+readings.join(' or ')+'.');
 }
 if(split.length)return {unit:split[0].unit,power:split[0].power};
 throw Error('Unknown unit "'+token+'" at position '+(pos+1)+'.'+suggest(token));
}
function collisions(){return Object.keys(UNITS).filter(n=>decompositions(n).length);}

const SUPER={'⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9','⁻':'-'};
const IDENT=/[A-Za-z\u00b5\u03bc\u03a9\u2126\u00b0\u2103\u2109_]/;
function tokenize(src){
 const tokens=[];let i=0;
 while(i<src.length){
  const c=src[i];
  if(/\s/.test(c)){i++;continue;}
  if(IDENT.test(c)){let j=i;while(j<src.length&&IDENT.test(src[j]))j++;tokens.push({t:'id',v:src.slice(i,j),pos:i});i=j;continue;}
  if(/\d/.test(c)){let j=i;while(j<src.length&&/\d/.test(src[j]))j++;tokens.push({t:'num',v:src.slice(i,j),pos:i});i=j;continue;}
  if(SUPER[c]!==undefined){
   let j=i,text='';while(j<src.length&&SUPER[src[j]]!==undefined){text+=SUPER[src[j]];j++;}
   if(!/^-?\d+$/.test(text))throw Error('Malformed superscript exponent at position '+(i+1)+'.');
   tokens.push({t:'sup',v:Number(text),pos:i});i=j;continue;
  }
  if('*·⋅×/^()-'.includes(c)){tokens.push({t:'op',v:c==='⋅'||c==='×'||c==='·'?'*':c,pos:i});i++;continue;}
  throw Error('Unexpected character "'+c+'" at position '+(i+1)+'.');
 }
 return tokens;
}
/* term = {m, p, dim, atoms}; factor = m × 10^p. atoms tracks referenced units for temperature semantics. */
function unity(){return {m:1,p:0,dim:ZERO_DIM(),atoms:[]};}
function combine(a,b,sign){
 return {m:sign>0?a.m*b.m:a.m/b.m,p:a.p+sign*b.p,dim:a.dim.map((r,i)=>radd(r,rmul(b.dim[i],rat(sign)))),
  atoms:a.atoms.concat(b.atoms.map(x=>({unit:x.unit,exp:rmul(x.exp,rat(sign))})))};
}
function power(a,e){
 const v=rval(e);
 return {m:Math.pow(a.m,v),p:a.p*v,dim:a.dim.map(r=>rmul(r,e)),atoms:a.atoms.map(x=>({unit:x.unit,exp:rmul(x.exp,e)}))};
}
function parse(expression){
 const src=String(expression??'').trim();
 if(!src)throw Error('Enter a unit expression, for example kg*m/s^2.');
 if(src.length>MAX_EXPR)throw Error('Unit expression exceeds '+MAX_EXPR+' characters.');
 const tokens=tokenize(src);let k=0;
 const peek=()=>tokens[k],end=()=>k>=tokens.length;
 const where=()=>end()?'at the end':'at position '+(peek().pos+1);
 const isOp=v=>!end()&&peek().t==='op'&&peek().v===v;
 function integer(){
  let sign=1;if(isOp('-')){k++;sign=-1;}
  if(end()||peek().t!=='num')throw Error('Expected an integer exponent '+where()+'.');
  return sign*Number(tokens[k++].v);
 }
 function exponent(){
  if(!end()&&peek().t==='sup')return rat(tokens[k++].v);
  if(isOp('(')){
   k++;const n=integer();let d=1;
   if(isOp('/')){k++;d=integer();if(d<=0)throw Error('Exponent denominator must be a positive integer.');}
   if(!isOp(')'))throw Error('Expected ")" to close the exponent '+where()+'.');
   k++;return rat(n,d);
  }
  return rat(integer());
 }
 function primary(){
  if(end())throw Error('Expected a unit, "1" or "(" at the end of the expression.');
  const tok=peek();
  if(tok.t==='id'){k++;const r=resolveUnit(tok.v,tok.pos),u=r.unit;
   return {m:u.m,p:u.p+r.power,dim:u.dim.slice(),atoms:[{unit:u,exp:rat(1),prefixed:r.power!==0}]};}
  if(tok.t==='num'){
   if(tok.v!=='1')throw Error('Numeric factor "'+tok.v+'" at position '+(tok.pos+1)+' is not allowed in a unit; use ^(p/q) for rational exponents.');
   k++;return unity();
  }
  if(isOp('(')){k++;const inner=expr();if(!isOp(')'))throw Error('Expected ")" '+where()+'.');k++;return inner;}
  throw Error('Expected a unit, "1" or "(" '+where()+'.');
 }
 function factor(){
  let base=primary();
  if(!end()&&(isOp('^')||peek().t==='sup')){
   if(isOp('^'))k++;
   const e=exponent();
   if(Math.abs(rval(e))>MAX_EXP||e[1]>12)throw Error('Exponent '+e[0]+(e[1]===1?'':'/'+e[1])+' is outside the supported range.');
   base=power(base,e);
   if(!end()&&(isOp('^')||peek().t==='sup'))throw Error('Chained exponents are not allowed '+where()+'; use parentheses.');
  }
  return base;
 }
 function expr(){
  let left=factor();
  while(isOp('*')||isOp('/')){const sign=tokens[k++].v==='*'?1:-1;left=combine(left,factor(),sign);}
  return left;
 }
 const result=expr();
 if(!end())throw Error('Unexpected "'+peek().v+'" '+where()+'; join units with * or /.');
 const factorValue=result.m*Math.pow(10,result.p);
 if(!Number.isFinite(factorValue)||factorValue===0)throw Error('Unit scale factor is outside the floating-point range.');
 const single=result.atoms.length===1&&result.atoms[0].exp[0]===1&&result.atoms[0].exp[1]===1?result.atoms[0].unit:null;
 return Object.freeze({expression:src,factor:factorValue,m:result.m,p:result.p,dim:result.dim,
  vector:result.dim.map(rval),dimension:dimensionText(result.dim),si:siText(result.dim),
  bareTemperature:single&&single.temp?single:null,
  affineInCompound:result.atoms.some(x=>x.unit.zero!==0)&&!(single&&single.temp)});
}
function ratio(a,b){return (a.m/b.m)*Math.pow(10,a.p-b.p);}
function parseValue(value){
 if(typeof value==='number'){if(!Number.isFinite(value))throw Error('Value must be a finite number.');return value;}
 const s=String(value??'').trim();
 if(!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(s))throw Error('Value must be a finite decimal number such as 12.5 or 1e-3.');
 const v=Number(s);if(!Number.isFinite(v))throw Error('Value must be a finite number.');
 return v;
}
function dimensions(expression){const u=parse(expression);return {vector:u.vector,text:u.dimension,si:u.si};}
function simplify(expression){
 const u=parse(expression);
 const named=NAMED.find(n=>sameDim(n.dim,u.dim));
 return {factor:u.factor,si:u.si,dimension:u.dimension,vector:u.vector,
  named:named&&Math.abs(u.factor-1)<=1e-12?named.name:null,
  text:u.expression+' = '+u.factor+' '+u.si};
}
/* Temperatures: absolute (affine) conversion only between two bare temperature units such as degC → degF.
   Inside compound expressions °C/°F/K/R are temperature differences (W/(m^2*degC) ≡ W/(m^2*K)).
   options.difference = true treats bare temperatures as differences too (10 degC difference = 18 degF). */
function convert(value,from,to,options={}){
 const v=parseValue(value),a=parse(from),b=parse(to),difference=!!(options&&options.difference);
 if(!sameDim(a.dim,b.dim))throw Error('Dimension mismatch: "'+a.expression+'" has dimension '+a.dimension+' '+vectorText(a.dim)+
  ' but "'+b.expression+'" has dimension '+b.dimension+' '+vectorText(b.dim)+' over (m, kg, s, A, K, mol, cd).');
 let out,mode='linear',factor=ratio(a,b);
 const ta=a.bareTemperature,tb=b.bareTemperature;
 if(!difference&&ta&&tb){
  /* Anchor at the ice point (0 °C) so that e.g. 100 °C → 212 °F and −40 °C → −40 °F are exact in binary64. */
  if((v-ta.ice)*a.factor+273.15<-1e-9)throw Error('Temperature '+v+' '+a.expression+' is below absolute zero.');
  out=(v-ta.ice)*(a.factor/b.factor)+tb.ice;mode='absolute';factor=null;
 }else if(!difference&&(ta||tb)&&((ta||tb).zero!==0||(ta?b:a).affineInCompound)){
  throw Error('Absolute temperature conversion between bare "'+(ta?a:b).expression+'" and compound "'+(ta?b:a).expression+
   '" is not defined. Inside compound units temperatures are differences; tick "Temperature difference" or use bare temperature units on both sides.');
 }else if(difference&&(ta||tb)||a.affineInCompound||b.affineInCompound)mode='difference';
 out=mode==='absolute'?out:v*factor;
 if(!Number.isFinite(out))throw Error('Converted value overflows the floating-point range.');
 return {value:out,from:a.expression,to:b.expression,factor,mode,dimension:a.dimension,vector:a.vector,si:a.si,
  siValue:mode==='absolute'?(v-ta.ice)*a.factor+273.15:v*a.factor};
}
function formatNumber(x){
 if(x===0)return '0';
 const t=Number(x.toPrecision(15));
 return Math.abs(t)>=1e15||Math.abs(t)<1e-6?t.toExponential():String(t);
}
const api=Object.freeze({parse,convert,dimensions,simplify,formatNumber,
 units:()=>Object.keys(UNITS),prefixes:()=>Object.assign({},PREFIX),_collisions:collisions});
M.units=api;

const panel=typeof document!=='undefined'&&document.getElementById('calculator-panel');
if(!panel)return;
const $=id=>document.getElementById(id);
const area=document.createElement('details');area.id='units-details';
area.innerHTML='<summary>Unit conversion and dimensional analysis · offline</summary>'+
 '<p class="small-note">SI base, prefixed (q…Q, µ/u, da), derived and exact NIST US customary units. Write products with * or ·, quotients with /, exponents as ^2, ^-1 or ^(1/2), e.g. W/(m^2*K). '+
 'Absolute °C/°F conversion applies to bare temperatures only; inside compound units temperatures are differences (W/(m^2*degC) ≡ W/(m^2*K)). Leave “To unit” empty to simplify to SI base units. Floating-point (binary64) results.</p>'+
 '<div class="units-fields"><label for="units-value">Value<input id="units-value" type="text" inputmode="decimal" spellcheck="false" autocomplete="off" value="1"></label>'+
 '<label for="units-from">From unit<input id="units-from" type="text" spellcheck="false" autocomplete="off" value="mi"></label>'+
 '<label for="units-to">To unit<input id="units-to" type="text" spellcheck="false" autocomplete="off" value="m"></label></div>'+
 '<label class="units-delta"><input id="units-delta" type="checkbox"> Temperature difference (Δ, no offset)</label>'+
 '<div class="data-toolbar"><button id="units-convert" class="primary" type="button">Convert</button></div>'+
 '<pre id="units-output" role="status" aria-live="polite">Enter a value and units, then press Convert or Enter.</pre>';
panel.append(area);
const style=document.createElement('style');style.textContent=
 '#units-details{margin:16px 22px 22px;padding:14px;border:1px solid #dce4f6;border-radius:12px;background:#fbfcff;min-width:0;max-width:100%;box-sizing:border-box}'+
 '#units-details summary{cursor:pointer;font-weight:750;color:#3c50ae;min-height:40px;display:flex;align-items:center}'+
 '.units-fields{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:12px 0}'+
 '.units-fields label{display:flex;flex-direction:column;gap:5px;font-size:12px;color:#566784;font-weight:700;min-width:0}'+
 '.units-fields input{min-width:0;width:100%;box-sizing:border-box;min-height:40px;border:1px solid #cdd8ec;border-radius:8px;padding:9px;background:white;font:inherit}'+
 '.units-delta{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:700;color:#566784;min-height:40px}'+
 '.units-delta input{width:20px;height:20px}'+
 '#units-convert{min-height:40px;min-width:40px}'+
 '#units-output{white-space:pre-wrap;overflow-wrap:anywhere;background:white;border:1px solid #dce5f3;border-radius:9px;padding:12px;max-height:250px;overflow:auto}'+
 '#units-output.error{color:#a82241;background:#fff2f4}'+
 '@media(max-width:600px){.units-fields{grid-template-columns:1fr}#units-details{margin:12px}}';
document.head.append(style);
const output=$('units-output');
function run(){
 try{
  const to=$('units-to').value.trim();
  if(!to){
   const s=simplify($('units-from').value),v=parseValue($('units-value').value);
   output.textContent=formatNumber(v*s.factor)+' '+s.si+(s.named?'  (≡ '+s.named+')':'')+'\nDimension: '+s.dimension+'\nScale: 1 '+$('units-from').value.trim()+' = '+formatNumber(s.factor)+' '+s.si;
  }else{
   const r=convert($('units-value').value,$('units-from').value,to,{difference:$('units-delta').checked});
   output.textContent=formatNumber(r.value)+' '+r.to+'\nDimension: '+r.dimension+' · SI base: '+formatNumber(r.siValue)+' '+r.si+'\n'+
    (r.mode==='absolute'?'Absolute temperature conversion (affine offset applied).':r.mode==='difference'?'Temperature-difference conversion (no offset).':'Factor: 1 '+r.from+' = '+formatNumber(r.factor)+' '+r.to);
  }
  output.classList.remove('error');
 }catch(e){output.classList.add('error');output.textContent=e.message+'\nCorrect the input and press Convert again.';}
}
$('units-convert').addEventListener('click',run);
for(const id of ['units-value','units-from','units-to']){
 $(id).addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();run();}});
 $(id).addEventListener('input',()=>{output.classList.remove('error');output.textContent='Inputs changed. Press Convert or Enter.';});
}
$('units-delta').addEventListener('change',()=>{output.classList.remove('error');output.textContent='Option changed. Press Convert or Enter.';});
})();
