import { scanDirectory } from "../scanner/scanner.js";
import { reportToConsole } from "../reporters/consoleReporter.js";
import { reportToJson } from "../reporters/jsonReporter.js";
import { readFile } from "node:fs/promises";
import * as path from "node:path";

export async function runCli(): Promise<void> {
  const args = process.argv.slice(2);

  const targetPath = args.find(arg => !arg.startsWith("--")) ?? process.cwd();

  const reporterArg = getFlagValue(args, "--reporter");
  const reporter =
    reporterArg === "json"
      ? "json"
      : reporterArg === "console"
      ? "console"
      : args.includes("--json")
      ? "json"
      : "console";

  const quiet = args.includes("--quiet");
  const showVersion = args.includes("--version");

  const entropyThresholdArg = getFlagValue(args, "--entropy-threshold");
  const minEntropyLengthArg = getFlagValue(args, "--min-entropy-length");

  if (showVersion) {
    await printVersion();
    return;
  }

  try {
    const start = Date.now();

    const findings = await scanDirectory(targetPath, {
      entropyThreshold: entropyThresholdArg
        ? Number(entropyThresholdArg)
        : undefined,
      minEntropyLength: minEntropyLengthArg
        ? Number(minEntropyLengthArg)
        : undefined
    });

    const duration = Date.now() - start;

    if (!quiet) {
      if (reporter === "json") {
        console.log(reportToJson(findings));
      } else {
        reportToConsole(findings);
      }

      console.log(`Scan completed in ${duration}ms.`);
    }

    if (findings.length > 0) {
      process.exitCode = 1;
    }
  } catch (err) {
    console.error("Error during scan:", err);
    process.exit(2);
  }
}

function getFlagValue(args: string[], flag: string): string | undefined {
  const index = args.indexOf(flag);
  if (index !== -1 && index + 1 < args.length) {
    return args[index + 1];
  }
  return undefined;
}

async function printVersion(): Promise<void> {
  try {
    const pkgPath = new URL("../../package.json", import.meta.url);
    const pkgRaw = await readFile(pkgPath, "utf8");
    const pkg = JSON.parse(pkgRaw);
    console.log(`SecretScanner v${pkg.version}`);
  } catch {
    console.log("SecretScanner (version unknown)");
  }
}
