import pandas as pd

def check_bank_reconciliation(invoice_id, csv_path="data/bank_statements.csv"):
    """
    Search CSV using pandas for pending/completed payments related to the given invoice_id.
    """
    try:
        df = pd.read_csv(csv_path)
        # Check if the invoice_id is in the description
        matched = df[df['description'].str.contains(invoice_id, case=False, na=False)]
        
        if not matched.empty:
            return {
                "reconciled": True,
                "transactions": matched.to_dict(orient='records')
            }
        else:
            return {
                "reconciled": False,
                "transactions": []
            }
    except Exception as e:
        return {"error": str(e)}
