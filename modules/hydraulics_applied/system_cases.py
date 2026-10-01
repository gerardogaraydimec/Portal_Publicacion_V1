from __future__ import annotations

LINE_COLORS = {
    "pressure": "#d84030",
    "return": "#2a63b8",
    "pilot": "#d6b72c",
    "suction": "#4e9b57",
    "drain": "#e58b32",
    "inactive": "#8a8f98",
}

# Los circuitos son reconstrucciones didácticas genéricas basadas en convenciones
# de potencia fluida y en el material de formación aportado. No son esquemas OEM.
SYSTEM_CASES = {
    "Sistema estacionario": {
        "Cilindro 4/3 básico": {
            "circuit": "stationary_basic",
            "states": ["Reposo", "Avance", "Retroceso"],
            "description": "Circuito base para aprender a leer P, T, A y B, distinguir caudal de movimiento y presión de carga, y ubicar puntos de medición.",
            "components": ["Depósito", "Bomba fija", "Alivio", "Direccional 4/3", "Cilindro doble efecto", "Filtro retorno"],
            "field": ["P antes de la válvula", "A/B en maniobra", "caudal", "temperatura", "filtro"],
            "risks": ["presión residual", "atrapamiento", "fuga a alta presión"],
            "learning": "Primero identifique la condición de centro; después trace la casilla accionada y recién entonces prediga movimiento.",
        },
        "Carga vertical + contrabalance": {
            "circuit": "counterbalance",
            "states": ["Elevar", "Sostener", "Bajar controlado"],
            "description": "Circuito de carga motriz para entender por qué una carga vertical no debe quedar gobernada solo por la direccional.",
            "components": ["Bomba", "Alivio", "Direccional", "Contrabalance", "Cilindro vertical", "Manómetro"],
            "field": ["presión de carga", "presión piloto", "presión aguas arriba del contrabalance", "estabilidad del descenso"],
            "risks": ["caída de carga", "presión atrapada", "oscilación"],
            "learning": "La válvula de contrabalance crea una contrapresión controlada y abre por presión/pilotaje para evitar descenso libre.",
        },
        "Avance regenerativo": {
            "circuit": "regenerative",
            "states": ["Reposo", "Avance rápido", "Trabajo", "Retroceso"],
            "description": "Circuito para comparar velocidad y fuerza cuando el caudal del lado de vástago se suma al caudal de bomba durante avance regenerativo.",
            "components": ["Bomba", "Alivio", "Direccional", "Check", "Cilindro", "Retorno"],
            "field": ["Q bomba", "Q regenerado", "presiones A/B", "velocidad de avance", "fuerza disponible"],
            "risks": ["velocidad inesperada", "fuerza menor durante regeneración"],
            "learning": "En regeneración aumenta el caudal efectivo de avance, pero disminuye la fuerza neta porque ambas cámaras quedan presurizadas.",
        },
        "Secuencia de dos cilindros": {
            "circuit": "sequence",
            "states": ["Reposo", "Cilindro A", "Cilindro B", "Retorno"],
            "description": "Secuencia por presión: el segundo actuador recibe caudal cuando la primera función alcanza la condición de presión establecida.",
            "components": ["Bomba", "Alivio", "Direccional", "Válvula de secuencia", "Cilindro A", "Cilindro B"],
            "field": ["presión antes de secuencia", "ajuste de secuencia", "presiones A/B", "orden de movimiento"],
            "risks": ["secuencia prematura", "ajuste excesivo", "movimiento inesperado"],
            "learning": "No confunda orden temporal con control eléctrico: aquí la propia presión del circuito habilita la siguiente función.",
        },
    },
    "Camión minero": {
        "Levante de tolva": {
            "circuit": "truck_hoist",
            "states": ["Raise", "Hold", "Float", "Lower"],
            "description": "Arquitectura funcional genérica de levante: bomba/compensación, válvula de levante, retención de carga, control de descenso y cilindros telescópicos equivalentes.",
            "components": ["Bomba", "Control/compensador", "Hoist valve", "Load check", "Control de descenso", "Cilindros", "Tanque"],
            "field": ["P principal", "A/B de levante", "presión de carga", "pilotaje", "tiempo de ciclo", "temperatura"],
            "risks": ["carga suspendida", "descenso no controlado", "presión residual", "zona de aplastamiento"],
            "learning": "La posición de la válvula no basta: debe verificarse qué cámara recibe presión, cuál descarga y qué elemento sostiene la carga.",
        },
        "Dirección hidrostática": {
            "circuit": "steering",
            "states": ["Izquierda", "Neutro", "Derecha"],
            "description": "Dirección hidrostática genérica con prioridad, unidad de medición/dirección (HMU), señal LS y dos cilindros opuestos.",
            "components": ["Bomba", "Prioridad", "HMU", "LS", "Alivios cruzados", "Cilindros L/R", "Retorno"],
            "field": ["P alimentación", "LS", "L/R", "caudal", "fuga de cilindros", "respuesta del mando"],
            "risks": ["pérdida de dirección", "movimiento inesperado", "presión atrapada"],
            "learning": "La señal LS representa la carga que debe 'ver' el control de bomba/prioridad; no es una línea de potencia principal.",
        },
        "Freno con acumuladores": {
            "circuit": "brake_accum",
            "states": ["Carga", "Standby", "Aplicación"],
            "description": "Circuito didáctico de almacenamiento de energía: carga de acumuladores, espera y aplicación de freno.",
            "components": ["Bomba", "Válvula de carga", "Acumuladores", "Válvula de freno", "Frenos", "Retorno"],
            "field": ["presión de acumulador", "cut-in/cut-out", "presión de aplicación", "fugas", "temperatura"],
            "risks": ["energía residual", "pérdida de frenado", "descarga intempestiva"],
            "learning": "Un equipo detenido puede conservar energía. El acumulador debe tratarse como una fuente activa hasta verificar descarga segura.",
        },
    },
    "Cargador frontal": {
        "Levante de brazos LS": {
            "circuit": "loader_lift_ls",
            "states": ["Raise", "Hold", "Float", "Lower"],
            "description": "Circuito genérico de implementos con bomba variable LS, compensación de sección, load check y función float.",
            "components": ["Bomba LS", "Compensador", "Banco implementos", "Load check", "Cilindros lift", "Shuttle LS", "Tanque"],
            "field": ["P bomba", "LS", "Δp de margen", "A/B", "caudal de sección", "deriva"],
            "risks": ["carga suspendida", "cavitación", "descenso inesperado"],
            "learning": "En LS la bomba ajusta desplazamiento para mantener margen de presión sobre la carga; el mando dosifica caudal y por tanto velocidad.",
        },
        "Inclinación de balde": {
            "circuit": "loader_tilt",
            "states": ["Rollback", "Hold", "Dump"],
            "description": "Sección de tilt con retención de carga y control de ambos puertos del cilindro.",
            "components": ["Bomba", "Banco implementos", "Load check", "Cilindro tilt", "Retorno"],
            "field": ["P", "A/B", "velocidad", "deriva", "fuga interna"],
            "risks": ["movimiento del implemento", "zona de pellizco", "presión atrapada"],
            "learning": "La cinemática del balde amplifica o reduce el efecto del cilindro; el circuito debe leerse junto al mecanismo físico.",
        },
        "Dirección articulada": {
            "circuit": "steering",
            "states": ["Izquierda", "Neutro", "Derecha"],
            "description": "Dirección articulada con dos cilindros opuestos y control hidrostático.",
            "components": ["Bomba/prioridad", "Unidad de dirección", "LS", "Alivios cruzados", "Cilindros", "Pivote", "Retorno"],
            "field": ["P", "LS", "L/R", "fuga", "juego de pivote"],
            "risks": ["aplastamiento en articulación", "movimiento inesperado", "presión residual"],
            "learning": "Observe simultáneamente el circuito y el giro relativo de los bastidores: un cilindro se extiende mientras el opuesto retrae.",
        },
    },
}


