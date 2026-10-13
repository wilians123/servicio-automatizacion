# Reporte Fase 2

## 1. Resumen

Se implementó la lectura tolerante del contrato congelado, el plan offline de campos pendientes y el flujo Playwright síncrono para crear una DUCA-T nueva y recorrer los pasos 1 a 10. Al final se pausa para revisión; no se guarda ni envía la declaración. No se añadió ninguna dependencia.

En las pruebas manuales posteriores, el usuario completó en `embarque_1.json` los campos que faltaban y ejecutó la automatización con la configuración actual. El recorrido llegó hasta el paso 10 sin errores; el usuario reportó exitosas todas las pruebas realizadas. La declaración queda para revisión y no se guarda ni se envía automáticamente.

Estado base antes de programar: **9 pruebas pasaron** (`python -m pytest -q`).

## 2. Archivos creados/modificados y equivalencias

| Archivo(s) | Motivo |
| --- | --- |
| `app/contrato.py`, `app/valores.py` | Leer JSON tolerando claves faltantes y convertir números sin notación científica ni pérdida de escala decimal. |
| `app/paises.py`, `app/aduanas.py` | Resolver alias/ISO de países y generar términos de búsqueda de aduanas con comparación exacta normalizada. |
| `app/plan.py` | Predecir campos que requieren intervención sin abrir el navegador; aplicar la excepción de `OtrosGastos`. |
| `app/pasos/comunes.py`, `app/pasos/crear_duca.py`, `app/pasos/paso1.py`…`paso9.py` | Portar helpers y pasos con los selectores del spec TypeScript. |
| `app/flujo.py` | Ejecutar la secuencia original y detenerse en la pausa de revisión manual. |
| `scripts/ejecutar_embarque.py` | Ejecutar por contrato/archivos, o emitir el plan offline con `--plan-only`. |
| `app/runner.py` | Evitar que el texto de una excepción pueda registrar valores del formulario: registra el paso y la clase del error. |
| `app/pasos/comunes.py`, `app/pasos/paso1.py` | Corregir los argumentos `arg=` de `page.wait_for_function`, requeridos por la versión instalada de Playwright; completar el país de destino con la búsqueda Select2 `Salvador` → `El Salvador` y esperar los controles dependientes del paso 1. |
| `app/pasos/paso6.py` | Limpiar la licencia del conductor antes de ingresarla: elimina espacios y caracteres especiales. Ejemplo: `02039206-1` → `020392061`. |
| `app/pasos/paso7.py` | Procesar cada mercancía de la lista antes de llenar gastos; limpiar y limitar la partida a 10 dígitos, seleccionar la opción visible que coincide con su código, corregir las esperas entre campos, limitar el peso a dos decimales y aplicar valores predeterminados de gastos para cumplir las reglas del portal. |
| `tests/test_valores.py`, `test_paises.py`, `test_aduanas.py`, `test_flujo_nulos.py`, ajuste a `test_runner.py` | Probar conversiones, mapeos, nulls, redacción de errores y los tres fixtures sin navegador. |
| `REPORTE_FASE_2.md` | Registrar equivalencias, verificaciones, diferencias y validación manual. |

### Equivalencias: paso original → módulo Python

| `sieca-bot/tests/test-1.spec.ts` | Python |
| --- | --- |
| Helpers de Select2, combos, archivos y documentos | `app.pasos.comunes` |
| Crear `DUCA - T Nueva` y descartar diálogo | `app.pasos.crear_duca` |
| Paso 1: aduanas, destino, observaciones | `app.pasos.paso1` |
| Paso 2: exportador | `app.pasos.paso2` |
| Paso 3: importador | `app.pasos.paso3` |
| Paso 4: aduana de paso y ruta | `app.pasos.paso4` |
| Paso 5: transportista y placa | `app.pasos.paso5` |
| Paso 6: documento y licencia del conductor | `app.pasos.paso6` |
| Paso 7: mercancías y gastos | `app.pasos.paso7` |
| Paso 8: facturas, manifiestos y otros documentos | `app.pasos.paso8` |
| Paso 9: equipamiento | `app.pasos.paso9` |
| Secuencia y pausa final | `app.flujo.ejecutar_duca` |
| `iniciarSesionSieca` y wrapper `paso` | `app.sieca_login` y `app.runner` (existentes) |

