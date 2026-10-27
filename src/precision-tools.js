/* ProMathStudio: bounded exact-decimal calculator and rounded division (offline BigInt). */
(()=>{'use strict';
const M=window.MathStudio, panel=document.getElementById('calculator-panel');
if(!M||!panel)return;
const $=id=>document.getElementById(id);
const MAX_DIGITS=300;
function parseDecimal(raw,label){
 const s=String(raw??'').trim();
 if(!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/.test(s))throw Error(label+' must be a plain finite decimal (no exponent or expression).');
 const digits=s.replace(/^[+-]/,'').replace('.','');
 if(digits.length>MAX_DIGITS)throw Error(label+' exceeds the 300-digit input limit.');
 const dot=s.indexOf('.');
 return {n:BigInt(s.replace('.','')),scale:dot<0?0:s.length-dot-1};
}
function pow10(n){if(!Number.isInteger(n)||n<0||n>700)throw Error('Decimal scale exceeds the supported range.');return 10n**BigInt(n);}
function formatDecimal(n,scale){
 const negative=n<0n;let digits=(negative?-n:n).toString();
 if(scale>0){digits=digits.padStart(scale+1,'0');digits=digits.slice(0,-scale)+'.'+digits.slice(-scale);digits=digits.replace(/\.?0+$/,'');}
 const output=(negative&&n!==0n?'-':'')+digits;
 if(output.length>800)throw Error('Decimal result exceeds the output limit.');
 return output;
}
function roundQuotient(num,den){
 const q=num/den,r=num%den;
 const twice=r*2n;
 return q+(twice>den||(twice===den&&q%2n===1n)?1n:0n);
}
function divide(a,b,precision){
 if(b.n===0n)throw Error('Division by zero.');
 if(a.n===0n)return '0';
 const sign=(a.n<0n)!==(b.n<0n)?-1n:1n;
 const num=(a.n<0n?-a.n:a.n)*pow10(b.scale);
 const den=(b.n<0n?-b.n:b.n)*pow10(a.scale);
 let order=num.toString().length-den.toString().length;
 if(order>=0){if(num<den*pow10(order))order--;}
 else if(num*pow10(-order)<den)order--;
 const shift=precision-1-order;
 if(Math.abs(shift)>700)throw Error('Division precision exceeds the supported scale.');
 if(shift>=0)return formatDecimal(sign*roundQuotient(num*pow10(shift),den),shift);
 return formatDecimal(sign*roundQuotient(num,den*pow10(-shift))*pow10(-shift),0);
}
function isExactDivision(a,b,result){
 const r=parseDecimal(result,'Division result');
 return a.n*pow10(b.scale+r.scale)===r.n*b.n*pow10(a.scale);
}
function calculate({a,b,operation='add',precision=40}={}){
 const p=Number(precision);
 if(!Number.isInteger(p)||p<16||p>80)throw Error('Precision must be an integer from 16 to 80 significant digits.');
 if(!['add','subtract','multiply','divide'].includes(operation))throw Error('Unsupported decimal operation.');
 const x=parseDecimal(a,'First operand'),y=parseDecimal(b,'Second operand');
 let result;
 if(operation==='divide')result=divide(x,y,p);
 else if(operation==='multiply')result=formatDecimal(x.n*y.n,x.scale+y.scale);
 else{
  const scale=Math.max(x.scale,y.scale),left=x.n*pow10(scale-x.scale),right=y.n*pow10(scale-y.scale);
  result=formatDecimal(operation==='add'?left+right:left-right,scale);
 }
 return {result,exact:operation!=='divide'||isExactDivision(x,y,result),precision:p,operation};
}

function evaluateExpression(raw,precision=40){
 const p=Number(precision);
 if(!Number.isInteger(p)||p<16||p>80)throw Error('Precision must be an integer from 16 to 80 significant digits.');
 const input=String(raw??'').trim();
 if(!input||input.length>1200)throw Error('Expression must contain 1–1200 characters.');
 const tokens=input.match(/(?:\d+(?:\.\d*)?|\.\d+)|[()+\-*/]/g);
 if(!tokens||tokens.join('')!==input.replace(/\s+/g,''))throw Error('Unsupported expression token.');
 if(tokens.length>120)throw Error('Expression exceeds the 120-token limit.');
 let pos=0,depth=0,operations=0,rounded=false;
 const apply=(a,b,op)=>{
  if(++operations>100)throw Error('Expression exceeds the 100-operation limit.');
  const outcome=calculate({a,b,operation:({'+':'add','-':'subtract','*':'multiply','/':'divide'})[op],precision:p});
  if(!outcome.exact)rounded=true;
  return outcome.result;
 };
 const factor=()=>{
  let sign=1;
  while(tokens[pos]==='+'||tokens[pos]==='-'){if(tokens[pos]==='-')sign=-sign;pos++;}
  let value;
  if(tokens[pos]==='('){pos++;if(++depth>16)throw Error('Expression exceeds the 16-level nesting limit.');value=expression();if(tokens[pos]!==')')throw Error('Missing closing parenthesis.');pos++;depth--;}
  else {
   const token=tokens[pos];
   if(!token||!/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(token))throw Error('Expected a decimal operand.');
   const parsed=parseDecimal(token,'Expression operand');
   value=formatDecimal(parsed.n,parsed.scale);pos++;
  }
  return sign<0?apply('0',value,'-'):value;
 };
 const term=()=>{let value=factor();while(tokens[pos]==='*'||tokens[pos]==='/'){const op=tokens[pos++];value=apply(value,factor(),op);}return value;};
 const expression=()=>{let value=term();while(tokens[pos]==='+'||tokens[pos]==='-'){const op=tokens[pos++];value=apply(value,term(),op);}return value;};
 const result=expression();if(pos!==tokens.length)throw Error('Unexpected token or missing operator.');
 return {result,precision:p,exact:!rounded,operations};
}

const area=document.createElement('details');area.id='precision-details';
area.innerHTML='<summary>High-precision decimal arithmetic · offline</summary>'+
 '<p class="small-note">Exact decimal +, − and ×; division rounded to 16–80 significant digits (ties to even). Plain decimal operands only, up to 300 digits each. Separate from the standard binary64 Calculator.</p>'+
 '<div class="precision-fields"><label>First decimal<input id="precision-a" type="text" spellcheck="false" value="1"></label>'+
 '<label>Operation<select id="precision-op"><option value="add">Add (+)</option><option value="subtract">Subtract (−)</option><option value="multiply">Multiply (×)</option><option value="divide">Divide (÷)</option></select></label>'+
 '<label>Second decimal<input id="precision-b" type="text" spellcheck="false" value="3"></label>'+
 '<label>Division significant digits<input id="precision-digits" type="number" min="16" max="80" step="1" value="40"></label></div>'+
 '<div class="data-toolbar"><button id="precision-run" class="primary" type="button">Calculate decimal</button></div>'+
 '<pre id="precision-output" role="status" aria-live="polite">Enter two decimal numbers.</pre>';
panel.append(area);

const expressionBox=document.createElement('section');expressionBox.className='precision-expression';
expressionBox.innerHTML='<label for="precision-expression">Decimal expression (+, −, ×, ÷, parentheses)</label>'+
 '<textarea id="precision-expression" rows="2" spellcheck="false" placeholder="(0.1 + 0.2) * 3"></textarea>'+
 '<div class="data-toolbar"><button id="precision-expression-run" type="button">Evaluate expression</button></div>'+
 '<pre id="precision-expression-output" role="status" aria-live="polite">Enter a decimal expression.</pre>';
area.append(expressionBox);

const style=document.createElement('style');style.textContent=
 '#precision-details{margin:16px 22px 22px;padding:14px;border:1px solid #dce4f6;border-radius:12px;background:#fbfcff}'+
 '#precision-details summary{cursor:pointer;font-weight:750;color:#3c50ae}'+
 '.precision-fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:12px 0}'+
 '.precision-fields label{display:flex;flex-direction:column;gap:5px;font-size:12px;color:#566784;font-weight:700}'+
 '.precision-fields input,.precision-fields select{min-width:0;width:100%;border:1px solid #cdd8ec;border-radius:8px;padding:9px;background:white}'+
 '#precision-output{white-space:pre-wrap;overflow-wrap:anywhere;background:white;border:1px solid #dce5f3;border-radius:9px;padding:12px;max-height:250px;overflow:auto}'+
 '#precision-output.error{color:#a82241;background:#fff2f4}'+
 '.precision-expression{margin-top:16px;padding-top:12px;border-top:1px solid #dce5f3}'+
 '.precision-expression label{display:block;font-size:12px;font-weight:700;color:#566784;margin-bottom:6px}'+
 '.precision-expression textarea{display:block;width:100%;min-height:62px;border:1px solid #cdd8ec;border-radius:8px;padding:9px;font:inherit}'+
 '#precision-expression-output{white-space:pre-wrap;overflow-wrap:anywhere;background:white;border:1px solid #dce5f3;border-radius:9px;padding:12px}'+
 '#precision-expression-output.error{color:#a82241;background:#fff2f4}'+
 '@media(max-width:600px){.precision-fields{grid-template-columns:1fr}#precision-details{margin:12px}}';
document.head.append(style);
function invalidate(){$('precision-output').textContent='Inputs changed. Calculate again.';$('precision-output').classList.remove('error');}
for(const id of ['precision-a','precision-b','precision-digits'])$(id).addEventListener('input',invalidate);
$('precision-op').addEventListener('change',invalidate);
$('precision-run').addEventListener('click',()=>{
 try{const r=calculate({a:$('precision-a').value,b:$('precision-b').value,operation:$('precision-op').value,precision:$('precision-digits').value});
  $('precision-output').classList.remove('error');$('precision-output').textContent=r.result+'
'+(r.exact?'Exact decimal result':'Rounded to '+r.precision+' significant digits (half-even)');
 }catch(e){$('precision-output').classList.add('error');$('precision-output').textContent=e.message;}
});

$('precision-expression').addEventListener('input',()=>{
 $('precision-expression-output').textContent='Expression changed. Evaluate again.';
 $('precision-expression-output').classList.remove('error');
});
$('precision-digits').addEventListener('input',()=>{
 $('precision-expression-output').textContent='Precision changed. Evaluate again.';
 $('precision-expression-output').classList.remove('error');
});
$('precision-expression').addEventListener('keydown',event=>{
 if((event.ctrlKey||event.metaKey)&&event.key==='Enter'){event.preventDefault();$('precision-expression-run').click();}
});
$('precision-expression-run').addEventListener('click',()=>{
 try{
  const r=evaluateExpression($('precision-expression').value,$('precision-digits').value);
  $('precision-expression-output').classList.remove('error');
  $('precision-expression-output').textContent=r.result+'
'+(r.exact?'Exact decimal expression':'Division steps rounded to '+r.precision+' significant digits (half-even)');
 }catch(e){$('precision-expression-output').classList.add('error');$('precision-expression-output').textContent=e.message;}
});

M.precisionTools={calculate,evaluateExpression};
})();
