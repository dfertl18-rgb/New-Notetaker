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
// Private Daten (echte Personen) nur, wenn lokal vorhanden – der Ordner privat/ wird nicht ins Repository übernommen
const priv = path.join(src, "privat", "realdata.js");
const share = process.argv.includes("--share"); // Weitergabe-Version: ohne private Daten
if (!share && fs.existsSync(priv)) { html = html.replace("<script>", () => "<script>\n" + fs.readFileSync(priv, "utf8") + "</script>\n<script>"); console.log("Private Daten eingebettet."); }
// Echte Senderlogos (Markenrechte) ebenfalls nur in der privaten Version
// Titeldatenbank (Wikidata + IMDb-Datensätze, nur private Nutzung) ebenfalls nur privat
for (const extra of ["titles.js"]) { const fp = path.join(src, "privat", extra); if (!share && fs.existsSync(fp)) { html = html.replace("<script>", () => "<script>\n" + fs.readFileSync(fp, "utf8") + "</script>\n<script>"); console.log("Private Datei eingebettet:", extra); } }
const privLogos = path.join(src, "privat", "logos.js");
if (!share && fs.existsSync(privLogos)) { html = html.replace("<script>", () => "<script>\n" + fs.readFileSync(privLogos, "utf8") + "</script>\n<script>"); console.log("Private Logos eingebettet."); }
fs.writeFileSync(path.join(out, "index.html"), html);
fs.copyFileSync(path.join(__dirname, "build", "icon.png"), path.join(out, "icon.png"));

const logos = path.join(src, "logos");
if (fs.existsSync(logos)) fs.cpSync(logos, path.join(out, "logos"), { recursive: true });
console.log("App vorbereitet:", out);
