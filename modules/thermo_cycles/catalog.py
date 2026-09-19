CYCLE_FAMILIES = {
    "Ciclos de potencia con gas": [
        {"title":"Carnot con gas ideal","mode":"solver","solver":"gas_carnot","schematic":"heat_engine"},
        {"title":"Otto","mode":"solver","solver":"otto","schematic":"reciprocating"},
        {"title":"Diesel","mode":"solver","solver":"diesel","schematic":"reciprocating"},
        {"title":"Dual","mode":"solver","solver":"dual","schematic":"reciprocating"},
        {"title":"Stirling","mode":"solver","solver":"stirling","schematic":"heat_engine"},
        {"title":"Ericsson","mode":"solver","solver":"ericsson","schematic":"heat_engine"},
        {"title":"Brayton ideal","mode":"solver","solver":"brayton_ideal","schematic":"brayton"},
        {"title":"Brayton real","mode":"solver","solver":"brayton_real","schematic":"brayton"},
        {"title":"Brayton con regeneración","mode":"solver","solver":"brayton_regen","schematic":"brayton_regen"},
        {"title":"Brayton con interenfriamiento + recalentamiento + regeneración","mode":"solver","solver":"brayton_advanced","schematic":"brayton_advanced"},
        {"title":"Turborreactor ideal","mode":"solver","solver":"turbojet","schematic":"turbojet"},
    ],
    "Ciclos de potencia con vapor": [
        {"title":"Carnot de vapor","mode":"solver","solver":"vapor_carnot","schematic":"heat_engine"},
        {"title":"Rankine ideal","mode":"solver","solver":"rankine_ideal","schematic":"rankine"},
        {"title":"Rankine real","mode":"solver","solver":"rankine_real","schematic":"rankine"},
        {"title":"Rankine con recalentamiento","mode":"solver","solver":"rankine_reheat","schematic":"rankine_reheat"},
        {"title":"Rankine regenerativo con calentador abierto","mode":"solver","solver":"rankine_regen_open","schematic":"rankine_regen"},
        {"title":"Rankine regenerativo con calentador cerrado","mode":"structural","key":"rankine_closed","schematic":"rankine_closed"},
        {"title":"Rankine regenerativo con múltiples extracciones","mode":"structural","key":"rankine_multi","schematic":"rankine_multi"},
    ],
    "Ciclos combinados y cogeneración": [
        {"title":"Cogeneración con extracción de vapor","mode":"solver","solver":"cogeneration","schematic":"cogeneration"},
        {"title":"Ciclo combinado Brayton–Rankine","mode":"solver","solver":"combined","schematic":"combined"},
        {"title":"Ciclo binario de vapor","mode":"structural","key":"binary","schematic":"binary"},
    ],
    "Ciclos de refrigeración y bombas de calor": [
        {"title":"Refrigerador / bomba de calor — balance global","mode":"solver","solver":"basic_cop","schematic":"refrigerator"},
        {"title":"Carnot invertido","mode":"solver","solver":"carnot_reverse","schematic":"refrigerator"},
        {"title":"Compresión de vapor ideal","mode":"solver","solver":"vcr_ideal","schematic":"vcr"},
        {"title":"Compresión de vapor real","mode":"solver","solver":"vcr_real","schematic":"vcr"},
        {"title":"Bomba de calor por compresión de vapor","mode":"solver","solver":"heat_pump","schematic":"heat_pump"},
        {"title":"Refrigeración en cascada","mode":"solver","solver":"cascade","schematic":"cascade"},
        {"title":"Compresión de vapor multietapa con cámara flash","mode":"structural","key":"multistage_flash","schematic":"multistage_ref"},
        {"title":"Refrigeración con múltiples evaporadores","mode":"structural","key":"multi_evap","schematic":"multipurpose_ref"},
        {"title":"Refrigeración de gas — Brayton invertido","mode":"solver","solver":"gas_refrigeration","schematic":"gas_refrigeration"},
        {"title":"Refrigeración por absorción — límite reversible","mode":"solver","solver":"absorption","schematic":"absorption"},
        {"title":"Licuefacción de gases — ciclo regenerativo con JT","mode":"structural","key":"liquefaction","schematic":"liquefaction"},
    ],
}

