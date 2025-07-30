import main as jeans
import numpy as np

alpha=2.
beta=5.
gamma=0.
luminosity_tot=1.
r_scale=1.

shite=jeans.get_tracer('abg',r_scale=1.,alpha=2.,beta=5.,gamma=0.,luminosity_tot=1.,upsilon=1.)
np.pause()
xxx=0.5
shite=jeans.abg_luminosity_density_2d(xxx,alpha,beta,gamma)
scale=jeans.get_abg_scale(luminosity_tot,r_scale,alpha,beta,gamma)

boober1=shite*scale[1]
print(boober1)
piss=jeans.plum_luminosity_density_2d(xxx)
scale2=jeans.get_plum_scale(luminosity_tot,r_scale)
boober2=piss*scale2[1]
print(boober2)
print(boober2/boober1)
