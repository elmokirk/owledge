"use strict";
// Optional reminder only. Never reads customer files, grants rights or blocks tools.
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const LIMIT = 65536;
const parts = [];
let size = 0;
let finished = false;
const timer = setTimeout(() => finish("Hinweis-Hook: Eingabe nicht abgeschlossen."), 2000);
function finish(warning) {
  if (finished) return;
  finished = true;
  clearTimeout(timer);
  if (warning) process.stderr.write("Owledge: " + warning + "\n");
  process.exit(0);
}
process.stdin.on("error", () => finish("Hinweis-Hook: Eingabe nicht lesbar."));
process.stdin.on("data", chunk => {
  size += chunk.length;
  if (size > LIMIT) return finish("Hinweis-Hook: Eingabe zu gross.");
  parts.push(chunk);
});
process.stdin.on("end", () => {
  try {
    const raw = new TextDecoder("utf-8", { fatal: true }).decode(Buffer.concat(parts));
    const event = JSON.parse(raw);
    if (!event || Array.isArray(event) || event.hook_event_name !== "SessionStart") return finish();
    const root = fs.realpathSync(path.join(__dirname, ".."));
    let file = root;
    for (const part of ["skills", "governance", "SKILL.md"]) {
      file = path.join(file, part);
      if (fs.lstatSync(file).isSymbolicLink()) throw new Error("linked profile");
    }
    const stat = fs.statSync(file);
    if (!stat.isFile() || stat.size > LIMIT) throw new Error("invalid profile");
    const bytes = fs.readFileSync(file);
    const digest = crypto.createHash("sha256").update(bytes).digest("hex");
    const message = "Owledge Governance ist als Skill verfuegbar. Lade vor Suche, Import, " +
      "Wissensaenderung oder Handoff das installierte Profil: " + JSON.stringify(file) +
      ". SHA-256: " + digest + ". Dieser Hook erinnert nur an das Profil; er erzwingt keine " +
      "Berechtigungen und prueft keine Freigaben. Bestehende hoehere Regeln bleiben gueltig.";
    process.stdout.write(JSON.stringify({hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:message}}) + "\n");
    finish();
  } catch (_) {
    finish("Profil-Hinweis nicht geladen. Skill ausdruecklich auswaehlen; keine Durchsetzung behaupten.");
  }
});
