import os
import socket
from flask import Flask

import mysql.connector
import psycopg2

app = Flask(__name__)


def get_ipv4_addresses():
    hostname = socket.gethostname()
    addresses = []

    try:
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = info[4][0]
            if ip not in addresses:
                addresses.append(ip)
    except Exception:
        pass

    return addresses


def get_db_data():
    driver = os.getenv("DB_DRIVER")
    host = os.getenv("DB_HOST")
    port = int(os.getenv("DB_PORT", "0"))
    db_name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if driver == "mysql":
        conn = mysql.connector.connect(
            host=host,
            port=port,
            database=db_name,
            user=user,
            password=password,
            charset="utf8mb4",
            connection_timeout=5
        )

        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, group_code FROM student_record")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return rows

    if driver == "postgres":
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=db_name,
            user=user,
            password=password,
            connect_timeout=5
        )

        cursor = conn.cursor()
        cursor.execute("SET statement_timeout = 5000")
        cursor.execute("SELECT id, full_name, group_code FROM student_record")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return rows

    raise Exception("Невідомий DB_DRIVER")


@app.route("/")
def index():
    hostname = socket.gethostname()
    ips = get_ipv4_addresses()

    driver = os.getenv("DB_DRIVER", "not set")
    host = os.getenv("DB_HOST", "not set")
    port = os.getenv("DB_PORT", "not set")

    try:
        rows = get_db_data()

        result_html = ""
        for row in rows:
            result_html += f"""
            <tr>
                <td>{row[0]}</td>
                <td>{row[1]}</td>
                <td>{row[2]}</td>
            </tr>
            """

        db_status = f"""
        <p><strong>Статус БД:</strong> Підключення успішне</p>

        <table border="1" cellpadding="6">
            <tr>
                <th>ID</th>
                <th>ПІБ</th>
                <th>Група</th>
            </tr>
            {result_html}
        </table>
        """

    except Exception as e:
        db_status = f"""
        <p><strong>Статус БД:</strong> Помилка підключення</p>
        <p>{str(e)}</p>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <title>Лабораторна робота №5</title>
    </head>
    <body>

        <h1>Лабораторна робота №5</h1>

        <p><strong>Студент:</strong> Тимков Дмитро Віталійович</p>
        <p><strong>Група:</strong> 6.1214-пі-2</p>

        <h2>Інформація про контейнер</h2>

        <p><strong>Hostname:</strong> {hostname}</p>
        <p><strong>IPv4:</strong> {", ".join(ips)}</p>

        <h2>Підключення до БД</h2>

        <p><strong>DB_DRIVER:</strong> {driver}</p>
        <p><strong>DB_HOST:</strong> {host}</p>
        <p><strong>DB_PORT:</strong> {port}</p>

        {db_status}

    </body>
    </html>
    """


app.run(host="0.0.0.0", port=8080)