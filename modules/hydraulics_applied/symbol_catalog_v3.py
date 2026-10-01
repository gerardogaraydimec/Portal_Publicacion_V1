from __future__ import annotations

"""Catálogo didáctico original de símbolos hidráulicos.

La geometría de los símbolos se dibuja en symbol_studio/component.py siguiendo
convenciones gráficas de potencia fluida (familia ISO 1219 / material didáctico
aportado por el usuario), sin reproducir láminas de terceros.
"""

PORTS = {
    "P": "alimentación / presión desde bomba",
    "T": "retorno principal a depósito",
    "A": "puerto de trabajo A",
    "B": "puerto de trabajo B",
    "X": "alimentación externa de pilotaje / señal",
    "Y": "drenaje externo de pilotaje",
    "L": "drenaje de fugas o carcasa",
}

FAMILIES = [
    "Líneas y conexiones",
    "Fuentes y depósitos",
    "Bombas y motores",
    "Actuadores lineales",
    "Válvulas direccionales",
    "Control de presión",
    "Control de caudal y bloqueo",
    "Acondicionamiento y medición",
    "Accionamientos",
]


def _s(family, name, ports, function, how, rest, field, failure, level="Básico"):
    return {
        "family": family,
        "name": name,
        "ports": ports,
        "function": function,
        "how": how,
        "rest": rest,
        "field": field,
        "failure": failure,
        "level": level,
    }


