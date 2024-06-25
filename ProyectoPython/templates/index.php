<?php
// Conexión a la base de datos
$conexion = mysqli_connect('localhost', 'root', '', 'lectura');

if (!$conexion) {
    die("Conexión fallida: " . mysqli_connect_error());
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
   <meta charset="UTF-8">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <title>HOLA</title> 
</head>
<body>
    <br>
    <table border="1">
        <tr>
            <td>Temperatura</td>
            <td>Humedad</td>
            <td>Presión Atmosférica</td>
            <td>Velocidad del viento</td>
            <td>Dirección</td>
            <td>Pluvialidad</td>
            <td>Hora</td>
        </tr>
        <?php
        $sql = "SELECT * FROM lectura";
        $result = mysqli_query($conexion, $sql);

        if (mysqli_num_rows($result) > 0) {
            while ($mostrar = mysqli_fetch_assoc($result)) {
        ?>
        <tr>
            <td><?php echo $mostrar['temperatura']; ?></td>
            <td><?php echo $mostrar['humedad']; ?></td>
            <td><?php echo $mostrar['presionAtmosferica']; ?></td>
            <td><?php echo $mostrar['velocidad_del_viento']; ?></td>
            <td><?php echo $mostrar['direccion_del_viento']; ?></td>
            <td><?php echo $mostrar['pluvialidad']; ?></td>
            <td><?php echo $mostrar['hora']; ?></td>
        </tr>
        <?php
            }
        } else {
            echo "<tr><td colspan='7'>No hay datos disponibles</td></tr>";
        }

        // Cerrar la conexión
        mysqli_close($conexion);
        ?>
    </table>
</body>
</html>
