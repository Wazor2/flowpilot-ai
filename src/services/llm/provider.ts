export interface LLMProvider {
  generatePlan(objective: string): Promise<any>;
  analyzeCases(context: any): Promise<any>;
  generateDrafts(cases: any[]): Promise<any>;
}

// In a real implementation, we would have GeminiProvider and OpenAIProvider
// implementing this interface.
