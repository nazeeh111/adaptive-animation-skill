/** Opt-in receiving-side regression for this example, not a universal style gate. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';

const executablePath=process.env.ANIMATION_TEST_BROWSER;
test('preview reflows without losing input state or changing fixed capture',
  {skip:!executablePath,timeout:60000},async t=>{
  const require=createRequire(import.meta.url);
  const {chromium}=require(process.env.ANIMATION_PLAYWRIGHT_MODULE||'playwright');
  const browser=await chromium.launch({executablePath,headless:true,args:['--disable-gpu']});
  t.after(()=>browser.close());
  const source=pathToFileURL(fileURLToPath(new URL('./index.html',import.meta.url))).href;
  const page=await browser.newPage({viewport:{width:320,height:900}});
  const errors=[];page.on('pageerror',error=>errors.push(String(error)));
  await page.goto(source+'?preview=1');
  await page.evaluate(()=>document.fonts.ready);
  const state=()=>page.evaluate(()=>({
    time:Number(document.querySelector('#seek').value),
    route:document.querySelector('#route').textContent,
    focus:document.activeElement.id,
    caption:document.querySelector('#caption').textContent,
    playing:document.querySelector('#play').getAttribute('aria-pressed')==='true'
  }));
  const displayedLabelSize=()=>page.locator('#source text').evaluate(el=>{
    const matrix=el.getScreenCTM();
    return parseFloat(getComputedStyle(el).fontSize)*Math.hypot(matrix.a,matrix.b);
  });
  // A local acceptance condition for this explanation, not an accessibility standard.
  assert.ok(await displayedLabelSize()>=16,'The narrow-host label is unreadable');
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator('#route').click(); // Select the direct route.
  await page.evaluate(()=>window.renderFrame(4.26));
  const selected=await state();
  for(const width of [600,960,320]){
    await page.setViewportSize({width,height:900});
    await page.waitForFunction(w=>Math.abs(document.querySelector('main').getBoundingClientRect().width-Math.min(w,960))<1,width);
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    assert.ok(await displayedLabelSize()>=16,'A resized label shrank below the example contract');
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    const actual=await state();
    assert.equal(actual.time,selected.time);
    assert.equal(actual.route,selected.route);
    assert.equal(actual.focus,'route');
  }
  await page.evaluate(()=>window.renderFrame(0));
  await page.locator('#play').click();
  await page.waitForFunction(()=>Number(document.querySelector('#seek').value)>.05);
  await page.setViewportSize({width:600,height:900});
  await page.waitForFunction(()=>Number(document.querySelector('#seek').value)>.1);
  assert.equal((await state()).playing,true);
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.waitForFunction(()=>Number(document.querySelector('#seek').value)===8&&document.querySelector('#play').disabled);
  assert.match((await state()).caption,/skips Review/);
  await page.locator('#route').focus();
  await page.keyboard.press('Enter');
  assert.match((await state()).caption,/Review clears/);
  assert.equal((await state()).time,8);
  assert.equal((await state()).playing,false);
  await page.emulateMedia({reducedMotion:'no-preference'});
  await page.waitForFunction(()=>!document.querySelector('#play').disabled);
  assert.equal((await state()).playing,false);

  const capture=await browser.newPage({viewport:{width:320,height:900},reducedMotion:'reduce'});
  capture.on('pageerror',error=>errors.push(String(error)));
  await capture.goto(source);
  await capture.evaluate(()=>window.renderFrame(4.26));
  const fixed=await capture.evaluate(()=>{
    const root=document.querySelector('main'),box=root.getBoundingClientRect();
    return {width:box.width,height:box.height,viewBox:document.querySelector('svg').getAttribute('viewBox'),
      controlsHidden:document.querySelector('#controls').hidden,time:Number(document.querySelector('#seek').value)};
  });
  assert.deepEqual(fixed,{width:960,height:540,viewBox:'0 0 864 290',controlsHidden:true,time:4.26});
  assert.deepEqual(errors,[]);
});
