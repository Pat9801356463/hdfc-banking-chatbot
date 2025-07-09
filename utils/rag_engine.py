# utils/rag_engine.py

import os
import fitz  # PyMuPDF
from docx import Document

USECASE_DOC_PATHS = {
    "Investment (non-sharemarket)": ["data/usecases/Investment_Suggestion/sip_guidelines.docx"],
    "Documentation & Process Query": [
        "data/usecases/Documentation_Process/loan_process.docx",
        "data/usecases/Documentation_Process/credit_card_terms_1.pdf",
        "data/usecases/Documentation_Process/credit_card_terms_2.pdf"
    ],
    "Loan Prepurchase Query": ["data/usecases/Documentation_Process/loan_process.docx"],
    "Banking Norms": [
        "data/usecases/BankingNorms/Hdfc/",  # folder with 14 PDFs
        "data/usecases/BankingNorms/Rbi/"    # folder with 13 PDFs
    ],
    "Fraud Complaint - Scenario": [
        "data/usecases/Fraud_Safety/fraud_process.docx",
        "data/usecases/Fraud_Safety/rules.pdf",
        "data/usecases/Fraud_Safety/safety1.pdf",
        "data/usecases/Fraud_Safety/safety2.pdf"
    ],
    "KYC & Details Update": [
        "data/usecases/KYC_Details/kyc_norms.pdf",
        "data/usecases/KYC_Details/kyc_urls.docx"
    ]
}

def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join(para.text.strip() for para in doc.paragraphs if para.text.strip())

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def load_documents_for_use_case(use_case):
    if use_case not in USECASE_DOC_PATHS:
        return "⚠️ No documents configured for this use case."

    all_text = []
    paths = USECASE_DOC_PATHS[use_case]

    for path in paths:
        if os.path.isdir(path):
            for file in os.listdir(path):
                full_path = os.path.join(path, file)
                if file.endswith(".pdf"):
                    all_text.append(extract_text_from_pdf(full_path))
        elif path.endswith(".docx"):
            all_text.append(extract_text_from_docx(path))
        elif path.endswith(".pdf"):
            all_text.append(extract_text_from_pdf(path))

    if not all_text:
        return "⚠️ No retrievable content found."

    # Optionally limit to top N characters
    return "\n---\n".join(all_text)[:3000]  # trim for Gemini prompt size
