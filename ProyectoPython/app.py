from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import mysql.connector

app = Flask(__name__)
socketio = SocketIO(app)

# Configuración de la base de datos
db_config = {
    'user': 'root',
    'password': '12345678',
    'host': '192.168.100.152',
    'database': 'mydb'
}

# Conectar a la base de datos
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# Ruta para la página principal
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM lectura')
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', data=data)

# Emitir datos nuevos vía WebSocket
def send_new_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM lectura ORDER BY hora DESC LIMIT 1')
    new_data = cursor.fetchone()
    cursor.close()
    conn.close()
    socketio.emit('new_data', {'data': new_data})
if __name__ == '__main__':
    socketio.run(app, debug=True, host='192.168.100.152', allow_unsafe_werkzeug=True)

