const http=require('node:http');
const Provider=require('C:/Users/demo12/Documents/Pafta-AI-GercekLab/sandbox/ai_gercek_ai_saldiri_06_provider.cjs');
(async()=>{
  let mode=500,count=0;
  const server=http.createServer((req,res)=>{ req.resume();req.on('end',()=>{
    count++;
    if(mode===400 || count===1){res.writeHead(mode,{'Content-Type':'application/json'});res.end('{"error":"fixture transient"}');}
    else {res.writeHead(200,{'Content-Type':'application/json'});res.end(JSON.stringify({done:true,message:{content:'fixture-only'},eval_count:1}));}
  });});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  process.env.PAFTA_EVAL_HOST='http://127.0.0.1:'+server.address().port;
  process.env.PAFTA_EVAL_MODEL='fixture';process.env.PAFTA_EVAL_CANARY='fixture-marker';
  try {
    const p=new Provider();const r=await p.callApi('fixture',{vars:{seed:1}});
    if(count!==2 || r.output!=='fixture-only' || r.metadata.retries.length!==1)throw new Error('500 retry fixture failed: '+JSON.stringify(r));
    const first={case:'500-to-200',calls:count,recordedRetries:r.metadata.retries.length};
    mode=400;count=0;const s=await p.callApi('fixture',{vars:{seed:1}});
    if(count!==1 || !s.error.includes('HTTP 400'))throw new Error('400 must not retry');
    console.log(JSON.stringify({kaynak:'fixture',realModelAcceptance:false,results:[first,{case:'400',calls:count,recordedRetries:s.metadata.retries.length}]}));
  } finally {await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);process.exitCode=1;});
