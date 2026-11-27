// The World in One Day — Friday, 27 November 2026.
//
// The front page is drawn by draw.py and committed as entry.png. This
// program's only job is to copy that image into the output directory the
// grader hands it. It reads nothing else, reaches no network, and writes
// exactly the bytes it was given, so two runs always agree.
import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SOURCE = join(HERE, "entry.png");
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "out";

const bytes = readFileSync(SOURCE);
const PNG_MAGIC = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
if (bytes.length < PNG_MAGIC.length) {
  throw new Error("entry.png is too short to be a PNG file");
}
for (let i = 0; i < PNG_MAGIC.length; i++) {
  if (bytes[i] !== PNG_MAGIC[i]) {
    throw new Error("entry.png does not start with the PNG magic bytes");
  }
}
if (bytes.length > 1048576) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
}

mkdirSync(OUT_DIR, { recursive: true });
const target = join(OUT_DIR, "entry.png");
copyFileSync(SOURCE, target);
console.log(`wrote ${bytes.length} bytes to ${target}`);
