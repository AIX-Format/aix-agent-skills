/**
 * tui.ts
 * Sovereign Dashboard for IQRA Constitutional Runtime.
 * A premium terminal interface for real-time monitoring and interaction.
 */

import chalk from "chalk";
import readline from "readline";
import { ConstitutionalRuntime } from "./standalone-runtime.js";

const runtime = new ConstitutionalRuntime();
runtime.registerSkill("system", (input: any) => ({ 
  status: "Sovereign process active", 
  processed_content: input 
}));

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: chalk.cyan("IQRA> "),
});

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

function clearScreen() {
  process.stdout.write("\x1Bc");
}

async function bootSequence() {
  clearScreen();
  const logo = `
   ██╗ ██████╗ ██████╗  █████╗ 
   ██║██╔═══██╗██╔══██╗██╔══██╗
   ██║██║   ██║██████╔╝███████║
   ██║██║▄▄ ██║██╔══██╗██╔══██║
   ██║╚██████╔╝██║  ██║██║  ██║
   ╚═╝ ╚══▀▀═╝ ╚═╝  ╚═╝╚═╝  ╚═╝
  `;
  
  console.log(chalk.cyan(logo));
  console.log(chalk.bold.white("  CONSTITUTIONAL RUNTIME v1.0.0"));
  console.log(chalk.dim("  Initializing Sovereign Kernel..."));
  console.log("");

  const steps = [
    "Loading Constitutional Rules...",
    "Verifying Trust Chain Integrity...",
    "Syncing Sharia Compliance Filters...",
    "Booting Skill Engine...",
    "Establishing Sovereign Identity..."
  ];

  for (const step of steps) {
    process.stdout.write(chalk.white(`  [ ] ${step}`));
    await sleep(400);
    process.stdout.write("\r");
    process.stdout.write(chalk.green(`  [✔] ${step}\n`));
  }

  console.log(chalk.cyan("\n  SYSTEM STABLE. READY FOR COMMANDS.\n"));
  await sleep(800);
}

function renderHeader() {
  const integrity = runtime.verifyChain();
  const count = runtime.getChainCount();
  const statusIcon = "🟢";
  const chainIcon = integrity.valid ? "🛡️" : "⚠️";

  console.log(chalk.bgCyan.black.bold(" ⚖️  IQRA CONSTITUTIONAL RUNTIME — SOVEREIGN DASHBOARD "));
  console.log(chalk.cyan("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓"));
  
  const statusLine = [
    chalk.bold(" STATUS: ") + chalk.green(`${statusIcon} ACTIVE`),
    chalk.bold("CHAIN: ") + (integrity.valid ? chalk.green(`${chainIcon} VERIFIED`) : chalk.red(`${chainIcon} TAMPERED`)),
    chalk.bold("ENTRIES: ") + chalk.yellow(count.toString().padStart(4, "0")),
  ].join("  │  ");

  console.log(chalk.cyan("┃") + statusLine + chalk.cyan(" ┃"));
  console.log(chalk.cyan("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"));
}

function renderLog(response: any) {
  const passed = response.governance.passed;
  const icon = passed ? "✅" : "🛑";
  const actionColor = passed ? chalk.green : chalk.red;
  const boxColor = passed ? chalk.green : chalk.red;
  
  console.log(boxColor(`  ┌─── ${passed ? "EXECUTION SUCCESS" : "GOVERNANCE BLOCK"} ───────────────────────────`));
  console.log(boxColor(`  │ `) + `${chalk.bold("Request ID:")} ${chalk.dim(response.requestId)}`);
  console.log(boxColor(`  │ `) + `${chalk.bold("Governance:")} ${actionColor(response.governance.recommendation.toUpperCase())} ${icon}`);
  
  if (!passed) {
    response.governance.flags.forEach((f: any) => {
      console.log(boxColor(`  │ `) + chalk.red(`[!] ${f.layer}: ${f.reason}`));
    });
    console.log(boxColor(`  │ `) + chalk.dim("Result: Execution terminated by constitutional decree."));
  } else {
    console.log(boxColor(`  │ `) + chalk.green(`[🧬] Skill '${response.skillId}' executed successfully.`));
    console.log(boxColor(`  │ `) + chalk.dim(`[⛓️] TrustChain Index: ${response.chainEntryId}`));
  }
  console.log(boxColor(`  └──────────────────────────────────────────────────────────`));
  console.log("");
}

async function start() {
  await bootSequence();
  clearScreen();
  renderHeader();
  console.log(chalk.italic.gray("  Type content to verify (e.g., 'hello world' or 'harmful text').\n  Type 'exit' to disconnect.\n"));
  rl.prompt();

  rl.on("line", (line) => {
    const input = line.trim();
    
    if (input.toLowerCase() === "exit") {
      console.log(chalk.yellow("\n  Sovereign process terminated. Farewell. 👋\n"));
      process.exit(0);
    }

    if (input === "") {
      rl.prompt();
      return;
    }

    const response = runtime.execute({
      requestId: `ui-${Date.now()}`,
      skillId: "system",
      content: input,
    });

    clearScreen();
    renderHeader();
    renderLog(response);
    rl.prompt();
  }).on("close", () => {
    console.log(chalk.yellow("\n  Session closed."));
    process.exit(0);
  });
}

// Start the TUI
start();
