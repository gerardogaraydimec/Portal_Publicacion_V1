/* GG DIMEC display colors. No physical values are changed here. */
export const BRAND = Object.freeze({
  orange:'#f28e1c', copper:'#b85d18', graphite:'#292a2d', ivory:'#fbf7f0',
  velocity:['#ac784f','#ee9a42','#ffe0ad'],
  pressure:['#858789','#bfbcb5','#fff0da'],
  energy:['#484b50','#f28e1c','#bda282'],
  energyText:['#484b50','#a95110','#796247'],
  grid:'#5f594f', tube:'#b4a390', tubeRing:'#918374', tubeLine:'#a39685',
  flange:'#c1af98', flangeOuter:'#908271', station1:'#ead9c1', station2:'#f2a050',
  probe:'#fff3df', hemisphereSky:'#fff0da', hemisphereGround:'#38332d', light:'#ffc784'
});
export const rgb = hex => [1,3,5].map(i => parseInt(hex.slice(i,i+2),16)/255);
export const colorNumber = hex => parseInt(hex.slice(1),16);
export const gradient = mode => `linear-gradient(90deg,${BRAND[mode].join(',')})`;
