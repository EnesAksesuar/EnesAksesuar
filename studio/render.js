const { chromium } = require('playwright');
const path = require('path'); const fs = require('fs');
const http = require('http');

const scene = process.argv[2] || 'ayakta';
const ROOT = path.join(__dirname);
const FRAMES = path.join('/tmp/claude-0/-home-user-EnesAksesuar/57d0c4c9-193d-564a-89af-bb1d6e48178e/scratchpad','frames_'+scene);
fs.rmSync(FRAMES,{recursive:true,force:true}); fs.mkdirSync(FRAMES,{recursive:true});

const MIME={'.html':'text/html','.js':'text/javascript','.ttf':'font/ttf'};
const server=http.createServer((req,res)=>{
  const p=path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if(!p.startsWith(ROOT)||!fs.existsSync(p)){res.writeHead(404);return res.end();}
  res.writeHead(200,{'Content-Type':MIME[path.extname(p)]||'application/octet-stream'});
  fs.createReadStream(p).pipe(res);
});

(async()=>{
  await new Promise(r=>server.listen(8731,r));
  const browser=await chromium.launch({args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader',
    '--enable-unsafe-swiftshader','--disable-lcd-text','--font-render-hinting=none']});
  const page=await browser.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  page.setDefaultTimeout(180000);
  page.on('console',m=>{if(m.type()==='error')console.log('PAGE ERR:',m.text());});
  page.on('pageerror',e=>console.log('PAGE EXC:',e.message));
  await page.goto(`http://127.0.0.1:8731/scenes/${scene}.html`,{waitUntil:'load'});
  await page.waitForFunction('window.READY===true',{timeout:30000});
  await page.evaluate(()=>document.fonts.ready);
  const meta=await page.evaluate(()=>window.META);
  const total=Math.round(meta.DUR*meta.FPS);
  console.log(`scene=${scene} ${meta.W}x${meta.H} ${meta.FPS}fps ${meta.DUR}s -> ${total} frames`);
  const t0=Date.now();
  for(let f=0;f<total;f++){
    await page.evaluate(t=>window.renderFrame(t), f/meta.FPS);
    await page.screenshot({path:path.join(FRAMES,String(f).padStart(5,'0')+'.jpg'),
      type:'jpeg',quality:94,timeout:180000});
    if(f%60===0) console.log(`  ${f}/${total}  ${((Date.now()-t0)/1000).toFixed(0)}s`);
  }
  console.log(`frames done in ${((Date.now()-t0)/1000).toFixed(0)}s -> ${FRAMES}`);
  await browser.close(); server.close();
})().catch(e=>{console.error(e);process.exit(1);});
