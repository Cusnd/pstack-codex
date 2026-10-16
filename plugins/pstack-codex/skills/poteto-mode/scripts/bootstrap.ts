import { createHash } from "node:crypto";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, renameSync, rmSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { homedir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

// Installed plugin trees can be read-only. Never put dependencies in that tree.
export function ensureDependenciesInstalled(): string {
  const manifest = readFileSync(join(import.meta.dir, "package.json"));
  const lock = readFileSync(join(import.meta.dir, "bun.lock"));
  const key = createHash("sha256").update(manifest).update(lock)
    .update(`${process.platform}:${process.arch}:${Bun.version}`).digest("hex");
  const base = process.env.PSTACK_CACHE_DIR ?? join(
    process.env.LOCALAPPDATA ?? process.env.XDG_CACHE_HOME ?? join(homedir(), ".cache"), "pstack"
  );
  const root = join(base, "tools");
  const cache = join(root, key);
  const marker = join(cache, ".ready");
  if (!existsSync(marker)) {
    mkdirSync(root, { recursive: true });
    const staging = mkdtempSync(join(root, `${key}-install-`));
    try {
      writeFileSync(join(staging, "package.json"), manifest);
      writeFileSync(join(staging, "bun.lock"), lock);
      const result = Bun.spawnSync([process.execPath, "install", "--frozen-lockfile"], { cwd: staging });
      if (result.exitCode !== 0) {
        process.stderr.write(result.stderr);
        throw new Error(`Dependency install failed (${result.exitCode}); cache: ${staging}`);
      }
      createRequire(join(staging, "package.json")).resolve("commander");
      writeFileSync(join(staging, ".ready"), key);
      try { renameSync(staging, cache); }
      catch (error) { if (!existsSync(marker)) throw error; }
    } finally {
      // This exact directory was created above, beneath the selected cache root.
      rmSync(staging, { recursive: true, force: true });
    }
  }
  return pathToFileURL(createRequire(join(cache, "package.json")).resolve("commander")).href;
}
