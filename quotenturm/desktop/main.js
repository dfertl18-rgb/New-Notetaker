// Windows-Hülle für Medienmanager 2027: ein Fenster, kein Menü, Spielstand bleibt im Benutzerprofil
const { app, BrowserWindow, shell, ipcMain } = require("electron");
const fs = require("fs");
const path = require("path");

// Spielstände aus der Zeit als „Quotenturm“ weiter nutzen
app.setPath("userData", path.join(app.getPath("appData"), "Quotenturm"));

function createWindow() {
  const win = new BrowserWindow({
    width: 1440, height: 900, minWidth: 1024, minHeight: 700,
    title: "Medienmanager 2027", backgroundColor: "#0b0e1c", autoHideMenuBar: true,
    icon: path.join(__dirname, "app", "icon.png"),
    webPreferences: { contextIsolation: true, sandbox: true, preload: path.join(__dirname, "preload.js") },
  });
  win.removeMenu();
  win.loadFile(path.join(__dirname, "app", "index.html"));
  // F11: Vollbild, Strg+R: neu laden
  win.webContents.on("before-input-event", (e, input) => {
    if (input.type !== "keyDown") return;
    if (input.key === "F11") { win.setFullScreen(!win.isFullScreen()); e.preventDefault(); }
    if (input.control && input.key.toLowerCase() === "r") { win.reload(); e.preventDefault(); }
  });
  // Externe Links im normalen Browser öffnen
  win.webContents.setWindowOpenHandler(({ url }) => { shell.openExternal(url); return { action: "deny" }; });
}

// Eingebaute KI: Sprachmodell (GGUF) lokal per node-llama-cpp – Grafikkarte (Vulkan) wenn vorhanden, sonst Prozessor.
// Das starke Modell (~4,7 GB) passt nicht in den Installer (Grenze ~2 GB) und wird beim ersten Start einmalig geladen.
const STRONG_MODEL = { uri: "https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf", file: "Qwen2.5-7B-Instruct-Q4_K_M.gguf", name: "Qwen2.5-7B-Instruct (Apache-2.0)", size: 4683074240 };
const userModels = () => path.join(app.getPath("userData"), "models");
const modelDirs = () => [userModels(), path.join(process.resourcesPath || "", "models"), process.env.PORTABLE_EXECUTABLE_DIR || "", path.dirname(process.execPath), path.join(__dirname, "models")].filter(d => d && fs.existsSync(d));
const modelFile = () => { for (const d of modelDirs()) { const f = fs.readdirSync(d).filter(x => x.endsWith(".gguf") && !x.includes(".part")).sort((a, b) => fs.statSync(path.join(d, b)).size - fs.statSync(path.join(d, a)).size)[0]; if (f) return path.join(d, f); } return null; };
let ai = null, aiQueue = Promise.resolve(), dl = null;
async function loadAI() {
  if (ai) return ai;
  const file = modelFile(); if (!file) throw new Error("Kein Modell installiert");
  const { getLlama } = await import("node-llama-cpp");
  let llama; try { llama = await getLlama({ gpu: "auto", build: "never" }); } catch (e) { llama = await getLlama({ gpu: false, build: "never" }); }
  const model = await llama.loadModel({ modelPath: file });
  const context = await model.createContext({ contextSize: 4096 });
  ai = { model, context, name: path.basename(file), gpu: llama.gpu || "cpu" };
  return ai;
}
ipcMain.handle("ai:info", () => ({ available: !!modelFile(), model: modelFile() ? path.basename(modelFile()) : null, loaded: !!ai, gpu: ai ? ai.gpu : null, downloading: dl ? dl.progress : null, strong: STRONG_MODEL }));
ipcMain.handle("ai:download", async e => {
  if (dl) return { busy: true };
  const { createModelDownloader } = await import("node-llama-cpp");
  fs.mkdirSync(userModels(), { recursive: true });
  dl = { progress: 0 };
  try {
    const d = await createModelDownloader({ modelUri: STRONG_MODEL.uri, dirPath: userModels(), fileName: STRONG_MODEL.file, onProgress: ({ totalSize, downloadedSize }) => { dl.progress = totalSize ? downloadedSize / totalSize : 0; if (!e.sender.isDestroyed()) e.sender.send("ai:progress", dl.progress); } });
    await d.download();
    ai = null; dl = null; return { ok: true };
  } catch (err) { dl = null; return { ok: false, error: err.message }; }
});
ipcMain.handle("ai:gen", (_e, prompt, maxTokens) => {
  const job = aiQueue.then(async () => {
    const { LlamaChatSession } = await import("node-llama-cpp");
    const a = await loadAI(), seq = a.context.getSequence();
    try {
      const session = new LlamaChatSession({ contextSequence: seq, systemPrompt: "Du bist ein Textgenerator für ein deutsches Fernseh-Managerspiel. Antworte kurz, sachlich und auf Deutsch. Keine Beleidigungen, keine erfundenen Zitate echter Personen." });
      return await session.prompt(prompt, { maxTokens, temperature: 0.3 });
    } finally { seq.dispose(); }
  });
  aiQueue = job.catch(() => {});
  return job.catch(err => { console.error("KI:", err.message); return null; });
});

app.whenReady().then(createWindow);
app.on("window-all-closed", () => app.quit());
