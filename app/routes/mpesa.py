from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.mpesa_transaction import MpesaTransaction
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64
import requests
import datetime

mpesa_bp = Blueprint("mpesa", __name__)

def _mpesa_get_access_token():
    key = current_app.config.get("MPESA_CONSUMER_KEY", "")
    secret = current_app.config.get("MPESA_CONSUMER_SECRET", "")
    auth = (key, secret)
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    if current_app.config.get("MPESA_ENV") == "production":
        url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    res = requests.get(url, auth=auth, timeout=30)
    res.raise_for_status()
    return res.json().get("access_token")

def _mpesa_password(shortcode, passkey, timestamp):
    combo = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(combo.encode()).decode()

@mpesa_bp.post("/stkpush")
@jwt_required()
def stk_push():
    uid = get_jwt_identity()
    data = request.get_json() or {}
    phone = data["phone_number"]
    amount = data["amount"]
    account_ref = data.get("account_reference", "ORDER")
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    shortcode = current_app.config.get("MPESA_SHORTCODE", "")
    passkey = current_app.config.get("MPESA_PASSKEY", "")
    password = _mpesa_password(shortcode, passkey, timestamp)
    callback_url = current_app.config.get("MPESA_CALLBACK_URL", "")
    access_token = _mpesa_get_access_token()
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    if current_app.config.get("MPESA_ENV") == "production":
        url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": account_ref,
        "TransactionDesc": "Order Payment"
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.post(url, json=payload, headers=headers, timeout=60)
    res.raise_for_status()
    data_res = res.json()
    checkout_request_id = data_res.get("CheckoutRequestID")
    tr = MpesaTransaction(
        checkout_request_id=checkout_request_id,
        phone_number=phone,
        account_reference=account_ref,
        user_id=uid,
        amount=amount,
        status="pending",
    )
    db.session.add(tr)
    db.session.commit()
    return jsonify({"message": "stk_push_sent", "checkout_request_id": checkout_request_id})

@mpesa_bp.post("/callback")
def callback():
    payload = request.get_json() or {}
    cb = payload.get("Body", {}).get("stkCallback", {})
    checkout_request_id = cb.get("CheckoutRequestID")
    result_code = cb.get("ResultCode")
    result_desc = cb.get("ResultDesc")
    tr = MpesaTransaction.query.filter_by(checkout_request_id=checkout_request_id).first()
    if not tr:
        return jsonify({"error": "transaction_not_found"}), 404
    tr.result_code = result_code
    tr.result_desc = result_desc
    tr.status = "success" if result_code in (0, "0") else "failed"
    items = cb.get("CallbackMetadata", {}).get("Item", [])
    for it in items:
        name = it.get("Name")
        if name == "MpesaReceiptNumber":
            tr.mpesa_receipt_number = it.get("Value")
        if name == "TransactionDate":
            tr.transaction_date = str(it.get("Value"))
    db.session.commit()
    return jsonify({"message": "callback_received"})

@mpesa_bp.get("/transactions")
@jwt_required()
def list_transactions():
    items = MpesaTransaction.query.order_by(MpesaTransaction.created_at.desc()).all()
    return jsonify([
        {
            "id": str(t.id),
            "checkout_request_id": t.checkout_request_id,
            "phone_number": t.phone_number,
            "account_reference": t.account_reference,
            "result_code": t.result_code,
            "result_desc": t.result_desc,
            "mpesa_receipt_number": t.mpesa_receipt_number,
            "transaction_date": t.transaction_date,
            "status": t.status,
            "amount": str(t.amount),
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in items
    ])