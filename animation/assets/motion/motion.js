// Capture scaffold only. Author the action and its consequence for the brief.
// No preselected shapes, reveal, decorative motion, copy or font pairing.
window.__timelines=window.__timelines||{};
const totalDuration=Number(document.querySelector('#studio').dataset.duration);
const tl=gsap.timeline({paused:true});
// Retain a seekable time range while the scene is being authored.
// Replace/extend this dummy clock with the scene's actual timeline.
tl.to({progress:0},{progress:1,duration:totalDuration,ease:'none'},0);
window.renderFrame=seconds=>{tl.pause().seek(Math.max(0,Math.min(totalDuration,seconds)),false);};
if(new URLSearchParams(location.search).get('preview')==='1'){
 document.querySelector('#preview').hidden=false;
 const seek=document.querySelector('#seek'),label=document.querySelector('#time'),play=document.querySelector('#play');
 const preference=matchMedia('(prefers-reduced-motion: reduce)');
 function reflect(){seek.value=tl.time();label.textContent=tl.time().toFixed(2)+' s';play.textContent=tl.paused()?'Play':'Pause';play.setAttribute('aria-pressed',String(!tl.paused()));}
 function applyPreference(){if(preference.matches)tl.pause().seek(totalDuration,false);play.disabled=preference.matches;reflect();}
 play.onclick=()=>{if(preference.matches)return;if(tl.time()>=tl.duration())tl.restart();else tl.paused(!tl.paused());reflect();};
 document.querySelector('#restart').onclick=()=>{tl.pause().seek(preference.matches?totalDuration:0,false);reflect();};
 seek.oninput=()=>{window.renderFrame(Number(seek.value));reflect();};
 tl.eventCallback('onUpdate',reflect);preference.addEventListener('change',applyPreference);applyPreference();
}
