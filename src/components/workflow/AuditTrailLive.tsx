"use client";

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { ArrowLeft, CheckCircle, Filter, RefreshCw, ShieldAlert } from 'lucide-react';
import { api, type AuditEvent, type Workflow } from '@/lib/api';

export default function AuditTrailLive() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [workflowId, setWorkflowId] = useState('');
  const [filter, setFilter] = useState('ALL');
  const [error, setError] = useState<string | null>(null);
  const load = async (selected = workflowId) => { try { const nextWorkflows = await api<Workflow[]>('/api/workflows'); setWorkflows(nextWorkflows); const id = selected || nextWorkflows[0]?.id || ''; setWorkflowId(id); setEvents(id ? await api<AuditEvent[]>(`/api/workflows/${id}/events`) : []); setError(null); } catch (e) { setError(e instanceof Error ? e.message : 'Could not load audit events'); } };
  useEffect(() => { const queryId = new URLSearchParams(window.location.search).get('workflowId') || ''; void load(queryId); }, []);
  const filters = ['ALL', ...Array.from(new Set(events.map((event) => event.event_type)))];
  const visible = filter === 'ALL' ? events : events.filter((event) => event.event_type === filter);
  return <div className="mx-auto w-full max-w-6xl space-y-6"><header className="flex items-center justify-between"><div className="flex items-center gap-4"><Link href="/" className="text-slate-500"><ArrowLeft className="h-5 w-5" /></Link><div><h1 className="text-3xl font-bold">Audit Trail</h1><p className="mt-1 text-slate-500">Immutable workflow events loaded from PostgreSQL.</p></div></div><button onClick={() => void load()} className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm"><RefreshCw className="h-4 w-4" />Refresh</button></header>{error && <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>}<div className="flex flex-wrap items-center gap-3 rounded-xl border border-slate-200 bg-white p-4"><Filter className="h-4 w-4 text-slate-400" /><select value={workflowId} onChange={(e) => { setWorkflowId(e.target.value); void load(e.target.value); }} className="rounded-lg border p-2 text-sm"><option value="">Select workflow</option>{workflows.map((workflow) => <option key={workflow.id} value={workflow.id}>{workflow.id} — {workflow.objective.slice(0, 60)}</option>)}</select><div className="flex flex-wrap gap-2">{filters.map((item) => <button key={item} onClick={() => setFilter(item)} className={`rounded-full px-3 py-1 text-xs font-bold ${filter === item ? 'bg-slate-800 text-white' : 'border border-slate-200 bg-white text-slate-600'}`}>{item}</button>)}</div></div><section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"><div className="space-y-5">{visible.length === 0 && <div className="py-12 text-center text-slate-500">No events recorded for this workflow.</div>}{visible.map((event) => <div key={event.id} className="flex gap-4 border-b border-slate-100 pb-5 last:border-0"><div>{event.status === 'FAILED' ? <ShieldAlert className="text-red-500" /> : <CheckCircle className="text-green-500" />}</div><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-2"><span className="font-bold">{event.event_type}</span><span className="text-xs text-slate-400">{event.actor}{event.tool ? ` · ${event.tool}` : ''}</span></div><p className="mt-1 text-sm text-slate-600">{event.reason || event.result_summary || event.summary || event.input_summary || 'Recorded event'}</p></div><time className="text-xs text-slate-400">{event.timestamp ? new Date(event.timestamp).toLocaleString() : '—'}</time></div>)}</div></section></div>;
}
