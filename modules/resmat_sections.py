from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class SectionData:
    name: str
    area_mm2: float
    iz_mm4: float
    iy_mm4: float
    rz_mm: float
    ry_mm: float
    c_y_mm: float
    jt_mm4: float | None
    centroid_z_mm: float = 0.0
    note: str = ""


def _validate_profile(h: float, bf: float, tw: float, tf: float):
    if min(h,bf,tw,tf) <= 0:
        raise ValueError("Todas las dimensiones deben ser mayores que cero.")
    if 2*tf >= h:
        raise ValueError("Debe cumplirse 2·tf < h.")
    if tw >= bf:
        raise ValueError("Debe cumplirse tw < bf.")


def section_data(section_type: str, p: dict) -> SectionData:
    if section_type == "Rectangular":
        b=float(p['b_mm']); h=float(p['h_mm'])
        if min(b,h)<=0: raise ValueError("b y h deben ser mayores que cero.")
        A=b*h; Iz=b*h**3/12; Iy=h*b**3/12
        B=max(b,h); H=min(b,h)
        J=B*H**3*(1/3 - 0.21*(H/B)*(1-H**4/(12*B**4)))
        return SectionData(section_type,A,Iz,Iy,math.sqrt(Iz/A),math.sqrt(Iy/A),h/2,J,
            note="J corresponde a una aproximación de Saint-Venant para rectángulos macizos.")
    if section_type == "Circular maciza":
        d=float(p['d_mm']);
        if d<=0: raise ValueError("d debe ser mayor que cero.")
        A=math.pi*d**2/4; I=math.pi*d**4/64; J=math.pi*d**4/32
        r=math.sqrt(I/A)
        return SectionData(section_type,A,I,I,r,r,d/2,J)
    if section_type == "Tubular circular":
        do=float(p['do_mm']); t=float(p['t_mm']); di=do-2*t
        if do<=0 or t<=0 or di<=0: raise ValueError("Debe cumplirse Dₒ>0, t>0 y Dᵢ=Dₒ−2t>0.")
        A=math.pi*(do**2-di**2)/4; I=math.pi*(do**4-di**4)/64; J=math.pi*(do**4-di**4)/32
        r=math.sqrt(I/A)
        return SectionData(section_type,A,I,I,r,r,do/2,J)
    if section_type in ("Perfil I / H","Canal C"):
        h=float(p['h_mm']); bf=float(p['bf_mm']); tw=float(p['tw_mm']); tf=float(p['tf_mm'])
        _validate_profile(h,bf,tw,tf)
        hw=h-2*tf
        A=2*bf*tf+tw*hw
        Iz=2*(bf*tf**3/12 + bf*tf*(h/2-tf/2)**2) + tw*hw**3/12
        if section_type=="Perfil I / H":
            Iy=2*(tf*bf**3/12)+hw*tw**3/12
            zbar=0.0
        else:
            Aweb=tw*hw; Af=bf*tf
            z_web=tw/2; z_fl=bf/2
            zbar=(Aweb*z_web+2*Af*z_fl)/A
            Iy=hw*tw**3/12+Aweb*(z_web-zbar)**2+2*(tf*bf**3/12+Af*(z_fl-zbar)**2)
        J=(2*bf*tf**3 + hw*tw**3)/3
        return SectionData(section_type,A,Iz,Iy,math.sqrt(Iz/A),math.sqrt(Iy/A),h/2,J,zbar,
            note="J usa la aproximación de pared delgada abierta; apropiada para comparar rigidez torsional, no para resolver alabeo restringido.")
    if section_type == "Propiedades ingresadas":
        A=float(p['area_mm2']); Iz=float(p['inertia_mm4']); c=float(p.get('c_mm',1))
        Iy=float(p.get('iy_mm4',Iz)); jt=p.get('jt_mm4')
        J=None if jt in (None,"") else float(jt)
        if min(A,Iz,Iy,c)<=0: raise ValueError("A, Iz, Iy y c deben ser mayores que cero.")
        return SectionData(section_type,A,Iz,Iy,math.sqrt(Iz/A),math.sqrt(Iy/A),c,J,
            note="La geometría real no se dibuja cuando solo se ingresan propiedades equivalentes.")
    raise KeyError(section_type)


def profile_params_from_sidebar(st, section_type: str, key_prefix: str="") -> dict:
    k=lambda s: f"{key_prefix}{s}"
    if section_type == "Rectangular":
        return {"b_mm":float(st.number_input("Ancho b [mm]",min_value=1.0,value=100.0,step=5.0,key=k('b'))),
                "h_mm":float(st.number_input("Altura h [mm]",min_value=1.0,value=200.0,step=5.0,key=k('h')))}
    if section_type == "Circular maciza":
        return {"d_mm":float(st.number_input("Diámetro d [mm]",min_value=1.0,value=100.0,step=5.0,key=k('d')))}
    if section_type == "Tubular circular":
        return {"do_mm":float(st.number_input("Diámetro exterior Dₒ [mm]",min_value=2.0,value=120.0,step=5.0,key=k('do'))),
                "t_mm":float(st.number_input("Espesor t [mm]",min_value=0.5,value=8.0,step=0.5,key=k('t')))}
    if section_type in ("Perfil I / H","Canal C"):
        return {
            "h_mm":float(st.number_input("Altura total h [mm]",min_value=10.0,value=300.0,step=10.0,key=k('ph'))),
            "bf_mm":float(st.number_input("Ancho de ala bᶠ [mm]",min_value=10.0,value=150.0,step=5.0,key=k('pbf'))),
            "tw_mm":float(st.number_input("Espesor de alma tʷ [mm]",min_value=1.0,value=8.0,step=1.0,key=k('ptw'))),
            "tf_mm":float(st.number_input("Espesor de ala tᶠ [mm]",min_value=1.0,value=12.0,step=1.0,key=k('ptf'))),
        }
    return {
        "area_mm2":float(st.number_input("Área A [mm²]",min_value=1.0,value=20000.0,step=100.0,key=k('A'))),
        "inertia_mm4":float(st.number_input("Iz [mm⁴]",min_value=1.0,value=6.6667e7,step=1e6,format="%.3e",key=k('Iz'))),
        "iy_mm4":float(st.number_input("Iy [mm⁴]",min_value=1.0,value=2.0e7,step=1e6,format="%.3e",key=k('Iy'))),
        "c_mm":float(st.number_input("Fibra extrema c [mm]",min_value=0.1,value=100.0,step=5.0,key=k('c'))),
        "jt_mm4":float(st.number_input("Constante torsional Jt [mm⁴]",min_value=1.0,value=1.0e6,step=1e5,format="%.3e",key=k('Jt'))),
    }

def visual_section_payload(section_type: str, p: dict) -> dict:
    """Dimensionless section geometry for browser visualizations; ratios are preserved."""
    if section_type=='Rectangular': return {'kind':'rect','b':float(p['b_mm']),'h':float(p['h_mm'])}
    if section_type=='Circular maciza': return {'kind':'solid_circle','d':float(p['d_mm'])}
    if section_type=='Tubular circular': return {'kind':'tube','do':float(p['do_mm']),'di':float(p['do_mm'])-2*float(p['t_mm'])}
    if section_type in ('Perfil I / H','Canal C'):
        return {'kind':'i_profile' if section_type=='Perfil I / H' else 'channel','h':float(p['h_mm']),'b':float(p['bf_mm']),'tw':float(p['tw_mm']),'tf':float(p['tf_mm'])}
    return {'kind':'custom'}
