/** Rebuild this editable release deck in an existing Artifact Tool environment.
 * Usage: node build.mjs [repository-root] [new-output-directory]
 * The existing output directory is never overwritten. See README.md.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const {PresentationFile,FileBlob}=process.env.ANIMATION_ARTIFACT_MODULE
  ? await import(pathToFileURL(path.resolve(process.env.ANIMATION_ARTIFACT_MODULE)).href)
  : await import('@oai/artifact-tool');
const here=path.dirname(fileURLToPath(import.meta.url));
const root=process.argv[2]?path.resolve(process.argv[2]):path.resolve(here,'../../..');
const out=process.argv[3]?path.resolve(process.argv[3]):path.join(here,'out');
const {createRetargetedSpring}=await import(pathToFileURL(path.join(root,'animation/assets/motion/retargeted-spring.mjs')).href);
const p=await PresentationFile.importPptx(await FileBlob.load(path.join(here,'base.pptx')));
// Preserve the existing public deck's current palette, type and dimensions.
const C={paper:'#F4F7FA',ink:'#16242B',muted:'#526773',teal:'#006F70',pale:'#DCEEEF',accent:'#7248B4',line:'#A8BAC5'};
const [cover,purpose,workflow,time,handoff,oldQA,pack]=p.slides.items;
p.slides.keep([0,1,2,3,4,6]);
function find(s,name){const x=s.shapes.items.find(x=>x.name===name);if(!x)throw Error('Missing base element '+name);return x;}
function set(s,name,value){find(s,name).text=value;}
function text(s,name,t,x,y,w,h,size=28,color=C.ink,bold=false){const a=s.shapes.add({name,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});a.text=t;a.text.style={typeface:'Arial',fontSize:size,color,bold,alignment:'left',verticalAlignment:'middle',wrap:'square',insets:0};return a;}
function rect(s,name,x,y,w,h,fill,stroke='none',geometry='rect'){return s.shapes.add({name,geometry,position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:stroke==='none'?0:1.5,style:'solid'}});}
function line(s,name,x,y,w,h,color=C.line,width=1.5){return s.shapes.add({name,geometry:'line',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:color,width,style:'solid'}});}
function base(title){const s=p.slides.add();s.background.fill=C.paper;text(s,'title',title,66,47,1148,70,46,C.ink,true);text(s,'page','00',1160,647,54,28,17,C.muted);return s;}
function notes(s,body,links){s.speakerNotes.text=body+'\n\nSources:\n'+links.join('\n');}
const repo='https://github.com/nazeeh111/adaptive-animation-skill';
set(cover,'cover-subtitle','An adaptive production skill for authored motion,\nnative sources and evidence that matches the claim.');
notes(cover,'The skill adapts craft, tools and verification to the subject and receiving system. This deck describes the current workflow and bounded examples. Its visual design belongs to this release deck and does not prescribe the look of future animations.',[repo,'animation/SKILL.md']);
set(purpose,'craft-body-2','Movement and intentional stillness create contrast.');
notes(purpose,'Craft guidance is conditional on the actual brief. A held drawing, a spring, a scientific diagram and an edit may need different timing. Constant movement is not a quality target. Preserve identity and judge cause, contact and payoff in sequence.',['animation/SKILL.md','animation/references/purposeful-motion.md','animation/references/styles-and-techniques.md']);
notes(workflow,'The editable six-stage diagram combines rendering with review and treats packaging as part of the handoff. Material findings return to craft. Receiving-application defects return to build. Simple tasks can combine stages. The standalone SVG in animation/docs/diagram.svg has eight more explicit stages.',['animation/SKILL.md','animation/docs/diagram.svg']);
set(time,'title','Explicit time and input');
set(time,'offline-formula','Frame + declared inputs');set(time,'live-formula','Events + current state');
set(time,'offline-body','Evaluate any requested time.\nBake simulations when needed.\nWait for media and fonts.\nCheck cues and shuffled seeks.');
set(time,'live-body','Define pause, reset and replay.\nRetain inputs needed for replay.\nBound ongoing work and memory.\nRespect motion controls as needed.');
set(time,'time-note','Share meaningful cues. Keep global edit time, local shot time and overlap distinct.');
notes(time,'Deterministic capture evaluates the same declared time and inputs to the same scene state. Live interaction can evolve, with an explicit time and input contract. Named cues coordinate the existing project rather than requiring another framework. Frame checks cover the exercised states and do not establish compelling motion.',['animation/references/purposeful-motion.md','https://www.remotion.dev/docs/flickering','https://gsap.com/docs/v3/GSAP/Timeline/seek()/','https://motioncanvas.io/docs/time-events/','https://www.remotion.dev/docs/transitions/transitionseries','https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html']);
set(handoff,'title','Native tools and editable handoffs');
set(handoff,'tool-thesis','Choose the route for the medium and the controls the receiver needs.');
notes(handoff,'These are examples of native routes, not a complete list or a performance ranking. A browser frame does not establish 3D editability, an exported timeline does not prove a receiver preserved every control, and a completed render does not establish the best artistic choice. Check material properties in the actual receiving application.',['animation/SKILL.md','animation/references/production.md','animation/references/styles-and-techniques.md','https://threejs.org/manual/pages/cleanup.html']);
set(pack,'title','A usable handoff');
set(pack,'package-body-0','Requested media, native source and necessary assets.');
set(pack,'package-body-1','Relative paths, dependency notes and retained notices.');
set(pack,'package-body-3','Separate passed, failed and unavailable checks.');
notes(pack,'Deliver the requested masters, source and necessary dependencies with a clear entry point. Keep the last valid version until a replacement passes relevant checks. Preserve software and asset terms. A file, sampled image, full decode, receiving-system check and perceptual review establish different evidence.',['animation/SKILL.md','animation/references/production.md','animation/references/portable-setup.md']);
// New slide: actual reviewed examples in their original aspect ratios.
const demo=base('Two authored motion languages');
text(demo,'demo-intro','Four-second scenes from the same neutral scaffold',70,120,1120,43,27,C.muted);
async function image(s,rel,alt,x,y,w,h){const bytes=await fs.readFile(path.join(root,rel));s.images.add({blob:bytes,contentType:'image/png',alt,fit:'contain',position:{left:x,top:y,width:w,height:h}});}
await image(demo,'examples/ink-study/preview.png','Original botanical ink SVG study with attached stem, leaves and opening flower',70,170,304,380);
await image(demo,'examples/power-cell/preview.png','Original pixel maintenance rover after inserting a power cell, with powered machine and moving conveyor',454,170,676,380);
text(demo,'ink-label','Botanical ink study',70,574,350,43,28,C.ink,true);text(demo,'ink-detail','SVG growth and unfolding',70,617,360,35,24,C.muted);
text(demo,'pixel-label','Pixel maintenance rover',454,574,720,43,28,C.ink,true);text(demo,'pixel-detail','Stepped insertion, power and conveyor',454,617,700,35,24,C.muted);
notes(demo,'Original silent examples. Ink preview is a decoded 3.5-second frame from the selected 720x900 master. Power-cell preview is a decoded 3.2-second frame from the selected 960x540 master. Both scenes retain editable native code. Sampled replay and full-decode checks are scoped evidence. These stills cannot establish normal-speed rhythm or universal stylistic range. No third-party gallery media or font binaries appear here.',['examples/ink-study/README.md','examples/ink-study/preview.png','examples/ink-study/ink-study.mp4','examples/ink-study/LICENSE','examples/power-cell/README.md','examples/power-cell/preview.png','examples/power-cell/power-cell.mp4','examples/power-cell/LICENSE','examples/power-cell/THIRD-PARTY.txt']);
// New slide: scaffold infrastructure is deliberately separated from artwork.
const scaffold=base('Neutral scaffold and explicit example');
text(scaffold,'scaffold-intro','Capture infrastructure carries geometry and time. The brief supplies the scene.',70,126,1135,64,29,C.muted);
line(scaffold,'scaffold-split',630,228,0,301);
text(scaffold,'generic-title','Generic motion scaffold',70,218,520,63,33,C.teal,true);
text(scaffold,'generic-code','--template motion --duration 4',70,302,520,53,26,C.ink,true);
text(scaffold,'generic-body','Dimensions, a paused clock,\nlocal runtime and preview controls.\nAuthor the artwork and action.',70,383,520,132,28,C.muted);
text(scaffold,'example-title','Selected authored study',682,218,520,63,33,C.teal,true);
text(scaffold,'example-code','--template motion\n--example orbit-title',682,296,520,87,26,C.ink,true);
text(scaffold,'example-body','Copies the six-second title study,\nincluding its original artwork,\nfonts and retained licenses.',682,399,520,125,28,C.muted);
text(scaffold,'scaffold-bottom','The generic scaffold supplies no palette, copy, typography or staging.',70,592,1110,56,28,C.ink,true);
notes(scaffold,'These are optional studio.py init flags, for example: python animation/scripts/studio.py init project --brief "An authored action" --template motion --duration 4. Plain init can also create an empty workspace. Generic motion has a usable seekable time range but intentionally no artwork. --example orbit-title explicitly selects the preserved authored study and requires its original six-second duration. Existing projects are unaffected.',['animation/scripts/studio.py','animation/assets/motion/','animation/assets/examples/orbit-title/','animation/references/portable-setup.md']);
// New slide: actual helper-derived data stays editable as a native chart.
const spring=base('A replayable spring track');
text(spring,'spring-thesis','Preserve position and velocity\nwhen a target changes\nbefore settling.',70,162,390,164,32,C.teal,true);
text(spring,'spring-body','Evaluate directly at any time.\nReplay the same target history.\nUse native interruption behavior\nwhen it already fits.',70,365,390,154,27,C.muted);
const options={initialValue:40,frequencyHz:2.3,dampingRatio:.61,events:[{time:.1,target:240},{time:.28,target:90}]};
const track=createRetargetedSpring(options);const times=Array.from({length:61},(_,i)=>i/50);const values=times.map(t=>Number(track.sample(t).value.toPrecision(12)));
const chart=spring.charts.add('scatter',{position:{left:490,top:162,width:710,height:402},hasLegend:true,legend:{position:'bottom',textStyle:{fontSize:20,fill:C.ink}},scatterOptions:{style:'line'},chartFill:'none',chartLine:{fill:'none',width:0},plotAreaFill:'none',plotAreaLine:{fill:'none',width:0},series:[{name:'Target',xValues:[0,.1,.1,.28,.28,1.2],values:[40,40,240,240,90,90],line:{fill:C.accent,width:2,style:'solid'},marker:{symbol:'none'}},{name:'Response',xValues:times,values,line:{fill:C.teal,width:3,style:'solid'},marker:{symbol:'none'}}],xAxis:{title:{text:'Time (s)',textStyle:{fontSize:21,fill:C.ink}},min:0,max:1.2,majorUnit:.3,numberFormatCode:'0.0',textStyle:{fontSize:20,fill:C.muted},line:{fill:C.line,width:1},majorGridlines:null},yAxis:{title:{text:'Position (px)',textStyle:{fontSize:21,fill:C.ink}},min:0,max:260,majorUnit:80,numberFormatCode:'0',textStyle:{fontSize:20,fill:C.muted},line:{fill:C.line,width:1},majorGridlines:{fill:C.line,width:.6,style:'solid'}},dataLabels:{showValue:false,textStyle:{fontSize:20,fill:C.ink}}});
for(const style of [chart.legend.textStyle,chart.dataLabels.textStyle,chart.xAxis.textStyle,chart.yAxis.textStyle,chart.xAxis.title.textStyle,chart.yAxis.title.textStyle])style.typeface='Arial';
text(spring,'spring-limit','Fixed scalar spring, damping below critical. Illustrative values. No contact solver.',70,596,1130,58,24,C.muted);
notes(spring,'Chart values come directly from createRetargetedSpring, rounded to 12 significant digits for the embedded chart workbook, with initial position 40 px, targets 240 px at 0.10 s and 90 px at 0.28 s, natural frequency 2.3 Hz and damping ratio 0.61. They illustrate a fixed underdamped linear model with zero initial velocity. The helper evaluates the sum of step responses without a per-frame simulation cache. Its independent tests compare with numerical integration and continuity probes. It is optional and does not establish aesthetic quality, collisions, changing coefficients or unbounded streaming behavior.',['animation/assets/motion/retargeted-spring.mjs','animation/references/retargeted-motion.md','animation/tests/test_retargeted_spring.mjs','https://github.com/yihui-dev/awesome-opus5-5-videos/blob/92aee2f586ac0715cb3cbcb6384834f98a33383d/prompts/twoclipping-402193.md']);
// New diagnostic explanation replaces the older broad QA list.
const diagnostics=base('Checks at significant moments');
text(diagnostics,'diagnostic-intro','A short action can fall between default samples.',70,125,1110,57,30,C.muted);
const x0=82,span=1100,axisY=268;line(diagnostics,'time-axis',x0,axisY,span,0,C.line,3);
rect(diagnostics,'action-window',x0+span*2/12,axisY-18,span*.3/12,36,C.accent);
const defaults=[0,.6,1.5,3,6,9,10.8,11.88];for(let i=0;i<defaults.length;i++)rect(diagnostics,'default-sample-'+i,x0+span*defaults[i]/12-5,axisY-5,10,10,C.muted,'none','ellipse');
text(diagnostics,'event-label','300 ms action at 2.0–2.3 s',210,198,580,43,27,C.accent,true);
text(diagnostics,'time-start','0 s',70,287,90,35,23,C.muted);text(diagnostics,'time-end','12 s',1116,287,90,35,23,C.muted);
text(diagnostics,'default-label','Default fractions miss the change in this 12-second test.',70,337,1120,47,28,C.ink);
text(diagnostics,'explicit-title','Samples around the actual event',70,416,1100,50,32,C.teal,true);
text(diagnostics,'explicit-times','--times 1.95,2.05,2.20,2.35',70,476,1100,49,29,C.ink,true);
text(diagnostics,'diagnostic-body','Replay earlier times after later ones. Compare pixels as well as numeric state.',70,548,1120,55,26,C.ink);
text(diagnostics,'diagnostic-limit','These samples diagnose selected moments. Playback, sound and receiver checks remain separate.',70,609,1120,43,23,C.muted);
notes(diagnostics,'The regression test authors a 300 ms state change at t>=2 and t<2.3 within 12 seconds. Default samples use duration fractions 0, .05, .125, .25, .5, .75, .9 and .99, so none enters the interval. Explicit seconds include 1.95, 2.05, 2.2 and 2.35 and add time zero. This is a concrete sampling example, not a universal recommended schedule. Browser diagnostics cover selected states, raster tolerances and local resources. They cannot approve artistic quality, facts outside the scene or unavailable audiovisual review.',['animation/scripts/check_motion.mjs','animation/tests/test_motion_browser.py','docs/pass2-validation.md','animation/references/purposeful-motion.md']);
// New research summary keeps conditional mechanisms and evidence boundaries.
const research=base('Research transfers and limits');
text(research,'research-intro','A useful mechanism must earn its place in the current brief.',70,128,1110,63,32,C.teal,true);
const rows=[['Reusable ideas','Shared cues, explicit clocks, interruption behavior and artifact-first critique.'],['Conditional techniques','Paint mechanisms and CSS 3D fade structure depend on the actual medium.'],['Evidence limits','Source reading and gallery examples establish leads. Runtime comparisons test specific behavior.']];
for(let i=0;i<rows.length;i++){const y=240+i*110;text(research,'research-label-'+i,rows[i][0],70,y,292,70,28,C.ink,true);text(research,'research-body-'+i,rows[i][1],390,y,796,80,27,C.muted);if(i<2)line(research,'research-rule-'+i,70,y+93,1115,0);}
text(research,'research-bottom','Choose palette, typography and rhythm for the subject. Keep performance claims scoped.',70,603,1120,51,25,C.ink);
notes(research,'Research selected mechanisms rather than copying a whole framework or aesthetic taxonomy. Gallery prompts and external source trees were inspected at cited versions. Procedural paint remained conditional because no painterly brief justified an engine import. The separate CSS3D grouping example adds an actual browser comparison about preserve-3d flattening and opacity, not a general creative-quality claim. No universal palette ban, motion quota, mandatory style menu or renderer speed ranking follows from these sources.',['docs/pass2-research.md','docs/research-addendum.md','examples/css3d-grouping/README.md','https://motioncanvas.io/docs/time-events/','https://github.com/Nutlope/hallmark/blob/7ec868225c6caa040558c321ee0fefa0e73f83a8/skills/hallmark/references/review-finish.md','https://github.com/pbakaus/impeccable/blob/a05436993fc753ec9a302f0db8d395025b246633/.agents/skills/impeccable/reference/critique.md','https://github.com/alchaincyf/huashu-art-motion/tree/8a0d7d72ca65fcce6f8ba82c4a6c8dfe35b8422c']);
const ordered=[cover,demo,purpose,scaffold,time,spring,diagnostics,workflow,handoff,research,pack];p.slides.reorder(ordered.map(s=>'sl/'+s.id));
for(let i=0;i<ordered.length;i++){const page=ordered[i].shapes.items.find(x=>x.name==='page');if(page)page.text=String(i+1).padStart(2,'0');}
await fs.mkdir(out);
for(let i=0;i<p.slides.items.length;i++){const s=p.slides.items[i];const png=await p.export({slide:s,format:'png',scale:1});await fs.writeFile(path.join(out,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));const layout=await s.export({format:'layout'});await fs.writeFile(path.join(out,`slide-${i+1}.layout.json`),await layout.text());}
await (await PresentationFile.exportPptx(p)).save(path.join(out,'candidate.pptx'));
await fs.writeFile(path.join(out,'spring-series.json'),JSON.stringify({options,times,values},null,2));
console.log(JSON.stringify({slides:p.slides.items.length,out,chartSlide:6}));