### Selectores modificados

**Ningún ID de selector del formulario fue cambiado.** Los términos y opciones que antes eran valores fijos de embarque ahora salen del contrato o de las constantes autorizadas. Se refinó la búsqueda de la partida arancelaria para esperar y seleccionar la única fila visible que contiene el código ingresado, en vez de seleccionar la primera fila sin comprobar su código. Las esperas de Playwright del paso 1 y el paso 7 pasan sus datos mediante `arg=`.

## 3. Comandos ejecutados y resultado

- Estado base: `python -m pytest -q` → **9 pasaron**.
- Compilación sintáctica: `python -m compileall -q app scripts tests` → completada.
- Suite final: `python -m pytest -q` → **20 pasaron**, sin navegador real.
- Plan offline, sin Chrome ni login, ejecutado para los tres fixtures con `--plan-only` → los tres se cargaron y generaron su lista de campos pendientes.
- Recorrido manual en SIECA reportado por el usuario, con los campos faltantes de `embarque_1.json` completados: se llegó al paso 10 sin errores. Todas las pruebas realizadas con la configuración actual fueron exitosas.
- Tras los últimos cambios del paso 7, `python -m py_compile app/pasos/paso7.py` → compilación correcta. El usuario confirmó en la ejecución manual la configuración actual, incluido el avance hasta el paso 10.
- El estado Git de este proyecto muestra los archivos de Fase 2 y conserva cambios previos del usuario. La inspección de `sieca-bot` fue solo lectura; su `.gitignore` modificado ya aparecía en una revisión anterior y no se tocó. No se ejecutó código de ese proyecto ni se modificaron `contrato/` o `test_data/`.

## 4. Estado de pruebas antes y después

- Antes: 9/9 de Fase 1C pasaron.
- La última suite automatizada registrada en Fase 2 fue 20/20. Incluye conversiones, campos null, países, comparación de aduanas y lectura/plan de los tres fixtures.
- En la validación manual posterior, el usuario completó los datos faltantes de `embarque_1.json`; todos los casos ejecutados con la configuración actual fueron exitosos y la automatización llegó al paso 10.
- La ejecución llegó hasta la etapa de revisión final. No se guardó ni envió la declaración.

## 5. Decisiones tomadas y desviaciones

- Se permaneció en la rama existente `fase-1c-automatizacion`; Fase2 indica expresamente no crear ramas.
- En el repositorio hermano, el estado de solo lectura conserva el `.gitignore` ya modificado que se había observado antes de Fase 2; no se intentó revertirlo.
- Los argumentos manuales usan `test_data/embarque_N`, que es la carpeta presente en este proyecto. El prompt describe `test-data/embarques/embarque_N`.
- El planificador imprime nombres de campos y pasos, nunca valores del embarque. El runner omite el texto de excepciones en logs por la misma razón.
- `cartaporte` vacío se omite. `ValorTotal`, `PaisProcedencia`, la identificación del exportador del JSON, el país de destino del JSON y los tipos fijos se manejan según las reglas de Fase 2.
- El paso 7 recorre la lista completa de mercancías y solo empieza a escribir los gastos después de procesar la última. Para cada línea espera a que termine el indicador de carga antes de continuar.
- La partida arancelaria conserva solo dígitos y limita la búsqueda a 10; espera una opción visible con ese código y la selecciona únicamente si hay una coincidencia.
- El peso se redondea a dos decimales. Si `GastosTransporte` llega como `null`, vacío o cero, se escribe `0.01` porque SIECA exige un valor mayor que cero. `GastosSeguro` y `OtrosGastos` vacíos o `null` se escriben como `0`; sus valores informados se conservan. Esto evita pausar por esos dos campos.
- La automatización completó una ejecución manual hasta el paso 10. La repetición de mercancías, el llenado de gastos y la navegación por los pasos posteriores funcionaron en las pruebas reportadas con la configuración actual.

### Campos previstos para pausa por fixture