STRUCTURAL_CYCLES = {
    "rankine_closed": {
        "summary":"Configuración Rankine regenerativa donde el vapor extraído cede calor al agua de alimentación sin mezclarse directamente con ella.",
        "processes":[
            ["Turbina → extracción","Expansión con extracción","Se deriva una fracción y del flujo","Turbina"],
            ["Agua alimentación → calentador","Calentamiento a alta presión","Sin mezcla directa","Calentador cerrado"],
            ["Vapor extraído → drenaje","Condensación","Entrega calor al agua","Lado carcasa"],
            ["Drenaje → retorno","Estrangulamiento o bombeo","Depende de configuración","Sistema de drenajes"],
        ],
        "equations":[
            r"\dot m_{fw}(h_{out}-h_{in})=\dot m_y(h_{y,in}-h_{y,out})",
            r"\dot m_{t,downstream}=(1-y)\dot m",
            r"\eta_{th}=\frac{\dot W_{neto}}{\dot Q_{in}}",
        ],
        "study":[
            "Seguir la fracción extraída y en cada tramo de turbina.",
            "Verificar que en el calentador cerrado no existe mezcla directa de corrientes.",
            "Comparar con un calentador abierto usando la misma presión de extracción."
        ]
    },
    "rankine_multi": {
        "summary":"Rankine regenerativo con varias extracciones para elevar progresivamente la temperatura del agua de alimentación.",
        "processes":[
            ["Turbina","Expansiones sucesivas","El flujo disminuye tras cada extracción","Producción de trabajo"],
            ["Calentadores","Precalentamiento escalonado","Abiertos y/o cerrados","Regeneración"],
            ["Caldera","Adición principal de calor","Flujo total reconstituido","Fuente térmica"],
            ["Condensador","Rechazo final de calor","Flujo remanente","Sumidero térmico"],
        ],
        "equations":[
            r"\sum \dot m_{in}=\sum \dot m_{out}",
            r"\sum \dot m h_{in}=\sum \dot m h_{out}",
            r"\dot W_t=\sum_i \dot m_i(h_{in,i}-h_{out,i})",
        ],
        "study":[
            "Seguir el caudal que continúa expandiéndose después de cada extracción.",
            "Comparar aumento de eficiencia con reducción del trabajo disponible en etapas posteriores.",
            "Revisar cómo cambia la temperatura media de adición de calor."
        ]
    },
    "binary": {
        "summary":"Dos ciclos de vapor acoplados térmicamente, usando diferentes fluidos o niveles térmicos.",
        "processes":[
            ["Ciclo superior","Produce trabajo a mayor temperatura","Fluido A","Ciclo superior"],
            ["Intercambiador intermedio","Rechaza/recibe calor","Acoplamiento térmico","Sin mezcla de fluidos"],
            ["Ciclo inferior","Produce trabajo con calor recuperado","Fluido B","Ciclo inferior"],
        ],
        "equations":[
            r"\dot m_A(h_{A,in}-h_{A,out})=\dot m_B(h_{B,out}-h_{B,in})",
            r"\dot W_{neto,tot}=\dot W_A+\dot W_B",
            r"\eta_{th}=\frac{\dot W_{neto,tot}}{\dot Q_{in,A}}",
        ],
        "study":[
            "Separar claramente los balances de cada fluido.",
            "Usar el intercambiador como vínculo energético entre ambos ciclos.",
            "Comparar con un ciclo combinado gas-vapor."
        ]
    },
    "multistage_flash": {
        "summary":"Ciclo de compresión de vapor en dos etapas con cámara de vaporización instantánea para mejorar el desempeño y controlar la compresión.",
        "processes":[
            ["Evaporador","Absorción de calor","Baja presión","Efecto refrigerante"],
            ["Compresor 1","Compresión de baja etapa","Hasta presión intermedia","Trabajo de entrada"],
            ["Cámara flash","Separación y mezcla","Presión intermedia","Redistribución de flujo"],
            ["Compresor 2","Compresión de alta etapa","Hasta presión de condensación","Trabajo de entrada"],
            ["Condensador","Rechazo de calor","Alta presión","Condensación"],
            ["Válvulas","Estrangulamiento","h = cte","Dos niveles de presión"],
        ],
        "equations":[
            r"\dot W_c=\dot m_1(h_2-h_1)+\dot m_2(h_4-h_3)",
            r"\sum \dot m_{in}=\sum \dot m_{out}",
            r"\sum \dot m h_{in}=\sum \dot m h_{out}",
            r"COP_R=\frac{\dot Q_L}{\dot W_c}",
        ],
        "study":[
            "Observar cómo la presión intermedia afecta el trabajo total.",
            "Seguir por separado los flujos de líquido y vapor en la cámara flash.",
            "Comparar el COP contra un ciclo de una etapa."
        ]
    },
    "multi_evap": {
        "summary":"Configuración con varios evaporadores operando a distintas temperaturas y un compresor común.",
        "processes":[
            ["Condensador","Rechazo de calor","Presión alta común","Condensación"],
            ["Ramificación","Distribución de refrigerante","Varios niveles","Separación de caudal"],
            ["Evaporadores","Absorción de calor","Presiones distintas","Cargas independientes"],
            ["Regulación","Ajuste de presión","Válvulas reductoras","Iguala presión antes de mezcla"],
            ["Compresor","Compresión del flujo combinado","Presión de succión común","Trabajo de entrada"],
        ],
        "equations":[
            r"\dot m_c=\sum_i \dot m_i",
            r"\dot Q_{L,i}=\dot m_i(h_{out,i}-h_{in,i})",
            r"COP_R=\frac{\sum_i\dot Q_{L,i}}{\dot W_c}",
        ],
        "study":[
            "Seguir cada caudal másico desde la ramificación hasta la mezcla.",
            "Relacionar cada presión de evaporación con su temperatura de refrigeración.",
            "Ver cómo la válvula reguladora introduce irreversibilidad."
        ]
    },
    "liquefaction": {
        "summary":"Configuración regenerativa que enfría progresivamente un gas y utiliza estrangulamiento Joule–Thomson para alcanzar la región bifásica.",
        "processes":[
            ["Compresión","Eleva la presión","Trabajo de entrada","Compresor"],
            ["Enfriamiento","Reduce temperatura","Rechazo de calor","Intercambiador"],
            ["Regeneración","Preenfría la corriente de alta presión","Intercambiador contracorriente","Recuperación interna"],
            ["Estrangulamiento JT","Caída de presión","h = cte","Válvula"],
            ["Separación","Obtiene líquido y vapor","Equilibrio bifásico","Separador"],
        ],
        "equations":[
            r"h_{in}=h_{out}\quad\text{(válvula JT)}",
            r"\mu_{JT}=\left(\frac{\partial T}{\partial P}\right)_h",
            r"\dot m_{in}=\dot m_L+\dot m_V",
        ],
        "study":[
            "Verificar que el estrangulamiento es isoentálpico, no isentrópico.",
            "Observar el papel del intercambiador regenerativo.",
            "Relacionar la fracción licuada con el estado después de la válvula."
        ]
    },
}
