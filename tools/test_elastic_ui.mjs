// Render contract only; no browser or Elasticsearch is used here.
import test from "node:test";
import assert from "node:assert/strict";
import { codeBlock, render } from "../web/md.js";
import { highlightLines } from "../web/hl.js";

test("native query fences are reading blocks inside the Python track", () => {
  for (const [language, label] of [["kibana", "KIBANA KQL"], ["lucene", "LUCENE"], ["eql", "ELASTIC EQL"]]) {
    const html = codeBlock('process.name: "cmd.exe"', language, { dil: "python" });
    assert.ok(html.includes(label + " · OKUMA"));
    assert.ok(!html.includes('data-act="run"'));
    assert.ok(!html.includes('data-act="bench"'));
    const markdown = render("```" + language + '\nfield: "value"\n```', { dil: "python" });
    assert.ok(markdown.includes(label));
    assert.ok(!markdown.includes('data-act="run"'));
  }
});

test("Python exercise examples retain their run and bench controls", () => {
  const html = codeBlock("print(42)", "python", { dil: "python" });
  assert.ok(html.includes('data-act="run"'));
  assert.ok(html.includes('data-act="bench"'));
});

test("query highlighting preserves and escapes source text", () => {
  const source = 'field: "<img src=x>" AND amount >= 1024\nNOT field: *';
  for (const language of ["kibana", "lucene", "eql"]) {
    const html = highlightLines(source, language).join("\n");
    assert.ok(!html.includes("<img"));
    const plain = html.replace(/<span class="tok-[^"]+">/g, "").replace(/<\/span>/g, "")
      .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
    assert.equal(plain, source);
  }
});
