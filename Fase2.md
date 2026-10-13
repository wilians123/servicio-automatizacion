# SESIÓN FASE 2 · Proyecto: servicio-automatizacion

Directorio de trabajo (único con escritura): C:\Users\Usuario\Desktop\DUCAS-BOT\servicio-automatizacion
Lectura adicional autorizada (SOLO LECTURA): C:\Users\Usuario\Desktop\DUCAS-BOT\sieca-bot

- Puedes leer todo salvo las carpetas user_data_sieca\* y Temp (no las abras).
- NO ejecutes nada de sieca-bot (ni npm, ni npx, ni playwright). Solo leer código.
  Ajustes al bloque común para esta fase: (a) la regla 3 queda anulada solo para la ruta de sieca-bot en modo lectura; (b) NO crees ramas: trabaja en la rama actual y, al final, crea la etiqueta fin-fase-2-automatizacion.

## Propósito

Implementar en Python los pasos de creación de la DUCA-T (crear nueva DUCA y pasos 1 a 9) leyendo los datos del JSON del contrato congelado (contrato/CONTRATO.md y contrato/fixtures/embarque_N.json). Es un PORT LITERAL de sieca-bot/tests/test-1.spec.ts: mismos selectores, mismas esperas y mismo orden. Los únicos cambios son que los valores hardcodeados ahora salen del JSON y que los null se manejan como se indica abajo. No se llega a guardar la DUCA: al final, igual que el original, se pausa para que el operador revise y guarde.

## Regla de oro

No mejores, simplifiques ni "robustezcas" selectores ni esperas del original. Si algo del original parece discutible, anótalo en "Hallazgos fuera de alcance". Si un selector necesita ajuste para funcionar contra SIECA real, hazlo mínimo y documéntalo con el motivo en el reporte.

## Decisiones fijas (no preguntar)

1. Valores fijos escritos por el bot, ignorando el JSON:
   - paso1: país de destino siempre "El Salvador" (se selecciona con el patrón del original: buscar "Salvador"). País de procedencia no se toca (el portal ya trae Guatemala).
   - paso2: NumeroIdentificacionExportador siempre "S/N". Nunca escribas aquí lo que venga en el JSON.
   - paso2 y paso3: tipo de identificación siempre "Número de Identificacion Tributaria" (como el original).
   - paso4: aduana de paso siempre La Ermita (como el original).
   - paso9: TipoEquipamiento "Contenedor" y TipoCarga "Contenerizada" (como el original).
2. Valores que vienen del JSON (leer tal cual llegan, string o número; convertir a texto solo al escribir en el formulario, sin notación científica y conservando decimales): todo lo demás de paso1 a paso9, incluidos Observaciones, aduanas, exportador/importador, transportista, placa, licencia, gastos, mercancías, documentos y equipamiento.
3. Null:
   - Si un campo necesario es null o vacío, NO escribas nada y NO falles: llama a pausar_para_usuario con un motivo claro ("Falta <campo> en el paso N: complétalo manualmente") y, al reanudar, continúa con el siguiente campo. Regístralo en el log.
   - Excepción: OtrosGastos null se escribe como 0 solo si GastosTransporte y GastosSeguro tienen valor; si no, pausa.
   - ValorTotal no se usa (el portal lo calcula). cartaporte vacío es normal: se omite sin pausa.