def _base():
    return {
        "pressure": [], "return": [], "pilot": [], "suction": ["tank-pump"], "drain": [],
        "motion": "Sin movimiento", "machine_value": 0.0, "active_components": [], "notes": [],
        "readings": {},
    }


def _set(d, *, pressure=None, ret=None, pilot=None, drain=None, motion=None, value=None, active=None, notes=None, readings=None):
    if pressure is not None: d["pressure"] = pressure
    if ret is not None: d["return"] = ret
    if pilot is not None: d["pilot"] = pilot
    if drain is not None: d["drain"] = drain
    if motion is not None: d["motion"] = motion
    if value is not None: d["machine_value"] = value
    if active is not None: d["active_components"] = active
    if notes is not None: d["notes"] = notes
    if readings is not None: d["readings"] = readings
    return d


def _state(machine: str, subsystem: str, state: str):
    d=_base()
    if machine=="Sistema estacionario" and subsystem=="Cilindro 4/3 básico":
        if state=="Avance":
            return _set(d,pressure=["pump-p","p-valve","valve-a","a-cyl"],ret=["cyl-b","b-valve","valve-t","t-filter","filter-tank"],motion="El cilindro avanza",value=1,active=["Bomba fija","Direccional 4/3","Cilindro doble efecto"],readings={"P":"sube según carga","A":"alta","B":"baja/retorno","T":"baja"})
        if state=="Retroceso":
            return _set(d,pressure=["pump-p","p-valve","valve-b","b-cyl"],ret=["cyl-a","a-valve","valve-t","t-filter","filter-tank"],motion="El cilindro retrocede",value=-1,active=["Bomba fija","Direccional 4/3","Cilindro doble efecto"],readings={"P":"sube según carga","A":"baja/retorno","B":"alta","T":"baja"})
        return _set(d,pressure=["pump-p","p-relief"],ret=["relief-t","t-filter","filter-tank"],motion="Reposo: centro de la 4/3 define descarga y bloqueo",active=["Bomba fija","Alivio"],readings={"P":"depende del centro","A":"bloqueada","B":"bloqueada","T":"retorno"})

    if machine=="Sistema estacionario" and subsystem=="Carga vertical + contrabalance":
        if state=="Elevar":
            return _set(d,pressure=["pump-p","p-valve","valve-a","a-cb-check","cb-cyl"],ret=["cyl-b","b-valve","valve-t","t-tank"],motion="La carga sube; el check del contrabalance permite libre flujo hacia el cilindro",value=1,active=["Bomba","Direccional","Contrabalance","Cilindro vertical"],readings={"P":"según carga","A/carga":"alta","piloto":"baja","T":"baja"})
        if state=="Bajar controlado":
            return _set(d,pressure=["pump-p","p-valve","valve-b","b-cyl"],ret=["cyl-a","a-cb","cb-valve","valve-t","t-tank"],pilot=["b-pilot","pilot-cb"],motion="La bomba presuriza el lado de descenso y el pilotaje abre el contrabalance de forma controlada",value=-1,active=["Direccional","Contrabalance","Cilindro vertical"],readings={"B":"presión de mando","piloto":"presente","A/carga":"controlada > retorno","T":"baja"})
        return _set(d,pressure=["load-cb"],motion="Carga sostenida: el contrabalance bloquea la salida del aceite",value=.45,active=["Contrabalance"],readings={"A/carga":"presión de carga atrapada","piloto":"0/bajo","T":"baja"})

    if machine=="Sistema estacionario" and subsystem=="Avance regenerativo":
        if state=="Avance rápido":
            return _set(d,pressure=["pump-p","p-valve","valve-a","a-cyl","cyl-b-regen","regen-a"],motion="Avance rápido: Qbomba + Qretorno del lado vástago alimentan la cámara plena",value=.85,active=["Bomba","Direccional","Check","Cilindro"],notes=["La fuerza neta es menor que en avance convencional porque ambas cámaras están presurizadas."],readings={"A":"alta","B":"alta","Q efectivo A":"Qbomba + Qreg","T":"mínimo"})
        if state=="Trabajo":
            return _set(d,pressure=["pump-p","p-valve","valve-a","a-cyl"],ret=["cyl-b","b-valve","valve-t","t-tank"],motion="Avance de trabajo: circuito convencional para recuperar fuerza",value=1,active=["Bomba","Direccional","Cilindro"],readings={"A":"alta según carga","B":"retorno","Q A":"Qbomba"})
        if state=="Retroceso":
            return _set(d,pressure=["pump-p","p-valve","valve-b","b-cyl"],ret=["cyl-a","a-valve","valve-t","t-tank"],motion="Retroceso convencional",value=-1,active=["Bomba","Direccional","Cilindro"],readings={"B":"alta","A":"retorno"})
        return _set(d,pressure=["pump-p"],motion="Reposo",active=["Bomba"],readings={"P":"standby/descarga según centro"})

    if machine=="Sistema estacionario" and subsystem=="Secuencia de dos cilindros":
        if state=="Cilindro A":
            return _set(d,pressure=["pump-p","p-valve","valve-a","a-cyla"],ret=["cyla-ret","ret-valve","valve-t","t-tank"],motion="Primero avanza A; la válvula de secuencia permanece cerrada",value=.35,active=["Direccional","Cilindro A"],readings={"P antes secuencia":"menor que ajuste","A":"moviendo"})
        if state=="Cilindro B":
            return _set(d,pressure=["pump-p","p-valve","valve-a","a-seq","seq-cylb"],ret=["cylb-ret","ret-valve","valve-t","t-tank"],motion="Al aumentar la presión tras completar A, abre secuencia y avanza B",value=1,active=["Válvula de secuencia","Cilindro A","Cilindro B"],readings={"P antes secuencia":"≥ ajuste","B":"presurizado"})
        if state=="Retorno":
            return _set(d,pressure=["pump-p","p-valve","valve-ret","ret-cyls"],ret=["cyls-a","a-valve","valve-t","t-tank"],motion="Retorno de los actuadores por la ruta de reversa/check correspondiente",value=-1,active=["Direccional","Cilindro A","Cilindro B"],readings={"retorno":"activo"})
        return _set(d,pressure=["pump-p"],motion="Reposo",readings={"P":"standby"})

    if machine=="Camión minero" and subsystem=="Levante de tolva":
        if state=="Raise":
            return _set(d,pressure=["pump-p","p-hoist","hoist-check","check-head","head-cyl"],ret=["cyl-rod","rod-hoist","hoist-t","t-tank"],pilot=["work-ls","ls-pump"],motion="Los cilindros elevan la tolva; la presión aumenta según la carga",value=.7,active=["Bomba","Hoist valve","Load check","Cilindros"],readings={"P":"carga + margen","Head":"alta","Rod":"retorno","LS":"≈ carga"})
        if state=="Lower":
            return _set(d,pressure=["pump-p","p-hoist","hoist-rod","rod-cyl"],ret=["cyl-head","head-control","control-t","t-tank"],pilot=["rod-pilot","pilot-control","work-ls","ls-pump"],motion="Descenso controlado: el elemento de control de carga modula la salida del lado cargado",value=-.55,active=["Hoist valve","Control de descenso","Cilindros"],readings={"Rod":"mando/presión","Head":"presión controlada","LS":"según carga"})
        if state=="Float":
            return _set(d,ret=["cyl-head","head-hoist-t","cyl-rod","rod-hoist-t","hoist-t","t-tank"],pilot=["float-pilot"],motion="Float: ambas cámaras se comunican con retorno para permitir movimiento por carga externa",value=.2,active=["Hoist valve"],readings={"Head":"baja","Rod":"baja","P":"standby"})
        return _set(d,pressure=["load-check"],pilot=["ls-standby"],motion="Hold: la carga queda sostenida por bloqueo/retención; la bomba queda en standby según arquitectura",value=.7,active=["Load check","Control de descenso"],readings={"Head":"presión de carga atrapada","Rod":"baja","P":"standby"})

    if machine in ("Camión minero","Cargador frontal") and subsystem in ("Dirección hidrostática","Dirección articulada"):
        if state=="Izquierda":
            return _set(d,pressure=["pump-priority","priority-hmu","hmu-l","l-cyl"],ret=["r-cyl","cyl-r-hmu","hmu-t","t-tank"],pilot=["hmu-ls","ls-priority"],motion="Giro a la izquierda: un cilindro recibe presión y el opuesto descarga",value=-1,active=["Prioridad","HMU","Cilindros L/R"],readings={"P":"disponible","L":"alta","R":"retorno","LS":"carga"})
        if state=="Derecha":
            return _set(d,pressure=["pump-priority","priority-hmu","hmu-r","r-cyl"],ret=["l-cyl","cyl-l-hmu","hmu-t","t-tank"],pilot=["hmu-ls","ls-priority"],motion="Giro a la derecha",value=1,active=["Prioridad","HMU","Cilindros L/R"],readings={"P":"disponible","R":"alta","L":"retorno","LS":"carga"})
        return _set(d,pressure=["pump-priority"],pilot=["ls-standby"],motion="Neutro: HMU sin demanda significativa; prioridad mantiene disponibilidad",active=["Prioridad"],readings={"P":"standby","LS":"bajo","L/R":"bajas"})

    if machine=="Camión minero" and subsystem=="Freno con acumuladores":
        if state=="Carga":
            return _set(d,pressure=["pump-charge","charge-accum"],ret=["charge-t","t-tank"],motion="La bomba carga los acumuladores hasta la condición de corte",value=.4,active=["Bomba","Válvula de carga","Acumuladores"],readings={"Acumulador":"subiendo","P carga":"alta"})
        if state=="Aplicación":
            return _set(d,pressure=["accum-brake","brake-wheel"],ret=["brake-t","t-tank"],motion="El acumulador entrega energía al circuito de freno a través de la válvula de aplicación",value=1,active=["Acumuladores","Válvula de freno","Frenos"],readings={"Acumulador":"disminuye","Freno":"proporcional al mando"})
        return _set(d,pressure=["accum-hold"],motion="Standby: acumuladores cargados; existe energía aunque la bomba no esté entregando caudal",active=["Acumuladores"],readings={"Acumulador":"presurizado","Freno":"0/bajo"})

    if machine=="Cargador frontal" and subsystem=="Levante de brazos LS":
        if state=="Raise":
            return _set(d,pressure=["pump-p","p-comp","comp-spool","spool-check","check-a","a-cyl"],ret=["cyl-b","b-spool","spool-t","t-tank"],pilot=["a-shuttle","shuttle-ls","ls-pump"],motion="Raise: la sección dosifica caudal; LS informa la mayor presión de carga al control de bomba",value=1,active=["Bomba LS","Compensador","Banco implementos","Load check","Cilindros lift","Shuttle LS"],readings={"P":"LS + margen","LS":"≈ carga","A":"alta","B":"retorno"})
        if state=="Lower":
            return _set(d,pressure=["pump-p","p-comp","comp-spool","spool-b","b-cyl"],ret=["cyl-a","a-spool","spool-t","t-tank"],pilot=["b-shuttle","shuttle-ls","ls-pump"],motion="Lower: inversión de A/B con control de caudal; observe posible carga motriz",value=-1,active=["Bomba LS","Banco implementos","Cilindros lift","Shuttle LS"],readings={"P":"LS + margen","B":"mando","A":"retorno/controlado","LS":"según carga"})
        if state=="Float":
            return _set(d,ret=["cyl-a","a-spool-t","cyl-b","b-spool-t","spool-t","t-tank"],pilot=["ls-vent","ls-pump"],motion="Float: A y B descargan a T; el implemento puede seguir el terreno",value=-.15,active=["Banco implementos"],readings={"A":"baja","B":"baja","P":"standby","LS":"vent"})
        return _set(d,pressure=["pump-standby","load-check"],pilot=["ls-vent"],motion="Hold: carga retenida por la sección/load check y bomba en standby",value=.45,active=["Load check"],readings={"A":"presión de carga","B":"baja","P":"standby"})

    if machine=="Cargador frontal" and subsystem=="Inclinación de balde":
        if state=="Rollback":
            return _set(d,pressure=["pump-p","p-spool","spool-a","a-cyl"],ret=["cyl-b","b-spool","spool-t","t-tank"],pilot=["work-ls","ls-pump"],motion="Rollback del balde",value=1,active=["Banco implementos","Load check","Cilindro tilt"],readings={"A":"alta","B":"retorno","LS":"carga"})
        if state=="Dump":
            return _set(d,pressure=["pump-p","p-spool","spool-b","b-cyl"],ret=["cyl-a","a-spool","spool-t","t-tank"],pilot=["work-ls","ls-pump"],motion="Dump del balde",value=-1,active=["Banco implementos","Cilindro tilt"],readings={"B":"alta","A":"retorno","LS":"carga"})
        return _set(d,pressure=["load-check"],motion="Hold: el balde mantiene posición",active=["Load check"],readings={"A/B":"carga atrapada según geometría"})

    return d


