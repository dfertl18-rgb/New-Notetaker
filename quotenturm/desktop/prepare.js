// Kopiert das Spiel (eine HTML-Datei), bettet die Schriften lokal ein (offline spielbar) und übernimmt optionale eigene Logos
const fs = require("fs"), path = require("path");
const src = path.join(__dirname, ".."), out = path.join(__dirname, "app");
fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(path.join(out, "fonts"), { recursive: true });

const FONTS = [["Inter", "inter", [400, 500, 600, 700]], ["Barlow Condensed", "barlow-condensed", [500, 600, 700]]];
let css = "";
for (const [family, pkg, weights] of FONTS) for (const w of weights) {
  for (const sub of ["latin", "latin-ext"]) {
    const file = `${pkg}-${sub}-${w}-normal.woff2`;
    fs.copyFileSync(path.join(__dirname, "node_modules", "@fontsource", pkg, "files", file), path.join(out, "fonts", file));
    css += `@font-face{font-family:"${family}";font-style:normal;font-weight:${w};font-display:swap;src:url(fonts/${file}) format("woff2");}\n`;
  }
}
fs.writeFileSync(path.join(out, "fonts.css"), css);

let html = fs.readFileSync(path.join(src, "index.html"), "utf8");
html = html.replace(/<link rel="preconnect"[^>]*>\n?/g, "").replace(/<link rel="stylesheet" href="https:\/\/fonts\.googleapis\.com[^>]*>/, '<link rel="stylesheet" href="fonts.css">');
// Excel-Modul (SheetJS) lokal beilegen, damit der Import offline funktioniert
fs.mkdirSync(path.join(out, "vendor"), { recursive: true });
fs.copyFileSync(path.join(__dirname, "node_modules", "xlsx", "dist", "xlsx.full.min.js"), path.join(out, "vendor", "xlsx.full.min.js"));
html = html.replace("https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js", "vendor/xlsx.full.min.js");
fs.writeFileSync(path.join(out, "index.html"), html);

const logos = path.join(src, "logos");
if (fs.existsSync(logos)) fs.cpSync(logos, path.join(out, "logos"), { recursive: true });
console.log("App vorbereitet:", out);
