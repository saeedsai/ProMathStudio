(()=>{'use strict';
const $=id=>document.getElementById(id);const slider=$('table-zoom');const field=$('table-zoom-value');const content=$('table-zoom-content');
function apply(value){const v=Math.max(50,Math.min(200,Number(value)||100));slider.value=String(v);field.textContent=v+'%';slider.setAttribute('aria-valuetext',v+'%');content.style.zoom=String(v/100);try{localStorage.setItem('promath-table-zoom',String(v))}catch{}}
slider.addEventListener('input',()=>apply(slider.value));$('table-zoom-in').addEventListener('click',()=>apply(Number(slider.value)+10));$('table-zoom-out').addEventListener('click',()=>apply(Number(slider.value)-10));$('table-zoom-reset').addEventListener('click',()=>apply(100));
try{apply(localStorage.getItem('promath-table-zoom')||100)}catch{apply(100)}
window.MathStudio.tableZoom={value:()=>Number(slider.value),set:apply};
window.addEventListener('mathstudio:project-loaded',()=>{});
})();
