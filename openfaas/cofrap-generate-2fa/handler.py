import json
import base64
from io import BytesIO

import psycopg2
import qrcode
import pyotp
from cryptography.fernet import Fernet


def read_secret(name):
    with open(f"/var/openfaas/secrets/{name}", "r") as f:
        return f.read().strip()


def db_connect():
    return psycopg2.connect(
        host=read_secret("db-host"),
        database=read_secret("db-name"),
        user=read_secret("db-user"),
        password=read_secret("db-password"),
        port=5432
    )


def qr_to_base64(data):
    img = qrcode.make(data)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def handle(event, context):
    if event.method == "OPTIONS":
        return {"statusCode": 200, "headers": cors(), "body": ""}

    data = json.loads(event.body)
    username = data.get("username")

    if not username:
        return response(400, {"error": "username is required"})

    secret = pyotp.random_base32()

    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name="COFRAP"
    )

    fernet = Fernet(read_secret("fernet-key").encode())
    encrypted_secret = fernet.encrypt(secret.encode()).decode()

    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET mfa = %s
        WHERE username = %s;
    """, (encrypted_secret, username))

    if cur.rowcount == 0:
        conn.rollback()
        cur.close()
        conn.close()
        return response(404, {"error": "user not found"})

    conn.commit()
    cur.close()
    conn.close()

    return response(200, {
        "status": "success",
        "username": username,
        "secret": secret,
        "qrcode": qr_to_base64(uri)
    })


def cors():
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }


def response(code, body):
    return {
        "statusCode": code,
        "headers": cors(),
        "body": json.dumps(body)
    }