import json
import time

import psycopg2
import pyotp
from cryptography.fernet import Fernet


SIX_MONTHS_SECONDS = 180 * 24 * 60 * 60


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


def handle(event, context):
    if event.method == "OPTIONS":
        return {"statusCode": 200, "headers": cors(), "body": ""}

    data = json.loads(event.body)

    username = data.get("username")
    password = data.get("password")
    code = data.get("totp")

    if not username or not password or not code:
        return response(400, {"error": "username, password and totp are required"})

    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT password, mfa, gendate, expired
        FROM users
        WHERE username = %s;
    """, (username,))

    user = cur.fetchone()

    if not user:
        cur.close()
        conn.close()
        return response(404, {"status": "failed", "reason": "user_not_found"})

    encrypted_password, encrypted_mfa, gendate, expired = user

    if expired or int(time.time()) - int(gendate) > SIX_MONTHS_SECONDS:
        cur.execute("""
            UPDATE users
            SET expired = true
            WHERE username = %s;
        """, (username,))
        conn.commit()
        cur.close()
        conn.close()

        return response(200, {
            "status": "expired",
            "message": "renew_credentials"
        })

    fernet = Fernet(read_secret("fernet-key").encode())

    decrypted_password = fernet.decrypt(encrypted_password.encode()).decode()
    decrypted_mfa = fernet.decrypt(encrypted_mfa.encode()).decode()

    if password != decrypted_password:
        cur.close()
        conn.close()
        return response(401, {"status": "failed", "reason": "invalid_password"})

    totp = pyotp.TOTP(decrypted_mfa)

    if not totp.verify(code):
        cur.close()
        conn.close()
        return response(401, {"status": "failed", "reason": "invalid_totp"})

    cur.close()
    conn.close()

    return response(200, {
        "status": "authenticated",
        "username": username
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