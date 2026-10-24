// Setzt Programmsymbol und Versionsangaben direkt in die Windows-EXE (ohne Wine, reines JavaScript)
const fs = require("fs"), path = require("path");
exports.default = async ctx => {
  if (ctx.electronPlatformName !== "win32") return;
  const ResEdit = await require("resedit/cjs").load();
  const exe = path.join(ctx.appOutDir, `${ctx.packager.appInfo.productFilename}.exe`);
  const ex = ResEdit.NtExecutable.from(fs.readFileSync(exe), { ignoreCert: true });
  const res = ResEdit.NtExecutableResource.from(ex);
  const ico = ResEdit.Data.IconFile.from(fs.readFileSync(path.join(__dirname, "build", "icon.ico")));
  const grp = ResEdit.Resource.IconGroupEntry.fromEntries(res.entries)[0];
  ResEdit.Resource.IconGroupEntry.replaceIconsForResource(res.entries, grp ? grp.id : 1, grp ? grp.lang : 1033, ico.icons.map(i => i.data));
  const vi = ResEdit.Resource.VersionInfo.fromEntries(res.entries)[0];
  const v = ctx.packager.appInfo.version, lang = { lang: 1033, codepage: 1200 };
  vi.setStringValues(lang, { ProductName: "Medienmanager 2027", FileDescription: "Medienmanager 2027 – TV- & Streaming-Manager", CompanyName: "Privat", LegalCopyright: "Privates Spiel", OriginalFilename: "Medienmanager 2027.exe", InternalName: "Medienmanager 2027" });
  vi.setFileVersion(...v.split(".").map(Number), 0); vi.setProductVersion(...v.split(".").map(Number), 0);
  vi.outputToResourceEntries(res.entries);
  res.outputResource(ex);
  fs.writeFileSync(exe, Buffer.from(ex.generate()));
  console.log("Symbol und Versionsangaben gesetzt:", path.basename(exe));
};
