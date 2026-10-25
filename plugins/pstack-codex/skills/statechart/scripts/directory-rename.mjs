import fs from "node:fs";

// Windows reports EPERM when rename would replace an existing directory,
// including an empty one. Treat only that shape as a destination collision:
// other EPERM errors must still fail, and the caller's guarded move-aside /
// rollback path performs ordinary filesystem permission checks.
export function renameCollision(error, from, to, platform = process.platform) {
  if (platform !== "win32" || error.code !== "EPERM") return error.code;
  try {
    if (fs.lstatSync(from).isDirectory() && fs.lstatSync(to).isDirectory()) return "EEXIST";
  } catch {
    // Missing or unreadable paths do not prove a destination collision.
  }
  return error.code;
}