def system_state(machine: str, subsystem: str, state: str) -> dict:
    out=_state(machine,subsystem,state)
    meta=SYSTEM_CASES[machine][subsystem]
    return {**out, **{k:meta[k] for k in ("circuit","description","components","field","risks","learning")}}


def course_comparison_rows():
    return [
        ["Fuente de potencia", "Motor eléctrico + bomba fija/variable", "Motor térmico/eléctrico + bomba variable; prioridad/LS frecuente"],
        ["Carga", "Más repetitiva y conocida", "Variable por terreno, implemento, carga y maniobra"],
        ["Conductores", "Tubería fija + manguera local", "Mangueras, articulaciones, rutas móviles"],
        ["Control", "Manifold, válvulas discretas, secuencias", "Banco seccional, compensación, LS, retención de carga"],
        ["Medición", "Puntos estables y accesibles", "Puntos distribuidos; condición de operación define el dato"],
        ["Riesgo", "Atrapamiento, prensas, energía residual", "Carga suspendida, dirección/freno, articulación, presión residual"],
    ]


DIAGNOSTIC_CASES = {
    "Alta presión y sin movimiento": {
        "physics": "Hay resistencia suficiente para desarrollar presión, pero no hay desplazamiento útil.",
        "first": ["Confirmar bloqueo/carga mecánica", "Verificar que la direccional conmuta", "Comparar P con A/B", "Revisar retenciones pilotadas/contrabalance"],
        "evidence": ["P alta + A alta + sin movimiento → carga/bloqueo/actuador", "P alta pero A/B no cambian → válvula/mando", "P cae y vuelve a subir → ruta llega al actuador pero encuentra resistencia"],
        "avoid": "No concluir 'bomba mala' solo porque el actuador no se mueve.",
    },
    "Movimiento lento": {
        "physics": "La velocidad depende del caudal efectivo que entra/sale del actuador.",
        "first": ["Comparar velocidad en ambos sentidos", "Medir caudal o tiempo de ciclo", "Revisar filtro/restricción", "Revisar fuga interna y viscosidad"],
        "evidence": ["Lento en ambos sentidos → fuente/caudal común", "Lento en un solo sentido → válvula/ruta específica", "P normal + Q bajo → restricción o desgaste"],
        "avoid": "Subir presión no corrige una falta de caudal.",
    },
    "Baja presión y baja fuerza": {
        "physics": "Si el circuito no desarrolla presión, el caudal está escapando o la fuente/control no permite construir resistencia.",
        "first": ["Nivel, succión y cebado", "Ajuste/estado de alivio", "Fuga interna", "Prueba directa de bomba si lo anterior es normal"],
        "evidence": ["P baja en todo estado → fuga aguas arriba / bomba / alivio", "P normal antes de válvula y baja después → válvula/ruta", "Componente caliente → posible fuga interna con Δp"],
        "avoid": "No diagnosticar por temperatura aislada; ubique dónde se disipa potencia.",
    },
    "Cavitación / ruido de bomba": {
        "physics": "La demanda local de fluido excede la alimentación y la presión absoluta puede caer hasta formar vapor/aire liberado.",
        "first": ["Nivel de aceite", "Respiradero", "Filtro/strainer de succión", "Manguera de succión colapsada", "Fittings flojos", "Viscosidad/temperatura"],
        "evidence": ["Ruido + espuma → aireación probable", "Ruido + vacío alto en succión → restricción", "Daño erosivo → revisar alimentación y anti-cavitación"],
        "avoid": "No confundir aireación externa con cavitación por baja presión absoluta.",
    },
    "Sobretemperatura": {
        "physics": "Potencia hidráulica perdida por caída de presión sin trabajo útil se transforma en calor.",
        "first": ["Buscar alivio abierto", "Medir Δp en filtros/estrangulamientos", "Revisar fuga interna", "Verificar enfriador y viscosidad"],
        "evidence": ["Un componente claramente más caliente orienta a pérdidas localizadas", "P alta con retorno continuo a tanque sugiere disipación", "Viscosidad baja aumenta fuga interna"],
        "avoid": "No asumir que 'la bomba genera calor' sin localizar la caída de presión responsable.",
    },
    "Equipo detenido con energía residual": {
        "physics": "Cilindros, cargas y acumuladores pueden conservar energía con la bomba detenida.",
        "first": ["Aislar", "Bloquear/etiquetar", "Asegurar mecánicamente la carga", "Descargar acumuladores según procedimiento", "Verificar presión cero"],
        "evidence": ["Manómetro o test point confirma energía remanente", "Movimiento de la carga indica energía potencial aún disponible"],
        "avoid": "Nunca asumir energía cero por motor detenido.",
    },
}


def diagnostic_cases():
    return DIAGNOSTIC_CASES
