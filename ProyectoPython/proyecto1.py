from asyncio import sleep
import random
import time
import json
from threading import Thread
from paho.mqtt import client as mqtt_client
import mysql.connector
from websocket import create_connection

broker = "test.mosquitto.org"
port = 1883
base_topic = "estacion"

def Datos():
    hora_actual = time.localtime()
    hora_formateada = time.strftime("%H:%M:%S", hora_actual)

    return {
        "temperatura": round(random.uniform(18, 35), 2),
        "humedad": round(random.uniform(0, 100), 2),
        "presionAtmosferica": round(random.uniform(950, 1050), 2),
        "velocidadViento": round(random.uniform(0, 100), 2),
        "direccionViento": round(random.uniform(0, 255), 2),
        "pluvialidad": round(random.uniform(0, 100), 2),
        "hora": hora_formateada
    }

def connect_mqtt(client_id):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Conectado al broker {client_id}!")
        else:
            print(f"Conexion fallida {rc}\n")

    client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, station_id):
    while True:
        datos = Datos()
        payload = json.dumps(datos)
        topic = f"{base_topic}/{station_id}/sensores"
        result = client.publish(topic, payload)
        status = result[0]
        if status == 0:
            print(f"Enviado `{payload}` a `{topic}`")
        else:
            print(f"Mensaje fallido {topic}")
        time.sleep(5)

def subscribe(client, station_ids):
    def on_message(client, userdata, msg):
        datos = json.loads(msg.payload.decode())
        connection = mysql.connector.connect(
            host='192.168.100.152',
            user='root',
            password='12345678',
            database='mydb'
        )

        cursor = connection.cursor()
        insert_query = """
        INSERT INTO lectura (temperatura, humedad, presionAtmosferica, velocidad_del_viento, direccion_del_viento, pluvialidad, hora)
        VALUES (%(temperatura)s, %(humedad)s, %(presionAtmosferica)s, %(velocidadViento)s, %(direccionViento)s, %(pluvialidad)s, %(hora)s)
        """
        cursor.execute(insert_query, datos)
        connection.commit()

        # Send data to WebSocket server
        try:
            ws = create_connection("ws://localhost:8080")
            ws.send(json.dumps(datos))
            ws.close()
        except Exception as e:
            print(f"WebSocket error: {e}")

        print(f"Recibido `{msg.payload.decode()}` de `{msg.topic}`")

    for station_id in station_ids:
        topic = f"{base_topic}/{station_id}/sensores"
        client.subscribe(topic)
        client.message_callback_add(topic, on_message)

def run_publisher(station_ids):
    threads = []
    for station_id in station_ids:
        client_id = f'publish-{station_id}-{random.randint(0, 1000)}'
        client = connect_mqtt(client_id)
        t = Thread(target=publish, args=(client, station_id))
        t.start()
        threads.append(t)
        sleep(5)
    for t in threads:
        t.join()

def run_subscriber():
    client_id = f'subscribe-{random.randint(0, 1000)}'
    client = connect_mqtt(client_id)
    station_ids = ["estacion1", "estacion2"]  # Puedes agregar más estaciones aquí si es necesario
    subscribe(client, station_ids)
    client.loop_forever()

if __name__ == '__main__':
    connection = mysql.connector.connect(
            host='192.168.100.152',
            user='root',
            password='12345678',
            database='mydb'
        )

    # Crear un cursor
    cursor = connection.cursor()

    # Definir el comando SQL para crear la tabla
    crear_tabla_query = """
        CREATE TABLE IF NOT EXISTS lectura (
            temperatura FLOAT,
            humedad FLOAT,
            presionAtmosferica FLOAT,
            velocidad_del_viento FLOAT,
            direccion_del_viento FLOAT,
            pluvialidad FLOAT,
            hora VARCHAR(100)
        )
        """

    # Ejecutar el comando SQL para crear la tabla
    cursor.execute(crear_tabla_query)

    # Confirmar los cambios en la base de datos
    connection.commit()

    # Cerrar el cursor y la conexión
    cursor.close()
    connection.close()

    # Ejecuta el publicador y el suscriptor en hilos separados
    Thread(target=run_publisher, args=([f"estacion{i}" for i in range(1, 3)],)).start()
    Thread(target=run_subscriber).start()
