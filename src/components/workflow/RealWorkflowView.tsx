"use client";

import { useCallback, useEffect, useState } from 'react';
import { CheckCircle, CircleAlert, Loader2, RefreshCw, ShieldCheck } from 'lucide-react';
import { api, type Approval, type AuditEvent, type Workflow } from '@/lib/api';

const terminal = new Set(['COMPLETED', 'FAILED', 'PAUSED', 'REJECTED']);

export function RealWorkflowView({ workflowId }: { workflowId: string }) {
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busyApproval, setBusyApproval] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [nextWorkflow, nextEvents, nextApprovals] = await Promise.all([
        api<Workflow>(`/api/workflows/${workflowId}`),
        api<AuditEvent[]>(`/api/workflows/${workflowId}/events`),
        api<Approval[]>(`/api/workflows/${workflowId}/approvals`),
      ]);
      setWorkflow(nextWorkflow);
      setEvents(nextEvents);
      setApprovals(nextApprovals.filter((approval) => approval.status === 'PENDING'));
      setError(null);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Could not load workflow');
    }
  }, [workflowId]);

  useEffect(() => { void load(); }, [load]);

  useEffect(() => {
    if (!workflow || terminal.has(workflow.status)) return;
    const timer = window.setInterval(() => { void load(); }, 2000);
    return () => window.clearInterval(timer);
  }, [workflow, load]);

  const decide = async (approvalId: string, action: 'approve' | 'reject') => {
    setBusyApproval(approvalId);
    try {
      await api(`/api/workflows/${workflowId}/${action}`, {
        method: 'POST',
        body: JSON.stringify({ approval_id: approvalId, actor: 'dashboard-user' }),
      });
      await load();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : `Could not ${action} approval`);
    } finally {
      setBusyApproval(null);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-20">
      <header className="bg-slate-950 text-white px-8 py-5 flex items-center justify-between">
        <div><h1 className="text-xl font-bold">FLOWPILOT AI</h1><p className="text-slate-400 text-sm">Live backend workflow</p></div>
        <button onClick={() => void load()} className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-sm"><RefreshCw className="w-4 h-4" />Refresh</button>
      </header>
      <main className="max-w-6xl mx-auto px-8 py-8 space-y-6">
        {error && <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>}
        {!workflow && !error && <div className="flex items-center gap-2 text-slate-500"><Loader2 className="animate-spin" />Loading workflow...</div>}
        {workflow && <>
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-4"><div><div className="text-xs font-bold uppercase tracking-wider text-slate-400">Workflow {workflow.id}</div><h2 className="mt-2 text-2xl font-bold">{workflow.objective}</h2></div><span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-bold text-blue-700">{workflow.status}</span></div>
            <div className="mt-6 grid gap-4 md:grid-cols-3"><div><div className="text-xs uppercase tracking-wider text-slate-400">Current step</div><div className="font-semibold">{workflow.current_step ?? '—'}</div></div><div><div className="text-xs uppercase tracking-wider text-slate-400">Mode</div><div className="font-semibold">{workflow.mode}</div></div><div><div className="text-xs uppercase tracking-wider text-slate-400">Plan steps</div><div className="font-semibold">{Array.isArray(workflow.current_plan) ? workflow.current_plan.length : 0}</div></div></div>
          </section>
          {approvals.length > 0 && <section className="rounded-2xl border-2 border-amber-200 bg-amber-50 p-6"><div className="mb-4 flex items-center gap-2"><ShieldCheck className="text-amber-600" /><h2 className="text-xl font-bold text-amber-900">Human approval required</h2></div><div className="space-y-3">{approvals.map((approval) => <div key={approval.id} className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-amber-200 bg-white p-4"><div><div className="font-semibold">{approval.action}</div><div className="text-sm text-slate-600">{approval.reason || 'Sensitive action requested by the workflow'}</div></div><div className="flex gap-2"><button disabled={busyApproval === approval.id} onClick={() => void decide(approval.id, 'reject')} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">Reject</button><button disabled={busyApproval === approval.id} onClick={() => void decide(approval.id, 'approve')} className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-bold text-white">{busyApproval === approval.id ? 'Working...' : 'Approve'}</button></div></div>)}</div></section>}
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"><h2 className="mb-5 text-sm font-bold uppercase tracking-wider text-slate-500">Live audit trail</h2><div className="space-y-3">{events.length === 0 && <div className="text-slate-500">No events recorded yet.</div>}{events.map((event) => <div key={event.id} className="flex gap-3 border-b border-slate-100 pb-3 last:border-0"><div className="pt-0.5">{event.status === 'FAILED' ? <CircleAlert className="text-red-500" /> : <CheckCircle className="text-green-500" />}</div><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-2"><span className="font-bold">{event.event_type}</span><span className="text-xs text-slate-400">{event.actor}{event.tool ? ` · ${event.tool}` : ''}</span></div><div className="text-sm text-slate-600">{event.reason || event.result_summary || event.summary || event.input_summary || 'Recorded event'}</div></div><time className="text-xs text-slate-400">{event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : ''}</time></div>)}</div></section>
        </>}
      </main>
    </div>
  );
}
