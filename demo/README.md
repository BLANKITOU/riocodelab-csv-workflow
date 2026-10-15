# Muestra personal: limpieza y combinación de CSV

Esta es una muestra pequeña de un flujo específico desarrollado en Python. Todos los nombres, correos y registros son **datos sintéticos**. No representa un encargo de un cliente ni una herramienta capaz de interpretar cualquier archivo.

Funciona localmente, sin red, cuentas, paquetes externos ni API de pago. Requiere Python 3.10 o posterior y usa solamente su biblioteca estándar. La verificación de esta entrega se realizó con Python 3.12.14.

## Ejecutar la muestra

Desde esta carpeta, en PowerShell, Terminal o una consola con Python disponible:

```text
python clean_csv.py samples/customers_a.csv samples/customers_b.csv --merged output/merged.csv --rejected output/rejected.csv
```

El resultado esperado es:

```text
Read: 8 | Accepted: 5 | Rejected: 3
```

`output/merged.csv` reúne cinco registros aceptados. `output/rejected.csv` contiene tres registros rechazados con el nombre del archivo de origen, la línea y el motivo. Las copias de referencia están en `expected/`. El comando vuelve a generar y sobrescribe únicamente las rutas de salida indicadas; rechaza una salida que coincida con una entrada. Un error de formato se detecta antes de escribir salidas. Un fallo de disco durante la escritura puede dejar una salida incompleta; este ejemplo no implementa una transacción entre ambos archivos.

Para reutilizarlo con otros archivos del **mismo formato**:

```text
python clean_csv.py carpeta/enero.csv carpeta/febrero.csv --merged resultados/combinado.csv --rejected resultados/rechazados.csv
```

## Contrato de entrada y reglas

Los archivos deben ser CSV con delimitador coma, codificación UTF-8 (se acepta BOM) y estos cinco encabezados exactos, en este orden:

```text
customer_id,name,email,status,city
```

Se permiten comas y saltos de línea dentro de campos entrecomillados conforme a CSV. Los encabezados incompatibles, las filas con un número distinto de campos y los CSV o textos UTF-8 inválidos producen un error con código de salida 2. Las filas completamente vacías cuentan como formato incompatible. Los archivos originales no se modifican.

Las reglas, aplicadas en el orden de los archivos y filas suministrados, son:

1. Quitar espacios al principio y al final de todos los valores mediante `str.strip()`; conservar los espacios interiores.
2. Rechazar una clave `customer_id` vacía después de ese recorte: `missing_customer_id`.
3. Conservar solo filas cuyo `status` recortado sea exactamente `active`, distinguiendo mayúsculas. Las demás reciben `filtered_status`. La opción `--active-status otro_valor` cambia ese valor esperado.
4. Eliminar duplicados por la clave `customer_id` exacta después del recorte; conservar la primera **fila aceptada**. Las siguientes reciben `duplicate_customer_id`. Una fila filtrada no reserva su clave. `0001` y `1` son claves diferentes.
5. Seleccionar las columnas `customer_id,name,email,city` para el resultado combinado. Se omite `status` porque ya se aplicó su filtro.

Cada rechazo tiene un único motivo, según la prioridad anterior, y conserva los valores de la fila original para facilitar su revisión. `source_line` indica la última línea física del registro CSV; una fila con un campo multilínea puede ocupar varias líneas. Las salidas usan UTF-8 sin BOM y saltos de línea LF.

Todos los valores se manejan como **texto**. Los ceros iniciales se conservan en el CSV; al abrirlo en una planilla, se debe importar `customer_id` como texto para impedir la conversión automática de la planilla. No se validan correos ni ciudades; no se modifican acentos ni mayúsculas. No hay uniones complejas, coincidencias aproximadas, interpretación de Excel ni corrección manual. Los valores tampoco se ejecutan ni evalúan como fórmulas.

## Comprobaciones

```text
python -m unittest -v
```

Las siete pruebas verifican duplicados entre archivos, conservación de ceros iniciales, encabezados incompatibles sin alterar salidas previas, filtro y claves vacías, longitud incorrecta de fila, protección de entradas y coincidencia exacta con las salidas de referencia.

El flujo carga los registros en memoria antes de escribir. Esta muestra de ocho filas no establece un límite de volumen ni acredita rendimiento con archivos grandes; el volumen y el formato deben probarse para cada encargo.

## Archivos incluidos

- `clean_csv.py`: interfaz de línea de comandos y reglas.
- `samples/`: dos entradas sintéticas del mismo formato.
- `expected/`: resultados de referencia revisables.
- `test_clean_csv.py`: comprobaciones repetibles con archivos temporales.
- `README.md`: instrucciones y alcance.
- `LICENSE`: licencia MIT de esta muestra original.

No se incluyen datos reales de clientes, credenciales, cachés ni servicios alojados.

## Licencia

La licencia MIT incluida en `LICENSE`, con copyright 2026 RioCodeLab, cubre solamente el código, las pruebas, la documentación y los ejemplos originales de esta muestra. Los datos de los ejemplos son ficticios. Esta licencia no concede derechos sobre software o materiales de terceros ni sobre datos que se incorporen en otros encargos.
