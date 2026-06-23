import json
import time
import string
import secrets
import base64
from io import BytesIO

import psycopg2
import qrcode
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


def generate_password():
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*()-_=+")
    ]

    password += [secrets.choice(chars) for _ in range(20)]
    secrets.SystemRandom().shuffle(password)

    return "".join(password)


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

    password = generate_password()

    fernet = Fernet(read_secret("fernet-key").encode())
    encrypted_password = fernet.encrypt(password.encode()).decode()

    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (username, password, gendate, expired)
        VALUES (%s, %s, %s, false)
        ON CONFLICT (username)
        DO UPDATE SET password = EXCLUDED.password,
                      gendate = EXCLUDED.gendate,
                      expired = false;
    """, (username, encrypted_password, int(time.time())))

    conn.commit()
    cur.close()
    conn.close()

    return response(200, {
        "status": "success",
        "username": username,
        "password": password,
        "qrcode": qr_to_base64(password)
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