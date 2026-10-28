// Baut das Spiel aus src/ zusammen (ersetzt build.sh / build_private.sh, läuft auch unter Windows)
//   node tools/build.js            → index.html (öffentliche Version, ohne private Daten)
//   node tools/build.js --privat   → zusätzlich privat/index.html (mit echten Personen, Titeln, Logos, Besetzung; ohne Fotos)
const fs = require("fs"), path = require("path"), { execFileSync } = require("child_process");
const root = path.join(__dirname, ".."), src = path.join(root, "src");

const game = fs.readFileSync(path.join(src, "quotenturm.html"), "utf8");
const cut = game.indexOf("\n</style>\n") + "\n</style>\n".length;
if (cut < 10) throw new Error("</style> nicht gefunden");
// three.js + HumanForge als window.THREE / window.HF (gebaut aus src/hf/entry.js, siehe ENTWICKLUNG.md)
const hf = fs.readFileSync(path.join(src, "hf", "hf.iife.js"), "utf8");
const html = '<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  + game.slice(0, cut) + '</head>\n<body>\n<script id="three-lib">\n' + hf + '\n</script>\n' + game.slice(cut) + '</body>\n</html>\n';
fs.writeFileSync(path.join(root, "index.html"), html);

// Syntaxprüfung des Spielskripts
const m = html.match(/\n<script>\n([\s\S]*?)\n<\/script>/);
const chk = path.join(require("os").tmpdir(), "mm-check.js");
fs.writeFileSync(chk, m[1]);
execFileSync(process.execPath, ["--check", chk], { stdio: "inherit" });
console.log("index.html gebaut, Syntax OK");

if (process.argv.includes("--privat")) {
  const pd = path.join(root, "privat");
  const parts = ["realdata.js", "logos.js", "titles.js", "extra.js", "besetzung.js"]
    .filter(f => fs.existsSync(path.join(pd, f))).map(f => fs.readFileSync(path.join(pd, f), "utf8"));
  if (!parts.length) throw new Error("Ordner privat/ fehlt oder ist leer");
  if (html.split("<script>").length !== 2) throw new Error("Erwartet genau einen <script>-Block");
  fs.writeFileSync(path.join(pd, "index.html"), html.replace("<script>", () => "<script>\n" + parts.join("\n") + "</script>\n<script>"));
  console.log("privat/index.html gebaut");
}
