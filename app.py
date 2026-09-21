import streamlit as st
import pandas as pd
import json
from agents.orchestrator import Orchestrator
from tools.communication_tools import send_approved_email
from utils.audit_logger import AuditLogger
import os

st.set_page_config(page_title="Workflow Automation Prototype", layout="wide")
logger = AuditLogger()

st.title("Autonomous Business Workflow Automation Prototype")
st.subheader("Accounts Receivable & Payment Recovery")

if 'workflow_results' not in st.session_state:
    st.session_state.workflow_results = None

# ---- Control Panel ----
st.markdown("### Control Panel")
if st.button("Run Autonomous Recovery Workflow"):
    with st.spinner("Agents are analyzing data and planning recovery..."):
        orchestrator = Orchestrator()
        results = orchestrator.run_workflow()
        st.session_state.workflow_results = results
        st.success("Workflow execution completed!")

# ---- Live Progress & State Graph ----
# For simplicity, we just display the current stage textually, but this could be a dynamic graph.
st.markdown("---")
st.markdown("### Execution State")
if st.session_state.workflow_results:
    st.info("State: VERIFICATION_AND_APPROVAL_GATEWAY")
else:
    st.info("State: IDLE")

# ---- Interactive HITL Approval Gateway ----
if st.session_state.workflow_results:
    st.markdown("---")
    st.markdown("### Human-in-the-Loop (HITL) Approval Gateway")
    
    for idx, item in enumerate(st.session_state.workflow_results):
        status = item.get("status")
        invoice_id = item.get("invoice_id")
        
        with st.expander(f"Invoice: {invoice_id} - Status: {status}", expanded=True):
            if status == "RESOLVED_INTERNALLY":
                st.success(f"No action required. Reason: {item.get('reason')}")
            
            elif status == "FAILED":
                st.error(f"Workflow failed. Reason: {item.get('reason')}")
                
            elif status == "DRAFT_READY":
                draft = item.get("draft", {})
                requires_hitl = item.get("requires_hitl", False)
                hitl_reason = item.get("hitl_reason", "")
                
                if requires_hitl:
                    st.warning(f"Requires Approval: {hitl_reason}")
                
                # Editable draft
                edited_subject = st.text_input("Subject", value=draft.get("subject", ""), key=f"subj_{idx}")
                edited_body = st.text_area("Body", value=draft.get("body", ""), key=f"body_{idx}")
                
                col1, col2, col3 = st.columns([1, 1, 4])
                if col1.button("Approve & Send", key=f"approve_{idx}"):
                    # Send action
                    resp = send_approved_email(draft.get("email_id"))
                    logger.log_event("Human", "Approved Email", {"email_id": draft.get("email_id")})
                    st.success("Email sent successfully!")
                
                if col2.button("Reject", key=f"reject_{idx}"):
                    logger.log_event("Human", "Rejected Email", {"email_id": draft.get("email_id")})
                    st.error("Email draft rejected.")

# ---- Audit Log Panel ----
st.markdown("---")
st.markdown("### Audit Log Viewer")
if st.button("Refresh Logs"):
    pass # Re-runs the script to reload logs

logs = logger.get_logs()
if logs:
    with st.expander("View JSON Audit Logs"):
        # Sort logs descending
        logs.reverse()
        for log in logs:
            st.json(log)
else:
    st.write("No logs available yet.")