SYMBOLS = {
    # Líneas y conexiones
    "main_line": _s("Líneas y conexiones", "Línea principal", "—", "Transporta caudal de potencia.", "Línea continua.", "No aplica.", "Presión, caída de presión, fuga, temperatura.", "Restricción, fuga, aplastamiento."),
    "pilot_line": _s("Líneas y conexiones", "Línea de pilotaje", "X / señal", "Transporta una señal hidráulica de mando.", "Línea discontinua de trazos largos.", "Depende de la lógica.", "Presión de pilotaje y continuidad.", "Pilotaje insuficiente, orificio tapado."),
    "drain_line": _s("Líneas y conexiones", "Línea de drenaje", "Y / L", "Evacúa fugas internas o aceite de control.", "Línea discontinua de trazos cortos.", "Debe trabajar con baja contrapresión.", "Contrapresión de carcasa/pilotaje.", "Drenaje obstruido, sellos dañados."),
    "flex_line": _s("Líneas y conexiones", "Línea flexible", "—", "Representa manguera o conductor flexible.", "Arco entre puntos terminales.", "No aplica.", "Abrasión, radio de curvatura, roce y fitting.", "Fuga, colapso, rotura."),
    "junction": _s("Líneas y conexiones", "Unión de líneas", "—", "Indica conexión hidráulica entre conductores.", "Cruce con punto de unión.", "No aplica.", "Verificar que el nodo realmente conecta.", "Interpretar un cruce como unión o viceversa."),
    "crossing": _s("Líneas y conexiones", "Cruce sin conexión", "—", "Dos líneas se cruzan sin comunicarse.", "Cruce sin punto / puente gráfico.", "No aplica.", "Seguir cada línea por separado.", "Diagnóstico erróneo por asumir conexión."),
    "fixed_orifice": _s("Líneas y conexiones", "Restricción fija", "A-B", "Produce una caída de presión dependiente del caudal.", "Dos curvas enfrentadas sin flecha diagonal.", "Siempre presente.", "Δp a través de la restricción.", "Obstrucción, erosión, calentamiento.", "Intermedio"),
    "test_point": _s("Líneas y conexiones", "Punto de prueba", "M / test", "Permite conectar instrumentación para diagnóstico.", "Terminal de medición marcado sobre la línea.", "No modifica el circuito si está cerrado.", "Conectar manómetro/transductor con rango adecuado.", "Medir en punto equivocado."),
    "quick_disconnect": _s("Líneas y conexiones", "Acople rápido con retención", "A-B", "Permite desacoplar una línea minimizando pérdida de fluido.", "Dos mitades de acople con retenciones.", "Cerrado al separar.", "Acople completo, suciedad, caída de presión.", "Acople parcial, retención trabada."),

    # Fuentes y depósitos
    "reservoir_vented": _s("Fuentes y depósitos", "Depósito abierto / ventilado", "T / succión", "Almacena fluido y referencia el retorno a baja presión.", "Recipiente abierto en la parte superior.", "Atmosférico.", "Nivel, respiradero, espuma, contaminación, temperatura.", "Nivel bajo, aireación, contaminación."),
    "reservoir_pressurized": _s("Fuentes y depósitos", "Depósito presurizado", "T / succión", "Mantiene el fluido por encima de presión atmosférica.", "Recipiente cerrado.", "Presurizado.", "Presión del depósito y condición del venteo.", "Sobrepresión o pérdida de presurización.", "Intermedio"),
    "tank_above": _s("Fuentes y depósitos", "Retorno sobre nivel", "T", "Descarga al depósito por encima del nivel del fluido.", "Línea termina sobre la línea de nivel.", "No aplica.", "Riesgo de aireación / espuma.", "Aireación por caída libre."),
    "tank_below": _s("Fuentes y depósitos", "Retorno bajo nivel", "T", "Descarga al depósito bajo el nivel del fluido.", "Línea penetra bajo la línea de nivel.", "No aplica.", "Ubicación y profundidad del retorno.", "Remoción deficiente de aire / turbulencia si está mal ubicado."),

    # Bombas y motores
    "pump_fixed": _s("Bombas y motores", "Bomba de desplazamiento fijo", "S-P", "Convierte potencia mecánica en caudal hidráulico.", "Círculo con triángulo apuntando hacia afuera.", "Mientras gira desplaza volumen por revolución.", "Caudal real, succión, ruido, temperatura, drenaje.", "Cavitación, desgaste, fuga interna."),
    "pump_variable": _s("Bombas y motores", "Bomba de desplazamiento variable", "S-P-X/L según diseño", "Entrega caudal variable modificando su desplazamiento.", "Símbolo de bomba con flecha diagonal de variabilidad.", "Depende del control.", "Desplazamiento, compensador, LS, drenaje.", "Desajuste, fuga interna, control bloqueado.", "Intermedio"),
    "pump_reversible": _s("Bombas y motores", "Bomba reversible", "A-B", "Puede invertir el sentido de entrega.", "Dos triángulos opuestos apuntando hacia afuera.", "Neutro según control.", "Presiones de ambos lados y drenaje.", "Pérdida de carga, fuga interna.", "Avanzado"),
    "motor_fixed": _s("Bombas y motores", "Motor hidráulico", "A-B / L", "Convierte presión y caudal en torque y giro.", "Círculo con triángulo apuntando hacia adentro.", "Se detiene si no hay caudal.", "Δp, caudal, drenaje de carcasa, velocidad.", "Drenaje alto, cavitación, fuga interna."),
    "motor_reversible": _s("Bombas y motores", "Motor hidráulico reversible", "A-B / L", "Genera giro en ambos sentidos.", "Dos triángulos opuestos apuntando hacia el centro.", "Depende de la válvula o bomba reversible.", "Presiones A/B, caudal y drenaje.", "Contrapresión, fuga interna.", "Intermedio"),

    # Actuadores
    "cyl_single": _s("Actuadores lineales", "Cilindro de simple efecto", "A", "Genera fuerza hidráulica en un solo sentido.", "Rectángulo con un puerto y vástago.", "Retorno por carga o resorte según diseño.", "Presión A, carrera, sellos y carga.", "Fuga, trabamiento, desalineación."),
    "cyl_double": _s("Actuadores lineales", "Cilindro de doble efecto", "A-B", "Genera movimiento hidráulico en avance y retroceso.", "Rectángulo, pistón, vástago y dos puertos.", "Depende del centro de la válvula.", "Presiones A/B, deriva, fugas, alineamiento.", "Fuga interna, sello, carga lateral."),
    "cyl_double_rod": _s("Actuadores lineales", "Cilindro de doble vástago", "A-B", "Área efectiva simétrica a ambos lados.", "Vástago sale por ambos extremos.", "Depende del control.", "Sincronismo, carrera, sellos.", "Fugas, desalineación."),
    "cyl_cushion": _s("Actuadores lineales", "Cilindro con amortiguación", "A-B", "Reduce velocidad cerca de fin de carrera.", "Marcas de amortiguación en los extremos.", "Activa cerca del fin de carrera.", "Tiempo de desaceleración, ajuste y presión pico.", "Golpe de fin de carrera, ajuste cerrado."),
    "cyl_telescopic": _s("Actuadores lineales", "Cilindro telescópico", "A / A-B", "Obtiene gran carrera con longitud retraída compacta.", "Etapas concéntricas escalonadas.", "Secuencia de etapas dependiente del diseño.", "Presión por etapa, sincronización y fugas.", "Etapa trabada, desalineación.", "Intermedio"),

    # Direccionales
    "dcv_22_nc": _s("Válvulas direccionales", "Válvula 2/2 normalmente cerrada", "P-A", "Abre o bloquea un paso.", "Dos casillas; reposo bloqueado.", "Cerrada.", "Presión antes/después y accionamiento.", "No abre, fuga en cerrado."),
    "dcv_32_nc": _s("Válvulas direccionales", "Válvula 3/2 normalmente cerrada", "P-A-T", "Alimenta y descarga un actuador simple.", "Dos casillas y tres vías.", "P cerrado; A comunicado con T según configuración.", "P/A/T y accionamiento.", "Spool trabado, pilotaje deficiente."),
    "dcv_42": _s("Válvulas direccionales", "Válvula 4/2", "P-T-A-B", "Invierte el sentido de un actuador de doble efecto.", "Dos casillas y cuatro vías.", "Una de las dos posiciones según retorno/retención.", "Presiones A/B y conmutación.", "No conmuta, fuga interna."),
    "dcv_43_closed": _s("Válvulas direccionales", "4/3 centro cerrado", "P-T-A-B", "Bloquea los cuatro puertos en neutro.", "Tres casillas; centro con puertos bloqueados.", "Centro cerrado.", "Presión P en neutro, deriva del actuador.", "Calentamiento con bomba fija si no hay descarga.", "Intermedio"),
    "dcv_43_open": _s("Válvulas direccionales", "4/3 centro abierto", "P-T-A-B", "Comunica múltiples puertos en neutro para descarga.", "Centro con conexiones abiertas.", "Centro abierto.", "Presiones en P/A/B/T en neutro.", "Movimiento no deseado según carga.", "Intermedio"),
    "dcv_43_tandem": _s("Válvulas direccionales", "4/3 centro tándem", "P-T-A-B", "Descarga P→T y bloquea A/B en neutro.", "Centro P-T comunicado; A/B bloqueados.", "Centro tándem.", "Baja presión de bomba y retención del actuador.", "Deriva por fugas o carga.", "Intermedio"),
    "dcv_43_float": _s("Válvulas direccionales", "4/3 centro flotante", "P-T-A-B", "Comunica A/B con T y bloquea P en neutro.", "Centro A y B descargados a T.", "Centro flotante.", "Movimiento por carga externa y presión baja en A/B.", "Descenso no controlado si se usa mal.", "Intermedio"),
    "dcv_prop": _s("Válvulas direccionales", "Válvula proporcional 4/3", "P-T-A-B", "Modula apertura y caudal de forma continua.", "Direccional con indicación proporcional / posición continua.", "Centro según diseño.", "Señal eléctrica, Δp, posición spool y caudal.", "Contaminación, histéresis, señal incorrecta.", "Avanzado"),

    # Presión
    "relief": _s("Control de presión", "Válvula de alivio", "P-T", "Limita presión máxima derivando caudal a tanque.", "Válvula de presión normalmente cerrada con resorte.", "Cerrada hasta alcanzar ajuste.", "Presión de apertura, caudal por alivio, temperatura.", "Ajuste bajo, trabada abierta, chatter."),
    "reducing": _s("Control de presión", "Válvula reductora", "P-A / Y", "Mantiene presión menor aguas abajo.", "Válvula normalmente abierta sensando presión de salida.", "Abierta mientras la presión reducida no excede ajuste.", "Presión entrada/salida y drenaje.", "Drenaje bloqueado, ajuste incorrecto."),
    "sequence": _s("Control de presión", "Válvula de secuencia", "P-A / X/Y", "Habilita una segunda función cuando se alcanza una presión.", "Válvula de presión normalmente cerrada con salida a una rama.", "Cerrada hasta presión de secuencia.", "Presión de apertura y orden de actuadores.", "Secuencia prematura, drenaje/pilotaje incorrecto."),
    "counterbalance": _s("Control de presión", "Válvula contrabalance", "A-B / pilot", "Sostiene y controla cargas motrices / verticales.", "Válvula de presión con check de libre flujo y pilotaje.", "Restringe salida de la carga hasta recibir condición de apertura.", "Presión de carga, pilotaje y estabilidad de descenso.", "Carga cae, oscilación, calentamiento.", "Avanzado"),
    "unloading": _s("Control de presión", "Válvula de descarga", "P-T / pilot", "Descarga la bomba a baja presión cuando se cumple una señal.", "Válvula de presión pilotada hacia tanque.", "Según señal de pilotaje.", "Presión de carga/descarga y temperatura.", "Bomba trabajando contra alivio innecesariamente.", "Avanzado"),

    # Caudal/bloqueo
    "check": _s("Control de caudal y bloqueo", "Válvula de retención", "A-B", "Permite flujo en un sentido y bloquea el opuesto.", "Asiento/bola contra asiento.", "Cerrada al flujo inverso.", "Δp y estanqueidad.", "No abre, fuga inversa."),
    "pilot_check": _s("Control de caudal y bloqueo", "Retención pilotada", "A-B / X", "Bloquea una carga y abre mediante presión de pilotaje.", "Check dentro de envolvente con puerto piloto.", "Bloqueada en reversa sin pilotaje.", "Presión de pilotaje y carga atrapada.", "No desbloquea, fuga interna.", "Intermedio"),
    "flow_adjust": _s("Control de caudal y bloqueo", "Control de caudal ajustable", "A-B", "Regula velocidad variando el área de paso.", "Restricción con flecha diagonal.", "Ajuste fijo durante operación salvo intervención.", "Δp y caudal.", "Ajuste incorrecto, contaminación."),
    "flow_oneway": _s("Control de caudal y bloqueo", "Regulador unidireccional", "A-B", "Regula en un sentido y deja libre el retorno.", "Restricción ajustable en paralelo con check.", "Depende del sentido.", "Caudal por cada sentido y orientación del check.", "Montaje invertido, check trabado.", "Intermedio"),
    "flow_comp": _s("Control de caudal y bloqueo", "Control de caudal compensado", "A-B", "Mantiene caudal más estable frente a cambios de presión.", "Restricción ajustable con compensador.", "Actúa modulando para sostener Δp.", "Caudal real y compensación.", "Spool compensador pegado, suciedad.", "Avanzado"),
    "shuttle": _s("Control de caudal y bloqueo", "Válvula shuttle / selectora", "A1-A2-B", "Selecciona automáticamente la mayor de dos señales.", "Dos entradas convergen a una salida mediante elemento móvil.", "Toma una de las dos entradas.", "Presiones en ambas entradas y salida.", "Señal LS incorrecta, bola trabada.", "Intermedio"),

    # Acondicionamiento/medición
    "filter": _s("Acondicionamiento y medición", "Filtro / colador", "IN-OUT", "Retiene partículas del fluido.", "Rombo con línea interior.", "En servicio; puede incorporar bypass.", "Δp, indicador de saturación, elemento.", "Filtro saturado, bypass abierto."),
    "cooler": _s("Acondicionamiento y medición", "Enfriador", "IN-OUT", "Extrae calor del fluido.", "Rombo con indicación térmica.", "Según termostato/control.", "Temperaturas entrada/salida y caudal.", "Suciedad, restricción, baja transferencia."),
    "accumulator_gas": _s("Acondicionamiento y medición", "Acumulador cargado con gas", "P", "Almacena energía hidráulica y amortigua transitorios.", "Recipiente con separación gas/fluido.", "Puede permanecer presurizado con bomba detenida.", "Pre-carga, presión mínima/máxima, aislamiento.", "Pérdida de precarga, energía residual.", "Intermedio"),
    "gauge": _s("Acondicionamiento y medición", "Manómetro", "M", "Mide presión local.", "Círculo con aguja.", "Lectura depende del punto.", "Rango, pulsación, cero y ubicación.", "Instrumento fuera de rango/descalibrado."),
    "pressure_switch": _s("Acondicionamiento y medición", "Presostato", "P + eléctrico", "Convierte una condición de presión en una señal discreta.", "Elemento de presión asociado a contacto eléctrico.", "Conmuta en ajuste.", "Punto de consigna e histéresis.", "Contacto/sensor defectuoso."),
    "flow_meter": _s("Acondicionamiento y medición", "Caudalímetro", "IN-OUT", "Mide caudal real.", "Símbolo de medición insertado en la línea.", "No aplica.", "Rango, Δp y dirección.", "Lectura incorrecta o restricción añadida."),
    "temperature": _s("Acondicionamiento y medición", "Indicador de temperatura", "—", "Mide temperatura del fluido/componente.", "Círculo con indicador térmico.", "No aplica.", "Temperatura y tendencia.", "Sensor mal ubicado o fuera de rango."),

    # Accionamientos
    "spring": _s("Accionamientos", "Retorno por resorte", "—", "Lleva el elemento móvil a su posición de reposo.", "Zigzag de resorte junto a la válvula.", "Define la posición de reposo.", "Integridad y precarga.", "Resorte roto o fatigado."),
    "manual": _s("Accionamientos", "Accionamiento manual", "—", "El operador desplaza directamente la válvula.", "Símbolo manual en el extremo del spool.", "Según posición del mando.", "Recorrido, trabamiento, detent.", "Mando duro o incompleto."),
    "solenoid": _s("Accionamientos", "Solenoide", "eléctrico", "Convierte señal eléctrica en fuerza de accionamiento.", "Rectángulo/diagonal de bobina en el extremo de la válvula.", "Desenergizado salvo orden.", "Tensión, corriente, comando y movimiento del spool.", "Bobina abierta, señal ausente, spool pegado."),
    "hyd_pilot": _s("Accionamientos", "Pilotaje hidráulico", "X/Y", "Usa presión de mando para desplazar una válvula.", "Triángulo negro / conexión de pilotaje.", "Depende de señal.", "Presión piloto y drenaje.", "Pilotaje insuficiente, drenaje bloqueado."),
    "detent": _s("Accionamientos", "Enclavamiento / detent", "—", "Mantiene una posición sin acción continua del operador.", "Muesca mecánica asociada al actuador.", "Conserva posición hasta superar el enclavamiento.", "Liberación y desgaste.", "Válvula no retorna o no retiene."),
}


def families() -> list[str]:
    present = {v["family"] for v in SYMBOLS.values()}
    return [f for f in FAMILIES if f in present]


def symbols_in_family(family: str) -> list[tuple[str, str]]:
    return [(k, v["name"]) for k, v in SYMBOLS.items() if v["family"] == family]
