import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
import {codeBlock,render,stripAnno,regexParcala,dilAdi} from '../web/md.js';
import {highlightLines,esc} from '../web/hl.js';

function appHarness() {
  const element=()=>({content:'token',innerHTML:'',classList:{add(){},toggle(){}},
    querySelector(){return element();},querySelectorAll(){return [];}});
  const document={querySelector(){return element();},querySelectorAll(){return [];}};
  let source=readFileSync(new URL('../web/app.js',import.meta.url),'utf8');
  source=source.replace(/^import .*;\r?\n/gm,'').replace(/\bboot\(\);\s*$/,'');
  return runInNewContext(source+'\n({Bench,firstCode,lessonLanguage,TAHMIN_DIL});',
    {document,render,codeBlock,stripAnno,regexParcala,dilAdi,esc,console,setTimeout,clearTimeout});
}

test('real packet CLI fences are runnable and populate the editor',()=>{
  const app=appHarness();
  for(const [language,source] of [['tshark','tshark -r secili -q -z io,phs'],
    ['tcpdump-lab','tcpdump -i lo -nn -s 64 -c 3 -w sonuc.pcap udp']]) {
    const html=codeBlock(source,language,{dil:language});
    assert.ok(html.includes('data-act="run"'));
    assert.ok(html.includes('data-act="bench"'));
    assert.equal(app.firstCode('```'+language+'\n'+source+'\n```',language).code.trim(),source);
    assert.equal(app.lessonLanguage({dil:'packets'},{steps:[]},{meta:{dil:language}}),language);
    assert.ok(app.TAHMIN_DIL[language]);
    assert.ok(!codeBlock(source,language,{dil:language,runnable:false,bench:false}).includes('data-act="run"'));
    const encoded=highlightLines(source+' <tag>',language).join('\n');
    assert.ok(!encoded.includes('<tag>'));
  }
});

test('CLI stdout and exported-file tables are both visible and escaped',()=>{
  const app=appHarness();
  for(const dialect of ['tshark','tcpdump-lab']) {
    const pane={innerHTML:''};
    app.Bench.prototype.paintOut.call({pane},{packet_dialect:dialect,packet_backend:'real CLI',
      segs:[['out','Paketler: 3\n<tag>']],tablolar:[{satir:1,sutunlar:['Dosya','Bayt'],satirlar:[['download',13]]}]});
    assert.ok(pane.innerHTML.includes('Paketler: 3'));
    assert.ok(pane.innerHTML.includes('download'));
    assert.ok(pane.innerHTML.includes('real CLI'));
    assert.ok(!pane.innerHTML.includes('<tag>'));
  }
});
