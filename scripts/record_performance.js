const fs = require('fs');
const path = require('path');

const LEDGER_PATH = path.join(__dirname, '..', 'performance_ledger.json');

// Parse command line arguments
const args = process.argv.slice(2);
let skillName = null;
let success = null;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--skill' && args[i + 1]) {
    skillName = args[i + 1];
    i++;
  } else if (args[i] === '--success' && args[i + 1]) {
    success = args[i + 1].toLowerCase() === 'true';
    i++;
  }
}

if (!skillName || success === null) {
  console.error('Usage: node scripts/record_performance.js --skill <name> --success <true|false>');
  process.exit(1);
}

// Ensure the ledger file exists
if (!fs.existsSync(LEDGER_PATH)) {
  fs.writeFileSync(LEDGER_PATH, JSON.stringify({}, null, 2), 'utf8');
}

// Read and update the ledger
try {
  const ledgerData = fs.readFileSync(LEDGER_PATH, 'utf8');
  const ledger = JSON.parse(ledgerData);

  if (!ledger[skillName]) {
    ledger[skillName] = {
      success_count: 0,
      failure_count: 0,
      last_used: null,
      last_result: null
    };
  }

  const now = new Date().toISOString();

  if (success) {
    ledger[skillName].success_count++;
  } else {
    ledger[skillName].failure_count++;
  }

  ledger[skillName].last_used = now;
  ledger[skillName].last_result = success ? 'success' : 'failure';

  fs.writeFileSync(LEDGER_PATH, JSON.stringify(ledger, null, 2), 'utf8');
  console.log(`Successfully recorded performance for skill '${skillName}'.`);
} catch (error) {
  console.error('Error reading or writing to the ledger:', error);
  process.exit(1);
}
