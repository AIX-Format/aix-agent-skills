import { createHash } from 'crypto';

/**
 * Legacy TrustChain Entry — سجل الثقة (النسخة القديمة)
 */
export interface TrustChainEntry {
  timestamp: number;
  action: string;
  inputHash: string;
  outputHash: string;
  auditHash: string;
  safetyScore: number;
  /** النية — من ḤISĀB.md: "النية مهمة أيضاً" */
  intention?: string;
}

let trustChain: TrustChainEntry[] = [];

/**
 * Append to TrustChain with audit hash verification
 *
 * ḤISĀB.md: "النية مهمة أيضاً" — النية تُسجَّل لتحليل المساءلة
 */
export function appendToTrustChain(
  action: string,
  input: string,
  output: string,
  safetyScore: number,
  intention?: string
): string {
  const inputHash = createHash('sha256').update(input).digest('hex');
  const outputHash = createHash('sha256').update(output).digest('hex');
  const prevHash = trustChain.length > 0 ? trustChain[trustChain.length - 1].auditHash : 'SOVEREIGN_GENESIS';

  const auditHash = createHash('sha256')
    .update(prevHash + action + inputHash + outputHash)
    .digest('hex');

  const entry: TrustChainEntry = {
    timestamp: Date.now(),
    action,
    inputHash,
    outputHash,
    auditHash,
    safetyScore,
    intention,
  };

  trustChain.push(entry);
  return auditHash;
}

/**
 * Returns the current state of the legacy trust chain
 */
export function getLegacyTrustChain(): TrustChainEntry[] {
  return trustChain;
}
