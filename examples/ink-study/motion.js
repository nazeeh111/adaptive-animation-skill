// Original native SVG drawings and scene time. No borrowed title/shape animation.
const q=id=>document.getElementById(id);
const unit=n=>Math.max(0,Math.min(1,n));
const ease=n=>{n=unit(n);return n*n*(3-2*n)};
const phase=(t,a,b)=>ease((t-a)/(b-a));
const lerp=(a,b,t)=>a+(b-a)*t;
const leaves=[
 {x:325,y:646,angle:8,start:.45,size:1.05},
 {x:300,y:535,angle:176,start:.79,size:1.12},
 {x:347,y:447,angle:19,start:1.02,size:.84},
 {x:333,y:363,angle:173,start:1.25,size:.57}
];
q('leaves').innerHTML=leaves.map((leaf,i)=>`<g id="leaf-${i}"><path class="leaf" d="M0 0C-17-5-34-9-47-21L-53-27L-62-31L-67-42L-76-49L-82-64C-59-70-39-56-28-42C-14-29-3-16 0 0Z"/><path class="vein" d="M-2-2C-26-25-43-40-77-61M-24-22L-45-24M-35-33L-50-34M-44-42L-62-42M-22-22L-23-40M-39-36L-37-51"/><path class="vein" d="M-6-5C-24-20-44-43-76-60" transform="translate(.6 .5)" opacity=".45"/></g>`).join('');
const petalShape="M0 0C-19-11-41-40-31-66L-27-76C-21-91-10-94 0-92C15-96 28-84 32-66C41-44 21-11 0 0Z";
q('petals').innerHTML=Array.from({length:5},(_,i)=>`<g id="petal-${i}"><path class="petal" d="${petalShape}"/><path class="petal-vein" d="M0-4C-8-33-9-63-1-85M-4-31L-20-55M0-45L16-67M-2-58L-16-75"/><path class="petal-vein" d="M-2-2C-21-26-32-55-25-70" opacity=".4"/></g>`).join('');
q('heart').innerHTML=Array.from({length:7},(_,i)=>{const a=(i*52-90)*Math.PI/180,x=Math.cos(a)*18,y=Math.sin(a)*18;return `<path class="stamen" d="M0 1Q${x*.7} ${y*.6} ${x} ${y}"/><ellipse cx="${x}" cy="${y}" rx="2.2" ry="3" fill="#8e7139" transform="rotate(${i*52} ${x} ${y})"/>`}).join('')+'<ellipse cx="0" cy="1" rx="5" ry="4" fill="#a08c50" stroke="#4d5839" stroke-width=".8"/>';
const stemLength=q('stem').getTotalLength(),echoLength=q('stem-echo').getTotalLength();
function reveal(id,p,length){q(id).style.strokeDasharray=length;q(id).style.strokeDashoffset=length*(1-p);}
window.renderFrame=function(seconds){
 const t=Math.max(0,Math.min(4,Number(seconds)||0));
 const growth=phase(t,.08,1.48);reveal('stem',growth,stemLength);reveal('stem-echo',growth,echoLength);
 q('roots').style.opacity=phase(t,0,.28);
 leaves.forEach((leaf,i)=>{const p=phase(t,leaf.start,leaf.start+.54);const recoil=p<1?0:Math.sin((t-leaf.start-.54)*8)*Math.exp(-(t-leaf.start-.54)*7)*2;q('leaf-'+i).setAttribute('transform',`translate(${leaf.x} ${leaf.y}) rotate(${leaf.angle+lerp(-50,0,p)+recoil}) scale(${p*leaf.size} ${lerp(.18,1,p)*p*leaf.size})`);});
 const uncoil=phase(t,1.32,2.2),x=lerp(394,432,uncoil),y=lerp(304,242,uncoil);
 const c1x=lerp(421,402,uncoil),c1y=lerp(286,277,uncoil),c2x=lerp(432,410,uncoil),c2y=lerp(331,269,uncoil);
 const d=`M390 293C${lerp(414,398,uncoil)} ${lerp(281,288,uncoil)} ${c1x} ${c1y} ${c2x} ${c2y}C${lerp(402,416,uncoil)} ${lerp(342,255,uncoil)} ${lerp(378,427,uncoil)} ${lerp(319,251,uncoil)} ${x} ${y}`;
 q('tip-stroke').setAttribute('d',d);q('tip-echo').setAttribute('d',d);q('tip-echo').setAttribute('transform','translate(1.5 .5)');
 // Reveal the tip only after the growing stem reaches its fixed attachment.
 q('tip').style.opacity=phase(t,1.48,1.56);
 const born=phase(t,1.56,1.96),opening=phase(t,2.04,3.25);
 q('flower').setAttribute('transform',`translate(${x} ${y}) scale(${born})`);
 for(let i=0;i<5;i++){const p=phase(t,2.04+i*.045,3.05+i*.045),angle=lerp((i-2)*3,i*72+[-4,3,0,-3,2][i],p);q('petal-'+i).setAttribute('transform',`rotate(${angle}) scale(${lerp(.16,[1,.92,1.04,.94,1.02][i],p)} ${lerp(.62,[1,.94,.98,1.04,.97][i],p)})`);}
 q('heart').style.opacity=phase(t,2.65,3.2);q('heart').setAttribute('transform',`scale(${lerp(.4,1,opening)})`);
 q('note-one').style.opacity=phase(t,.6,.95);q('note-two').style.opacity=phase(t,1.5,1.85);q('note-three').style.opacity=phase(t,2.75,3.15);
 // Recreate the native SVG drawing tree so frame captures do not reuse
 // history-dependent incremental SVG raster caches. Geometry is unchanged.
 const plate=q('plate');plate.replaceWith(plate.cloneNode(true));
 return {time:t,growth,uncoil,born,opening,tip:{x,y},stamensVisible:phase(t,2.65,3.2)};
};
window.renderFrame(0);
