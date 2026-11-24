const { chromium } = require('playwright');
const path=require('path'),fs=require('fs'),http=require('http');
const scene=process.argv[2]||'ayakta';
const times=(process.argv[3]||'1,5.5,9,11.5,14.5,17').split(',').map(Number);
const ROOT=path.join(__dirname,'..','studio');
const OUT='/tmp/claude-0/-home-user-EnesAksesuar/57d0c4c9-193d-564a-89af-bb1d6e48178e/scratchpad/prev';
fs.rmSync(OUT,{recursive:true,force:true}); fs.mkdirSync(OUT,{recursive:true});
const MIME={'.html':'text/html','.js':'text/javascript','.ttf':'font/ttf'};
const srv=http.createServer((q,r)=>{const p=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));
  if(!p.startsWith(ROOT)||!fs.existsSync(p)){r.writeHead(404);return r.end();}
  r.writeHead(200,{'Content-Type':MIME[path.extname(p)]||'application/octet-stream'});
  fs.createReadStream(p).pipe(r);});
(async()=>{await new Promise(r=>srv.listen(8732,r));
 const b=await chromium.launch({args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--font-render-hinting=none']});
 const pg=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
 pg.on('pageerror',e=>console.log('EXC:',e.message));
 await pg.goto(`http://127.0.0.1:8732/scenes/${scene}.html`,{waitUntil:'load'});
 await pg.waitForFunction('window.READY===true',{timeout:30000});
 await pg.evaluate(()=>document.fonts.ready);
 for(let i=0;i<times.length;i++){await pg.evaluate(t=>window.renderFrame(t),times[i]);
  await pg.screenshot({path:path.join(OUT,String(i)+'.jpg'),type:'jpeg',quality:92});}
 console.log('preview ok',times.join(','));await b.close();srv.close();})().catch(e=>{console.error(e);process.exit(1);});
