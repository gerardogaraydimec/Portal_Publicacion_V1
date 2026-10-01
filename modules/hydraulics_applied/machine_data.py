from __future__ import annotations

MACHINE_CASES = {
    "Camión minero": {
        "Levante de tolva": {
            "states": ["Elevar", "Mantener", "Flotar", "Bajar"],
            "description": "Circuito didáctico de levante con cilindros telescópicos/paralelos, control direccional, alivio y función de control de descenso.",
            "components": ["Depósito", "Bomba", "Alivio", "Válvula de levante", "Control de descenso", "Cilindros de levante", "Retorno"],
            "field": ["presión en línea de levante", "presión de retorno", "temperatura", "fugas internas", "sincronismo de cilindros"],
        },
        "Dirección": {
            "states": ["Izquierda", "Neutro", "Derecha"],
            "description": "Arquitectura didáctica de dirección hidrostática con unidad de mando, alivios cruzados y dos cilindros de dirección.",
            "components": ["Bomba de dirección", "Control load-sensing", "Unidad de mando", "Alivios cruzados", "Cilindros de dirección", "Retorno"],
            "field": ["presión de alimentación", "señal LS", "presiones L/R", "juego mecánico", "fugas de cilindro"],
        },
        "Freno / enfriamiento": {
            "states": ["Reposo", "Servicio"],
            "description": "Vista funcional para relacionar alimentación, válvulas de freno y circuito de enfriamiento. Es deliberadamente conceptual y no replica una arquitectura OEM.",
            "components": ["Alimentación", "Válvula de freno", "Acumulación/seguridad", "Enfriamiento", "Retorno"],
            "field": ["presión de carga", "presión de freno", "temperatura de aceite", "caudal de enfriamiento", "alarmas"],
        },
    },
    "Cargador frontal": {
        "Levante de brazos": {
            "states": ["Elevar", "Mantener", "Flotar", "Bajar"],
            "description": "Circuito didáctico de implementos con dos cilindros de levante y una sección direccional de cuatro posiciones.",
            "components": ["Bomba", "Alivio", "Banco de válvulas", "Cilindros de levante", "Retorno"],
            "field": ["presión de implementos", "caudal", "deriva de brazos", "fugas", "tiempos de ciclo"],
        },
        "Inclinación de balde": {
            "states": ["Recoger", "Mantener", "Descargar"],
            "description": "Accionamiento del balde mediante cilindro de inclinación y mecanismo de barras simplificado.",
            "components": ["Bomba", "Sección de inclinación", "Cilindro de tilt", "Mecanismo del balde", "Retorno"],
            "field": ["presión A/B", "velocidad de cilindro", "fugas internas", "pasadores/bujes", "deriva"],
        },
        "Dirección articulada": {
            "states": ["Izquierda", "Neutro", "Derecha"],
            "description": "Dirección articulada didáctica mediante cilindros opuestos que rotan los bastidores delantero y trasero alrededor del pivote central.",
            "components": ["Bomba", "Unidad de dirección", "Cilindros de articulación", "Pivote", "Retorno"],
            "field": ["presiones de cilindros", "señal de mando", "fugas", "juego del pivote", "velocidad de giro"],
        },
    },
}


def state_paths(machine: str, subsystem: str, state: str) -> dict:
    pressure = []
    ret = []
    pilot = []
    motion = "Sin movimiento"
    if machine == "Camión minero" and subsystem == "Levante de tolva":
        if state == "Elevar":
            pressure = ["P→V", "V→A", "A→CIL"]
            ret = ["CIL-B→T"]
            pilot = ["pilotaje elevar"]
            motion = "Cilindros extienden y la tolva aumenta su ángulo"
        elif state == "Bajar":
            pressure = ["P→V", "V→B"]
            ret = ["CIL-A→control descenso→T"]
            pilot = ["pilotaje bajar"]
            motion = "La tolva desciende de forma controlada"
        elif state == "Flotar":
            ret = ["A/B→T"]
            motion = "Las cámaras quedan descargadas según la lógica de flotación"
        else:
            pressure = ["P→descarga/control"]
            motion = "La tolva queda sostenida hidráulicamente"
    elif subsystem in ("Dirección", "Dirección articulada"):
        if state == "Izquierda":
            pressure = ["P→unidad dirección", "unidad→L"]
            ret = ["R→T"]
            pilot = ["LS→control bomba"]
            motion = "La máquina gira a la izquierda"
        elif state == "Derecha":
            pressure = ["P→unidad dirección", "unidad→R"]
            ret = ["L→T"]
            pilot = ["LS→control bomba"]
            motion = "La máquina gira a la derecha"
        else:
            pressure = ["P→standby"]
            motion = "Dirección en neutro"
    elif machine == "Cargador frontal" and subsystem == "Levante de brazos":
        if state == "Elevar":
            pressure = ["P→sección lift", "A→cilindros"]
            ret = ["B→T"]
            motion = "Los brazos se elevan"
        elif state == "Bajar":
            pressure = ["P→sección lift", "B→cilindros"]
            ret = ["A→T"]
            motion = "Los brazos bajan"
        elif state == "Flotar":
            ret = ["A/B→T"]
            motion = "Los brazos pueden seguir el terreno"
        else:
            pressure = ["P→standby"]
            motion = "Los brazos mantienen posición"
    elif machine == "Cargador frontal" and subsystem == "Inclinación de balde":
        if state == "Recoger":
            pressure = ["P→tilt", "A→cilindro"]
            ret = ["B→T"]
            motion = "El balde recoge / hace rollback"
        elif state == "Descargar":
            pressure = ["P→tilt", "B→cilindro"]
            ret = ["A→T"]
            motion = "El balde descarga"
        else:
            pressure = ["P→standby"]
            motion = "El balde mantiene posición"
    else:
        pressure = ["P→servicio"] if state == "Servicio" else ["P→standby"]
        ret = ["servicio→T"] if state == "Servicio" else []
        motion = "Circuito de servicio activo" if state == "Servicio" else "Sistema en reposo"
    return {"pressure": pressure, "return": ret, "pilot": pilot, "motion": motion}
