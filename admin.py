import os, asyncio
from firebase_admin import messaging, credentials, initialize_app
import json

FIREBASE_CERT_JSON = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
_app = None
if FIREBASE_CERT_JSON:
    try:
        cred_dict = json.loads(FIREBASE_CERT_JSON)
        cred = credentials.Certificate(cred_dict)
        _app = initialize_app(cred)
    except Exception as e:
        print('Failed to init firebase_admin:', e)

async def send_push_for_results(query, results):
    # Example: send push to all tokens stored in TOKENS env var (JSON array)
    tokens_env = os.environ.get('FCM_TOKENS_JSON')
    if not tokens_env or not _app:
        return False
    try:
        tokens = json.loads(tokens_env)
    except:
        return False

    messages = []
    for r in results:
        if r.get('inStock'):
            msg = messaging.Message(
                notification=messaging.Notification(
                    title=f"{r.get('store')} - {r.get('product')}",
                    body=f"Now in stock: {r.get('product')}"
                ),
                token=tokens[0] if tokens else None, # simple example; send to first token or iterate
            )
            messages.append(msg)

    # Send messages sequentially to avoid quota issues
    for m in messages:
        try:
            resp = messaging.send(m)
            print('sent', resp)
        except Exception as e:
            print('err send', e)
    return True
