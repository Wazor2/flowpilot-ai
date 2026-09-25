"use client";

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { Loader2, Plus, RefreshCw, Workflow } from 'lucide-react';
import { api, type Workflow as WorkflowRecord } from '@/lib/api';

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<WorkflowRecord[]>([]);
  const [error, setError] = useState<string | null>(null);
  const load = async () => { try { setWorkflows(await api<WorkflowRecord[]>('/api/workflows')); setError(null); } catch (e) { setError(e instanceof Error ? e.message : 'Could not load workflows'); } };
  useEffect(() => { void load(); }, []);
  return <div className="mx-auto w-full max-w-6xl space-y-6">
    <div className="flex items-center justify-between"><div><h1 className="text-3xl font-bold">Workflows</h1><p className="mt-1 text-slate-500">Live workflows created in the FastAPI backend.</p></div><div className="flex gap-2"><button onClick={() => void load()} className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm"><RefreshCw className="h-4 w-4" />Refresh</button><Link href="/workflows/new" className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white"><Plus className="h-4 w-4" />New workflow</Link></div></div>
    {error && <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>}
    {!error && workflows.length === 0 && <div className="rounded-xl border border-slate-200 bg-white p-12 text-center text-slate-500"><Workflow className="mx-auto mb-3 h-10 w-10 text-slate-300" />No workflows created yet.</div>}
    <div className="grid gap-4">{workflows.map((workflow) => <Link key={workflow.id} href={`/workflows/${workflow.id}`} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-blue-300 hover:shadow"><div className="flex flex-wrap items-start justify-between gap-3"><div><div className="font-mono text-xs text-slate-400">{workflow.id}</div><h2 className="mt-2 font-semibold text-slate-900">{workflow.objective}</h2></div><span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-700">{workflow.status}</span></div><div className="mt-4 flex gap-6 text-sm text-slate-500"><span>Mode: {workflow.mode}</span><span>Created: {workflow.created_at ? new Date(workflow.created_at).toLocaleString() : '—'}</span><span>Step: {workflow.current_step ?? '—'}</span></div></Link>)}</div>
    {workflows.length > 0 && <div className="text-center text-xs text-slate-400"><Loader2 className="mr-1 inline h-3 w-3" />Data is loaded from PostgreSQL through the FastAPI API.</div>}
  </div>;
}
