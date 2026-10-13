# CONTEXTO GLOBAL (leer completo antes de actuar)

Trabajas en UNA de tres piezas de un sistema de automatización aduanera DUCA-T:

- servicio-extraccion (FastAPI/Python): extrae texto de PDF/Excel de un correo, lo envía a una IA y devuelve un JSON "DucaTForm" (paso1..paso9).
- duca-bot (Next.js/TypeScript): lee Gmail, llama al servicio de extracción, muestra la previsualización editable de la DUCA-T.
- servicio-automatizacion (Python/Playwright): automatización que llena el formulario de SIECA con el JSON. Es la migración a Python de un proyecto anterior (sieca-bot, en TypeScript).

Objetivo global de esta iteración: una versión MÍNIMA pero FUNCIONAL que, partiendo de un correo y sus adjuntos seleccionados, extraiga los datos, los muestre al operador y la automatización en Python cree la DUCA-T en SIECA pasando los 9 pasos. NO se agregan funcionalidades fuera de lo que pide cada sesión.

## Reglas de aislamiento (INQUEBRANTABLES)

1. Tu directorio de trabajo es el ÚNICO donde puedes crear, editar o borrar archivos. Está indicado en tu prompt de sesión.
2. No leas, edites, listes ni ejecutes nada fuera de tu directorio, salvo que tu prompt lo autorice explícitamente y SOLO en modo lectura.
3. Rutas de los otros proyectos (PROHIBIDAS salvo autorización expresa):
   C:\Users\Usuario\Desktop\DUCAS-BOT\duca-bot
   C:\Users\Usuario\Desktop\DUCAS-BOT\servicio-extraccion
   C:\Users\Usuario\Desktop\DUCAS-BOT\servicio-automatizacion
   C:\Users\Usuario\Desktop\DUCAS-BOT\sieca-bot (nunca, bajo ninguna circunstancia)
4. Los proyectos se comunican solo por archivos congelados que copia el usuario a mano (CONTRATO.md, contrato.schema.json, fixtures/\*.json). Nunca asumas el contenido de otro proyecto: si necesitas un dato que no está en tu carpeta, DETENTE y pregunta.

## Reglas de alcance

5. Prohibido refactorizar, renombrar, reformatear, "limpiar", actualizar dependencias o mejorar código existente que tu prompt no mencione. Cambios mínimos y localizados.
6. No cambies lógica de negocio: reglas del manual de extracción, selectores, flujos, contratos, autenticación, reglas de Firestore. Lo que no esté en tu lista de tareas, no se toca.
7. Si encuentras un bug, inconsistencia o mejora fuera de alcance: NO lo corrijas. Anótalo en la sección "Hallazgos fuera de alcance" de tu reporte (archivo, línea, descripción, propuesta).
8. No agregues dependencias nuevas sin que el prompt lo autorice. Si crees necesaria una, pregunta antes.
9. Si una tarea es ambigua o choca con estas reglas, DETENTE y pregunta. No adivines.

## Reglas de seguridad

10. Nunca imprimas, copies a archivos versionados ni registres en logs valores de claves, contraseñas, tokens ni contenido de .env. Solo nombres de variables.
11. No escribas credenciales en el código. Toda credencial viene de variables de entorno.
12. Prohibido: git push, git reset --hard, git clean, git push --force, borrar ramas ajenas, borrar carpetas de datos o perfiles de navegador.

## Protocolo de trabajo

13. Primero ejecuta el estado base (tests/lint del proyecto) y regístralo, para distinguir fallos preexistentes de los tuyos.
14. Crea la rama indicada en tu prompt. Haz commits pequeños y descriptivos. Al final, crea la etiqueta indicada. Nunca trabajes sobre la rama principal.
15. Antes de dar la sesión por terminada, ejecuta todas las verificaciones de tu prompt. No marques algo como hecho si no lo ejecutaste; si no pudiste ejecutarlo (por ejemplo, requiere captcha manual), dilo explícitamente.
16. Entrega al final un archivo REPORTE_FASE_1X.md en la raíz de tu proyecto con estas secciones: (1) Resumen, (2) Archivos creados/modificados con el motivo de cada uno, (3) Comandos ejecutados y su resultado, (4) Estado de pruebas antes y después, (5) Decisiones tomadas y desviaciones, (6) Hallazgos fuera de alcance (no corregidos), (7) Riesgos y pendientes para la Fase 2, (8) Cómo validar manualmente.
