from __future__ import annotations

LINE_COLORS = {
    "pressure": "#d84030",
    "return": "#2a63b8",
    "pilot": "#d6b72c",
    "suction": "#4e9b57",
    "drain": "#e58b32",
    "inactive": "#8a8f98",
}

# These cases are didactic redraws inspired by the user's reference video and course material.
# They are intentionally generic and do not reproduce proprietary OEM schematics.

SYSTEM_CASES = {
    "Sistema estacionario": {
        "Unidad hidráulica + cilindro": {
            "states": ["Reposo", "Avance", "Retroceso"],
            "description": "Unidad hidráulica fija: depósito, motor eléctrico, bomba, alivio, válvula direccional, cilindro y retorno filtrado.",
            "components": ["Depósito", "Motor eléctrico", "Bomba", "Alivio", "Direccional 4/3", "Cilindro", "Filtro de retorno"],
            "field": ["nivel/estado del aceite", "ruido de bomba", "presión antes de la direccional", "presión A/B", "caudal", "temperatura", "filtro"],
            "risks": ["presión residual", "carga atrapada", "fuga a alta presión", "sobretemperatura"],
        },
        "Prensa hidráulica": {
            "states": ["Reposo", "Aproximación", "Prensado", "Retorno"],
            "description": "Circuito estacionario orientado a distinguir movimiento por caudal y fuerza por presión durante una operación de prensado.",
            "components": ["Depósito", "Bomba", "Alivio", "Direccional", "Cilindro de prensa", "Manómetro", "Retorno"],
            "field": ["presión de trabajo", "caudal de aproximación", "fuerza de prensado", "retorno", "temperatura"],
            "risks": ["energía atrapada", "zona de atrapamiento", "carga suspendida o comprimida", "despresurización insuficiente"],
        },
    },
    "Camión minero": {
        "Levante de tolva": {
            "states": ["Raise", "Raise snub / overcenter", "Hold", "Float", "Lower"],
            "description": "Secuencia didáctica de levante de tolva inspirada en el video aportado: bomba, válvula de levante, load checks, control de descenso/overcenter y cilindros de levante.",
            "components": ["Bomba de implementos", "Válvula de levante", "Load check", "Alivio", "Control overcenter/descenso", "Cilindros de levante", "Retorno"],
            "field": ["presión de levante", "presión de retorno", "temperatura", "velocidad de tolva", "fugas internas", "sincronismo"],
            "risks": ["carga suspendida", "presión residual", "descenso no controlado", "zona de atrapamiento"],
        },
        "Dirección": {
            "states": ["Izquierda", "Neutro", "Derecha"],
            "description": "Dirección hidrostática genérica con HMU, señal load-sensing/prioridad, alivios cruzados y dos cilindros de dirección, siguiendo la lógica visible en el video.",
            "components": ["Bomba/prioridad", "HMU", "LS", "Cross-over relief", "Cilindro L", "Cilindro R", "Retorno"],
            "field": ["presión de alimentación", "presión LS", "presiones L/R", "respuesta HMU", "fugas de cilindros", "juego mecánico"],
            "risks": ["pérdida de dirección", "presión atrapada", "latigazo de manguera", "movimiento inesperado"],
        },
        "Freno / enfriamiento": {
            "states": ["Standby", "Brake cooling", "Service brake"],
            "description": "Vista funcional genérica para separar acumulación/seguridad, aplicación de freno y circuito de enfriamiento. No replica un circuito OEM concreto.",
            "components": ["Bomba", "Acumuladores", "Válvula de freno", "Circuito de enfriamiento", "Filtros", "Retorno"],
            "field": ["presión de acumulador", "presión de freno", "caudal de enfriamiento", "temperatura", "alarmas"],
            "risks": ["energía acumulada", "temperatura elevada", "pérdida de frenado", "presión residual"],
        },
    },
    "Cargador frontal": {
        "Levante de brazos": {
            "states": ["Raise", "Hold", "Float", "Lower"],
            "description": "Circuito móvil de implementos con banco direccional, dos cilindros de levante, alivio y función de flotación.",
            "components": ["Bomba", "Alivio", "Banco de implementos", "Load check", "Cilindros de levante", "Retorno"],
            "field": ["presión de implementos", "presiones A/B", "caudal", "tiempo de ciclo", "deriva", "fugas"],
            "risks": ["carga suspendida", "descenso inesperado", "presión residual", "mangueras en movimiento"],
        },
        "Inclinación de balde": {
            "states": ["Rollback", "Hold", "Dump"],
            "description": "Accionamiento del balde mediante cilindro de inclinación y mecanismo de barras simplificado, con lectura simultánea del plano y del movimiento.",
            "components": ["Bomba", "Sección tilt", "Load check", "Cilindro tilt", "Mecanismo de barras", "Retorno"],
            "field": ["presión A/B", "velocidad del cilindro", "deriva", "fugas internas", "pasadores/bujes"],
            "risks": ["movimiento del implemento", "carga inestable", "presión atrapada", "zona de pellizco"],
        },
        "Dirección articulada": {
            "states": ["Izquierda", "Neutro", "Derecha"],
            "description": "Dirección articulada con cilindros opuestos alrededor del pivote central. El modelo conecta válvula, cilindros y giro relativo de los bastidores.",
            "components": ["Bomba/prioridad", "Unidad de dirección", "Alivios cruzados", "Cilindros de articulación", "Pivote", "Retorno"],
            "field": ["presión L/R", "señal de mando", "fugas", "juego de pivote", "velocidad de giro"],
            "risks": ["aplastamiento en articulación", "movimiento inesperado", "presión residual"],
        },
    },
}


