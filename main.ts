// Entry point for the news-image-20261127 entry.
//
// The front page is drawn by draw.py and committed as entry.png. This
// program only copies that committed image into the output directory the
// grader hands it (MAKEFUN_OUTPUT_DIR, or "out" when unset). It spawns
// nothing, reaches no network, and writes nothing into the repository
// itself, so it runs fine on the grader's read-only /bot.
import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SOURCE = join(HERE, "entry.png");
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "out";
const MAX_BYTES = 1024 * 1024;

const bytes = readFileSync(SOURCE);

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!bytes.subarray(0, PNG_MAGIC.length).equals(PNG_MAGIC)) {
  throw new Error("entry.png does not start with the PNG magic bytes");
}
if (bytes.length > MAX_BYTES) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
}

mkdirSync(OUT_DIR, { recursive: true });
const target = join(OUT_DIR, "entry.png");
copyFileSync(SOURCE, target);
console.log(`wrote ${bytes.length} bytes to ${target}`);
