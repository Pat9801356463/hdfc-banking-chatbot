# utils/session_manager.py
import json
import pandas as pd

def load_user_session(user_id, users_json_path="data/users.json", txn_folder="data/transactions"):
    with open(users_json_path) as f:
        users = json.load(f)

    user = users.get(user_id)
    if not user:
        return None, "❌ User not found."

    try:
        df = pd.read_csv(f"{txn_folder}/{user['file']}", parse_dates=["Date"])
    except FileNotFoundError:
        return None, f"⚠️ Transactions not found for user {user['name']}."

    session = {
        "user_id": user_id,
        "name": user["name"],
        "transactions": df,
        "memory": []  # Memory initialized here
    }
    return session, f"👋 Hello, {user['name']}! How may I help you today?"
