# Adaptación de flujos CSV con Python

Una muestra de código revisable y una propuesta de servicio para limpiar, filtrar y combinar archivos CSV con reglas explícitas. La muestra funciona localmente con la biblioteca estándar de Python, sin cuentas, red ni API de pago.

## Servicio propuesto: US$125

Adaptación de un flujo de línea de comandos para **hasta 5 archivos CSV del mismo esquema**, con un máximo conjunto de **25 MB y 100.000 filas**, y **hasta 5 reglas simples** acordadas antes de comenzar. Por ejemplo: quitar espacios exteriores, filtrar un estado, detectar claves vacías, eliminar duplicados por una clave exacta o seleccionar columnas.

La entrega propuesta incluye el código Python adaptado, instrucciones para ejecutarlo, un ejemplo con datos ficticios y comprobaciones de las reglas acordadas. El plazo propuesto es de **3 días desde la recepción de los insumos necesarios y la confirmación del alcance**. Incluye **1 revisión dentro de ese alcance**; los cambios de formato, reglas o funcionalidades se acuerdan por separado.

El precio y los límites son una propuesta de alcance, sujetos a revisar el formato y la viabilidad del trabajo. **El formato y el volumen del encargo se comprobarán antes de comprometer la entrega**.

No incluye interpretación de Excel, uniones complejas, coincidencias aproximadas, corrección manual de datos, integraciones con servicios externos ni una aplicación alojada.

## Revisar y ejecutar la muestra

El código y los ejemplos son originales y se ofrecen bajo [licencia MIT](demo/LICENSE). Se utilizó asistencia de IA para desarrollar el código y la documentación. Los ocho registros de ejemplo son **sintéticos**: esta muestra personal no representa un encargo ni resultados de clientes.

- [Documentación técnica y reglas exactas](demo/README.md)
- [Código de la herramienta](demo/clean_csv.py)
- [Pruebas repetibles](demo/test_clean_csv.py)
- [Entradas sintéticas](demo/samples/) y [resultados de referencia](demo/expected/)

Requiere **Python 3.10 o posterior**, sin paquetes externos. Desde la carpeta `demo/`, ejecutar el comando documentado en la muestra:

```text
python clean_csv.py samples/customers_a.csv samples/customers_b.csv --merged output/merged.csv --rejected output/rejected.csv
```

Resultado esperado:

```text
Read: 8 | Accepted: 5 | Rejected: 3
```

Para ejecutar las comprobaciones desde esa misma carpeta:

```text
python -m unittest -v
```

Las **7 pruebas** de la muestra pasaron con Python 3.12.14 en Windows. Cubren duplicados, claves con ceros iniciales, filtros, formato de entrada, protección de archivos de entrada y resultados de referencia. No constituyen una prueba de carga ni una verificación en otros sistemas operativos.

En una [comprobación de volumen separada](verification/volume-check.json), el mismo código procesó 5 archivos sintéticos con 100.000 filas y 24.500.175 bytes de entrada: 100.000 filas aceptadas, 0 rechazadas y todos los identificadores conservados en orden. La ejecución tardó 0,984 segundos en el equipo de prueba. Fue una sola corrida con el esquema fijo y registros ASCII simples; no garantiza ese tiempo en otros equipos o datos, ni establece un máximo seguro de memoria.

La muestra exige encabezados fijos `customer_id,name,email,status,city`, CSV con coma y texto UTF-8. Carga los registros en memoria antes de escribir. No valida direcciones de correo ni interpreta formatos desconocidos. Los originales no se modifican; las rutas de salida indicadas se pueden sobrescribir. Un fallo de disco puede dejar una salida incompleta. La [documentación técnica](demo/README.md) explica estas condiciones y las reglas completas.

## Consultar un posible encargo

Abrí una [consulta mediante la plantilla de issue](https://github.com/BLANKITOU/riocodelab-csv-workflow/issues/new?template=consulta.md) con una descripción genérica del problema, las columnas previstas, el volumen aproximado y las reglas deseadas. Usá únicamente datos ficticios.

**Los issues son públicos. No adjuntes archivos ni incluyas información privada, datos de clientes, credenciales o datos de contacto.** La consulta solo sirve para evaluar si el trabajo encaja. El alcance, los insumos, el canal adecuado para compartirlos y la contratación se acuerdan antes de comenzar.

Este repositorio no acepta contratos ni pagos mediante GitHub. No tiene pasarela de pago ni checkout activo. La licencia MIT de la muestra no constituye un contrato de prestación de servicios ni una aceptación de esta propuesta.
