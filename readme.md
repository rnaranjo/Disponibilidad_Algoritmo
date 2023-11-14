Actualmente para generar la disponibilidad se requieren los datos de demanda y turnos (forecast.csv & shifts.csv).  

El algoritmo devuelve un Datafrmae de cada colaborador donde 1 es que esta disponible y 0 no disponible  

Se requiere que la información provenga desde una base de datos y dejar de usar los archivos .csv, además necesitamos insertar el resultado "df_availability" en una tabla que tenga la siguiente estructura  

| collaborator | date | availability | note |  

donde note debe decir, "libre domingo" si tiene libre y es domingo, si es libre en cualquier otro día, solo debe decir "libre" si tiene disponibilidad debe estar vacío. 

** Extra **  

¿Cómo se podría modificar el algoritmo para garantizar, que el colaborador no trabaje más de 7 días consecutivos?