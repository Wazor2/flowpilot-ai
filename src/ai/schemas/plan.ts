import { z } from 'zod';

export const StepSchema = z.object({
  stepId: z.string().describe("A unique identifier for this step, e.g., 'step_1'"),
  action: z.string().describe("A human-readable description of what this step does"),
  tool: z.string().describe("The exact name of the tool to use from the registry"),
  arguments: z.record(z.string(), z.any()).describe("The arguments to pass to the tool"),
  dependsOn: z.array(z.string()).describe("Array of stepIds that must complete before this step"),
  requiresApproval: z.boolean().describe("Whether this specific step requires human approval before execution")
});

export const PlanSchema = z.object({
  objective: z.string().describe("The overall objective this plan achieves"),
  steps: z.array(StepSchema).describe("The sequence of steps to execute")
});

export type Step = z.infer<typeof StepSchema>;
export type Plan = z.infer<typeof PlanSchema>;
