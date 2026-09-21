"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Workflow, Sparkles, ArrowRight } from 'lucide-react';

export default function CreateWorkflow() {
  const [objective, setObjective] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  const handleCreate = () => {
    if (!objective.trim()) return;
    setIsSubmitting(true);
    // In a real app we would POST this to an API and get an ID.
    // We'll just pass it in state or redirect for the demo.
    setTimeout(() => {
      // Hardcoded ID for the demo
      router.push(`/workflows/demo-123?objective=${encodeURIComponent(objective)}`);
    }, 1000);
  };

  const useExample = () => {
    setObjective("Find all overdue invoices above ₹50,000, analyze the customers, prioritize the cases, prepare follow-up emails, and ask me for approval before sending.");
  };

  return (
    <div className="max-w-4xl mx-auto flex flex-col items-center justify-center min-h-[70vh]">
      <div className="bg-white p-10 rounded-2xl border border-slate-200 shadow-sm w-full">
        <div className="flex items-center gap-3 mb-6 justify-center text-blue-600">
          <Workflow className="w-10 h-10" />
        </div>
        <h1 className="text-3xl font-bold text-center tracking-tight mb-2">Create New Workflow</h1>
        <p className="text-slate-500 text-center mb-10 text-lg">What would you like the AI agent to accomplish?</p>

        <textarea
          value={objective}
          onChange={(e) => setObjective(e.target.value)}
          placeholder="e.g. Find overdue invoices above ₹50,000, prioritize them, draft follow-up emails and ask for approval before sending."
          className="w-full h-40 p-4 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all resize-none text-lg"
        />

        <div className="flex flex-col sm:flex-row gap-4 mt-8 justify-center">
          <button
            onClick={useExample}
            disabled={isSubmitting}
            className="px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
          >
            <Sparkles className="w-5 h-5" />
            Use Example
          </button>
          <button
            onClick={handleCreate}
            disabled={!objective.trim() || isSubmitting}
            className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Creating...' : 'Create Workflow'}
            {!isSubmitting && <ArrowRight className="w-5 h-5" />}
          </button>
        </div>
      </div>
    </div>
  );
}
