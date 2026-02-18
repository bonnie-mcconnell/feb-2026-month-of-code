import { scanDirectory } from "../scanner/scanner.js";
import { reportToConsole } from "../reporters/consoleReporter.js";
import { reportToJson } from "../reporters/jsonReporter.js";

export async function runCli(): Promise<void> {
  const args = process.argv.slice(2);

  const targetPath = args[0] ?? process.cwd();
  const jsonFlag = args.includes("--json");

  try {
    const findings = await scanDirectory(targetPath);

    if (jsonFlag) {
      console.log(reportToJson(findings));
    } else {
      reportToConsole(findings);
    }

    if (findings.length > 0) {
      process.exitCode = 1;
    }
  } catch (err) {
    console.error("Error during scan:", err);
    process.exit(2);
  }
}
