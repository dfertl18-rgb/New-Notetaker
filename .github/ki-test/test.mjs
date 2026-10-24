// Qualitätstest der KI-Aufgaben im Spiel (läuft nur in GitHub Actions)
import { getLlama, LlamaChatSession } from "node-llama-cpp";
const llama = await getLlama({ gpu: false, build: "never" });
const t0 = Date.now();
const model = await llama.loadModel({ modelPath: process.argv[2] });
const context = await model.createContext({ contextSize: 2048 });
console.log("Modell geladen in", Date.now() - t0, "ms");
const ask = async (p, max = 80) => { const seq = context.getSequence(); const t = Date.now(); const s = new LlamaChatSession({ contextSequence: seq, systemPrompt: "Du bist ein Textgenerator für ein deutsches Fernseh-Managerspiel. Antworte kurz und auf Deutsch." }); const r = await s.prompt(p, { maxTokens: max, temperature: 0.7 }); seq.dispose(); return `[${Date.now() - t} ms] ${r}`; };
const heads = ["Quartalsbericht: ProSieben mit Z1 14,2 %, Z2 7,3 %", "Themenwoche: Streikwelle im Verkehr", "Dringende Warnung vor Zahlungsunfähigkeit", "Hitzige Debatte zum Fachthema bei Markus Lanz", "Pfändung: „Inception“ an Media Venture Capital"];
for (const h of heads) for (let k = 0; k < 2; k++) console.log("KOMMENTAR |", h.slice(0, 40), "→", await ask(`Schreibe genau einen kurzen, sachlich-ironischen Kommentarsatz eines Branchenkenners zu dieser Schlagzeile aus einem Fernseh-Managerspiel. Keine Zahlen, keine Namen, keine Zitate, keine Beleidigungen, höchstens 20 Wörter. Antworte auf Deutsch.\nSchlagzeile: ${h}`));
const answers = [["Die Konkurrenz kann sich warm anziehen, deren Filme sind völlig überteuert.", 3], ["Wir arbeiten eng mit dem Vorstand zusammen, die Sanierung läuft nach Plan.", 1], ["Diese Regierung lässt die Menschen im Stich, kein Wunder, dass alle wütend sind.", 2], ["Am Samstag holen wir mit unserem Live-Event den Quotensieg, versprochen!", 0]];
for (const [a, want] of answers) console.log("KLASSE | soll", want, "→", await ask(`Ordne diese Antwort eines TV-Managers in einer Pressekonferenz genau einer Kategorie zu und antworte nur mit der Zahl: 0 = offensive Ansage mit großen Versprechen, 1 = diplomatisch und beruhigend, 2 = polemische Kritik an Politik oder Gesellschaft, 3 = Angriff auf Konkurrenzsender.\nAntwort: "${a}"`, 5));
console.log("ARTIKEL →", await ask("Fasse diese Meldung im Stil eines Branchendienstes in höchstens drei Sätzen neu. Erfinde keine Fakten, behalte alle Zahlen exakt bei.\nÜberschrift: Quartalsbericht: ProSieben mit Z1 14,2 %, Z2 7,3 %\nMeldung: Marktführer: Z1 ProSieben, Z2 RTL, Z3 ZDF, Z4 ZDF. Vorstand: Kernzielgruppe Z2 gehalten.", 160));
