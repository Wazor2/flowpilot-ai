export type WorkflowStatus = 'PENDING' | 'RUNNING' | 'WAITING_APPROVAL' | 'COMPLETED' | 'FAILED' | 'REPLANNING';

export interface WorkflowStep {
  id: string;
  name: string;
  description: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'SKIPPED';
  toolUsed?: string;
  resultSummary?: string;
  startTime?: string;
  durationMs?: number;
}

export interface Approval {
  id: string;
  actionRequired: string;
  context: any;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
}

export interface ToolResult {
  tool: string;
  result: any;
  timestamp: string;
}

export interface ReplanEvent {
  timestamp: string;
  reason: string;
  originalPlan: WorkflowStep[];
  newPlan: WorkflowStep[];
}

export interface WorkflowState {
  objective: string;
  context: Record<string, any>;
  plan: WorkflowStep[];
  currentStepId: string | null;
  completedSteps: string[];
  failedSteps: string[];
  pendingApprovals: Approval[];
  toolResults: ToolResult[];
  replans: ReplanEvent[];
  status: WorkflowStatus;
  
  // High level outputs
  priorityCases?: any[];
  recommendations?: any[];
  communicationDrafts?: any[];
}
