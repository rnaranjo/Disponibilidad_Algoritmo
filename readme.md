# Instrucciones para la ejecución:

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

```json
{
    "forecasts":
        [
            {
                ... dataframe en formato json ...
            },
        ]
}
```

Hacer esto no generará cambios en la base de datos.

# Respuestas a preguntas conceptuales

### Pregunta 1
Asumiendo que tanto la demanda como la disponibilidad deba ser calculada en intervalos de 15 minutos

### Pregunta 2
Es posible levantar los servicios descritos como una aplicación monolítica. Dado que la aplicación es relativamente pequeña a
estas alturas, es relativamente más sencillo desarrollarla como un único servicio que múltiples microservicios (por ejemplo, no
habría necesidad de realizar la consulta entre el servicio de base de datos y del modelo) y menos costoso en términos de recursos,
ya que existe redundancia entre los microservicios que podría evitarse levantando todo en un único servicio. Sin embargo, a
futuro, la arquitectura monolítica tiene muchas desventajas.

Por un lado, la arquitectura monolítica está limitada en términos de tecnología. Levantar todo en una única aplicación limita a
esta a seguir siendo desarrollada con el mismo lenguaje y herramientas disponibles. Separar el código en múltiples microservicios
le permite a los desarrolladores mayor flexibilidad a la hora de modificar éstos o implementar nuevas tecnologías en nodos
específicos sin tener que modificar la aplicación entera, permitiendo seleccionar herramientas más óptimas para cada microservicio.
Junto a esto, la modularidad en el desarrollo de cada componente permite realizar cambios a la aplicación sin arriesgar que el
servicio entero falle en producción para los clientes en caso de que algún componente en particular esté fallando.

Otra ventaja, es que en caso de recibir nuevos clientes, es más fácil escalar horizontalmente la demanda de los microservicios,
ya que estos pueden ser replicados con mayor facilidad que una aplicación monolítica. Esto además permite a los desarrolladores
mayor flexibilidad a la hora de identificar componentes que puedan ser cuellos de botella en el sistema debido a la alta demanda
de estos, lo cual permite solucionar cada caso de manera particular.

Por último, usar microservicios permite implementar con mayor facilidad servicios personalizados para clientes con requerimientos
específicos, ya que estos pueden ser desarrollados independientemente del resto de la funcionalidad del sistema.

### Pregunta 3
En caso de necesitar levantar este servicio múltiples veces, se puede hacer uso de la funcionalidad de réplicas de docker. Esto
permite escalar la aplicación de manera horizontal, poniendo a disposición múltiples containers con la misma imagen. Esto puede
lograrse agregando al servicio en el archivo docker-compose.yml:

```
    deploy:
      mode: replicated
      replicas: 1000
```

Cabe destacar que crear tantas réplicas puede traer altos costos de uso de memoria, por lo tanto hacer uso de un load balancer
apropiado o alguna herramienta de orquestación como Docker Swarm o Kubernetes.