4. Aduanas (AduanaInicio y AduanaDestino): el JSON trae el texto completo, por ejemplo "TERRESTRE ANGUIATÚ - 08 - ADUANA PORTUARIA". Haz el mapeo así: término de búsqueda = el código del segmento central (por ejemplo "08"; "PB"; "83"); luego elige entre los resultados la opción cuyo texto, comparado sin acentos y sin distinguir mayúsculas ni espacios múltiples, sea igual al valor del JSON. Si no hay coincidencia exacta, prueba como término de búsqueda la primera palabra distintiva del nombre; si sigue sin haber coincidencia única, pausa para el operador.
5. Países (PaisMercancia, PaisExportador, PaisImportador, PaisChasis): crea app/paises.py con una tabla pequeña (Guatemala, El Salvador, Honduras, Nicaragua, Costa Rica, Panamá, Estados Unidos, México, Colombia, China y los que aparezcan en los 3 fixtures) que acepte nombre en español, código ISO de 2 letras (por ejemplo "US") y "SALVADOR" (valor del contrato para PaisChasis). Para cada país define: el fragmento de búsqueda y el texto exacto de la opción para cada tipo de control, replicando lo que usa sieca-bot en cada paso (Select2 de los pasos 2, 3 y 7 con coincidencia exacta; combo DevExpress del paso 9 con coincidencia por celda). Lee los patrones concretos en test-1.spec.ts. Para un país que no esté en la tabla o cuya opción no aparezca: pausa para el operador, nunca adivines. Verificar que Pais_Origen del paso 7 quede con el código esperado (como el original, que comprueba "US").
6. Clase de bultos (paso 7): el JSON trae el código (VN, PK, etc.). Escríbelo en el combo, selecciona la primera fila de la lista que lo contenga y verifica que el valor oculto lo incluya, igual que el original hace con "3H". Si no aparece la fila, pausa.
7. Mercancías (paso 7): el JSON trae una lista. Repite por cada elemento el bloque del original (partida → Agregar Mercancía → descripción, cantidad, clase, país, peso → botón agregar mercancía) y rellena los gastos (FOB, transporte, seguro, otros) una sola vez al final de la lista. Respeta la guardia del original (no entrar a los gastos si la mercancía no fue creada). Si la repetición para el segundo elemento no se comporta como el primero en SIECA, que falle por el wrapper paso() (pausa) y documéntalo.
8. Paso 8 (documentos): los archivos físicos están en test-data/embarques/embarque_N/ con el mismo nombre que NombreDocumento* del JSON. Por cada objeto de facturas, manifiestos y otros: selecciona su carpeta (Facturas, Manifiestos, Otros), adjunta ese archivo, sube, y completa tipo y número desde el JSON, con la misma lógica del original (incluida la comparación exacta de "Manifiesto de carga" y la tecla Tab). El tipo de documento viene del JSON (TipoDocumento*). Si el archivo no existe en la carpeta, pausa para el operador. Una categoría vacía se omite. Si una opción de tipo del JSON (por ejemplo "Conocimiento de embarque hija") no existe en la lista del portal, pausa.
9. Pasos 5 y 6: código de transportista, placa, tipo de documento del conductor "Licencia" y número de licencia, con el mismo flujo del original.

## Estructura (agrega a la existente, sin reescribir lo de la Fase 1C)

app/contrato.py # carga y lectura tolerante del JSON (claves faltantes = null; string o número)
app/paises.py
app/valores.py # utilidades: a_texto(valor), es_vacio(valor), normalizar(texto), construir regex de opción
app/pasos/ # un módulo por grupo: crear_duca.py, paso1.py ... paso9.py (o agrupados), cada función recibe (page, datos, settings)
app/flujo.py # ejecutar_duca(page, datos, ruta_archivos, settings): llama a los pasos usando runner.paso() en el mismo orden del original y termina con pausa "Revisa y guarda la DUCA manualmente"
scripts/ejecutar_embarque.py # argumentos: --datos contrato/fixtures/embarque_N.json --archivos test-data/embarques/embarque_N ; abre el contexto, inicia sesión, ejecuta el flujo
tests/test_valores.py, tests/test_paises.py, tests/test_aduanas.py, tests/test_flujo_nulos.py # sin navegador

## Tareas

T1. Estado base: ejecuta pytest y registra el resultado.
T2. Leer sieca-bot (solo lectura) y escribir en el reporte una tabla "paso original → módulo Python" antes de programar.
T3. Implementar valores, países, contrato y los pasos en el orden del original (crear DUCA, 1, 2, ... 9). Mantén cada selector literal.
T4. Pruebas con pytest sin navegador: conversión de valores (número y string, decimales), mapeo de países (nombre, ISO, "SALVADOR", país desconocido), mapeo de aduanas (acentos, mayúsculas), manejo de null (pausa, excepción de OtrosGastos), lectura de los 3 fixtures sin error.
T5. Deja scripts/ejecutar_embarque.py listo. Tú NO puedes ejecutarlo contra SIECA (requiere captcha humano): marca la validación como PENDIENTE y documenta cómo correr cada fixture.
T6. Reporte con: tabla de equivalencias, lista de selectores modificados (idealmente ninguno) con motivo, qué campos de cada fixture provocarán pausa, qué países/aduanas de los fixtures no resolvió la tabla.

## PROHIBIDO

- Modificar sieca-bot o los fixtures/contrato/, y acceder a duca-bot o servicio-extraccion.
- Crear la API FastAPI, endpoints o integración con duca-bot (Fase 3).
- Guardar o enviar la DUCA en SIECA: la automatización se detiene en la pausa final.
- Escribir en NumeroIdentificacionExportador algo distinto de "S/N".
- Eludir o resolver el captcha, usar librerías anti-detección o agregar dependencias nuevas.
- Mejorar esperas, timeouts o selectores sin necesidad demostrada.
- Imprimir credenciales o contenido de .env, o escribir datos reales de embarques en logs (solo nombres de campos y pasos).

## Verificación de cierre

1. pytest en verde (sin navegador).
2. Los 3 fixtures se cargan y generan un plan de ejecución sin error (puedes mostrar el listado de campos que pausarían, sin abrir navegador).
3. git status: sin cambios fuera de servicio-automatizacion; sieca-bot intacto.
4. Etiqueta fin-fase-2-automatizacion creada.
5. REPORTE_FASE_2.md con las secciones del bloque común y "Cómo validar manualmente" (comando por fixture y qué esperar en cada paso).
