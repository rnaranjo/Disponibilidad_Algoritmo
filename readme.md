Instrucciones para la ejecución:

Antes de iniciar los contenedores de db_service y model_service, debe haber un network en docker llamada backend. Este se crea
al ejecutar el contendor "db_setup". Cada contenedor puede ser ejecutado desde su carpeta usando el comando:

docker-compose up --build -d

Los puertos para cada aplicación son:

- Base de datos postgres: 5432
- Database Service (servicio que se encarga de la lectura y escritura a la base de datos): 4001
- Model Service (servicio que se encarga de aplicar el algoritmo entregado para el cálculo de días disponibles): 4002

Cada microservicio tiene un endpoint para verificar si el servicio está andando en http://localhost::port:/test .

Al ejecutar el endpoint http://localhost:4001/write_availability , este automáticamente carga los datos de la base de datos
necesarios para llamar al endpoint del model service. Alternativamente, se puede llamar al model service pasando un json en el
request con la conversión a json de un dataframe pandas con los datos de forecast:

{
    "forecasts":
        [
            {
                ... dataframe en formato json ...
            },
        ]
}

Hacer esto no generará cambios en la base de datos.