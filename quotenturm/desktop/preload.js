// Brücke zwischen Spiel und eingebauter KI (nur Textgenerierung, keine weiteren Rechte)
const { contextBridge, ipcRenderer } = require("electron");
contextBridge.exposeInMainWorld("mmAI", {
  info: () => ipcRenderer.invoke("ai:info"),
  download: () => ipcRenderer.invoke("ai:download"),
  onProgress: cb => ipcRenderer.on("ai:progress", (_e, p) => cb(p)),
  generate: (prompt, maxTokens) => ipcRenderer.invoke("ai:gen", String(prompt).slice(0, 4000), Math.min(400, maxTokens || 220)),
});
