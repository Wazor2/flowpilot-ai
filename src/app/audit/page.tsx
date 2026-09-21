"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Filter, History, Database, CheckCircle, ShieldAlert, AlertCircle, FileText, ArrowRight } from 'lucide-react';

type AuditEvent = {
  time: string;
  wfId: string;
  event: string;
  actor: string;
  tool: string;
  status: 'SUCCESS' | 'FAILED' | 'PENDING' | 'REPLANNED';
  result: string;
  category: 'Planning' | 'Data Retrieval' | 'Approval' | 'Execution' | 'Failure' | 'Re-planning' | 'Verification';
};

export default function AuditTrail() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [filter, setFilter] = useState('All');

  useEffect(() => {
    // Simulated Audit Events based on the demo requirements
    const demoRun = localStorage.getItem('demoCompleted');
    if (demoRun === 'true') {
      const generateTime = (offset: number) => {
        const d = new Date();
        d.setMinutes(d.getMinutes() - 10);
        d.setSeconds(d.getSeconds() + offset);
        return d.toLocaleTimeString([], { hour12: false });
      };

      setEvents([
        { time: generateTime(0), wfId: 'WF-001', event: 'OBJECTIVE_RECEIVED', actor: 'System', tool: 'IntentParser', status: 'SUCCESS', result: 'Objective parsed successfully', category: 'Planning' },
        { time: generateTime(2), wfId: 'WF-001', event: 'PLAN_GENERATED', actor: 'AI Planner', tool: 'LangGraph', status: 'SUCCESS', result: '10-step execution plan generated', category: 'Planning' },
        { time: generateTime(5), wfId: 'WF-001', event: 'DATA_RETRIEVED', actor: 'System', tool: 'InvoiceDB', status: 'SUCCESS', result: '12 invoices retrieved', category: 'Data Retrieval' },
        { time: generateTime(6), wfId: 'WF-001', event: 'DATA_RETRIEVED', actor: 'System', tool: 'CustomerDB', status: 'SUCCESS', result: '6 customer records retrieved', category: 'Data Retrieval' },
        { time: generateTime(9), wfId: 'WF-001', event: 'CONTEXT_ANALYZED', actor: 'Decision Engine', tool: 'LLM', status: 'SUCCESS', result: '7 overdue cases evaluated', category: 'Planning' },
        { time: generateTime(12), wfId: 'WF-001', event: 'APPROVAL_REQUESTED', actor: 'System', tool: 'ApprovalGateway', status: 'PENDING', result: '3 actions require authorization', category: 'Approval' },
        { time: generateTime(35), wfId: 'WF-001', event: 'APPROVAL_RECEIVED', actor: 'Admin (Human)', tool: 'ApprovalGateway', status: 'SUCCESS', result: '3 actions approved', category: 'Approval' },
        { time: generateTime(37), wfId: 'WF-001', event: 'EXECUTION_STARTED', actor: 'Execution Engine', tool: 'ActionRunner', status: 'SUCCESS', result: 'Processing 6 actions', category: 'Execution' },
        { time: generateTime(38), wfId: 'WF-001', event: 'ACTION_EXECUTED', actor: 'System', tool: 'EmailTool', status: 'SUCCESS', result: 'INV-1001 escalation sent', category: 'Execution' },
        { time: generateTime(41), wfId: 'WF-001', event: 'EXECUTION_FAILED', actor: 'System', tool: 'EmailTool', status: 'FAILED', result: 'Invalid primary contact (invalid@delta-logistics.example)', category: 'Failure' },
        { time: generateTime(42), wfId: 'WF-001', event: 'FAILURE_DETECTED', actor: 'Execution Engine', tool: 'Observer', status: 'SUCCESS', result: 'Workflow paused due to action failure', category: 'Failure' },
        { time: generateTime(44), wfId: 'WF-001', event: 'WORKFLOW_REPLANNED', actor: 'AI Planner', tool: 'LangGraph', status: 'REPLANNED', result: 'Revised plan created for INV-1004', category: 'Re-planning' },
        { time: generateTime(46), wfId: 'WF-001', event: 'DATA_RETRIEVED', actor: 'System', tool: 'CustomerTool', status: 'SUCCESS', result: 'Alternate verified contact found', category: 'Data Retrieval' },
        { time: generateTime(49), wfId: 'WF-001', event: 'ACTION_EXECUTED', actor: 'System', tool: 'EmailTool', status: 'SUCCESS', result: 'INV-1004 recovered action sent', category: 'Execution' },
        { time: generateTime(52), wfId: 'WF-001', event: 'WORKFLOW_VERIFIED', actor: 'System', tool: 'Verifier', status: 'SUCCESS', result: '6/6 business actions completed', category: 'Verification' },
        { time: generateTime(53), wfId: 'WF-001', event: 'WORKFLOW_COMPLETED', actor: 'System', tool: 'Orchestrator', status: 'SUCCESS', result: 'Objective achieved', category: 'Verification' }
      ]);
    }
  }, []);

  const filters = ['All', 'Planning', 'Data Retrieval', 'Approval', 'Execution', 'Failure', 'Re-planning', 'Verification'];
  
  const filteredEvents = filter === 'All' ? events : events.filter(e => e.category === filter);

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 text-slate-900 pb-20">
      <header className="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between sticky top-0 z-50 shadow-sm">
        <div className="flex items-center gap-6">
          <Link href="/" className="text-slate-500 hover:text-slate-900 transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-xl font-bold flex items-center gap-2"><History className="w-5 h-5" /> Audit Trail</h1>
            <p className="text-sm text-slate-500">Immutable record of all workflow events</p>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto w-full px-8 pt-8">
        
        {events.length === 0 ? (
          <div className="text-center py-20 bg-white border border-slate-200 rounded-xl shadow-sm">
            <Database className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <h2 className="text-xl font-bold mb-2">No workflow executed yet</h2>
            <p className="text-slate-500 mb-6">Run the demo to populate the audit trail.</p>
            <Link href="/" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-bold transition-colors">
              Return to Dashboard
            </Link>
          </div>
        ) : (
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col h-[800px]">
            <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-4">
              <Filter className="w-4 h-4 text-slate-400" />
              <div className="flex flex-wrap gap-2">
                {filters.map(f => (
                  <button 
                    key={f} 
                    onClick={() => setFilter(f)}
                    className={`px-3 py-1 rounded-full text-xs font-bold transition-colors ${filter === f ? 'bg-slate-800 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-100'}`}
                  >
                    {f}
                  </button>
                ))}
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {filteredEvents.map((e, i) => (
                <div key={i} className="flex gap-6 border-b border-slate-100 pb-6 last:border-0 last:pb-0">
                  <div className="w-24 text-right shrink-0">
                    <div className="font-mono text-sm font-bold text-slate-700">{e.time}</div>
                    <div className="text-xs text-slate-400 mt-1">{e.wfId}</div>
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {e.status === 'SUCCESS' && <CheckCircle className="w-4 h-4 text-green-500" />}
                      {e.status === 'FAILED' && <ShieldAlert className="w-4 h-4 text-red-500" />}
                      {e.status === 'PENDING' && <AlertCircle className="w-4 h-4 text-amber-500" />}
                      {e.status === 'REPLANNED' && <ArrowRight className="w-4 h-4 text-purple-500" />}
                      <span className="font-bold text-sm tracking-wider">{e.event}</span>
                      <span className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded">{e.category}</span>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-4 bg-slate-50 border border-slate-100 rounded-lg p-4 mt-3">
                      <div>
                        <div className="text-[10px] uppercase tracking-widest text-slate-400 font-bold mb-1">Actor / Tool</div>
                        <div className="text-sm font-medium">{e.actor} <span className="text-slate-400">using</span> {e.tool}</div>
                      </div>
                      <div>
                        <div className="text-[10px] uppercase tracking-widest text-slate-400 font-bold mb-1">Status</div>
                        <div className={`text-sm font-bold ${
                          e.status === 'SUCCESS' ? 'text-green-600' : 
                          e.status === 'FAILED' ? 'text-red-600' : 
                          e.status === 'REPLANNED' ? 'text-purple-600' : 'text-amber-600'
                        }`}>
                          {e.status}
                        </div>
                      </div>
                      <div>
                        <div className="text-[10px] uppercase tracking-widest text-slate-400 font-bold mb-1">Result</div>
                        <div className="text-sm text-slate-700">{e.result}</div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