def _state(machine: str, subsystem: str, state: str) -> dict:
    # Common output contract for animated schematic + 3D.
    d = {
        "pressure": [],
        "return": [],
        "pilot": [],
        "suction": ["tank-pump"],
        "motion": "Sin movimiento",
        "machine_value": 0.0,
        "notes": [],
        "active_components": [],
    }

    if machine == "Sistema estacionario" and subsystem == "Unidad hidráulica + cilindro":
        if state == "Avance":
            d.update({'pressure': ["pump-relief", "relief-valve", "valve-A", "A-cylinder"], 'return': ["cylinder-B", "B-valve", "valve-filter", "filter-tank"], 'motion': "Cilindro avanza", 'machine_value': 1.0, 'active_components': ["Bomba", "Direccional 4/3", "Cilindro"]})
        elif state == "Retroceso":
            d.update({'pressure': ["pump-relief", "relief-valve", "valve-B", "B-cylinder"], 'return': ["cylinder-A", "A-valve", "valve-filter", "filter-tank"], 'motion': "Cilindro retrocede", 'machine_value': -1.0, 'active_components': ["Bomba", "Direccional 4/3", "Cilindro"]})
        else:
            d.update({'pressure': ["pump-relief", "relief-valve"], 'return': ["valve-filter", "filter-tank"], 'motion': "Actuador detenido; revisar lógica de centro de la válvula", 'active_components': ["Bomba", "Alivio"]})

    elif machine == "Sistema estacionario" and subsystem == "Prensa hidráulica":
        if state == "Aproximación":
            d.update({'pressure': ["pump-relief", "relief-valve", "valve-A", "A-cylinder"], 'return': ["cylinder-B", "B-valve", "valve-filter", "filter-tank"], 'motion': "La herramienta se aproxima a la pieza", 'machine_value': .55, 'active_components': ["Bomba", "Direccional", "Cilindro de prensa"]})
        elif state == "Prensado":
            d.update({'pressure': ["pump-relief", "relief-valve", "valve-A", "A-cylinder"], 'return': ["cylinder-B", "B-valve", "valve-filter", "filter-tank"], 'motion': "La presión aumenta hasta vencer la carga / alcanzar el trabajo", 'machine_value': 1.0, 'active_components': ["Bomba", "Alivio", "Cilindro de prensa", "Manómetro"], 'notes': ["Alta presión no implica necesariamente movimiento: depende de la carga resistente."]})
        elif state == "Retorno":
            d.update({'pressure': ["pump-relief", "relief-valve", "valve-B", "B-cylinder"], 'return': ["cylinder-A", "A-valve", "valve-filter", "filter-tank"], 'motion': "La herramienta retorna", 'machine_value': -1.0, 'active_components': ["Bomba", "Direccional", "Cilindro de prensa"]})
        else:
            d.update(pressure=["pump-relief"], motion="Prensa detenida; confirmar presión residual antes de intervenir", active_components=["Bomba"])

    elif machine == "Camión minero" and subsystem == "Levante de tolva":
        if state == "Raise":
            d.update({'pressure': ["pump-hoist", "hoist-loadcheck", "loadcheck-head", "head-hoistcyl"], 'return': ["hoistcyl-rod", "rod-hoist", "hoist-tank"], 'pilot': ["pilot-hoist"], 'motion': "Los cilindros elevan la tolva", 'machine_value': .55, 'active_components': ["Bomba de implementos", "Válvula de levante", "Load check", "Cilindros de levante"]})
        elif state == "Raise snub / overcenter":
            d.update({'pressure': ["pump-hoist", "hoist-overcenter", "overcenter-head", "head-hoistcyl"], 'return': ["hoistcyl-rod", "rod-hoist", "hoist-tank"], 'pilot': ["pilot-overcenter"], 'motion': "La tolva continúa elevándose con control de transición cerca del sobrecentro", 'machine_value': 1.0, 'active_components': ["Válvula de levante", "Control overcenter/descenso", "Cilindros de levante"], 'notes': ["La lógica exacta de snub/overcenter depende del fabricante; aquí se representa funcionalmente."]})
        elif state == "Float":
            d.update({'return': ["head-hoist", "rod-hoist", "hoist-tank"], 'pilot': ["pilot-float"], 'motion': "Las cámaras quedan descargadas/relacionadas con tanque según la función de flotación", 'machine_value': .35, 'active_components': ["Válvula de levante", "Cilindros de levante"]})
        elif state == "Lower":
            d.update({'pressure': ["pump-hoist", "hoist-rod", "rod-hoistcyl"], 'return': ["hoistcyl-head", "head-overcenter", "overcenter-hoist", "hoist-tank"], 'pilot': ["pilot-lower"], 'motion': "La tolva desciende bajo control de la válvula/elemento de descenso", 'machine_value': -.55, 'active_components': ["Válvula de levante", "Control overcenter/descenso", "Cilindros de levante"]})
        else:
            d.update(pressure=["pump-hoist"], motion="Tolva sostenida; las líneas de trabajo quedan bloqueadas según la lógica del control", machine_value=.55, active_components=["Load check", "Válvula de levante"])

    elif machine == "Camión minero" and subsystem == "Dirección":
        if state == "Izquierda":
            d.update({'pressure': ["pump-priority", "priority-hmu", "hmu-L", "L-steercyl"], 'return': ["steercyl-R", "R-hmu", "hmu-tank"], 'pilot': ["hmu-LS", "LS-priority"], 'motion': "Los cilindros producen giro a la izquierda", 'machine_value': -1.0, 'active_components': ["HMU", "LS", "Cilindro L", "Cilindro R"]})
        elif state == "Derecha":
            d.update({'pressure': ["pump-priority", "priority-hmu", "hmu-R", "R-steercyl"], 'return': ["steercyl-L", "L-hmu", "hmu-tank"], 'pilot': ["hmu-LS", "LS-priority"], 'motion': "Los cilindros producen giro a la derecha", 'machine_value': 1.0, 'active_components': ["HMU", "LS", "Cilindro L", "Cilindro R"]})
        else:
            d.update(pressure=["pump-priority"], pilot=["LS-priority"], motion="Dirección en neutro / standby", active_components=["Bomba/prioridad"])

    elif machine == "Camión minero" and subsystem == "Freno / enfriamiento":
        if state == "Brake cooling":
            d.update({'pressure': ["pump-cooler", "cooler-brakes"], 'return': ["brakes-filter", "filter-tank"], 'motion': "Circula aceite de enfriamiento por el circuito de frenos", 'machine_value': .4, 'active_components': ["Circuito de enfriamiento", "Filtros"]})
        elif state == "Service brake":
            d.update({'pressure': ["accum-brakevalve", "brakevalve-brakes"], 'return': ["brakes-tank"], 'motion': "Se aplica presión de servicio a los frenos", 'machine_value': 1.0, 'active_components': ["Acumuladores", "Válvula de freno"]})
        else:
            d.update(pressure=["pump-accum"], motion="Sistema en espera con energía disponible según la arquitectura", active_components=["Acumuladores"])

    elif machine == "Cargador frontal" and subsystem == "Levante de brazos":
        if state == "Raise":
            d.update({'pressure': ["pump-impl", "impl-loadcheck", "loadcheck-liftA", "liftA-cyl"], 'return': ["liftB-impl", "impl-tank"], 'pilot': ["pilot-lift"], 'motion': "Los brazos se elevan", 'machine_value': 1.0, 'active_components': ["Banco de implementos", "Load check", "Cilindros de levante"]})
        elif state == "Lower":
            d.update({'pressure': ["pump-impl", "impl-liftB", "liftB-cyl"], 'return': ["liftA-impl", "impl-tank"], 'pilot': ["pilot-lower"], 'motion': "Los brazos bajan", 'machine_value': -1.0, 'active_components': ["Banco de implementos", "Cilindros de levante"]})
        elif state == "Float":
            d.update({'return': ["liftA-impl", "liftB-impl", "impl-tank"], 'pilot': ["pilot-float"], 'motion': "Las cámaras quedan descargadas para seguir el terreno", 'machine_value': -.2, 'active_components': ["Banco de implementos"]})
        else:
            d.update(pressure=["pump-impl"], motion="Brazos sostenidos por la lógica de centro / load check", machine_value=.45, active_components=["Load check"])

    elif machine == "Cargador frontal" and subsystem == "Inclinación de balde":
        if state == "Rollback":
            d.update({'pressure': ["pump-tilt", "tilt-A", "A-tiltcyl"], 'return': ["tiltcyl-B", "B-tilt", "tilt-tank"], 'pilot': ["pilot-rollback"], 'motion': "El balde recoge / hace rollback", 'machine_value': 1.0, 'active_components': ["Sección tilt", "Cilindro tilt"]})
        elif state == "Dump":
            d.update({'pressure': ["pump-tilt", "tilt-B", "B-tiltcyl"], 'return': ["tiltcyl-A", "A-tilt", "tilt-tank"], 'pilot': ["pilot-dump"], 'motion': "El balde descarga", 'machine_value': -1.0, 'active_components': ["Sección tilt", "Cilindro tilt"]})
        else:
            d.update(pressure=["pump-tilt"], motion="El balde mantiene posición", active_components=["Load check"])

    elif machine == "Cargador frontal" and subsystem == "Dirección articulada":
        if state == "Izquierda":
            d.update({'pressure': ["pump-steer", "steer-L", "L-artcyl"], 'return': ["artcyl-R", "R-steer", "steer-tank"], 'pilot': ["steer-LS"], 'motion': "La articulación gira a la izquierda", 'machine_value': -1.0, 'active_components': ["Unidad de dirección", "Cilindros de articulación"]})
        elif state == "Derecha":
            d.update({'pressure': ["pump-steer", "steer-R", "R-artcyl"], 'return': ["artcyl-L", "L-steer", "steer-tank"], 'pilot': ["steer-LS"], 'motion': "La articulación gira a la derecha", 'machine_value': 1.0, 'active_components': ["Unidad de dirección", "Cilindros de articulación"]})
        else:
            d.update(pressure=["pump-steer"], pilot=["steer-LS"], motion="Dirección articulada en neutro", active_components=["Bomba/prioridad"])

    return d


