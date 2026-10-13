# Reporte Fase 2

## 1. Resumen

Se implementó la lectura tolerante del contrato congelado, el plan offline de campos pendientes y el flujo Playwright síncrono para crear una DUCA-T nueva y llenar los pasos 1 a 9. Al final se pausa para revisión; no se guarda ni envía la declaración. No se añadió ninguna dependencia.

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

**Ningún selector literal del original fue cambiado.** Los términos y opciones que antes eran valores fijos de embarque ahora salen del contrato o de las constantes autorizadas. La espera paralela de dos controles del Paso 1 se trasladó a `page.wait_for_function` con los mismos IDs, criterio de visibilidad y timeout de 30 segundos para conservar la concurrencia usando la API síncrona.

## 3. Comandos ejecutados y resultado

- Estado base: `python -m pytest -q` → **9 pasaron**.
- Compilación sintáctica: `python -m compileall -q app scripts tests` → completada.
- Suite final: `python -m pytest -q` → **20 pasaron**, sin navegador real.
- Plan offline, sin Chrome ni login, ejecutado para los tres fixtures con `--plan-only` → los tres se cargaron y generaron su lista de campos pendientes.
- El estado Git de este proyecto muestra los archivos de Fase 2 y conserva cambios previos del usuario. La inspección de `sieca-bot` fue solo lectura; su `.gitignore` modificado ya aparecía en una revisión anterior y no se tocó. No se ejecutó código de ese proyecto ni se modificaron `contrato/` o `test_data/`.

## 4. Estado de pruebas antes y después

- Antes: 9/9 de Fase 1C pasaron.
- Después: 20/20 pasaron. Incluyen números enteros/decimales, campos null, la regla de `OtrosGastos`, países, comparación de aduanas y lectura/plan de los tres fixtures.
- La interacción de SIECA no se probó con navegador real.

## 5. Decisiones tomadas y desviaciones

- Se permaneció en la rama existente `fase-1c-automatizacion`; Fase2 indica expresamente no crear ramas.
- En el repositorio hermano, el estado de solo lectura conserva el `.gitignore` ya modificado que se había observado antes de Fase 2; no se intentó revertirlo.
- Los argumentos manuales usan `test_data/embarque_N`, que es la carpeta presente en este proyecto. El prompt describe `test-data/embarques/embarque_N`.
- El planificador imprime nombres de campos y pasos, nunca valores del embarque. El runner omite el texto de excepciones en logs por la misma razón.
- `cartaporte` vacío se omite. `ValorTotal`, `PaisProcedencia`, la identificación del exportador del JSON, el país de destino del JSON y los tipos fijos se manejan según las reglas de Fase 2.
- No se llegó a SIECA, por lo que la presencia de las opciones exactas de aduanas/países y el comportamiento del segundo y siguientes elementos de mercancía quedan por validar manualmente.

### Campos previstos para pausa por fixture

| Fixture | Campos que el plan offline prevé que requieran atención |
| --- | --- |
| `embarque_1` | Paso 5: `CodigoTransportista`, `PlacaTransporte`; paso 6: `LicenciaConductor`; paso 7: `GastosTransporte`, `GastosSeguro`, `OtrosGastos`; paso 8: `NumeroDocumentoManifiesto`; paso 9: `PlacaChasis`, `MarchamoSat`, `PaisChasis`. |
| `embarque_2` | Paso 5: `CodigoTransportista`, `PlacaTransporte`; paso 6: `LicenciaConductor`; paso 8: `NombreDocumentoFactura` (archivo no encontrado con el nombre del JSON) y `NumeroDocumentoManifiesto`; paso 9: `PlacaChasis`, `MarchamoSat`, `PaisChasis`. `OtrosGastos` null se convierte en 0 porque transporte y seguro tienen valor. |
| `embarque_3` | Paso 5: `CodigoTransportista`, `PlacaTransporte`; paso 6: `LicenciaConductor`; paso 7: `GastosTransporte`, `GastosSeguro`, `OtrosGastos`; paso 9: `PlacaChasis`, `PaisChasis`. |

`ValorTotal` no genera pausa; lo calcula el portal. La lista vacía de `cartaporte` tampoco genera pausa.

### Países y aduanas de los fixtures

- No se encontraron países de los tres fixtures fuera de la tabla implementada.
- Todos los textos de `AduanaInicio` y `AduanaDestino` produjeron término de búsqueda por código y alternativa por nombre. La tabla offline no contiene las opciones vivas del portal, así que no puede confirmar si SIECA devuelve una coincidencia única; si no, el flujo pausa.

## 6. Hallazgos fuera de alcance

- El archivo de factura del fixture 2 no coincide exactamente con ningún archivo de `test_data/embarque_2`. No se alteraron el contrato ni los datos congelados; el flujo pausa y deja que el operador seleccione el archivo correcto.
- El path de datos recibido usa `test_data/embarque_N`, distinto al path descrito en la instrucción. El CLI permite pasar cualquier carpeta y sus ejemplos usan la carpeta presente.

## 7. Riesgos y pendientes para Fase 2

- **validación manual en SIECA: PENDIENTE (la hace el usuario)**. Requiere credenciales locales, captcha humano y comprobar que cada opción exacta exista en la sesión actual del portal.
- Validar en SIECA que agregar varias mercancías repita el mismo bloque del primer elemento.
- En la carga de documentos, verificar los tipos del JSON disponibles en el combo. Si falta uno, el wrapper pausará.
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
