import { GeminiProvider } from '../providers/gemini-provider';
import { ObjectiveAnalyzer } from '../prompts/objective-analyzer';
import { DynamicPlanner } from '../prompts/planner';
import { PlanVerifier } from '../prompts/plan-verifier';
import { Plan } from '../schemas/plan';
import { AIUnavailableError, CapabilityUnavailableError, ValidationError } from '../errors';

export interface OrchestrationResult {
  objectiveAnalysis: string;
  planGeneration: string;
  planVerification: string;
  overall: string;
  plan?: Plan;
  error?: string;
}

export class Day1Orchestrator {
  private ai: GeminiProvider;
  private analyzer: ObjectiveAnalyzer;
  private planner: DynamicPlanner;
  private verifier: PlanVerifier;

  constructor() {
    this.ai = new GeminiProvider();
    this.analyzer = new ObjectiveAnalyzer(this.ai);
    this.planner = new DynamicPlanner(this.ai);
    this.verifier = new PlanVerifier();
  }

  async processObjectiveWithReport(userInput: string): Promise<OrchestrationResult> {
    const report: OrchestrationResult = {
      objectiveAnalysis: 'PENDING',
      planGeneration: 'PENDING',
      planVerification: 'PENDING',
      overall: 'PENDING'
    };

    try {
      console.log(`\n[1] REAL USER OBJECTIVE\n    -> "${userInput}"`);
      
      // Step 1: Objective Analysis
      console.log(`[2] OBJECTIVE ANALYSIS...`);
      let structuredObjective;
      try {
        structuredObjective = await this.analyzer.analyze(userInput);
        report.objectiveAnalysis = 'SUCCESS';
        console.log(`    -> Parsed Objective: ${structuredObjective.objective}`);
        console.log(`    -> Entities: ${structuredObjective.entities.join(", ")}`);
        console.log(`    -> Required Actions: ${structuredObjective.requiredActions.join(", ")}`);
      } catch (e: any) {
        report.objectiveAnalysis = this.mapError(e);
        throw e;
      }

      // Step 2: Plan Generation
      console.log(`[3] DYNAMIC PLAN GENERATION...`);
      let plan;
      try {
        plan = await this.planner.plan(structuredObjective);
        report.planGeneration = 'SUCCESS';
        report.plan = plan;
        console.log(`    -> Generated ${plan.steps.length} steps.`);
      } catch (e: any) {
        report.planGeneration = this.mapError(e);
        throw e;
      }

      // Step 3: Verification
      console.log(`[4] PLAN VALIDATION & VERIFICATION...`);
      try {
        this.verifier.verify(plan);
        report.planVerification = 'SUCCESS';
        console.log(`    -> VALID`);
      } catch (e: any) {
        report.planVerification = this.mapError(e);
        throw e;
      }

      report.overall = 'SUCCESS';
      console.log(`[5] VERIFIED PLAN READY FOR EXECUTION\n`);
      return report;

    } catch (e: any) {
      if (e instanceof AIUnavailableError) {
        report.overall = 'RETRYABLE (AI_UNAVAILABLE)';
      } else if (e instanceof CapabilityUnavailableError) {
        // If it's a capability error, the system correctly rejected an impossible plan.
        // For testing purposes, this represents a PASS of the safety mechanism.
        report.overall = 'PASS (REJECTED UNAVAILABLE CAPABILITY)';
      } else if (e instanceof ValidationError) {
        report.overall = 'FAIL (VALIDATION_ERROR)';
      } else {
        report.overall = 'FAIL (UNKNOWN_ERROR)';
      }
      report.error = e.message;
      return report;
    }
  }

  private mapError(e: any): string {
    if (e instanceof AIUnavailableError) return 'AI_UNAVAILABLE';
    if (e instanceof CapabilityUnavailableError) return 'CAPABILITY_UNAVAILABLE';
    if (e instanceof ValidationError) return 'VALIDATION_ERROR';
    return 'UNKNOWN_ERROR';
  }
}