def system_state(machine: str, subsystem: str, state: str) -> dict:
    out = _state(machine, subsystem, state)
    meta = SYSTEM_CASES[machine][subsystem]
    return {**out, **{k: meta[k] for k in ("description", "components", "field", "risks")}}


def course_comparison_rows():
    return [
        ["Fuente de potencia", "Motor eléctrico + bomba fija/variable", "Motor diésel/eléctrico + bomba; prioridad/LS según sistema"],
        ["Carga", "Más repetitiva y controlada", "Muy variable por maniobra, terreno y carga externa"],
        ["Tuberías", "Predominan tuberías fijas", "Mangueras flexibles, articulaciones y recorridos móviles"],
        ["Control", "Válvulas en manifold/unidad", "Bancos de implementos, pilotaje, LS, retención de carga"],
        ["Riesgo clave", "Prensa, atrapamiento, presión residual", "Carga suspendida, movimiento inesperado, dirección/freno"],
        ["Diagnóstico", "Puntos fijos de medición", "Puntos distribuidos; condición operacional cambia el dato"],
    ]


def diagnostic_cases():
    return {
        "Alta presión y sin movimiento": {
            "interpretation": "La presión existe, pero el actuador no vence o no puede desplazar la carga.",
            "checks": ["carga/bloqueo mecánico", "válvula direccional", "línea obstruida", "retención pilotada", "presión real en la cámara de trabajo"],
        },
        "Movimiento lento con presión normal": {
            "interpretation": "El problema apunta primero a caudal o restricción, no necesariamente a falta de presión.",
            "checks": ["caudal de bomba", "filtro", "válvula de caudal", "aceite frío", "restricciones", "fuga interna"],
        },
        "Baja presión y baja fuerza": {
            "interpretation": "La fuerza disponible es insuficiente; revisar generación, alivio y pérdidas internas.",
            "checks": ["bomba", "ajuste/alivio abierto", "fuga interna", "cilindro", "punto de medición"],
        },
        "Movimiento brusco": {
            "interpretation": "El sistema puede tener aire, carga inestable o respuesta irregular de la válvula.",
            "checks": ["aireación", "cavitación", "carga mecánica", "válvula", "mangueras", "temperatura"],
        },
        "Equipo detenido con presión residual": {
            "interpretation": "Detener la bomba no elimina la energía almacenada en líneas, cilindros o acumuladores.",
            "checks": ["bloqueo y etiquetado", "descarga de presión", "soporte mecánico de la carga", "verificación de cero energía"],
        },
    }
