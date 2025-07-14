# utils/rag_engine.py

import os
import fitz  # PyMuPDF
import pandas as pd
from docx import Document
from sentence_transformers import SentenceTransformer, util

# Actual file/folder mappings from your data/
USECASE_DOC_PATHS = {
    "Investment (non-sharemarket)": [
        "data/usecases/Invest(non sharemarket)/HDFC FD.docx"
    ],
    "Documentation & Process Query": [
        "data/usecases/Document and Process Query/HomeLoanDocandProcess.docx",
        "data/usecases/Document and Process Query/Credit Card.pdf",
        "data/usecases/Document and Process Query/Credit_Card_Info.pdf"
    ],
    "Loan Prepurchase Query": [
        "data/usecases/Loan Purchase query/HomeLoanDocandProcess.docx"
    ],
    "Banking Norms": [
        "data/usecases/BankingNorms/Hdfc",  # folder with 14 PDFs
        "data/usecases/BankingNorms/Rbi"    # folder with 13 PDFs
    ],
    "Fraud Complaint - Scenario": [
        "data/usecases/FraudSafety/FraudComplaint.docx",
        "data/usecases/FraudSafety/FraudSafety.docx",
        "data/usecases/FraudSafety/Master Directions on Cyber Resilience and Digital Payment Security Controls for non-bank Payment System Operators.pdf",
        "data/usecases/FraudSafety/Master Directions on Fraud Risk Management in Urban Cooperative Banks (UCBs)  State Cooperative Banks (StCBs) Central Cooperative Banks (CCBs).pdf",
        "data/usecases/FraudSafety/Master Directions on Fraud Risk Management in Urban Cooperative Banks (UCBs) State Cooperative Banks (StCBs) Central Cooperative Banks (CCBs).pdf"
    ],
    "KYC & Details Update": [
        "data/usecases/KYCand Details update/KNOW YOUR CUSTOMER (KYC) NORMS.pdf",
        "data/usecases/KYCand Details update/KYCupdatelinks.docx"
    ],
    "Download Statement & Document": [
        "data/usecases/Download doc&statements/Download Statement and Documents.docx"
    ],
    "Mutual Funds & Tax Benefits": [
        "data/usecases/MutualFund&TaxBenifit/Debt Funds May.xlsx",
        "data/usecases/MutualFund&TaxBenifit/Equity Funds May.xlsx",
        "data/usecases/MutualFund&TaxBenifit/Hybrid funds May.xlsx",
        "data/usecases/MutualFund&TaxBenifit/Other Schemes-ETF Funds May.xlsx",
        "data/usecases/MutualFund&TaxBenifit/Other Schemes-Fund of Funds May.xlsx",
        "data/usecases/MutualFund&TaxBenifit/Other Schemes-Index Funds May.xlsx",
        "data/usecases/MutualFund&TaxBenifit/Solution Oriented Funds May.xlsx"
    ]
}

model = SentenceTransformer("all-MiniLM-L6-v2")  # For semantic matching

def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join(para.text.strip() for para in doc.paragraphs if para.text.strip())

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_xlsx(path):
    try:
        dfs = pd.read_excel(path, sheet_name=None)
        text_parts = []
        for name, df in dfs.items():
            preview = df.head(5).to_string(index=False)
            text_parts.append(f"📄 Sheet: {name}\n{preview}")
        return "\n\n".join(text_parts)
    except Exception as e:
        return f"⚠️ Failed to read Excel file {os.path.basename(path)}: {e}"

def load_documents_for_use_case(use_case):
    if use_case not in USECASE_DOC_PATHS:
        return "⚠️ No documents configured for this use case."

    all_text = []
    paths = USECASE_DOC_PATHS[use_case]

    for path in paths:
        if os.path.isdir(path):
            for file in sorted(os.listdir(path)):
                full_path = os.path.join(path, file)
                try:
                    if file.endswith(".pdf"):
                        all_text.append(extract_text_from_pdf(full_path))
                    elif file.endswith(".docx"):
                        all_text.append(extract_text_from_docx(full_path))
                    elif file.endswith(".xlsx"):
                        all_text.append(extract_text_from_xlsx(full_path))
                except Exception as e:
                    all_text.append(f"⚠️ Failed to load {file}: {e}")
        else:
            try:
                if path.endswith(".pdf"):
                    all_text.append(extract_text_from_pdf(path))
                elif path.endswith(".docx"):
                    all_text.append(extract_text_from_docx(path))
                elif path.endswith(".xlsx"):
                    all_text.append(extract_text_from_xlsx(path))
            except Exception as e:
                all_text.append(f"⚠️ Failed to load {path}: {e}")

    if not all_text:
        return "⚠️ No retrievable content found."

    return "\n---\n".join(all_text)[:3000]  # Trimmed to fit Gemini context

def find_best_document(query):
    """
    R&D Prototype: Return document text most semantically similar to the query.
    """
    best_doc = ""
    best_score = -1.0
    query_emb = model.encode(query, convert_to_tensor=True)

    for use_case, paths in USECASE_DOC_PATHS.items():
        for path in paths:
            if os.path.isfile(path):
                if path.endswith(".pdf"):
                    text = extract_text_from_pdf(path)
                elif path.endswith(".docx"):
                    text = extract_text_from_docx(path)
                elif path.endswith(".xlsx"):
                    text = extract_text_from_xlsx(path)
                else:
                    continue

                if not text.strip():
                    continue

                doc_emb = model.encode(text[:1000], convert_to_tensor=True)
                score = util.cos_sim(query_emb, doc_emb).item()
                if score > best_score:
                    best_score = score
                    best_doc = text

    return best_doc if best_doc else None
