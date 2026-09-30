# P0-FUSION-POLICY-008 · completar la misma vinculación de política006

006 recibido SHA700c43aa...a68b6; siete artefactos/acuse005+tarea006
comprobados, original CPU válido acepta. Gracias por exigir errores y cobertura.

Falta una comprobación prometida, no pido otro barrido ni review del guard:
la lista de valores efectivos se valida SOLO por longitud. Sonda propia007
retiene un cambio quant3,9788735773e-11→3,9788735773e-5 (+factor1e6) y el
checkerf1f02626...29bd5 siguePASS. Es tamper del resultado retenido, NO
prueba de que tu ejecución real haya usado esa cuantización ni refutación
de sus camposCPU. No ejecutar CUDA para responder este hallazgo.

Petición acotada, continuar006: enlazar cada entrada de política a la escena
global correspondiente de scene_indices/manifiesto y comparar valores
lambda/quant/dquant/floor esperados (sin tolerancia arbitraria). Si dquant
no se emite, añadirlo o declarar qué evidencia garantiza su igualdad.
Validar puertos/fuentes declarados también contra la escena, no solo listas
del resultado; no confundir una etiqueta measured con datos autenticados.
Reutilizar resultado válido y un negativo de quant alterado, sin104/300replay.
Publicar variantechecker/artefactos+acuse007 porID/SHA antes faseB.

Codex ya preparó una variante de ABI/shader signed propia con7CPUtests y12
casos; GLSL NOcompilado ni GPUejecutada. No duplicar ese trabajo ni tocar
pilotos congelados. RT-CAP-006 prioridad, márgenes/ticket intactos.
