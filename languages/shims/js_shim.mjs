// Process-protocol shim for JavaScript solutions, for Node and Bun.   usage: js_shim.mjs solution.js result.json
// stdin : {"function": "name", "args": [...]}  or  {"function": "ClassName", "calls": [[name, [args]], ...]}
// result: the JSON value, written to the result file. For class problems it is the list of return values (null
//         for the constructor; undefined is written as null, a BigInt as an exact integer). stdout and stderr stay the solution's, so
//         console.log() debugging is harmless. The solution is a CommonJS or ES module that exports the name.
import { readFileSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

const [solution, result] = process.argv.slice(2);
const mod = await import(pathToFileURL(solution).href);
const req = JSON.parse(readFileSync(0, "utf8"));
const target = mod[req.function] ?? mod.default?.[req.function];
if (typeof target !== "function") {
  console.error(`${solution} does not export ${req.function}; keep the export line of the stub ` +
                `(module.exports = { ${req.function} }, or export function ${req.function})`);
  process.exit(1);
}
let out;
if (req.calls) {
  out = [];
  let obj = null;
  for (const [i, [name, args]] of req.calls.entries()) {
    if (i === 0) {
      obj = new target(...args);
      out.push(null);
    } else {
      out.push(obj[name](...args) ?? null);
    }
  }
} else {
  out = target(...req.args) ?? null;
}
// A BigInt (for integers past 2^53) is written as a plain JSON integer: stringify writes it as a string with a
// random tag, which the replace turns back into digits.
const tag = "bigint-" + Math.random().toString(36).slice(2) + ":";
const text = JSON.stringify(out, (k, v) => typeof v === "bigint" ? tag + v : v)
  ?.replaceAll(new RegExp(`"${tag}(-?\\d+)"`, "g"), "$1") ?? "null";
writeFileSync(result, text);  // after stringify, so a value with no JSON form never touches the file
