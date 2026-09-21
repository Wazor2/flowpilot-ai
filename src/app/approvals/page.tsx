import { CheckCircle, XCircle } from 'lucide-react';
import Link from 'next/link';

export default function Approvals() {
  return (
    <div className="max-w-6xl mx-auto w-full">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Approvals Gateway</h1>
          <p className="text-slate-500 mt-1">Review actions requiring Human-in-the-Loop authorization.</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
          <div className="font-medium text-slate-700">Pending Requests (1)</div>
        </div>
        
        <div className="divide-y divide-slate-100">
          {/* Sample Approval Request */}
          <div className="p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <span className="bg-amber-100 text-amber-800 text-xs font-semibold px-2 py-0.5 rounded-full">High Priority</span>
                  <span className="text-sm text-slate-500">Workflow: <Link href="/workflows/demo-123" className="text-blue-600 hover:underline">Overdue Invoice Resolution</Link></span>
                </div>
                <h3 className="text-lg font-semibold text-slate-900">Approve Communication Drafts</h3>
              </div>
              <div className="text-sm text-slate-400">10 mins ago</div>
            </div>
            
            <div className="bg-slate-50 p-4 rounded-lg border border-slate-100 mb-6">
              <h4 className="font-medium text-sm text-slate-700 mb-3">Proposed Action Summary:</h4>
              <ul className="text-sm text-slate-600 space-y-2 list-disc pl-4 mb-4">
                <li>Send overdue reminder for INV-1042 (Amount: ₹185,000) to John Smith.</li>
                <li>Customer risk level is classified as HIGH.</li>
              </ul>
              
              <div className="bg-white border p-3 rounded text-sm text-slate-700 font-mono">
                <strong>Subject:</strong> Payment follow-up — Invoice INV-1042<br/><br/>
                Dear Finance Team,<br/><br/>
                This is a follow-up regarding invoice INV-1042 which is currently overdue.<br/><br/>
                Please arrange for payment as soon as possible.
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <button className="px-4 py-2 border border-slate-200 text-slate-600 hover:bg-slate-50 rounded-lg font-medium transition-colors flex items-center gap-2">
                <XCircle className="w-4 h-4" />
                Reject & Edit
              </button>
              <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2 shadow-sm">
                <CheckCircle className="w-4 h-4" />
                Approve & Execute
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
