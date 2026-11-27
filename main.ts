// Entry point for the news-image-20261127 entry.
//
// Runs draw.py (Pillow + DejaVu, deterministic, no network) to produce
// entry.png, then verifies the output exists and stays under the 1 MiB
// limit the competition sets for the image.
import { execFileSync } from "node:child_process";
import { existsSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? HERE;
const OUT_PATH = join(OUT_DIR, "entry.png");

execFileSync("python3", ["draw.py"], {
  cwd: HERE,
  env: { ...process.env, MAKEFUN_OUTPUT_DIR: OUT_DIR },
  stdio: "inherit",
});

if (!existsSync(OUT_PATH)) {
  throw new Error("draw.py did not produce entry.png");
}

const size = statSync(OUT_PATH).size;
if (size > 1024 * 1024) {
  throw new Error("entry.png is over the 1 MiB limit: " + size + " bytes");
}

console.log("entry.png ready: " + size + " bytes");