| Fixture | Campos que el plan offline prevé que requieran atención |
| --- | --- |
| `embarque_1` | El usuario completó los campos que faltaban antes de la ejecución manual. La configuración actual permitió llegar al paso 10 sin errores. Cuando transporte, seguro u otros llegan vacíos, se aplican los valores predeterminados descritos arriba. |
| `embarque_2` | Paso 5: `CodigoTransportista`, `PlacaTransporte`; paso 6: `LicenciaConductor`; paso 8: `NombreDocumentoFactura` (archivo no encontrado con el nombre del JSON) y `NumeroDocumentoManifiesto`; paso 9: `PlacaChasis`, `MarchamoSat`, `PaisChasis`. Los gastos faltantes se resuelven según la regla de ejecución. |
| `embarque_3` | Paso 5: `CodigoTransportista`, `PlacaTransporte`; paso 6: `LicenciaConductor`; paso 9: `PlacaChasis`, `PaisChasis`. Gastos vacíos se resuelven en ejecución: transporte `0.01`, seguro y otros `0`. |

`ValorTotal` no genera pausa; lo calcula el portal. La lista vacía de `cartaporte` tampoco genera pausa.

El planificador offline existente aún puede clasificar gastos vacíos como pausas, aunque el paso 7 ya los normaliza en ejecución (transporte `0.01`; seguro y otros `0`). Esta diferencia aplica al reporte `--plan-only`, no al llenado del formulario.

### Países y aduanas de los fixtures

- No se encontraron países de los tres fixtures fuera de la tabla implementada.
- Todos los textos de `AduanaInicio` y `AduanaDestino` produjeron término de búsqueda por código y alternativa por nombre. La tabla offline no contiene las opciones vivas del portal, así que no puede confirmar si SIECA devuelve una coincidencia única; si no, el flujo pausa.

## 6. Hallazgos fuera de alcance

- El archivo de factura del fixture 2 no coincide exactamente con ningún archivo de `test_data/embarque_2`. No se alteraron el contrato ni los datos congelados; el flujo pausa y deja que el operador seleccione el archivo correcto.
- El path de datos recibido usa `test_data/embarque_N`, distinto al path descrito en la instrucción. El CLI permite pasar cualquier carpeta y sus ejemplos usan la carpeta presente.

## 7. Riesgos y pendientes para Fase 2

- **Validación de la configuración actual en SIECA: EXITOSA según las pruebas reportadas por el usuario**. La automatización llegó al paso 10 sin errores.
- Para ampliar cobertura, queda ejecutar los otros fixtures en SIECA y comprobar sus documentos y opciones particulares.
- El flujo siempre termina antes de guardar o enviar la DUCA.

## 8. Cómo validar manualmente

Desde la raíz del proyecto, con `.venv` y `.env` ya preparados, ejecuta cada embarque con los datos congelados y la carpeta física existente:

```powershell
.\.venv\Scripts\python.exe scripts\ejecutar_embarque.py --datos contrato\fixtures\embarque_1.json --archivos test_data\embarque_1
.\.venv\Scripts\python.exe scripts\ejecutar_embarque.py --datos contrato\fixtures\embarque_2.json --archivos test_data\embarque_2
.\.venv\Scripts\python.exe scripts\ejecutar_embarque.py --datos contrato\fixtures\embarque_3.json --archivos test_data\embarque_3
```

Para ver solo los campos que podrían pausar, añade `--plan-only`; no abre Chrome ni consulta SIECA.

En la ejecución manual, Chrome abre SIECA y el operador resuelve el captcha. Luego se crea una DUCA-T nueva, se descarta el diálogo inicial y se recorren en orden los pasos 1 a 9: ruta/aduanas; exportador; importador; ruta de paso; transportista/placa; licencia; mercancías/gastos; documentos; equipamiento. Cada null o dato sin coincidencia requiere completar el campo manualmente y pulsar **Resume** para continuar. Para el fixture 2, selecciona manualmente el archivo faltante cuando el paso 8 lo solicite. Al concluir, la pausa final deja abierta la página para revisar y guardar la DUCA manualmente. No se guarda ni envía desde el bot.
