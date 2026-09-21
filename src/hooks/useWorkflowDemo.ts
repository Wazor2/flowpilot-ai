import { useState, useEffect } from 'react';

export type DemoStage = 
  | 'IDLE'
  | 'UNDERSTAND'
  | 'PLAN'
  | 'GATHER'
  | 'ANALYZE'
  | 'DECIDE'
  | 'APPROVE'
  | 'EXECUTE'
  | 'VERIFY'
  | 'REPLAN'
  | 'COMPLETE';

export function useWorkflowDemo() {
  const [stage, setStage] = useState<DemoStage>('IDLE');
  const [approvalsGranted, setApprovalsGranted] = useState(false);
  const [logs, setLogs] = useState<{ time: string, message: string }[]>([]);

  const addLog = (msg: string) => {
    setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), message: msg }]);
  };

  const runDemo = () => {
    setStage('UNDERSTAND');
    addLog('OBJECTIVE RECEIVED: Resolve high-value overdue invoices.');
    
    setTimeout(() => {
      setStage('PLAN');
      addLog('PLAN GENERATED: Adaptive workflow initialized.');
    }, 1200);

    setTimeout(() => {
      setStage('GATHER');
      addLog('DATA RETRIEVED: Queried Database, Customers, Policies.');
    }, 2500);

    setTimeout(() => {
      setStage('ANALYZE');
      addLog('CUSTOMER CONTEXT ANALYZED: Evaluated 7 overdue invoices.');
    }, 4000);

    setTimeout(() => {
      setStage('DECIDE');
      addLog('POLICIES EVALUATED: Case classification and recommendations completed.');
    }, 5500);

    setTimeout(() => {
      setStage('APPROVE');
      addLog('3 APPROVALS REQUESTED: High priority cases require human authorization.');
    }, 7000);
  };

  const grantApprovals = () => {
    setApprovalsGranted(true);
    addLog('3 APPROVALS RECEIVED: Human authorization granted.');
    setStage('EXECUTE');

    setTimeout(() => {
      addLog('ACTIONS EXECUTED: Dispatching communications.');
    }, 1000);

    setTimeout(() => {
      setStage('VERIFY');
      addLog('INV-1004 FAILED: Invalid primary email address.');
    }, 2500);

    setTimeout(() => {
      addLog('FAILURE DETECTED: Workflow cannot continue using the current execution path.');
      setStage('REPLAN');
    }, 3500);

    setTimeout(() => {
      addLog('WORKFLOW RE-PLANNED: Initiated recovery strategy.');
    }, 5000);

    setTimeout(() => {
      addLog('ALTERNATE CONTACT FOUND: Extracted secondary email from customer records.');
    }, 6500);

    setTimeout(() => {
      addLog('ACTION RECOVERED: Revised email dispatched successfully.');
      setStage('COMPLETE');
      addLog('WORKFLOW VERIFIED: Final audit logged.');
      addLog('WORKFLOW COMPLETED: Objective achieved.');
      localStorage.setItem('demoCompleted', 'true');
    }, 8500);
  };

  const resetDemo = () => {
    setStage('IDLE');
    setApprovalsGranted(false);
    setLogs([]);
    localStorage.removeItem('demoCompleted');
  };

  return {
    stage,
    logs,
    approvalsGranted,
    runDemo,
    grantApprovals,
    resetDemo
  };
}
