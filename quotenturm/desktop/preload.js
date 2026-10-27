// Brücke zwischen Spiel und eingebauter KI (nur Textgenerierung, keine weiteren Rechte)
const { contextBridge, ipcRenderer } = require("electron");
contextBridge.exposeInMainWorld("mmAI", {
  info: () => ipcRenderer.invoke("ai:info"),
  download: () => ipcRenderer.invoke("ai:download"),
  onProgress: cb => ipcRenderer.on("ai:progress", (_e, p) => cb(p)),
  generate: (prompt, maxTokens) => ipcRenderer.invoke("ai:gen", String(prompt).slice(0, 4000), Math.min(400, maxTokens || 220)),
});
// Spielstände als Dateien im Dokumente-Ordner (nur dieser eine Ordner, keine weiteren Dateirechte)
contextBridge.exposeInMainWorld("mmSave", {
  write: (name, data) => ipcRenderer.invoke("save:write", String(name), String(data)),
  list: () => ipcRenderer.invoke("save:list"),
  read: name => ipcRenderer.invoke("save:read", String(name)),
  del: name => ipcRenderer.invoke("save:del", String(name)),
  openDir: () => ipcRenderer.invoke("save:open"),
  dir: () => ipcRenderer.invoke("save:dir"),
});
