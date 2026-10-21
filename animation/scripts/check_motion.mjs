#!/usr/bin/env node
/** Sample local composition pixels in shuffled time order. Never approves craft. */
import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';

const argv=process.argv.slice(2);
if(argv.includes('--help') || !argv.length){
  console.log('Usage: node check_motion.mjs COMPOSITION --out NEW_DIRECTORY --browser CHROME_EXECUTABLE [--expect-motion] [--exact]\nRequires installed playwright and sharp. ANIMATION_PLAYWRIGHT_MODULE and ANIMATION_IMAGE_MODULE can name existing package entries. Local assets only. Sampled pixels, not motion/audio approval.');
  process.exit(argv.includes('--help')?0:2);
}
const source=path.resolve(argv.shift());
function option(name){const at=argv.indexOf(name);if(at<0||!argv[at+1])throw Error('Missing '+name);const value=argv[at+1];argv.splice(at,2);return value;}
const out=path.resolve(option('--out'));
const executablePath=path.resolve(option('--browser'));
const expectMotion=argv.includes('--expect-motion');
if(expectMotion)argv.splice(argv.indexOf('--expect-motion'),1);
const exact=argv.includes('--exact');if(exact)argv.splice(argv.indexOf('--exact'),1);
if(argv.length)throw Error('Unknown arguments: '+argv.join(' '));
// Symlink traversal is rejected both for the source and each served resource.
async function noLinks(file){let p=path.resolve(file);while(true){const stat=await fs.lstat(p);if(stat.isSymbolicLink())throw Error('Symlink path refused: '+p);const parent=path.dirname(p);if(parent===p)break;p=parent;}}
await noLinks(source);
await noLinks(path.dirname(out));
await fs.access(path.join(source,'index.html'));
await fs.access(executablePath);
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.ANIMATION_PLAYWRIGHT_MODULE||'playwright');
const sharp=require(process.env.ANIMATION_IMAGE_MODULE||'sharp');
await fs.mkdir(out); // Existing outputs, including dangling symlinks, remain untouched.
const failures=[],consoleErrors=[],blockedResources=[],pixels=[];
function difference(a,b){let changed=0,max=0;for(let i=0;i<a.length;i+=4){let delta=0;for(let c=0;c<4;c++)delta=Math.max(delta,Math.abs(a[i+c]-b[i+c]));if(delta)changed++;max=Math.max(max,delta);}return {changed_pixels:changed,max_channel_delta:max};}
const tolerance=exact?{max_channel_delta:0,max_changed_pixels:0}:{max_channel_delta:12,max_changed_pixels:16};
let server,browser,timer;
const report={schema:1,purpose:'Sampled seek pixels and local browser diagnostics; no artistic, audio or export approval',source,tolerance,checks:{},samples:[],failures,consoleErrors,blockedResources};
try{
  server=http.createServer(async(req,res)=>{
    try{
      const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
      const file=path.resolve(source,'.'+pathname+(pathname.endsWith('/')?'index.html':''));
      if(file!==source&&!file.startsWith(source+path.sep))throw Error('Path outside composition');
      await noLinks(file);
      if(!(await fs.stat(file)).isFile())throw Error('Not a regular file');
      const types={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.ttf':'font/ttf','.woff2':'font/woff2','.mp4':'video/mp4','.wav':'audio/wav'};
      res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');
      res.end(await fs.readFile(file));
    }catch(error){res.writeHead(404);res.end('Local resource unavailable');}
  });
  await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
  const origin='http://127.0.0.1:'+server.address().port;
  browser=await chromium.launch({executablePath,headless:true,args:['--disable-gpu']});
  timer=setTimeout(()=>{failures.push('60 second browser deadline exceeded');void browser.close();},60000);
  const page=await browser.newPage({viewport:{width:1280,height:720},deviceScaleFactor:1});
  page.setDefaultTimeout(15000);
  page.on('pageerror',error=>consoleErrors.push(String(error)));
  page.on('console',message=>{if(message.type()==='error')consoleErrors.push(message.text());});
  await page.route('**/*',async route=>{
    const u=new URL(route.request().url());
    if(u.origin===origin||['data:','blob:'].includes(u.protocol))return route.continue();
    blockedResources.push(u.origin+u.pathname);await route.abort('blockedbyclient');
  });
  await page.goto(origin+'/',{waitUntil:'networkidle'});
  const meta=await page.evaluate(()=>{
    const root=document.querySelector('[data-composition-id]');
    if(!root)throw Error('Missing composition metadata');
    return {id:root.dataset.compositionId,width:Number(root.dataset.width),height:Number(root.dataset.height),duration:Number(root.dataset.duration)};
  });
  if(![meta.width,meta.height,meta.duration].every(Number.isFinite)||meta.width<2||meta.height<2||meta.width>4096||meta.height>4096||meta.duration<=0||meta.duration>600)throw Error('Invalid or unsupported dimensions/duration');
  report.composition=meta;
  report.capture_profile={browser:'Chromium',headless:true,gpu:false,deviceScaleFactor:1};
  await page.setViewportSize({width:meta.width,height:meta.height});
  await page.evaluate(async()=>{
    await document.fonts.ready;
    await Promise.all([...document.images].map(image=>image.decode()));
  });
  const times=[0,.05,.125,.25,.5,.75,.9,.99,.5,.125,0].map(phase=>phase*meta.duration);
  for(let i=0;i<times.length;i++){
    const seconds=times[i];
    await page.evaluate(async({seconds,id})=>{
      if(typeof window.renderFrame==='function')await window.renderFrame(seconds);
      else{
        const timeline=window.__timelines?.[id];
        if(!timeline)throw Error('No renderFrame(seconds) or registered timeline');
        timeline.pause();timeline.seek(seconds,false);
      }
      await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
    },{seconds,id:meta.id});
    const bytes=await page.screenshot({path:path.join(out,'sample-'+i+'.png'),animations:'allow'});
    pixels.push(await sharp(bytes).ensureAlpha().raw().toBuffer());
    report.samples.push({seconds,file:'sample-'+i+'.png',sha256:createHash('sha256').update(bytes).digest('hex')});
  }
  report.comparisons=[];
  for(const [name,a,b] of [['midpoint',4,8],['early',2,9],['start',0,10]]){
    const {changed_pixels:changed,max_channel_delta:max}=difference(pixels[a],pixels[b]);
    const exactPixels=changed===0;
    const within=changed<=tolerance.max_changed_pixels&&max<=tolerance.max_channel_delta;
    report.comparisons.push({name,first:a,repeated:b,exact_pixels:exactPixels,changed_pixels:changed,max_channel_delta:max,within_tolerance:within});
  }
  report.checks.backward_seek_within_capture_tolerance=report.comparisons.every(c=>c.within_tolerance);
  report.checks.sampled_hashes_differ=new Set(report.samples.map(s=>s.sha256)).size>1;
  report.motion_comparisons=pixels.slice(1,8).map((p,index)=>({first:0,compared:index+1,...difference(pixels[0],p)}));
  report.checks.sampled_pixels_change=report.motion_comparisons.some(c=>c.changed_pixels>tolerance.max_changed_pixels||c.max_channel_delta>tolerance.max_channel_delta);
  if(!report.checks.backward_seek_within_capture_tolerance)failures.push('Repeated sampled time exceeded the declared pixel tolerance');
  if(expectMotion&&!report.checks.sampled_pixels_change)failures.push('Expected motion but sampled pixels were identical');
  if(consoleErrors.length)failures.push('Browser reported errors');
  if(blockedResources.length)failures.push('External resource requests blocked');
}catch(error){failures.push(String(error));}
finally{
  clearTimeout(timer);
  if(browser)await browser.close();
  if(server)await new Promise(resolve=>server.close(resolve));
  report.status=failures.length?'failed':'passed';
  await fs.writeFile(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
}
console.log(JSON.stringify(report,null,2));
process.exitCode=failures.length?1:0;
