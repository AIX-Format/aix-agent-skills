/**
 * Prompt Evaluator Skill — مقيّم المطالبات
 * TIER: PRO
 *
 * Evaluates prompt quality and safety before execution.
 */

import { RedTeamGuard, EvaluationResult } from './red-team-guard.js';
import path from 'path';
import fs from 'fs';

export class PromptEvaluator {
  private guard: RedTeamGuard;

  constructor() {
    this.guard = new RedTeamGuard();
  }

  async validatePrompt(prompt: string): Promise<EvaluationResult> {
    const configPath = this.guard.generateConfig(prompt);
    return await this.guard.evaluate(configPath);
  }
}
