import { StateGraph, START, END } from '@langchain/langgraph';
import { WorkflowState, WorkflowStatus } from '../state/types';
import { MockLLMProvider } from '../../services/llm/mockProvider';
import { InvoiceRepository } from '../../data/repositories/invoiceRepository';
import { CustomerRepository } from '../../data/repositories/customerRepository';
import { CommunicationRepository } from '../../data/repositories/communicationRepository';

const llmProvider = new MockLLMProvider();
const invoiceRepo = new InvoiceRepository();
const customerRepo = new CustomerRepository();
const commsRepo = new CommunicationRepository();

const workflowStateChannels = {
  objective: { value: (x: any, y: any) => y ?? x, default: () => "" },
  context: { value: (x: any, y: any) => ({ ...x, ...y }), default: () => ({}) },
  plan: { value: (x: any, y: any) => y ?? x, default: () => [] },
  currentStepId: { value: (x: any, y: any) => y ?? x, default: () => null },
  completedSteps: { value: (x: any, y: any) => [...x, ...(y||[])], default: () => [] },
  failedSteps: { value: (x: any, y: any) => [...x, ...(y||[])], default: () => [] },
  pendingApprovals: { value: (x: any, y: any) => [...x, ...(y||[])], default: () => [] },
  toolResults: { value: (x: any, y: any) => [...x, ...(y||[])], default: () => [] },
  replans: { value: (x: any, y: any) => [...x, ...(y||[])], default: () => [] },
  status: { value: (x: any, y: any) => y ?? x, default: () => "PENDING" as WorkflowStatus },
  priorityCases: { value: (x: any, y: any) => y ?? x, default: () => [] },
  recommendations: { value: (x: any, y: any) => y ?? x, default: () => [] },
  communicationDrafts: { value: (x: any, y: any) => y ?? x, default: () => [] },
};

async function understandObjectiveNode(state: WorkflowState): Promise<Partial<WorkflowState>> {
  const result = await llmProvider.generatePlan(state.objective);
  return {
    plan: result.plan,
    context: { understanding: result.understanding },
    currentStepId: "step-1",
    status: "RUNNING"
  };
}

async function retrieveInvoicesNode(state: WorkflowState): Promise<Partial<WorkflowState>> {
  const overdueInvoices = await invoiceRepo.getOverdueInvoices(50000);
  return {
    currentStepId: "step-3", // Skip step 2 for brevity
    completedSteps: ["step-1", "step-2"],
    context: { overdueInvoices }
  };
}

async function analyzeAndPrioritizeNode(state: WorkflowState): Promise<Partial<WorkflowState>> {
  const cases = await llmProvider.analyzeCases(state.context);
  return {
    currentStepId: "step-5", // Skip step 3,4 for brevity
    completedSteps: ["step-3", "step-4"],
    priorityCases: cases
  };
}

async function generateActionNode(state: WorkflowState): Promise<Partial<WorkflowState>> {
  const drafts = await llmProvider.generateDrafts(state.priorityCases || []);
  
  // High value triggers approval
  const needsApproval = state.priorityCases?.some(c => c.priority === "HIGH");
  
  if (needsApproval) {
    return {
      currentStepId: "step-6",
      completedSteps: ["step-5"],
      communicationDrafts: drafts,
      status: "WAITING_APPROVAL",
      pendingApprovals: [{
        id: "app-1",
        actionRequired: "Approve communication drafts for high-risk customers",
        context: drafts,
        status: "PENDING"
      }]
    };
  }

  return {
    currentStepId: "step-7",
    completedSteps: ["step-5", "step-6"],
    communicationDrafts: drafts
  };
}

function shouldAskForApproval(state: WorkflowState): string {
  if (state.status === "WAITING_APPROVAL") return "human_approval";
  return "execute";
}

async function humanApprovalNode(state: WorkflowState): Promise<Partial<WorkflowState>> {
  // This node just waits in a real implementation.
  // We'll simulate approval logic from the frontend mutating state.
  return {
    currentStepId: "step-7",
    status: "RUNNING"
  };
}

async function executeNode(state: WorkflowState): Promise<Partial<WorkflowState>> {
  // Simulate email sending and failure handling
  const drafts = state.communicationDrafts || [];
  
  // Inject intentional failure for demo (CUST-003 has bad email)
  const failed = drafts.find(d => d.invoice_id === "INV-1044");
  
  if (failed && !state.replans.length) {
    return {
      status: "REPLANNING",
      failedSteps: ["step-7"],
      replans: [{
        timestamp: new Date().toISOString(),
        reason: "Invalid email for CUST-003",
        originalPlan: state.plan,
        newPlan: state.plan
      }]
    };
  }
  
  return {
    currentStepId: "step-8",
    completedSteps: ["step-7"],
    status: "COMPLETED"
  };
}

export function createWorkflowGraph() {
  const builder = new StateGraph<WorkflowState>({ channels: workflowStateChannels })
    .addNode("UnderstandObjective", understandObjectiveNode)
    .addNode("RetrieveInvoices", retrieveInvoicesNode)
    .addNode("AnalyzeAndPrioritize", analyzeAndPrioritizeNode)
    .addNode("GenerateAction", generateActionNode)
    .addNode("HumanApproval", humanApprovalNode)
    .addNode("Execute", executeNode);

  builder.addEdge(START, "UnderstandObjective");
  builder.addEdge("UnderstandObjective", "RetrieveInvoices");
  builder.addEdge("RetrieveInvoices", "AnalyzeAndPrioritize");
  builder.addEdge("AnalyzeAndPrioritize", "GenerateAction");
  
  builder.addConditionalEdges("GenerateAction", shouldAskForApproval as any, {
    human_approval: "HumanApproval",
    execute: "Execute"
  });
  
  builder.addEdge("HumanApproval", "Execute");
  builder.addEdge("Execute", END);

  return builder.compile();
}
