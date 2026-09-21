import os
import PyPDF2
import re

def search_crm_pdf_notes(customer_name, notes_dir="data/customer_notes"):
    """
    Fallback parser to extract missing contact emails from PDFs for a given customer name.
    """
    try:
        if not os.path.exists(notes_dir):
            return {"error": "Notes directory not found"}
            
        for filename in os.listdir(notes_dir):
            if filename.endswith(".pdf"):
                file_path = os.path.join(notes_dir, filename)
                
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                        
                    # Check if the customer name is in the text
                    if customer_name.lower() in text.lower():
                        # Extract email using regex
                        email_match = re.search(r'Email:\s*([\w\.-]+@[\w\.-]+)', text)
                        if email_match:
                            return {
                                "found": True,
                                "email": email_match.group(1),
                                "source": filename
                            }
                            
        return {"found": False, "email": None}
    except Exception as e:
        return {"error": str(e)}
