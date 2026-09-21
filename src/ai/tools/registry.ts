export interface ToolDefinition {
  name: string;
  description: string;
  inputSchema: any; // Keep simple for Day 1
  outputSchema: any;
  requiresApproval?: boolean;
}

export const ToolRegistry: Record<string, ToolDefinition> = {
  "invoice.search": {
    name: "invoice.search",
    description: "Search for invoices matching specific conditions (e.g., status, amount, days overdue).",
    inputSchema: {
      type: "object",
      properties: {
        status: { type: "string" },
        minimumAmount: { type: "number" }
      }
    },
    outputSchema: { type: "array", items: { type: "object" } }
  },
  "customer.get": {
    name: "customer.get",
    description: "Retrieve customer details, risk profile, and metadata by customer ID.",
    inputSchema: {
      type: "object",
      properties: {
        customerIds: { type: "array", items: { type: "string" } }
      }
    },
    outputSchema: { type: "array", items: { type: "object" } }
  },
  "communication.history": {
    name: "communication.history",
    description: "Retrieve past communication records and their resolution status for a given customer.",
    inputSchema: {
      type: "object",
      properties: {
        customerIds: { type: "array", items: { type: "string" } }
      }
    },
    outputSchema: { type: "array", items: { type: "object" } }
  },
  "payment.status": {
    name: "payment.status",
    description: "Check the real-time processing status of a payment against an invoice.",
    inputSchema: {
      type: "object",
      properties: {
        invoiceIds: { type: "array", items: { type: "string" } }
      }
    },
    outputSchema: { type: "object" }
  },
  "policy.check": {
    name: "policy.check",
    description: "Evaluate a proposed action against internal business policies.",
    inputSchema: {
      type: "object",
      properties: {
        actionType: { type: "string" },
        context: { type: "object" }
      }
    },
    outputSchema: { type: "object", properties: { allowed: { type: "boolean" }, requiredApprovals: { type: "array" } } }
  }
};

/**
 * Returns a formatted string of available tools for injection into prompts.
 */
export function getAvailableToolsDescription(): string {
  return Object.values(ToolRegistry).map(tool => {
    return `- **${tool.name}**: ${tool.description}\n  Inputs: ${JSON.stringify(tool.inputSchema.properties)}`;
  }).join('\n\n');
}
