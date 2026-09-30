"""Plotly views synchronized with the same sampled geometry as the 3D scene.

The physical datum is z=0; section 2 in a Venturi is the throat.
"""
from __future__ import annotations
import numpy as np
import plotly.graph_objects as go
from .profile import sample_profile

ORANGE='#f28e1c'
COPPER='#b85d18'
PRESSURE='#484b50'
HEIGHT='#bda282'
GRAPHITE='#292a2d'


def _layout(fig, title, height=430):
    fig.update_layout(title=title, height=height, template='plotly_white',
                      paper_bgcolor='#fffdfa', plot_bgcolor='#fffdfa',
                      margin=dict(l=50,r=30,t=55,b=70),
                      font=dict(family='Segoe UI, Arial, sans-serif',color=GRAPHITE),
                      hovermode='x unified',
                      legend=dict(orientation='h',y=-.20),
                      colorway=[ORANGE,PRESSURE,HEIGHT,COPPER],
                      hoverlabel=dict(bgcolor='#fbf7f0',font_color=GRAPHITE))
    fig.update_xaxes(gridcolor='#ede5da',zerolinecolor='#c6b9a8')
    fig.update_yaxes(gridcolor='#ede5da',zerolinecolor='#c6b9a8')
    return fig


def make_system_figure(result, geometry='contraction', rho=1000.0, length_m=6.0):
    p=sample_profile(result,rho,geometry,length_m)
    x=np.asarray(p['x_m']); z=np.asarray(p['z_m']); D=np.asarray(p['diameter_m'])
    exaggeration=max(3.0,0.6*max(np.ptp(z),1.0)/float(np.max(D)))
    half=D*exaggeration/2
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=x,y=z+half,mode='lines',line=dict(color=GRAPHITE,width=2),name='Pared (ampliada)',hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=x,y=z-half,mode='lines',line=dict(color=GRAPHITE,width=2),fill='tonexty',fillcolor='rgba(242,142,28,.12)',showlegend=False,hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=x,y=z,mode='lines',line=dict(color=ORANGE,width=2,dash='dash'),name='Eje del conducto'))
    fig.add_hline(y=0,line_dash='dot',line_color='#aa9c8b',annotation_text='Datum real: z = 0',annotation_position='bottom left')
    for i,label,color in [(p['station1_index'],'Secci\u00f3n 1',GRAPHITE),(p['station2_index'],p['station2_name'],ORANGE)]:
        fig.add_shape(type='line',x0=x[i],x1=x[i],y0=z[i]-half[i]*1.2,y1=z[i]+half[i]*1.2,line=dict(color=color,width=3))
        fig.add_annotation(x=x[i],y=z[i]+half[i]*1.3,text=f'<b>{label}</b><br>D = {D[i]*1000:.0f} mm; z = {z[i]:.2f} m',showarrow=False,yanchor='bottom',font=dict(color=color,size=11),bgcolor='rgba(255,255,255,.9)')
    _layout(fig,'Geometr\u00eda y secciones de c\u00e1lculo',480)
    low=min(0,float(np.min(z-half)));high=max(0,float(np.max(z+half)))
    pad=max(1,(high-low)*.3)
    fig.update_xaxes(title='Coordenada horizontal ilustrativa [m]',range=[-.05*length_m,1.05*length_m])
    fig.update_yaxes(title='Cota z [m]',range=[low-pad*.4,high+pad])
    return fig


def make_energy_figure(result, geometry='contraction', rho=1000.0, length_m=6.0):
    p=sample_profile(result,rho,geometry,length_m)
    fig=go.Figure()
    for key,label,color,dash in [('egl_m','EGL: energ\u00eda total',ORANGE,'solid'),('hgl_m','HGL: presi\u00f3n + cota',PRESSURE,'dash'),('z_m','Cota z',HEIGHT,'dot')]:
        fig.add_trace(go.Scatter(x=p['s'],y=p[key],name=label,mode='lines',line=dict(color=color,width=3,dash=dash)))
    for i,label in [(p['station1_index'],'1'),(p['station2_index'],'2')]:
        fig.add_vline(x=p['s'][i],line_dash='dot',line_color='#bcae9a',annotation_text=label)
    _layout(fig,'L\u00ednea de energ\u00eda y l\u00ednea piezom\u00e9trica')
    fig.update_xaxes(title='Posici\u00f3n relativa en el conducto (0 a 1)')
    fig.update_yaxes(title='Altura de energ\u00eda [m]')
    return fig


def make_head_bars(result, station2_name='Secci\u00f3n 2'):
    labels=['Secci\u00f3n 1',station2_name]
    fig=go.Figure()
    for name,values,color in [('Cota z',[result.z1_m,result.z2_m],HEIGHT),('Presi\u00f3n p/(\u03c1g)',[result.pressure_head_1_m,result.pressure_head_2_m],PRESSURE),('Velocidad V\u00b2/(2g)',[result.velocity_head_1_m,result.velocity_head_2_m],ORANGE)]:
        fig.add_trace(go.Bar(name=name,x=labels,y=values,marker=dict(color=color,pattern_shape='/' if color==HEIGHT else '')))
    fig.add_trace(go.Scatter(name='Suma algebraica H',x=labels,y=[result.EGL1_m,result.EGL2_m],mode='markers',marker=dict(color=GRAPHITE,symbol='diamond',size=13)))
    fig.update_layout(barmode='relative')
    _layout(fig,'Reparto de energ\u00eda por secci\u00f3n')
    fig.update_yaxes(title='Altura [m]')
    return fig


def make_local_profile_figure(payload):
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=payload['s'],y=payload['velocity_ms'],name='Velocidad media [m/s]',line=dict(color=COPPER,width=3)))
    fig.add_trace(go.Scatter(x=payload['s'],y=np.asarray(payload['pressure_Pa'])/1000,name='Presi\u00f3n manom\u00e9trica [kPa]',yaxis='y2',line=dict(color=PRESSURE,width=3,dash='dash')))
    _layout(fig,'Velocidad y presi\u00f3n en la geometr\u00eda ilustrativa')
    fig.update_layout(yaxis=dict(title='Velocidad [m/s]'),yaxis2=dict(title='Presi\u00f3n [kPa]',overlaying='y',side='right',showgrid=False))
    fig.update_xaxes(title='Posici\u00f3n relativa en el conducto (0 a 1)')
    return fig
