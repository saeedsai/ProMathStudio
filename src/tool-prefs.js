/* Per-viewer "Find a tool" preferences: recently opened and pinned tool IDs. Storage only; it
   never opens tools or touches the DOM. Every storage access is guarded, so blocked, full or
   corrupt browser storage falls back to an in-memory session list. SPDX-License-Identifier: MIT. */
(()=>{'use strict';
const M=window.MathStudio;if(!M)return;
const KEY='promath-tool-search-prefs-v1',MAX_RECENT=8,MAX_PINS=20,MAX_ID_LENGTH=200,MAX_STORED_LENGTH=16384;
// Keep only distinct, short string IDs, in order, up to the bound.
function clean(list,max,keep){
 const out=[];if(!Array.isArray(list))return out;
 for(const id of list){
  if(typeof id!=='string'||!id.trim()||id.length>MAX_ID_LENGTH||/[\x00-\x1f\x7f]/.test(id)||out.includes(id))continue;
  if(keep&&!keep(id))continue;
  out.push(id);if(out.length>=max)break;
 }
 return out;
}
let persisted=true,unsupportedVersion=false;
function read(){
 try{
  const raw=window.localStorage.getItem(KEY);
  if(raw==null)return {recents:[],pins:[]};
  // A saved preference payload should be tiny. Avoid parsing unbounded or non-string data.
  if(typeof raw!=='string'||raw.length>MAX_STORED_LENGTH){persisted=false;return null;}
  const data=JSON.parse(raw);
  if(!data||typeof data!=='object'||Array.isArray(data)){persisted=false;return null;}
  // Never overwrite a newer schema that this application cannot interpret.
  if(data.v!==undefined&&data.v!==1){persisted=false;unsupportedVersion=true;return null;}
  // Legacy unversioned data remains readable but needs a v1 rewrite.
  if(data.v===undefined)persisted=false;
  // Keep a valid list if its sibling was corrupted, but report that storage
  // needs a successful rewrite before preferences are reliably persisted.
  const recents=clean(data.recents,MAX_RECENT),pins=clean(data.pins,MAX_PINS);
  // Discarded invalid, repeated or excessive IDs mean the stored lists need repair.
  if((data.recents!==undefined&&(!Array.isArray(data.recents)||data.recents.length!==recents.length))||
     (data.pins!==undefined&&(!Array.isArray(data.pins)||data.pins.length!==pins.length)))persisted=false;
  return {recents,pins};
 }catch{persisted=false;return null;} // Blocked storage or corrupt JSON: start session-only; retry on save.
}
const state=read()||{recents:[],pins:[]};
function save(){
 if(unsupportedVersion){persisted=false;return false;}
 try{window.localStorage.setItem(KEY,JSON.stringify({v:1,recents:state.recents,pins:state.pins}));persisted=true;}
 catch{persisted=false;}
 return persisted;
}
const ok=id=>typeof id==='string'&&!!id.trim()&&id.length<=MAX_ID_LENGTH&&!/[\x00-\x1f\x7f]/.test(id);
function addRecent(id,keep){
 if(!ok(id))return false;
 state.recents=clean([id,...state.recents],MAX_RECENT,keep);save();return true;
}
// Returns the new pinned state, or null when the pin list is full.
function setPinned(id,on,keep){
 if(!ok(id))return false;
 const pins=clean(state.pins,MAX_PINS,keep);
 if(on&&!pins.includes(id)){if(pins.length>=MAX_PINS){state.pins=pins;return null;}pins.push(id);}
 state.pins=on?pins:pins.filter(p=>p!==id);
 save();return state.pins.includes(id);
}
M.toolPrefs=Object.freeze({
 key:KEY,limits:Object.freeze({recent:MAX_RECENT,pins:MAX_PINS}),
 recent:keep=>clean(state.recents,MAX_RECENT,keep),
 pinned:keep=>clean(state.pins,MAX_PINS,keep),
 isPinned:id=>state.pins.includes(id),
 addRecent,setPinned,
 togglePin:(id,keep)=>setPinned(id,!state.pins.includes(id),keep),
 clear:()=>{state.recents=[];state.pins=[];return save();},
 persisted:()=>persisted
});
})();
