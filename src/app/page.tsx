"use client";

import { Activity, CheckCircle, AlertCircle, Clock, Workflow, RotateCcw, ArrowRight, Server, Zap, Database, PlayCircle } from 'lucide-react';
import Link from 'next/link';
import { useState, useEffect } from 'react';

const defaultMetrics = {
  invoices_analyzed: 0,
  actionable_cases: 0,
  monitoring_cases: 0,
  approval_requests: 0,
  approved: 0,
  rejected: 0,
  business_actions: 0,
  successful_actions: 0,
  failed_attempts: 0,
  recovered_failures: 0,
  replans: 0,
  unresolved: 0
};

export default function Dashboard() {
  const [metrics, setMetrics] = useState(defaultMetrics);
  const [isDemoCompleted, setIsDemoCompleted] = useState(false);

  useEffect(() => {
    const demoRun = localStorage.getItem('demoCompleted');
    if (demoRun === 'true') {
      setIsDemoCompleted(true);
      setMetrics({
        invoices_analyzed: 7,
        actionable_cases: 6,
        monitoring_cases: 1,
        approval_requests: 3,
        approved: 3,
        rejected: 0,
        business_actions: 6,
        successful_actions: 6,
        failed_attempts: 1,
        recovered_failures: 1,
        replans: 1,
        unresolved: 0
      });
    }
  }, []);

  const resetDemo = () => {
    localStorage.removeItem('demoCompleted');
    setIsDemoCompleted(false);
    setMetrics(defaultMetrics);
    alert("Demo reset successfully. Database and state restored.");
  };

  return (
    <div className="flex flex-col gap-12 w-full max-w-6xl mx-auto pb-24">
      
      {/* 2. LANDING / DASHBOARD HERO */}
      <section className="bg-slate-950 text-white rounded-3xl p-12 relative overflow-hidden mt-6 shadow-xl border border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 to-purple-900/20 pointer-events-none"></div>
        <div className="relative z-10 max-w-2xl">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4">FLOWPILOT AI</h1>
          <p className="text-xl md:text-2xl font-light text-slate-300 mb-6">From business intent<br/>to completed action.</p>
          <p className="text-slate-400 mb-8 max-w-xl leading-relaxed">
            Turn natural-language business objectives into intelligent, adaptive workflows. Not a chatbot. An AI-powered workflow orchestration and execution system.
          </p>
          
          <div className="flex flex-wrap gap-4 items-center mb-10">
            <Link href="/workflows/demo-123" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-bold transition-all shadow-lg shadow-blue-900/50 flex items-center gap-2">
              <PlayCircle className="w-5 h-5" /> Run Demo Workflow
            </Link>
            {isDemoCompleted && (
               <Link href="/audit" className="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white px-6 py-3 rounded-xl font-medium transition-colors">
                 View Audit Trail
               </Link>
            )}
            <button onClick={resetDemo} className="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white px-4 py-3 rounded-xl font-medium transition-colors flex items-center gap-2">
              <RotateCcw className="w-4 h-4" /> Reset Demo
            </button>
          </div>
          
          <div className="flex flex-wrap gap-x-6 gap-y-2 text-xs font-bold text-slate-500 tracking-wider">
            <span>AI PLANNING</span> •
            <span>MULTI-SOURCE REASONING</span> •
            <span>HUMAN APPROVAL</span> •
            <span>DYNAMIC RE-PLANNING</span> •
            <span>AUDIT TRAIL</span> •
            <span>TOOL EXECUTION</span>
          </div>
        </div>
      </section>

      {/* 3. DASHBOARD KPI AREA */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold tracking-tight">Live Workflow Metrics</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            { label: 'Invoices Analyzed', value: metrics.invoices_analyzed, color: 'text-slate-900' },
            { label: 'Actionable Cases', value: metrics.actionable_cases, color: 'text-blue-600' },
            { label: 'Approval Requests', value: metrics.approval_requests, color: 'text-amber-600' },
            { label: 'Successful Actions', value: metrics.successful_actions, color: 'text-green-600' },
            { label: 'Recovered Failures', value: metrics.recovered_failures, color: 'text-purple-600' },
            { label: 'Re-plans', value: metrics.replans, color: 'text-purple-600' }
          ].map(kpi => (
            <div key={kpi.label} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm text-center">
              <div className="text-sm font-medium text-slate-500 mb-2">{kpi.label}</div>
              <div className={`text-3xl font-extrabold ${kpi.color}`}>{kpi.value}</div>
            </div>
          ))}
        </div>
      </section>

      {/* 9. DEMO WORKFLOW CARD */}
      <section className="bg-blue-50 border border-blue-100 rounded-2xl p-8">
        <h2 className="text-lg font-bold text-blue-900 mb-2">Demo: Overdue Invoice Resolution</h2>
        <p className="text-blue-800/80 mb-6 max-w-3xl">Identify overdue invoices above ₹50,000, analyze customer context, prioritize cases, prepare actions, obtain required approvals, execute them, and recover automatically from execution failures.</p>
        
        <div className="flex flex-wrap items-center gap-2 text-sm font-medium text-blue-900">
           <span className="bg-white px-3 py-1 rounded-full border border-blue-200">12 invoices</span> <ArrowRight className="w-4 h-4 opacity-50"/>
           <span className="bg-white px-3 py-1 rounded-full border border-blue-200">7 matching</span> <ArrowRight className="w-4 h-4 opacity-50"/>
           <span className="bg-white px-3 py-1 rounded-full border border-blue-200">6 actionable</span> <ArrowRight className="w-4 h-4 opacity-50"/>
           <span className="bg-white px-3 py-1 rounded-full border border-amber-200 text-amber-800">3 approvals</span> <ArrowRight className="w-4 h-4 opacity-50"/>
           <span className="bg-white px-3 py-1 rounded-full border border-blue-200">6 business actions</span> <ArrowRight className="w-4 h-4 opacity-50"/>
           <span className="bg-white px-3 py-1 rounded-full border border-red-200 text-red-800">1 intentional failure</span> <ArrowRight className="w-4 h-4 opacity-50"/>
           <span className="bg-white px-3 py-1 rounded-full border border-purple-200 text-purple-800">1 dynamic re-plan</span> <ArrowRight className="w-4 h-4 opacity-50"/>
           <span className="bg-white px-3 py-1 rounded-full border border-green-200 text-green-800">6 successful actions</span>
        </div>
      </section>

      {/* 4. WHY FLOWPILOT? */}
      <section>
        <h2 className="text-2xl font-bold mb-8 text-center">From Static Automation to Adaptive Execution</h2>
        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-white border border-slate-200 rounded-xl p-8 shadow-sm text-center">
            <h3 className="text-sm font-bold tracking-widest text-slate-400 mb-6 uppercase">Traditional Automation</h3>
            <div className="flex flex-col items-center gap-3 text-sm font-medium text-slate-600">
               <div className="px-4 py-2 border rounded w-48 bg-slate-50">Fixed rules</div> ↓
               <div className="px-4 py-2 border rounded w-48 bg-slate-50">Fixed sequence</div> ↓
               <div className="px-4 py-2 border rounded w-48 bg-slate-50">Execute</div> ↓
               <div className="px-4 py-2 border border-red-200 bg-red-50 text-red-700 w-48">Failure</div> ↓
               <div className="px-4 py-2 border border-amber-200 bg-amber-50 text-amber-700 w-48">Manual intervention</div>
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-sm text-center text-slate-300">
            <h3 className="text-sm font-bold tracking-widest text-blue-400 mb-6 uppercase">FlowPilot AI</h3>
            <div className="flex flex-col items-center gap-2 text-sm font-medium">
               <div className="px-4 py-1.5 border border-slate-700 rounded w-48 bg-slate-800 text-white">Business Objective</div> ↓
               <div className="px-4 py-1.5 border border-slate-700 rounded w-48 bg-slate-800">Understand</div> ↓
               <div className="px-4 py-1.5 border border-slate-700 rounded w-48 bg-slate-800">Plan & Gather</div> ↓
               <div className="px-4 py-1.5 border border-slate-700 rounded w-48 bg-slate-800">Reason</div> ↓
               <div className="px-4 py-1.5 border border-slate-700 rounded w-48 bg-slate-800">Execute</div> ↓
               <div className="px-4 py-1.5 border border-purple-800 rounded w-48 bg-purple-900/30 text-purple-300">Observe & Re-plan</div> ↓
               <div className="px-4 py-1.5 border border-green-800 rounded w-48 bg-green-900/30 text-green-400">Recover & Complete</div>
            </div>
          </div>
        </div>
      </section>

      {/* 5. CORE CAPABILITIES */}
      <section>
        <h2 className="text-2xl font-bold mb-8 text-center">Core Capabilities</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            { id: '01', title: 'Objective Understanding', desc: 'Converts natural-language business goals into structured workflow requirements.' },
            { id: '02', title: 'Adaptive Planning', desc: 'Creates multi-step execution plans and changes them when conditions change.' },
            { id: '03', title: 'Multi-Source Intelligence', desc: 'Combines information from invoices, customer records, payment status, and policies.' },
            { id: '04', title: 'Intelligent Decisions', desc: 'Uses business context, customer history, and financial factors to determine actions.' },
            { id: '05', title: 'Human-in-the-Loop', desc: 'Pauses sensitive and high-value actions for explicit human approval.' },
            { id: '06', title: 'Failure Recovery', desc: 'Detects failed execution, searches for alternatives, dynamically re-plans, and continues.' }
          ].map(cap => (
            <div key={cap.id} className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
              <div className="text-2xl font-bold text-blue-100 mb-2">{cap.id}</div>
              <h3 className="font-bold text-slate-800 mb-2">{cap.title}</h3>
              <p className="text-sm text-slate-600 leading-relaxed">{cap.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 6 & 7. ARCHITECTURE & TECH STACK */}
      <section className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-slate-50 border border-slate-200 rounded-2xl p-8 font-mono text-xs md:text-sm text-slate-600 overflow-x-auto shadow-inner">
          <h3 className="font-sans font-bold text-lg text-slate-800 mb-6">System Architecture</h3>
          <pre className="leading-[1.15]">
{`                 USER
                  │
                  ▼
        NATURAL LANGUAGE OBJECTIVE
                  │
                  ▼
        ┌──────────────────────┐
        │ OBJECTIVE UNDERSTAND │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   AI PLANNER         │
        │ LangGraph Workflow   │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ WORKFLOW VERIFIER    │
        └──────────┬───────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
      TOOL LAYER       POLICY LAYER
          │                 │
          ├───────┬─────────┤
          ▼       ▼         ▼
      Invoice  Customer  Communication
          │       │         │
          └───────┴─────────┘
                  │
                  ▼
          DECISION ENGINE
                  │
                  ▼
          HUMAN APPROVAL
                  │
                  ▼
          ACTION EXECUTION
                  │
                  ▼
             OBSERVE
                  │
             ┌────┴────┐
             │         │
           SUCCESS   FAILURE
             │         │
             ▼         ▼
          VERIFY     REPLAN
             │         │
             └────┬────┘
                  ▼
             COMPLETION`}
          </pre>
        </div>
        
        <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm">
          <h3 className="font-bold text-lg text-slate-800 mb-6">Technology Stack</h3>
          <div className="space-y-6">
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Frontend</h4>
              <div className="text-sm font-medium text-slate-700">Next.js, React, TypeScript, Tailwind CSS, Lucide</div>
            </div>
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">AI / Orchestration</h4>
              <div className="text-sm font-medium text-slate-700">LangGraph, LLM Abstraction, Zod</div>
            </div>
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Backend / Data</h4>
              <div className="text-sm font-medium text-slate-700">Workflow State, Audit Events (Simulated)</div>
            </div>
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Tools</h4>
              <div className="text-sm font-medium text-slate-700">Invoice Tool, Customer Tool, Communication Tool, Policy Tool</div>
            </div>
          </div>
        </div>
      </section>

      {/* 8. PRIMARY DEMO CTA */}
      <section className="bg-blue-600 text-white rounded-2xl p-12 text-center shadow-xl shadow-blue-900/20 mt-8">
        <h2 className="text-3xl font-bold mb-4">READY TO SEE IT IN ACTION?</h2>
        <p className="text-blue-100 mb-8 max-w-xl mx-auto">Run the overdue invoice resolution workflow and watch the adaptive execution engine gather context, request approval, and recover from simulated failure.</p>
        <Link href="/workflows/demo-123" className="inline-flex items-center gap-2 bg-white text-blue-700 hover:bg-slate-50 px-8 py-4 rounded-xl font-bold text-lg transition-colors shadow-lg">
          <PlayCircle className="w-6 h-6" /> RUN LIVE DEMO
        </Link>
      </section>
    </div>
  );
}
