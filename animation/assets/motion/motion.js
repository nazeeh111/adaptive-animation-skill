// No random clock, autoplay or CSS animation: every frame follows one seekable timeline.
window.__timelines=window.__timelines||{};
// Keep the scaled seed in one paint layer across forward and backward seeks.
gsap.set('.seed',{willChange:'transform'});
const tl=gsap.timeline({paused:true,defaults:{force3D:false}});
tl.from('.context',{opacity:0,y:12,duration:.45,ease:'power2.out'},0)
 .from('h1 span',{opacity:0,y:30,duration:.8,ease:'power3.out'},.18)
 .from('h1 em',{opacity:0,y:34,duration:.9,ease:'power3.out'},.38)
 .from('.support',{opacity:0,y:14,duration:.7,ease:'power2.out'},1.1)
 .from('.orbit',{scale:.78,opacity:0,duration:1.2,ease:'power3.out'},.2)
 .from('.seed',{scale:0,duration:1.1,ease:'back.out(1.25)'},.6)
 .fromTo('.echo',{scale:1,opacity:.7},{scale:2.8,opacity:0,duration:1.5,ease:'power2.out'},1.1)
 .to('.seed',{xPercent:35,yPercent:-24,duration:1.4,ease:'sine.inOut'},2)
 .to('.seed',{xPercent:0,yPercent:0,duration:1.4,ease:'sine.inOut'},3.4)
 .from('.endnote',{opacity:0,duration:.6},1.5)
 .to('.orbit',{rotation:30,duration:6,ease:'none'},0);
// Initialize overlapping transform tweens before arbitrary capture seeks. Keep
// one transform mode so first and backward seeks paint the same pixels.
tl.totalTime(tl.duration(),true).totalTime(0,true);
// Controls are opt-in and excluded from ordinary render URLs.
if(new URLSearchParams(location.search).get('preview')==='1'){
 document.querySelector('#preview').hidden=false;
 const seek=document.querySelector('#seek'),label=document.querySelector('#time');
 const play=document.querySelector('#play');
 const preference=matchMedia('(prefers-reduced-motion: reduce)');
 function reflect(){play.textContent=tl.paused()?'Play':'Pause';play.setAttribute('aria-pressed',String(!tl.paused()));}
 function applyPreference(){if(preference.matches)tl.pause().seek(6,false);play.disabled=preference.matches;reflect();}
 play.onclick=()=>{if(tl.time()>=tl.duration())tl.restart();else tl.paused(!tl.paused());reflect();};
 preference.addEventListener('change',applyPreference);
 document.querySelector('#restart').onclick=()=>{if(preference.matches)tl.pause().seek(6,false);else tl.restart();reflect();};
 seek.oninput=()=>{tl.pause().seek(Number(seek.value),false);reflect();};
 tl.eventCallback('onUpdate',()=>{seek.value=tl.time();label.textContent=tl.time().toFixed(2)+' s';reflect();});
 tl.seek(1.6,false);applyPreference();
}
