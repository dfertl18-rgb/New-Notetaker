// Windows-Hülle für Medienmanager 2027: ein Fenster, kein Menü, Spielstand bleibt im Benutzerprofil
const { app, BrowserWindow, shell } = require("electron");
const path = require("path");

// Spielstände aus der Zeit als „Quotenturm“ weiter nutzen
app.setPath("userData", path.join(app.getPath("appData"), "Quotenturm"));

function createWindow() {
  const win = new BrowserWindow({
    width: 1440, height: 900, minWidth: 1024, minHeight: 700,
    title: "Medienmanager 2027", backgroundColor: "#0b0e1c", autoHideMenuBar: true,
    icon: path.join(__dirname, "app", "icon.png"),
    webPreferences: { contextIsolation: true, sandbox: true },
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

app.whenReady().then(createWindow);
app.on("window-all-closed", () => app.quit());
