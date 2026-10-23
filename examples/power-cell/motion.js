// Original integer-grid pixel animation. Every frame is drawn from declared time.
// Pose exposure: 10 drawings per second. No accumulated simulation or randomness.
window.__timelines=window.__timelines||{};
const totalDuration=Number(document.querySelector('#studio').dataset.duration);
const clock={time:0},tl=gsap.timeline({paused:true}).to(clock,{time:totalDuration,duration:totalDuration,ease:'none'},0);
const canvas=document.querySelector('#scene'),g=canvas.getContext('2d');g.imageSmoothingEnabled=false;
const P={ink:'#191b20',deep:'#29292b',wall:'#353132',line:'#514440',rust:'#8e5241',metal:'#777267',light:'#b2ac90',cream:'#e5dfb6',yellow:'#d8a74d',shadow:'#8b663a',lime:'#c0d35b',darklime:'#687d45',red:'#a65a48'};
const r=(x,y,w,h,c)=>{g.fillStyle=c;g.fillRect(Math.round(x),Math.round(y),w,h)};
function label(s,x,y,c=P.light,size=5){g.fillStyle=c;g.font=size+'px monospace';g.textBaseline='top';g.fillText(s,x,y);}
function bolt(x,y){r(x,y,2,2,P.ink);r(x,y,1,1,P.light);}
function crate(x,y){r(x,y,18,14,P.ink);r(x+1,y+1,16,12,P.rust);r(x+3,y+3,12,2,P.yellow);r(x+3,y+9,12,2,P.shadow);r(x+8,y+1,2,12,P.light);}
function robot(x,pose,powered,t){
 const bend=pose==='push'?2:pose==='brace'?1:0;
 // This is a wheeled maintenance rover, not a walking rig. Two visible wheels
 // share the floor at y=153. Spoke phase derives from traveled x, so a hold
 // does not spin the hubs and backward seeks restore their exact orientation.
 r(x-3,140,32,7,P.ink);r(x-1,142,28,3,P.metal);
 const spoke=Math.floor(x/3)%2;
 for(const wx of [x-3,x+19]){
  r(wx+2,143,6,10,P.ink);r(wx,145,10,6,P.ink);
  r(wx+2,145,6,6,P.metal);r(wx+4,147,2,2,P.cream);
  if(spoke){r(wx+2,145,2,2,P.cream);r(wx+6,149,2,2,P.cream);}
  else{r(wx+4,145,2,6,P.cream);r(wx+2,147,6,2,P.cream);}
 }
 r(x+3+bend,123,20,23,P.ink);r(x+5+bend,123,16,19,P.yellow);r(x+6+bend,125,4,11,P.cream);r(x+16+bend,128,3,4,powered?P.lime:P.shadow);
 r(x+1+bend,101+bend,25,23,P.ink);r(x+3+bend,103+bend,21,18,P.yellow);r(x+5+bend,107+bend,17,8,P.ink);
 r(x+7+bend,109+bend,4,3,powered?P.lime:P.cream);r(x+16+bend,109+bend,4,3,powered?P.lime:P.cream);
 r(x+6+bend,119+bend,14,2,P.shadow);r(x+10+bend,98+bend,3,4,P.metal);r(x+9+bend,96+bend,5,2,P.red);
 if(pose==='push'||pose==='brace'){
  r(x+21+bend,125,10-bend,6,P.ink);r(x+22+bend,126,8-bend,4,P.metal);r(x+28,123,4,10,P.cream);
 }else{
  r(x+22,126,5,14,P.ink);r(x+23,127,3,11,P.metal);r(x+23,138,6,5,P.cream);
 }
}
function draw(seconds){
 const t=Math.floor(Math.max(0,Math.min(4,seconds))*10+1e-7)/10;
 const pushing=Math.max(0,Math.min(1,(t-.5)/1.7));
 const cellX=128+Math.round(pushing*76),connected=t>=2.3,power=t>=2.5,belt=t>=2.9;
 // Asymmetric game stage. Left side gives room to read the approach and brace.
 r(0,0,320,180,P.ink);r(0,27,320,126,P.wall);
 for(let y=32;y<145;y+=23){r(0,y,320,1,P.deep);for(let x=(y%46?0:25);x<320;x+=51)r(x,y,1,23,P.deep);}
 r(12,42,128,7,P.deep);r(12,42,128,2,P.metal);r(12,42,4,74,P.metal);r(12,112,35,4,P.metal);r(42,112,5,20,P.metal);
 r(42,129,11,6,P.deep);r(43,129,9,2,P.light);
 label('LINE 07 / SERVICE BAY',12,12,P.cream,6);label('MANUAL START',12,24,P.metal,5);
 // Central-low rail physically supports the cell's weight.
 r(110,145,139,5,P.ink);r(110,145,139,2,P.metal);r(117,150,6,3,P.deep);
 // Machine casing, service opening and tall stack anchor the right-hand stage.
 r(193,31,111,118,P.ink);r(196,34,105,111,P.rust);r(198,36,101,8,P.shadow);
 r(204,49,87,43,P.deep);r(208,53,44,35,P.ink);
 for(let k=0;k<4;k++)r(212,58+k*6,34,2,power?P.darklime:P.wall);
 if(power){r(214,61,4,3,P.lime);r(219,67,8,3,P.lime);r(229,59,13,2,P.lime);r(231,76,9,2,P.lime);}
 r(259,53,25,4,P.metal);r(259,63,25,4,P.metal);r(259,73,25,4,P.metal);
 bolt(200,38);bolt(295,38);bolt(200,139);bolt(295,139);
 label('CELL',250,101,P.cream,5);
 r(194,113,50,31,P.ink);r(198,116,44,24,P.deep);r(236,118,4,20,connected?P.lime:P.red);
 // Empty cell insert approaches, contacts, then vanishes behind the socket lip.
 r(cellX,118,34,24,P.ink);r(cellX+2,120,30,20,P.metal);r(cellX+4,122,5,16,P.light);
 r(cellX+11,123,15,14,P.ink);r(cellX+13,125,11,10,P.lime);r(cellX+17,122,3,16,P.darklime);
 r(cellX+30,124,4,12,P.yellow);r(cellX+5,142,5,3,P.ink);r(cellX+25,142,5,3,P.ink);
 // Casing lip masks the insertion so the robot pushes against a real edge.
 r(233,113,12,31,P.ink);r(239,116,4,24,P.metal);
 if(connected){r(201,114,30,2,P.lime);r(201,141,30,2,P.lime);}
 const pose=t<.3?'idle':t<.5?'brace':t<2.4?'push':'idle';
 const rx=t<2.4?cellX-31:cellX-36-Math.min(7,Math.floor((t-2.4)*10));
 robot(rx,pose,power,t);
 // Status stack is off until the insertion finishes.
 r(280,18,9,16,P.ink);r(282,20,5,6,power?P.lime:P.red);r(282,28,5,4,P.metal);
 if(power){r(279,16,11,1,P.yellow);r(278,20,1,5,P.yellow);r(290,20,1,5,P.yellow);}
 // Conveyor begins only after the machine powers up, carrying one box away.
 r(213,146,107,10,P.ink);r(213,146,107,3,P.metal);r(213,154,107,3,P.shadow);
 // Only the exposed top run is shown. Belt marks and crate share the same
 // rightward displacement; the hidden return run is not depicted.
 const beltTravel=belt?Math.floor((t-2.9)*31):0,offset=beltTravel%8;
 g.save();g.beginPath();g.rect(213,149,107,5);g.clip();
 for(let x=205+offset;x<320;x+=8){r(x,150,5,2,P.light);r(x+1,152,3,2,P.deep);}
 g.restore();
 r(224,156,5,12,P.metal);r(295,156,5,12,P.metal);r(220,168,13,3,P.ink);r(291,168,13,3,P.ink);
 crate(259+beltTravel,132);
 // Ground and contact shadows remain fixed. No decorative ambient animation.
 r(0,153,207,27,P.deep);r(0,153,207,2,P.metal);
 for(let x=0;x<206;x+=22)r(x,166,16,1,P.line);
 r(rx-2,153,33,2,P.ink);
 if(connected&&t<2.6){const k=Math.floor((t-2.3)*10);r(220+k*3,108-k,2,2,P.cream);r(228-k*2,104+k,2,2,P.yellow);}
 label(power?'POWER ON':'NO POWER',251,94,power?P.lime:P.light,5);
}
window.renderFrame=function(seconds){const t=Math.max(0,Math.min(totalDuration,Number(seconds)||0));tl.pause().seek(t,false);draw(t);};
let reflect=()=>{};
tl.eventCallback('onUpdate',()=>{draw(tl.time());reflect();});
if(new URLSearchParams(location.search).get('preview')==='1'){
 document.querySelector('#preview').hidden=false;
 const seek=document.querySelector('#seek'),label=document.querySelector('#time'),play=document.querySelector('#play');
 const preference=matchMedia('(prefers-reduced-motion: reduce)');
 reflect=()=>{seek.value=tl.time();label.textContent=tl.time().toFixed(2)+' s';play.textContent=tl.paused()?'Play':'Pause';play.setAttribute('aria-pressed',String(!tl.paused()));};
 function applyPreference(){if(preference.matches)window.renderFrame(totalDuration);play.disabled=preference.matches;reflect();}
 play.onclick=()=>{if(preference.matches)return;if(tl.time()>=tl.duration())tl.restart();else tl.paused(!tl.paused());reflect();};
 document.querySelector('#restart').onclick=()=>{window.renderFrame(preference.matches?totalDuration:0);reflect();};
 seek.oninput=()=>{window.renderFrame(Number(seek.value));reflect();};preference.addEventListener('change',applyPreference);applyPreference();
}
window.renderFrame(new URLSearchParams(location.search).get('preview')==='1'&&matchMedia('(prefers-reduced-motion: reduce)').matches?totalDuration:0);
