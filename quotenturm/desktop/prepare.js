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
// Private Daten (echte Personen, Titel, Logos, Besetzung, Fotos) nur, wenn lokal vorhanden – der Ordner privat/ wird nicht ins Repository übernommen.
// Alles in EINEM Skriptblock und in fester Reihenfolge (realdata zuerst, da es window.MM_PRIVATE anlegt).
const share = process.argv.includes("--share"); // Weitergabe-Version: ohne private Daten
if (!share) {
  const parts = [];
  for (const name of ["realdata.js", "titles.js", "extra.js", "besetzung.js", "photos.js", "logos.js"]) {
    const fp = path.join(src, "privat", name);
    if (fs.existsSync(fp)) { parts.push(fs.readFileSync(fp, "utf8")); console.log("Private Datei eingebettet:", name); }
  }
  if (parts.length) html = html.replace("<script>", () => "<script>\n" + parts.join("\n;\n") + "</script>\n<script>");
}
fs.writeFileSync(path.join(out, "index.html"), html);
fs.copyFileSync(path.join(__dirname, "build", "icon.png"), path.join(out, "icon.png"));

// Fotos echter Personen (Wikimedia Commons, mit Fotograf und Lizenz) nur in der privaten Version
const photos = path.join(src, "privat", "photos");
if (!share && fs.existsSync(photos)) { fs.cpSync(photos, path.join(out, "photos"), { recursive: true }); console.log("Personenfotos kopiert:", fs.readdirSync(photos).length); }
// Realistische Menschenmodelle (MakeHuman/MPFB2, CC0) für Avatare, Wohnzimmer und Zwischensequenzen
const human = path.join(src, "human");
if (fs.existsSync(human)) { fs.cpSync(human, path.join(out, "human"), { recursive: true }); console.log("Menschenmodelle kopiert."); }
const logos = path.join(src, "logos");
if (fs.existsSync(logos)) fs.cpSync(logos, path.join(out, "logos"), { recursive: true });
console.log("App vorbereitet:", out);
