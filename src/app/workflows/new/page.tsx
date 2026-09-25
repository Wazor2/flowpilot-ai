"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Workflow, Sparkles, ArrowRight, Loader2 } from 'lucide-react';
import { api, type Workflow as WorkflowRecord } from '@/lib/api';

export default function CreateWorkflow() {
  const [objective, setObjective] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const handleCreate = async () => {
    if (!objective.trim()) return;
    setIsSubmitting(true); setError(null);
    try { const workflow = await api<WorkflowRecord>('/api/workflows', { method: 'POST', body: JSON.stringify({ objective: objective.trim(), mode: 'AUTONOMOUS' }) }); localStorage.setItem('lastWorkflowId', workflow.id); router.push(`/workflows/${workflow.id}`); }
    catch (e) { setError(e instanceof Error ? e.message : 'Could not create workflow'); setIsSubmitting(false); }
  };
  return <div className="mx-auto flex min-h-[70vh] max-w-4xl items-center"><div className="w-full rounded-2xl border border-slate-200 bg-white p-10 shadow-sm"><div className="mb-6 flex justify-center text-blue-600"><Workflow className="h-10 w-10" /></div><h1 className="mb-2 text-center text-3xl font-bold">Create New Workflow</h1><p className="mb-10 text-center text-lg text-slate-500">What would you like the AI agent to accomplish?</p><textarea value={objective} onChange={(e) => setObjective(e.target.value)} placeholder="e.g. Find overdue invoices above ₹50,000, prioritize them, draft follow-up emails and ask for approval before sending." className="h-40 w-full resize-none rounded-xl border border-slate-200 bg-slate-50 p-4 text-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500" />{error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}<div className="mt-8 flex flex-col justify-center gap-4 sm:flex-row"><button onClick={() => setObjective('Find all overdue invoices above ₹50,000, analyze the customers, prioritize the cases, prepare follow-up emails, and ask me for approval before sending.')} disabled={isSubmitting} className="flex items-center justify-center gap-2 rounded-xl bg-slate-100 px-6 py-3 font-medium text-slate-700"><Sparkles className="h-5 w-5" />Use Example</button><button onClick={() => void handleCreate()} disabled={!objective.trim() || isSubmitting} className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-8 py-3 font-medium text-white disabled:cursor-not-allowed disabled:opacity-50">{isSubmitting ? <><Loader2 className="h-5 w-5 animate-spin" />Creating...</> : <>Create Workflow<ArrowRight className="h-5 w-5" /></>}</button></div></div></div>;
}
