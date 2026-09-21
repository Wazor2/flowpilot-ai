"use client";

import { useWorkflowDemo, DemoStage } from '@/hooks/useWorkflowDemo';
import { 
  CheckCircle, AlertCircle, Clock, PlayCircle, Loader2, RotateCcw,
  Database, Users, History, FileText, ArrowRight, ShieldCheck, ListTodo, ShieldAlert
} from 'lucide-react';
import clsx from 'clsx';
import Link from 'next/link';

import React, { useState } from 'react';

export default function WorkflowControlCenter({ params }: { params: Promise<{ id: string }> }) {
  const { id } = React.use(params);
  const { stage, logs, approvalsGranted, runDemo, grantApprovals, resetDemo } = useWorkflowDemo();
  const [demoScriptMode, setDemoScriptMode] = useState(false);
  const [showWhatHappened, setShowWhatHappened] = useState(false);

  const isRunning = stage !== 'IDLE' && stage !== 'COMPLETE';
  const stageIndex = ['IDLE', 'UNDERSTAND', 'PLAN', 'GATHER', 'ANALYZE', 'DECIDE', 'APPROVE', 'EXECUTE', 'VERIFY', 'REPLAN', 'COMPLETE'].indexOf(stage);

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 text-slate-900 pb-20">
      
      {/* 2. TOP HEADER */}
      <header className="bg-slate-950 text-white px-8 py-4 flex items-center justify-between sticky top-0 z-50 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold tracking-tight">FLOWPILOT AI</h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-900/50 text-blue-400 border border-blue-800/50">DEMO MODE</span>
          </div>
          <p className="text-slate-400 text-sm mt-0.5">From business intent to completed action.</p>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 mr-4">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider cursor-pointer flex items-center gap-2">
              <input type="checkbox" checked={demoScriptMode} onChange={(e) => setDemoScriptMode(e.target.checked)} className="rounded bg-slate-800 border-slate-700 text-blue-500" />
              Demo Script Mode
            </label>
          </div>
          <div className="text-right">
            <div className="text-sm font-medium">Workflow: Invoice Resolution #{id.toUpperCase()}</div>
            <div className="text-xs text-slate-400 flex items-center gap-2 justify-end mt-1">
              {isRunning && <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />}
              {!isRunning && stage === 'COMPLETE' && <span className="w-2 h-2 rounded-full bg-green-500" />}
              {stage === 'IDLE' ? 'READY' : stage === 'COMPLETE' ? 'COMPLETED' : 'RUNNING'}
            </div>
          </div>
          <button onClick={resetDemo} className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg text-sm transition-colors border border-slate-700">
            <RotateCcw className="w-4 h-4" /> Reset Demo
          </button>
        </div>
      </header>

      <div className={clsx("flex flex-1", demoScriptMode ? "flex-row" : "flex-col")}>
      
      {/* SIDEBAR FOR DEMO SCRIPT MODE */}
      {demoScriptMode && (
        <aside className="w-64 bg-slate-900 border-r border-slate-800 p-6 flex-shrink-0 text-slate-300">
          <h2 className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-6">Demo Script</h2>
          <ul className="space-y-4 text-sm font-medium">
            <li className={clsx(stageIndex >= 0 ? "text-white" : "text-slate-600")}>① Start with objective</li>
            <li className={clsx(stageIndex >= 2 ? "text-white" : "text-slate-600")}>② Show generated plan</li>
            <li className={clsx(stageIndex >= 3 ? "text-white" : "text-slate-600")}>③ Show multi-source retrieval</li>
            <li className={clsx(stageIndex >= 5 ? "text-white" : "text-slate-600")}>④ Show AI prioritization</li>
            <li className={clsx(stageIndex >= 6 ? "text-white" : "text-slate-600")}>⑤ Open approval gateway</li>
            <li className={clsx(approvalsGranted ? "text-white" : "text-slate-600")}>⑥ Approve 3 actions</li>
            <li className={clsx(stageIndex >= 7 ? "text-white" : "text-slate-600")}>⑦ Start execution</li>
            <li className={clsx(stageIndex >= 8 ? "text-white" : "text-slate-600")}>⑧ Highlight INV-1004 failure</li>
            <li className={clsx(stageIndex >= 9 ? "text-white" : "text-slate-600")}>⑨ Show dynamic re-planning</li>
            <li className={clsx(stageIndex >= 10 ? "text-white" : "text-slate-600")}>⑩ Show successful recovery</li>
            <li className={clsx(stageIndex >= 10 ? "text-white" : "text-slate-600")}>⑪ Show final accounting</li>
            <li className={clsx(stageIndex >= 10 ? "text-white" : "text-slate-600")}>⑫ Open audit trail</li>
          </ul>
        </aside>
      )}

      <main className="max-w-6xl mx-auto w-full px-8 pt-8 flex flex-col gap-8 flex-1">
        
        {/* 3. BUSINESS OBJECTIVE CARD */}
        <section className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              Business Objective
              {stageIndex >= 1 && <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded font-mono font-medium">OBJECTIVE UNDERSTOOD ✓</span>}
            </h2>
            {stage === 'IDLE' && (
              <button onClick={runDemo} className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm flex items-center gap-2">
                <PlayCircle className="w-4 h-4" /> Run Demo Workflow
              </button>
            )}
          </div>
          <p className="text-slate-700 text-lg mb-6 border-l-4 border-blue-500 pl-4 py-1">
            "Find all overdue invoices above ₹50,000, analyze the customers, prioritize the cases, prepare follow-up actions, and execute approved actions."
          </p>
          
          {stageIndex >= 1 && (
            <div className="bg-slate-50 border border-slate-100 p-4 rounded-lg font-mono text-sm grid grid-cols-4 gap-4">
               <div><strong className="text-slate-500 block mb-1">Target:</strong>Overdue invoices</div>
               <div><strong className="text-slate-500 block mb-1">Threshold:</strong>₹50,000+</div>
               <div><strong className="text-slate-500 block mb-1">Required:</strong>Analyze → Prioritize → Act</div>
               <div><strong className="text-slate-500 block mb-1">Approval:</strong>Required for escalations</div>
            </div>
          )}
        </section>

        {/* 4. LIVE WORKFLOW PIPELINE */}
        {stageIndex >= 2 && (
          <section className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 overflow-hidden">
            <h2 className="text-sm font-bold text-slate-500 mb-6 uppercase tracking-wider">Orchestration Pipeline</h2>
            <div className="flex justify-between items-center relative">
              <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 h-0.5 bg-slate-100 z-0"></div>
              {['UNDERSTAND', 'PLAN', 'GATHER', 'ANALYZE', 'DECIDE', 'APPROVE', 'EXECUTE', 'VERIFY', 'REPLAN', 'COMPLETE'].map((s, i) => {
                const sIdx = i + 1;
                const isPast = stageIndex > sIdx;
                const isCurr = stageIndex === sIdx;
                return (
                  <div key={s} className="relative z-10 flex flex-col items-center gap-2 bg-white px-2">
                    <div className={clsx("w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-colors", 
                      isPast ? "bg-green-500 border-green-500 text-white" : 
                      isCurr ? "bg-blue-50 border-blue-500 text-blue-600" : "bg-white border-slate-200 text-slate-300"
                    )}>
                      {isCurr ? <Loader2 className="w-4 h-4 animate-spin" /> : isPast ? <CheckCircle className="w-4 h-4" /> : i+1}
                    </div>
                    <span className={clsx("text-[10px] font-bold tracking-wider", isCurr ? "text-blue-600" : isPast ? "text-slate-700" : "text-slate-400")}>{s}</span>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* 6. MULTI-SOURCE INTELLIGENCE PANEL */}
        {stageIndex >= 3 && (
          <section className="bg-slate-900 text-white rounded-xl shadow-sm p-6 border border-slate-800">
            <h2 className="text-lg font-semibold mb-6 text-slate-100 flex items-center gap-2"><Database className="w-5 h-5" /> Information Sources</h2>
            <div className="grid grid-cols-5 gap-4">
              <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                <div className="text-green-400 text-xs font-bold mb-2 flex items-center gap-1"><CheckCircle className="w-3 h-3"/> CONNECTED</div>
                <div className="font-semibold text-sm mb-1">Invoice Database</div>
                <div className="text-slate-400 text-xs">12 records retrieved</div>
              </div>
              <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                <div className="text-green-400 text-xs font-bold mb-2 flex items-center gap-1"><CheckCircle className="w-3 h-3"/> CONNECTED</div>
                <div className="font-semibold text-sm mb-1">Customer Database</div>
                <div className="text-slate-400 text-xs">6 records retrieved</div>
              </div>
              <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                <div className="text-green-400 text-xs font-bold mb-2 flex items-center gap-1"><CheckCircle className="w-3 h-3"/> CONNECTED</div>
                <div className="font-semibold text-sm mb-1">Communication History</div>
                <div className="text-slate-400 text-xs">9 records retrieved</div>
              </div>
              <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                <div className="text-green-400 text-xs font-bold mb-2 flex items-center gap-1"><CheckCircle className="w-3 h-3"/> CONNECTED</div>
                <div className="font-semibold text-sm mb-1">Payment Status</div>
                <div className="text-slate-400 text-xs">7 records retrieved</div>
              </div>
              <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                <div className="text-green-400 text-xs font-bold mb-2 flex items-center gap-1"><CheckCircle className="w-3 h-3"/> CONNECTED</div>
                <div className="font-semibold text-sm mb-1">Business Policies</div>
                <div className="text-slate-400 text-xs">8 rules retrieved</div>
              </div>
            </div>
          </section>
        )}

        {/* 7 & 8. AI ANALYSIS PANEL & CASE CLASSIFICATION */}
        {stageIndex >= 5 && (
          <div className="grid grid-cols-3 gap-6">
            <section className="col-span-1 bg-white border border-slate-200 rounded-xl shadow-sm p-6">
              <h2 className="text-sm font-bold text-slate-500 mb-6 uppercase tracking-wider">Case Classification</h2>
              <div className="text-3xl font-bold mb-1">7</div>
              <div className="text-sm text-slate-500 mb-6">Invoices evaluated</div>
              
              <div className="border border-slate-200 rounded-lg overflow-hidden">
                <div className="flex justify-between p-3 border-b border-slate-100 hover:bg-slate-50 cursor-pointer font-medium">
                  <span>Actionable</span>
                  <span className="bg-blue-100 text-blue-700 px-2 rounded">6</span>
                </div>
                <div className="flex justify-between p-3 hover:bg-slate-50 cursor-pointer text-slate-600">
                  <span>Monitoring</span>
                  <span className="bg-slate-100 text-slate-700 px-2 rounded">1</span>
                </div>
              </div>
            </section>

            <section className="col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm p-6">
              <h2 className="text-sm font-bold text-slate-500 mb-6 uppercase tracking-wider">Intelligent Decision Engine</h2>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-bold text-lg">INV-1001 <span className="text-sm font-normal text-slate-500 ml-2">Apex Manufacturing</span></h3>
                    <div className="flex gap-4 mt-2 text-sm">
                      <span className="text-red-600 font-semibold">₹185,000</span>
                      <span className="text-amber-600">47 days overdue</span>
                      <span className="text-slate-600">Risk: <strong className="text-red-500">HIGH</strong></span>
                      <span className="text-slate-600">Payment: NOT RECEIVED</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Approval Required</div>
                    <div className="bg-red-100 text-red-700 text-xs font-bold px-2 py-1 rounded">YES</div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-6 mt-6">
                  <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Recommended Action</h4>
                    <div className="font-medium text-slate-800">Escalation Follow-up</div>
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Decision Factors</h4>
                    <ul className="text-xs text-slate-600 space-y-1 list-disc pl-4">
                      <li>High invoice value (Rule 3)</li>
                      <li>47 days overdue</li>
                      <li>High customer risk</li>
                      <li>Previous reminders unresolved</li>
                    </ul>
                  </div>
                </div>
              </div>
            </section>
          </div>
        )}

        {/* 9. APPROVAL GATEWAY */}
        {stageIndex >= 6 && !approvalsGranted && (
          <section className="bg-amber-50 border-2 border-amber-200 rounded-xl shadow-sm p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-6 opacity-10"><ShieldCheck className="w-32 h-32 text-amber-500"/></div>
            <h2 className="text-xl font-bold text-amber-900 mb-2 relative z-10">Human Approval Required</h2>
            <p className="text-amber-700 mb-8 relative z-10 font-medium">3 actions require approval before the workflow can proceed.</p>
            
            <div className="grid grid-cols-3 gap-4 relative z-10">
              {/* Card 1 */}
              <div className="bg-white border border-amber-200 rounded-lg p-5 shadow-sm">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold">INV-1001</h3>
                  <span className="text-red-600 font-bold text-sm">₹185,000</span>
                </div>
                <div className="text-sm text-slate-600 mb-4">
                  <div>Escalation Email</div>
                  <div className="text-xs mt-1 text-slate-400">47 days overdue</div>
                </div>
                <div className="flex gap-2 text-xs">
                  <button className="flex-1 bg-amber-500 hover:bg-amber-600 text-white py-2 rounded font-bold transition-colors">Approve</button>
                  <button className="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-600 py-2 rounded font-bold transition-colors">Edit</button>
                </div>
              </div>
              
              {/* Card 2 */}
              <div className="bg-white border border-amber-200 rounded-lg p-5 shadow-sm">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold">INV-1004</h3>
                  <span className="text-red-600 font-bold text-sm">₹310,000</span>
                </div>
                <div className="text-sm text-slate-600 mb-4">
                  <div>Alt-contact escalation</div>
                  <div className="text-xs mt-1 text-slate-400">61 days overdue</div>
                </div>
                <div className="flex gap-2 text-xs">
                  <button className="flex-1 bg-amber-500 hover:bg-amber-600 text-white py-2 rounded font-bold transition-colors">Approve</button>
                  <button className="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-600 py-2 rounded font-bold transition-colors">Edit</button>
                </div>
              </div>

              {/* Card 3 */}
              <div className="bg-white border border-amber-200 rounded-lg p-5 shadow-sm">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold">INV-1006</h3>
                  <span className="text-red-600 font-bold text-sm">₹520,000</span>
                </div>
                <div className="text-sm text-slate-600 mb-4">
                  <div>Finance escalation</div>
                  <div className="text-xs mt-1 text-slate-400">71 days overdue</div>
                </div>
                <div className="flex gap-2 text-xs">
                  <button className="flex-1 bg-amber-500 hover:bg-amber-600 text-white py-2 rounded font-bold transition-colors">Approve</button>
                  <button className="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-600 py-2 rounded font-bold transition-colors">Edit</button>
                </div>
              </div>
            </div>
            
            <div className="mt-6 flex justify-end relative z-10">
               <button onClick={grantApprovals} className="bg-amber-600 hover:bg-amber-700 text-white px-6 py-3 rounded-lg font-bold shadow transition-colors flex items-center gap-2">
                 <CheckCircle className="w-5 h-5" /> Approve All Actions
               </button>
            </div>
          </section>
        )}

        {/* 10. EXECUTION MONITOR & 11, 12 RE-PLANNING */}
        {approvalsGranted && (
          <section className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <h2 className="text-sm font-bold text-slate-500 mb-6 uppercase tracking-wider">Action Execution Monitor</h2>
            
            <div className="grid grid-cols-2 gap-x-8 gap-y-4">
              <div className="flex items-center justify-between p-3 border-b border-slate-100">
                 <div>
                   <div className="font-bold text-sm">INV-1001</div>
                   <div className="text-xs text-slate-500">Escalation Email</div>
                 </div>
                 <div className="flex items-center gap-1 text-green-600 text-sm font-medium"><CheckCircle className="w-4 h-4" /> Successful</div>
              </div>
              
              <div className="flex items-center justify-between p-3 border-b border-slate-100">
                 <div>
                   <div className="font-bold text-sm">INV-1002</div>
                   <div className="text-xs text-slate-500">Schedule Follow-up</div>
                 </div>
                 <div className="flex items-center gap-1 text-green-600 text-sm font-medium"><CheckCircle className="w-4 h-4" /> Successful</div>
              </div>

              {/* FAIL SCENARIO FOR 1004 */}
              <div className="col-span-2 mt-4 mb-4">
                <div className="border border-red-200 bg-red-50 rounded-lg p-6 relative overflow-hidden">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <div className="font-bold text-lg text-red-900 flex items-center gap-2"><ShieldAlert className="w-5 h-5" /> INV-1004: Execution Attempt #1</div>
                      <div className="text-sm text-red-700 mt-1">Alternative Contact Escalation</div>
                    </div>
                    {stageIndex >= 8 && <div className="bg-red-600 text-white px-3 py-1 rounded text-sm font-bold">✕ FAILED</div>}
                  </div>
                  
                  {stageIndex >= 8 && (
                    <div className="mb-6 bg-white border border-red-100 p-4 rounded text-sm text-red-800">
                      <strong>Reason:</strong> Invalid primary email address (invalid@delta-logistics.example)
                    </div>
                  )}

                  {stageIndex >= 9 && (
                    <div className="border-t border-red-200 pt-6 mt-2">
                       <h3 className="font-bold text-purple-800 mb-4 text-center tracking-widest text-sm bg-purple-100 py-2 rounded uppercase border border-purple-200">Dynamic Re-Planning Initiated</h3>
                       
                       <div className="grid grid-cols-2 gap-8 text-sm">
                         <div className="opacity-50">
                           <div className="font-bold mb-3 text-slate-700 uppercase text-xs">Original Plan</div>
                           <div className="space-y-2 text-slate-600">
                             <div className="p-2 border rounded bg-white">1. Send email</div>
                             <div className="text-center text-xs">↓</div>
                             <div className="p-2 border rounded bg-white">2. Verify delivery</div>
                           </div>
                         </div>
                         <div>
                           <div className="font-bold mb-3 text-purple-900 uppercase text-xs">Revised Plan</div>
                           <div className="space-y-2">
                             <div className="p-2 border border-purple-200 rounded bg-white font-medium text-purple-900">1. Search customer records</div>
                             <div className="text-center text-xs text-purple-400">↓</div>
                             <div className="p-2 border border-purple-200 rounded bg-white font-medium text-purple-900">2. Find alternate verified contact</div>
                             <div className="text-center text-xs text-purple-400">↓</div>
                             <div className="p-2 border border-purple-200 rounded bg-white font-medium text-purple-900">3. Regenerate & Execute</div>
                           </div>
                         </div>
                       </div>
                       
                       {stageIndex >= 10 && (
                         <div className="mt-8 bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                           <div className="text-green-700 font-bold mb-1 flex items-center justify-center gap-2"><CheckCircle className="w-5 h-5"/> Alternate contact found</div>
                           <div className="text-sm font-mono text-green-800">finance@delta-logistics.example</div>
                           <div className="text-xs font-bold text-green-600 uppercase mt-3 tracking-wider">Revised execution successful</div>
                         </div>
                       )}
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex items-center justify-between p-3 border-b border-slate-100">
                 <div>
                   <div className="font-bold text-sm">INV-1005</div>
                   <div className="text-xs text-slate-500">Clarification Response</div>
                 </div>
                 <div className="flex items-center gap-1 text-green-600 text-sm font-medium"><CheckCircle className="w-4 h-4" /> Successful</div>
              </div>
              
              <div className="flex items-center justify-between p-3 border-b border-slate-100">
                 <div>
                   <div className="font-bold text-sm">INV-1006</div>
                   <div className="text-xs text-slate-500">Finance Escalation</div>
                 </div>
                 <div className="flex items-center gap-1 text-green-600 text-sm font-medium"><CheckCircle className="w-4 h-4" /> Successful</div>
              </div>
              
              <div className="flex items-center justify-between p-3 border-b border-slate-100">
                 <div>
                   <div className="font-bold text-sm">INV-1009</div>
                   <div className="text-xs text-slate-500">Standard Reminder</div>
                 </div>
                 <div className="flex items-center gap-1 text-green-600 text-sm font-medium"><CheckCircle className="w-4 h-4" /> Successful</div>
              </div>
            </div>
          </section>
        )}

        {/* 13 & 14. FINAL SUMMARY & AUDIT */}
        {stageIndex === 10 && (
          <div className="grid grid-cols-2 gap-6 mb-12">
            <section className="bg-slate-900 text-white border border-slate-800 rounded-xl shadow-sm p-6">
              <h2 className="text-sm font-bold text-slate-400 mb-6 uppercase tracking-wider text-center border-b border-slate-800 pb-4">Workflow Completed</h2>
              
              <div className="font-mono text-sm leading-relaxed max-w-sm mx-auto">
                <div className="flex justify-between py-1 border-b border-slate-800"><span className="text-slate-300">Invoices Analyzed</span><span className="font-bold text-green-400">7</span></div>
                <div className="flex justify-between py-1 border-b border-slate-800"><span className="text-slate-300">Actionable Cases</span><span className="font-bold text-green-400">6</span></div>
                <div className="flex justify-between py-1 border-b border-slate-800 mb-4"><span className="text-slate-300">Monitoring Cases</span><span className="font-bold text-slate-400">1</span></div>
                
                <div className="flex justify-between py-1 border-b border-slate-800"><span className="text-slate-300">Approval Requests</span><span className="font-bold text-amber-400">3</span></div>
                <div className="flex justify-between py-1 border-b border-slate-800 mb-4"><span className="text-slate-300">Approved</span><span className="font-bold text-amber-400">3</span></div>

                <div className="flex justify-between py-1 border-b border-slate-800"><span className="text-slate-300">Business Actions</span><span className="font-bold text-blue-400">6</span></div>
                <div className="flex justify-between py-1 border-b border-slate-800"><span className="text-slate-300">Execution Attempts</span><span className="font-bold text-slate-400">7</span></div>
                <div className="flex justify-between py-1 border-b border-slate-800"><span className="text-slate-300">Successful Actions</span><span className="font-bold text-blue-400">6</span></div>
                <div className="flex justify-between py-1 border-b border-slate-800"><span className="text-slate-300">Failed Attempts</span><span className="font-bold text-red-400">1</span></div>
                <div className="flex justify-between py-1 border-b border-slate-800"><span className="text-slate-300">Recovered Failures</span><span className="font-bold text-purple-400">1</span></div>
                <div className="flex justify-between py-1 border-b border-slate-800 mb-4"><span className="text-slate-300">Dynamic Re-plans</span><span className="font-bold text-purple-400">1</span></div>

                <div className="flex justify-between py-1"><span className="text-slate-300">Unresolved</span><span className="font-bold text-slate-500">0</span></div>
              </div>
              
              <div className="mt-8 text-center text-xs text-slate-500 italic">
                The workflow adapted to a real execution failure instead of stopping.
              </div>
              
              <div className="mt-8 pt-6 border-t border-slate-800">
                <button onClick={() => setShowWhatHappened(!showWhatHappened)} className="w-full bg-slate-800 hover:bg-slate-700 py-2 rounded text-sm font-bold text-slate-300 transition-colors">
                  What just happened? {showWhatHappened ? '▲' : '▼'}
                </button>
                {showWhatHappened && (
                  <div className="mt-4 text-xs font-mono text-slate-400 space-y-1 bg-slate-950 p-4 rounded border border-slate-800">
                    <p>1. The system interpreted the business objective.</p>
                    <p>2. It generated an execution plan.</p>
                    <p>3. It gathered information from multiple sources.</p>
                    <p>4. It evaluated business policies and customer context.</p>
                    <p>5. It classified 7 invoices.</p>
                    <p>6. It requested approval for 3 sensitive actions.</p>
                    <p>7. It executed the approved workflow.</p>
                    <p>8. INV-1004 failed because of an invalid contact.</p>
                    <p>9. The system detected the failure.</p>
                    <p>10. It searched for an alternate contact.</p>
                    <p>11. It re-planned the execution.</p>
                    <p>12. The revised action succeeded.</p>
                    <p>13. The workflow was verified and completed.</p>
                    <p>14. Every major event was recorded in the audit trail.</p>
                  </div>
                )}
              </div>
            </section>

            <section className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 overflow-hidden flex flex-col h-[500px]">
              <h2 className="text-sm font-bold text-slate-500 mb-4 uppercase tracking-wider flex items-center gap-2"><History className="w-4 h-4"/> Audit Trail</h2>
              <div className="flex-1 overflow-y-auto pr-4 text-xs font-mono space-y-3">
                {logs.map((log, i) => (
                  <div key={i} className="flex gap-4 border-l-2 border-slate-200 pl-4 py-1">
                    <div className="text-slate-400 w-20 shrink-0">{log.time}</div>
                    <div className={clsx(
                      "flex-1 font-medium",
                      log.message.includes('FAILED') ? 'text-red-600' :
                      log.message.includes('RE-PLANNED') ? 'text-purple-600' :
                      log.message.includes('APPROVALS') ? 'text-amber-600' :
                      'text-slate-700'
                    )}>
                      {log.message}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}

      </main>
      </div>
    </div>
  );
}
