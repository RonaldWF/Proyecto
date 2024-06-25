<?php
require 'vendor/autoload.php';

use Ratchet\MessageComponentInterface;
use Ratchet\ConnectionInterface;

class MyWebSocketServer implements MessageComponentInterface {
    protected $clients;

    public function __construct() {
        $this->clients = new \SplObjectStorage;
    }

    public function onOpen(ConnectionInterface $conn) {
        $this->clients->attach($conn);
    }

    public function onMessage(ConnectionInterface $from, $msg) {
        // No se necesita procesar mensajes entrantes en este ejemplo
    }

    public function onClose(ConnectionInterface $conn) {
        $this->clients->detach($conn);
    }

    public function onError(ConnectionInterface $conn, \Exception $e) {
        $conn->close();
    }

    public function sendUpdates() {
        $data = $this->getDataFromDb();
        foreach ($this->clients as $client) {
            $client->send(json_encode($data));
        }
    }

    private function getDataFromDb() {
        $host = '192.168.100.152';
        $db = 'mydb';
        $user = 'root';
        $pass = '12345678';
        $charset = 'utf8mb4';

        $dsn = "mysql:host=$host;dbname=$db;charset=$charset";
        $options = [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false,
        ];

        try {
            $pdo = new PDO($dsn, $user, $pass, $options);
        } catch (\PDOException $e) {
            throw new \PDOException($e->getMessage(), (int)$e->getCode());
        }

        $stmt = $pdo->query("SELECT temperatura, humedad, presionAtmosferica, velocidad_del_viento, direccion_del_viento, pluvialidad, hora FROM lectura");
        return $stmt->fetchAll();
    }
}

$server = new MyWebSocketServer();

$loop = React\EventLoop\Factory::create();
$webSock = new React\Socket\Server('0.0.0.0:8080', $loop);
$webServer = new Ratchet\Server\IoServer(
    new Ratchet\Http\HttpServer(
        new Ratchet\WebSocket\WsServer(
            $server
        )
    ),
    $webSock
);

// Enviar actualizaciones cada 5 segundos
$loop->addPeriodicTimer(5, function() use ($server) {
    $server->sendUpdates();
});

$loop->run();
