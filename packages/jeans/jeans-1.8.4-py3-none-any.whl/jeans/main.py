import numpy as np
import scipy
import scipy.optimize
import scipy.special
import warnings
import matplotlib.pyplot as plt
import astropy as ap
import astropy.units as u
import mpmath as mp
mp.dps=15; mp.pretty=True

g=0.004317#newton's G in units of km/s, pc, Msun
g_dim=g*u.km**2*u.pc/u.s**2/u.M_sun#now as an astropy.units quantity

def get_nfw_gc(c_triangle):
    return 1./(np.log(1.+c_triangle)-c_triangle/(1.+c_triangle))

def get_dehnen_core_gc(c_triangle):
    return ((1.+c_triangle)**3)/c_triangle**3

def get_dehnen_cusp_gc(c_triangle):
    return ((1.+c_triangle)**2)/c_triangle**2

def get_nfw_scale(triangle,h,m_triangle,c_triangle):#r_triangle, scale radius r_s and scale density rho_s, of NFW halo, units of pc and U(m_triangle) / u(r_scale)**3
    gc=get_nfw_gc(c_triangle)
    if type(m_triangle) is ap.units.quantity.Quantity:
        r_triangle=((2.*g_dim*m_triangle/triangle/(h*100.*u.km/u.s/u.Mpc)**2)**(1/3)).to(u.pc)#r_triangle in units of pc, where triangle is overdensity factor = [M_triangle / (4*pi*r_triangle**3)] / rho_crit_0, where rho_crit_0 = 3H_0^2/(8*pi*G), H_0 is hubble constant, m_triangle is given in units of Msun
    else:
        r_triangle=(2.*g*m_triangle/triangle*(1.e+6**2)/(h*100.)**2)**(1/3)#r_triangle in units of pc, where triangle is overdensity factor = [M_triangle / (4*pi*r_triangle**3)] / rho_crit_0, where rho_crit_0 = 3H_0^2/(8*pi*G), H_0 is hubble constant, m_triangle is given in units of Msun
    r_scale=r_triangle/c_triangle#scale radius in same units as r_triangle, where concentration is defined as c_triangle=r_triangle/r_scale
    rho_scale=gc*m_triangle/4./np.pi/r_scale**3
    if type(m_triangle) is ap.units.quantity.Quantity:    
        phi0=(-4.*np.pi*g_dim*rho_scale*r_scale**2).to(u.km*u.km/u.s/u.s)
    else:
        phi0=-4.*np.pi*g*rho_scale*r_scale**2
    return r_triangle,r_scale,rho_scale,phi0

def get_dehnen_core_scale(triangle,h,m_triangle,c_triangle):#r_triangle, scale radius r_s and scale density rho_s, of NFW halo, units of pc and U(m_triangle) / u(r_scale)**3
    gc=get_dehnen_core_gc(c_triangle)
    if type(m_triangle) is ap.units.quantity.Quantity:
        r_triangle=((2.*g_dim*m_triangle/triangle/(h*100.*u.km/u.s/u.Mpc)**2)**(1/3)).to(u.pc)#r_triangle in units of pc, where triangle is overdensity factor = [M_triangle / (4*pi*r_triangle**3)] / rho_crit_0, where rho_crit_0 = 3H_0^2/(8*pi*G), H_0 is hubble constant, m_triangle is given in units of Msun
    else:
        r_triangle=(2.*g*m_triangle/triangle*(1.e+6**2)/(h*100.)**2)**(1/3)#r_triangle in units of pc, where triangle is overdensity factor = [M_triangle / (4*pi*r_triangle**3)] / rho_crit_0, where rho_crit_0 = 3H_0^2/(8*pi*G), H_0 is hubble constant, m_triangle is given in units of Msun
    r_scale=r_triangle/c_triangle#scale radius in same units as r_triangle, where concentration is defined as c_triangle=r_triangle/r_scale
    rho_scale=gc*m_triangle/(4./3.)/np.pi/r_scale**3
    if type(m_triangle) is ap.units.quantity.Quantity:    
        phi0=(-2./3.*np.pi*g_dim*rho_scale*r_scale**2).to(u.km*u.km/u.s/u.s)
    else:
        phi0=-2./3.*np.pi*g*rho_scale*r_scale**2
    return r_triangle,r_scale,rho_scale,phi0

def get_dehnen_cusp_scale(triangle,h,m_triangle,c_triangle):#r_triangle, scale radius r_s and scale density rho_s, of NFW halo, units of pc and U(m_triangle) / u(r_scale)**3
    gc=get_dehnen_cusp_gc(c_triangle)
    if type(m_triangle) is ap.units.quantity.Quantity:
        r_triangle=((2.*g_dim*m_triangle/triangle/(h*100.*u.km/u.s/u.Mpc)**2)**(1/3)).to(u.pc)#r_triangle in units of pc, where triangle is overdensity factor = [M_triangle / (4*pi*r_triangle**3)] / rho_crit_0, where rho_crit_0 = 3H_0^2/(8*pi*G), H_0 is hubble constant, m_triangle is given in units of Msun
    else:
        r_triangle=(2.*g*m_triangle/triangle*(1.e+6**2)/(h*100.)**2)**(1/3)#r_triangle in units of pc, where triangle is overdensity factor = [M_triangle / (4*pi*r_triangle**3)] / rho_crit_0, where rho_crit_0 = 3H_0^2/(8*pi*G), H_0 is hubble constant, m_triangle is given in units of Msun
    r_scale=r_triangle/c_triangle#scale radius in same units as r_triangle, where concentration is defined as c_triangle=r_triangle/r_scale
    rho_scale=gc*m_triangle/(4./2.)/np.pi/r_scale**3
    if type(m_triangle) is ap.units.quantity.Quantity:    
        phi0=(-2.*np.pi*g_dim*rho_scale*r_scale**2).to(u.km*u.km/u.s/u.s)
    else:
        phi0=-2.*np.pi*g*rho_scale*r_scale**2
    return r_triangle,r_scale,rho_scale,phi0

def get_abg_triangle_scale(triangle,h,m_triangle,c_triangle,alpha,beta,gamma):#r_triangle, scale radius r_s and scale density, rho_s, of abg halo, given triangle parameters, units of U(m_triangle)/U(r_triangle)**3
    if type(m_triangle) is ap.units.quantity.Quantity:
        r_triangle=((2.*g_dim*m_triangle/triangle/(h*100.*u.km/u.s/u.Mpc)**2)**(1/3)).to(u.pc)#r_triangle in units of pc, where triangle is overdensity factor = [M_triangle / (4*pi*r_triangle**3)] / rho_crit_0, where rho_crit_0 = 3H_0^2/(8*pi*G), H_0 is hubble constant, m_triangle is given in units of Msun
    else:
        r_triangle=(2.*g*m_triangle/triangle*(1.e+6**2)/(h*100.)**2)**(1/3)#r_triangle in units of pc, where triangle is overdensity factor = [M_triangle / (4*pi*r_triangle**3)] / rho_crit_0, where rho_crit_0 = 3H_0^2/(8*pi*G), H_0 is hubble constant, m_triangle is given in units of Msun
    r_scale=r_triangle/c_triangle#scale radius in same units as r_triangle, where concentration is defined as c_triangle=r_triangle/r_scale
    a=(3.-gamma)/alpha
    b=(beta-gamma)/alpha
    c=(3.-gamma+alpha)/alpha
    z1=-c_triangle**alpha
    hf1=scipy.special.hyp2f1(a,b,c,z1)      
    rho_scale=m_triangle*(3.-gamma)/4./np.pi/(r_scale**3)/c_triangle**(3.-gamma)/hf1
    phi0=np.nan#not yet implemented
    return r_triangle,r_scale,rho_scale,phi0

def nfw_mass_density(x,c_triangle):# returns rho_NFW(x) / rho_scale, where x = r / r_triangle
    cx=c_triangle*x #r / r_scale
    return 1./cx/(1.+cx)**2

def dehnen_core_mass_density(x,c_triangle):# returns rho_NFW(x) / rho_scale, where x = r / r_triangle
    cx=c_triangle*x #r / r_scale
    return 1./(1.+cx)**4

def dehnen_cusp_mass_density(x,c_triangle):# returns rho_NFW(x) / rho_scale, where x = r / r_triangle
    cx=c_triangle*x #r / r_scale
    return 1./cx/(1.+cx)**3

def nfw_enclosed_mass(x,c_triangle):# returns enclosed mass M(x) / m_triangle, where x = r/r_triangle
    gc=get_nfw_gc(c_triangle)
    cx=c_triangle*x #r / r_scale
    return gc*(np.log(1.+cx)-cx/(1.+cx))

def nfw_potential(x,c_triangle): # returns gravitational potential phi(x) / phi(0), where x=r/r_triangle
    gc=get_nfw_gc(c_triangle)
    cx=c_triangle*x #r / r_scale
    return np.log(1.+cx)/cx
    
def dehnen_core_enclosed_mass(x,c_triangle):# returns enclosed mass M(x) / m_triangle, where x = r/r_triangle
    gc=get_dehnen_core_gc(c_triangle)
    cx=c_triangle*x #r / r_scale
    return gc*(cx**3)/(1.+cx)**3

def dehnen_core_potential(x,c_triangle): # returns gravitational potential phi(x) / phi(0), where x=r/r_triangle
    gc=get_dehnen_core_gc(c_triangle)
    cx=c_triangle*x #r / r_scale
    return (1.+3.*cx+2.*cx**2)/(1.+cx)**3

def dehnen_cusp_enclosed_mass(x,c_triangle):# returns enclosed mass M(x) / m_triangle, where x = r/r_triangle
    gc=get_dehnen_cusp_gc(c_triangle)
    cx=c_triangle*x #r / r_scale
    return gc*(cx**2)/(1.+cx)**2

def dehnen_cusp_potential(x,c_triangle):# returns gravitational potential phi(x) / phi(0), where x = r/r_triangle
    gc=get_dehnen_cusp_gc(c_triangle)
    cx=c_triangle*x #r / r_scale
    return 1./(1.+cx)

def fncore(x,r_core,n_core):#returns f^n(x) for coreNFW model (Read, Walker, Pascal 2018), where x=r/r_triangle, r_core=r_core/r_triangle
    return (np.tanh(np.float64(x)/r_core))**n_core

def cnfw_mass_density(x,c_triangle,r_core,n_core):#returns rho_coreNFW(x) / rho_s, where x = r/r_triangle and rho_s is scale radius of NFW profile
    ncorem1=n_core-1.
    two=2.
    return fncore(x,r_core,n_core)*nfw_mass_density(x,c_triangle)+n_core*fncore(x,r_core,ncorem1)*(1.-fncore(x,r_core,two))/(x**2)/get_nfw_gc(c_triangle)*nfw_enclosed_mass(x,c_triangle)/r_core/(c_triangle**3)

def cnfw_enclosed_mass(x,c_triangle,r_core,n_core):# returns M_cNFW(x) / m_triangle, where x=r/r_triangle, r_core=(core radius)/ r_triangle
    return fncore(x,r_core,n_core)*nfw_enclosed_mass(x,c_triangle)

def cnfw_potential(x,c_triangle,r_core,n_core):# returns phi_cNFW(x) / phi_cNFW(0), where x=r/r_triangle, r_core=(core radius)/ r_triangle
    ncorem1=n_core-1.
    two=2.
    cx=c_triangle*x #r / r_scale
    polylog_vec=np.frompyfunc(mp.polylog,2,1)
    return (fncore(x,r_core,n_core)/cx*(np.log(1.+cx)-cx/(1.+cx)+1./(1.+cx)-1./(1.+c_triangle))+1./c_triangle/r_core*n_core*fncore(x,r_core,ncorem1)*(1.-fncore(x,r_core,two))*(np.log(1.+cx)-np.log(1.+c_triangle)+polylog_vec(2,-cx)-float(mp.polylog(2,-c_triangle))))/(fncore(x,r_core,n_core)*(2.-1./(1.+c_triangle))+n_core*1./c_triangle/r_core*fncore(x,r_core,ncorem1)*fncore(x,r_core,two)*(-np.log(1.+c_triangle)-float(mp.polylog(2,-c_triangle))))

def cnfwt_mass_density(x,c_triangle,r_core,n_core,r_tide,delta):#returns rho_coreNFWtides(x) / rho_0, where x = r/r_triangle
    if ((type(x) is float)|(type(x) is np.float64)):
        if x<r_tide:
            return cnfw_mass_density(x,c_triangle,r_core,n_core)
        else:
            return cnfw_mass_density(r_tide,c_triangle,r_core,n_core)*((x/r_tide)**(-delta))
    elif ((type(x) is list)|(type(x) is np.ndarray)):
        val=np.zeros(len(x))
        val[x<r_tide]=cnfw_mass_density(x[x<r_tide],c_triangle,r_core,n_core)
        val[x>=r_tide]=cnfw_mass_density(r_tide,c_triangle,r_core,n_core)*((x[x>=r_tide]/r_tide)**(-delta))
        return val
    
def cnfwt_enclosed_mass(x,c_triangle,r_core,n_core,r_tide,delta):#returns M_cNFWt(x) / m_triangle, where x=r/r_triangle, r_core=(core radius)/r_triangle, r_tide=(tidal radius)/r_triangle
    if ((type(x) is float)|(type(x) is np.float64)):
        if x<r_tide:
            return cnfw_enclosed_mass(x,c_triangle,r_core,n_core)
        else:
            return cnfw_enclosed_mass(r_tide,c_triangle,r_core,n_core)+cnfw_mass_density(r_tide,c_triangle,r_core,n_core)*get_nfw_gc(c_triangle)/(3.-delta)*((c_triangle*r_tide)**3)*(((x/r_tide)**(3.-delta))-1.)
    elif ((type(x) is list)|(type(x) is np.ndarray)):
        val=np.zeros(len(x))
        val[x<r_tide]=cnfw_enclosed_mass(x[x<r_tide],c_triangle,r_core,n_core)
        val[x>=r_tide]=cnfw_enclosed_mass(r_tide,c_triangle,r_core,n_core)+cnfw_mass_density(r_tide,c_triangle,r_core,n_core)*get_nfw_gc(c_triangle)/(3.-delta)*((c_triangle*r_tide)**3)*(((x[x>=r_tide]/r_tide)**(3.-delta))-1.)
        return val

def cnfwt_potential(x,c_triangle,r_core,n_core):# returns phi_cNFW(x) / phi_cNFW(0), where x=r/r_triangle, r_core=(core radius)/ r_triangle
    ncorem1=n_core-1.
    two=2.
    cx=c_triangle*x #r / r_scale
    return np.nan

def abg_triangle_mass_density(x,c_triangle,alpha,beta,gamma):# returns rho_abg(x) / rho_scale, where x = r / r_triangle
    cx=c_triangle*x #r / r_scale
    return 1./(cx**gamma)/(1.+cx**alpha)**((beta-gamma)/alpha)

def abg_triangle_enclosed_mass(x,c_triangle,alpha,beta,gamma):# returns enclosed mass M_abg(x) / m_triangle, where x = r/r_triangle
    if type(x) is ap.units.quantity.Quantity:#have to work around problems with scipy.special.modstruve working with quantities
        cx=c_triangle*x.value#r / r_scale
    else:
        cx=c_triangle*x #r / r_scale
    a=(3.-gamma)/alpha
    b=(beta-gamma)/alpha
    c=(3.-gamma+alpha)/alpha
    z1=-cx**alpha
    z2=-c_triangle**alpha
    hf1=scipy.special.hyp2f1(a,b,c,z1)  
    hf2=scipy.special.hyp2f1(a,b,c,z2)
    return ((cx/c_triangle)**(3.-gamma))*hf1/hf2

def abg_triangle_potential(x,c_triangle,alpha,beta,gamma):# returns enclosed mass M_abg(x) / m_triangle, where x = r/r_triangle
    return np.nan#not yet implemented

def get_plum_scale(luminosity_tot,r_scale):#nu_scale, normalization factor for number density profile
    nu_scale=3.*luminosity_tot/4./np.pi/r_scale**3
    sigma0=luminosity_tot/np.pi/r_scale**2
    return nu_scale,sigma0

def get_exp_scale(luminosity_tot,r_scale):#nu_scale, normalization factor for number density profile
    nu_scale=luminosity_tot/2./np.pi**2/r_scale**3
    sigma0=luminosity_tot/2./np.pi/r_scale**2
    return nu_scale,sigma0

def get_a2bg_scale(luminosity_tot,r_scale,beta,gamma):#nu_scale, normalization factor for number density profile
    alpha=2. 
    a=(3.-gamma)/alpha
    b=(beta-gamma)/alpha
    c=beta/2.
    d=(beta-3.)/alpha
    nu_scale=luminosity_tot/2./np.pi/r_scale**3/scipy.special.gamma(d)/scipy.special.gamma(a)*scipy.special.gamma(b)
    sigma0=luminosity_tot/4./np.sqrt(np.pi)/(r_scale**2)*(beta-3.)*scipy.special.gamma(b)/scipy.special.gamma(a)/scipy.special.gamma(c)
    return nu_scale,sigma0

def integrand_abg_scale(x,alpha,beta,gamma):
    return x*abg_luminosity_density_2d(x,alpha,beta,gamma)

def get_abg_scale(luminosity_tot,r_scale,alpha,beta,gamma):#nu_scale, normalization factor for number density profile
    a=(3.-gamma)/alpha
    b=(beta-gamma)/alpha
    c=beta/2.
    d=(beta-3.)/alpha
    nu_scale=luminosity_tot/4./np.pi/r_scale**3*alpha*scipy.special.gamma(b)/scipy.special.gamma(d)/scipy.special.gamma(a)
    
    min0=0.
    max0=np.inf
    int1=scipy.integrate.quad(integrand_abg_scale,min0,max0,args=(alpha,beta,gamma))
    sigma0=luminosity_tot/2./np.pi/r_scale**2/int1[0]
    return nu_scale,sigma0

def plum_luminosity_density(x):#nu(x) / nu_scale, x=r/r_scale
    return 1./(1.+x**2)**(2.5)

def plum_luminosity_density_2d(x):#Sigma(X) / Sigma0, X=R/r_scale
    return 1./(1.+x**2)**2

def exp_luminosity_density(x):#nu(x) / nu_scale, x=r/r_scale
    if type(x) is ap.units.quantity.Quantity:#have to work around problems with scipy.special.modstruve working with quantities
        return scipy.special.kn(0,x.value)
    else:
        return scipy.special.kn(0,x)

def exp_luminosity_density_2d(x):#Sigma(X) / Sigma0, X=R/r_scale
    return np.exp(-x)

def a2bg_luminosity_density(x,beta,gamma):#nu(x) / nu_scale, x=r/r_scale
    return 1./(x**gamma)/(1.+x**2)**((beta-gamma)/2.)

def a2bg_luminosity_density_2d(x,beta,gamma):#Sigma(X)/Sigma0, X=R/r_scale
    a=(beta-1.)/2.
    b=(beta-gamma)/2.
    c=beta/2.
    if type(x) is ap.units.quantity.Quantity:#have to work around problems with scipy.special.modstruve working with quantities
        z1=-1./x.value**2
        if ((type(x.value) is list)|(type(x.value) is np.ndarray)):
            z1[x.value<1.e-50]=-1.e+50
    else:
        z1=-1./x**2
        if ((type(x) is list)|(type(x) is np.ndarray)):
            z1[x<1.e-50]=-1.e+50
    hf1=scipy.special.hyp2f1(a,b,c,z1)  
    return x**(1.-beta)*hf1
    
def abg_luminosity_density(x,alpha,beta,gamma):#nu(x) / nu_scale, x=r/r_scale
    return 1./(x**gamma)/(1.+x**alpha)**((beta-gamma)/alpha)

def abg_luminosity_density_2d(x,alpha,beta,gamma):#Sigma(X)/Sigma0, X=R/r_scale
    def integrand_abg_luminosity_density_2d(x,bigx,alpha,beta,gamma):
        return x**(1.-gamma)/(1.+x**alpha)**((beta-gamma)/alpha)/np.sqrt(x**2-bigx**2)
    min0=x
    max0=np.inf
    int1=scipy.integrate.quad(integrand_abg_luminosity_density_2d,min0,max0,args=(x,alpha,beta,gamma))
    return int1[0]

def plum_enclosed_luminosity(x):#L(x) / luminosity_tot, x=r/r_scale
    return (x**3)/(1.+x**2)**(1.5)

def exp_enclosed_luminosity(x):#L(x) / luminosity_tot, x=r/r_scale
    if type(x) is ap.units.quantity.Quantity:#have to work around problems with scipy.special.modstruve working with quantities
        result=1./(3.*np.pi)*x*(3.*np.pi*scipy.special.kn(2,x.value)*scipy.special.modstruve(1,x.value)+scipy.special.kn(1,x.value)*(3.*np.pi*scipy.special.modstruve(2,x.value)-4.*x.value))
        if ((type(x.value) is list)|(type(x.value) is np.ndarray)):
            result[x.value>100]=1.
        else:
            if x.value>100:
                result=1.
    else:
        result=1./(3.*np.pi)*x*(3.*np.pi*scipy.special.kn(2,x)*scipy.special.modstruve(1,x)+scipy.special.kn(1,x)*(3.*np.pi*scipy.special.modstruve(2,x)-4.*x))
        if ((type(x) is list)|(type(x) is np.ndarray)):
            result[x>100]=1.
        else:
            if x>100.:
                result=1.
    return result

def a2bg_enclosed_luminosity(x,beta,gamma):#L(x)/luminosity_tot, x=r/r_scale
    alpha=2.
    a=(3.-gamma)/alpha
    b=(beta-gamma)/alpha
    c=(3.-gamma+alpha)/alpha
    d=(beta-3.)/alpha
    if type(x) is ap.units.quantity.Quantity:#have to work around problems with scipy.special.modstruve working with quantities
        z1=-x.value**alpha
    else:
        z1=-x**alpha
    z2=-np.inf**alpha
    hf1=scipy.special.hyp2f1(a,b,c,z1)  
    hf2=scipy.special.hyp2f1(a,b,c,z2)
    #return abg_enclosed_luminosity(x,2.,beta,gamma)
    return alpha/(3.-gamma)*(x**(3.-gamma))*hf1*scipy.special.gamma(b)/scipy.special.gamma(d)/scipy.special.gamma(a)
    
def abg_enclosed_luminosity(x,alpha,beta,gamma):#L(x)/luminosity_tot, x=r/r_scale
    a=(3.-gamma)/alpha
    b=(beta-gamma)/alpha
    c=(3.-gamma+alpha)/alpha
    d=(beta-3.)/alpha
    if type(x) is ap.units.quantity.Quantity:#have to work around problems with scipy.special.modstruve working with quantities
        z1=-x.value**alpha
    else:
        z1=-x**alpha
    z2=-np.inf**alpha
    hf1=scipy.special.hyp2f1(a,b,c,z1)  
    hf2=scipy.special.hyp2f1(a,b,c,z2)
    #return (x**(3.-gamma))*hf1/hf2 #should be equivalent to below
    return alpha/(3.-gamma)*(x**(3.-gamma))*hf1*scipy.special.gamma(b)/scipy.special.gamma(d)/scipy.special.gamma(a)

def plum_lscalenorm():#L(r_scale)/(nu_scale *r_scale**3)
    return 4.*np.pi/3./(2.**1.5)

def exp_lscalenorm():#L(r_scale)/(nu_scale *r_scale**3)
    return 2.*np.pi/3.*(3.*np.pi*scipy.special.kn(2,1.)*scipy.special.modstruve(1,1.)+scipy.special.kn(1,1.)*(3.*np.pi*scipy.special.modstruve(2,1.)-4.))

def a2bg_lscalenorm(beta,gamma):#L(r_scale)/(nu_scale * r_scale**3)
    alpha=2.
    a=(3.-gamma)/alpha
    b=(beta-gamma)/alpha
    c=(3.-gamma+alpha)/alpha
    z2=-1.
    hf2=scipy.special.hyp2f1(a,b,c,z2)
    return 4.*np.pi/(3.-gamma)*hf2
    
def abg_lscalenorm(alpha,beta,gamma):#L(r_scale)/(nu_scale * r_scale**3)
    a=(3.-gamma)/alpha
    b=(beta-gamma)/alpha
    c=(3.-gamma+alpha)/alpha
    z2=-1.
    hf2=scipy.special.hyp2f1(a,b,c,z2)
    return 4.*np.pi/(3.-gamma)*hf2

def plum_ltotnorm():#L(r=infinity)/(nu_scale * r_scale**3)
    return 4.*np.pi/3.

def exp_ltotnorm():#L(r=infinity)/(nu_scale * r_scale**3)
    return 2.*(np.pi**2)

def a2bg_ltotnorm(beta,gamma):#L(r=infinity)/(nu_scale * r_scale**3)
    alpha=2.
    a=(3.-gamma)/alpha
    b=(beta-gamma)/alpha
    #c=(3.-gamma+alpha)/alpha
    d=(beta-3.)/alpha
    return 2.*np.pi*scipy.special.gamma(d)*scipy.special.gamma(a)/scipy.special.gamma(b)

def abg_ltotnorm(alpha,beta,gamma):#L(r=infinity)/(nu_scale * r_scale**3)
    a=(3.-gamma)/alpha
    b=(beta-gamma)/alpha
    #c=(3.-gamma+alpha)/alpha
    d=(beta-3.)/alpha
    return 4.*np.pi/alpha*scipy.special.gamma(d)*scipy.special.gamma(a)/scipy.special.gamma(b)

def get_dmhalo(model,**params):
    
    class dmhalo:
        
        def __init__(self,model=None,triangle=None,h=None,m_triangle=None,c_triangle=None,r_triangle=None,r_core=None,n_core=None,r_tide=None,delta=None,alpha=None,beta=None,gamma=None,rho_scale=None,r_scale=None,v_max=None,r_max=None,mass_density=None,enclosed_mass=None,vcirc=None,potential=None,phi0=None):

            self.model=model
            self.triangle=triangle
            self.h=h
            self.m_triangle=m_triangle
            self.c_triangle=c_triangle
            self.r_triangle=r_triangle
            self.r_core=r_core
            self.n_core=n_core
            self.r_tide=r_tide
            self.delta=delta
            self.alpha=alpha
            self.beta=beta
            self.gamma=gamma
            self.rho_scale=rho_scale
            self.r_scale=r_scale
            self.v_max=v_max
            self.r_max=r_max
            self.mass_density=mass_density
            self.enclosed_mass=enclosed_mass
            self.vcirc=vcirc
            self.potential=potential
            self.phi0=phi0
            
    if model=='nfw':
        
        r_triangle,r_scale,rho_scale,phi0=get_nfw_scale(params['triangle'],params['h'],params['m_triangle'],params['c_triangle'])
        
        def mass_density(x):
            return nfw_mass_density(x,params['c_triangle'])#returns mass density rho(x) / rho_scale, where x = r/r_triangle
        def enclosed_mass(x):# returns enclosed mass M(x) / m_triangle, where x = r/r_triangle
            return nfw_enclosed_mass(x,params['c_triangle'])
        def potential(x):
            return nfw_potential(x,params['c_triangle'])#returns potential Phi(x)/Phi(0), where x = r/r_triangle, Phi(0) is central potential
        
    if model=='dehnen_core':
        
        r_triangle,r_scale,rho_scale,phi0=get_dehnen_core_scale(params['triangle'],params['h'],params['m_triangle'],params['c_triangle'])
        
        def mass_density(x):
            return dehnen_core_mass_density(x,params['c_triangle'])
        def enclosed_mass(x):# returns enclosed mass M(x) / m_triangle, where x = r/r_triangle
            return dehnen_core_enclosed_mass(x,params['c_triangle'])
        def potential(x):
            return dehnen_core_potential(x,params['c_triangle'])

    if model=='dehnen_cusp':
        
        r_triangle,r_scale,rho_scale,phi0=get_dehnen_cusp_scale(params['triangle'],params['h'],params['m_triangle'],params['c_triangle'])
        
        def mass_density(x):
            return dehnen_cusp_mass_density(x,params['c_triangle'])
        def enclosed_mass(x):# returns enclosed mass M(x) / m_triangle, where x = r/r_triangle
            return dehnen_cusp_enclosed_mass(x,params['c_triangle'])
        def potential(x):
            return dehnen_cusp_potential(x,params['c_triangle'])

    elif model=='abg':

        r_triangle,r_scale,rho_scale,phi0=get_abg_triangle_scale(params['triangle'],params['h'],params['m_triangle'],params['c_triangle'],params['alpha'],params['beta'],params['gamma'])

        def mass_density(x):
            return abg_triangle_mass_density(x,params['c_triangle'],params['alpha'],params['beta'],params['gamma'])
        def enclosed_mass(x):
            return abg_triangle_enclosed_mass(x,params['c_triangle'],params['alpha'],params['beta'],params['gamma'])
        def potential(x):
            return abg_triangle_potential(x,params['c_triangle'])

    elif model=='cnfw':#params['r_core'] is core radius
        
        r_triangle,r_scale,rho_scale,phi0=get_nfw_scale(params['triangle'],params['h'],params['m_triangle'],params['c_triangle'])
        
        ncorem1=params['n_core']-1.
        two=2.
        if type(params['m_triangle']) is ap.units.quantity.Quantity:    
            phi0=(-4.*np.pi*g_dim*rho_scale*r_scale**2*(fncore(0.,params['r_core'],params['n_core'])*(2.-1./(1.+params['c_triangle']))+params['n_core']*1./params['c_triangle']/params['r_core']*fncore(0.,params['r_core'],ncorem1)*(1.-fncore(0.,params['r_core'],two))*(-np.log(1.+params['c_triangle'])-float(mp.polylog(2.,-params['c_triangle']))))).to(u.km*u.km/u.s/u.s)
        else:
            phi0=-4.*np.pi*g*rho_scale*r_scale**2*(fncore(0.,params['r_core'],params['n_core'])*(2.-1./(1.+params['c_triangle']))+params['n_core']*1./params['c_triangle']/params['r_core']*fncore(0.,params['r_core'],ncorem1)*(1.-fncore(0.,params['r_core'],two))*(-np.log(1.+params['c_triangle'])-float(mp.polylog(2.,-params['c_triangle']))))
        
        def mass_density(x):
            return cnfw_mass_density(x,params['c_triangle'],params['r_core'],params['n_core'])
        def enclosed_mass(x):# returns enclosed mass M(x) / m_triangle, where x = r/r_triangle
            return cnfw_enclosed_mass(x,params['c_triangle'],params['r_core'],params['n_core'])
        def potential(x):
            return cnfw_potential(x,params['c_triangle'],params['r_core'],params['n_core'])

    elif model=='cnfwt':#params['r_core'] is core radius / r_triangle, params['r_tide'] is tidal radius / r_triangle
        
        r_triangle,r_scale,rho_scale,phi0=get_nfw_scale(params['triangle'],params['h'],params['m_triangle'],params['c_triangle'])
        phi0=np.nan#not yet implemented
        
        def mass_density(x):
            return cnfwt_mass_density(x,params['c_triangle'],params['r_core'],params['n_core'],params['r_tide'],params['delta'])
        def enclosed_mass(x):# returns enclosed mass M(x) / m_triangle, where x = r/r_triangle
            return cnfwt_enclosed_mass(x,params['c_triangle'],params['r_core'],params['n_core'],params['r_tide'],params['delta'])
        def potential(x):
            return cnfwt_potential(x,params['c_triangle'],params['r_core'],params['n_core'],params['r_tide'],params['delta'])
        
    def vcirc(x):# returns circular velocity, km/s
        if type(params['m_triangle']) is ap.units.quantity.Quantity:
            return np.sqrt(g_dim*enclosed_mass(x)*params['m_triangle']/(x*r_triangle))
        else:
            return np.sqrt(g*enclosed_mass(x)*params['m_triangle']/(x*r_triangle))
            
    def neg_vcirc2(x):
        if x<0.:
            return 1.e+30
        return -enclosed_mass(x)/x
        
    res=scipy.optimize.minimize(neg_vcirc2,[1.],method='nelder-mead',options={'xatol': 1e-8, 'disp': True})
    r_max=res.x[0]*r_triangle
    v_max=vcirc(res.x[0])

    if model=='nfw':
        return dmhalo(model=model,triangle=params['triangle'],h=params['h'],m_triangle=params['m_triangle'],c_triangle=params['c_triangle'],r_triangle=r_triangle,rho_scale=rho_scale,r_scale=r_scale,v_max=v_max,r_max=r_max,mass_density=mass_density,enclosed_mass=enclosed_mass,vcirc=vcirc,potential=potential,phi0=phi0)
    if model=='dehnen_core':
        return dmhalo(model=model,triangle=params['triangle'],h=params['h'],m_triangle=params['m_triangle'],c_triangle=params['c_triangle'],r_triangle=r_triangle,rho_scale=rho_scale,r_scale=r_scale,v_max=v_max,r_max=r_max,mass_density=mass_density,enclosed_mass=enclosed_mass,vcirc=vcirc,potential=potential,phi0=phi0)
    if model=='dehnen_cusp':
        return dmhalo(model=model,triangle=params['triangle'],h=params['h'],m_triangle=params['m_triangle'],c_triangle=params['c_triangle'],r_triangle=r_triangle,rho_scale=rho_scale,r_scale=r_scale,v_max=v_max,r_max=r_max,mass_density=mass_density,enclosed_mass=enclosed_mass,vcirc=vcirc,potential=potential,phi0=phi0)
    elif model=='abg':
        return dmhalo(model=model,triangle=params['triangle'],h=params['h'],m_triangle=params['m_triangle'],c_triangle=params['c_triangle'],r_triangle=r_triangle,alpha=params['alpha'],beta=params['beta'],gamma=params['gamma'],rho_scale=rho_scale,r_scale=r_scale,v_max=v_max,r_max=r_max,mass_density=mass_density,enclosed_mass=enclosed_mass,vcirc=vcirc,potential=potential,phi0=phi0)
    elif model=='cnfw':
        return dmhalo(model=model,triangle=params['triangle'],h=params['h'],m_triangle=params['m_triangle'],c_triangle=params['c_triangle'],r_triangle=r_triangle,r_core=params['r_core'],n_core=params['n_core'],rho_scale=rho_scale,r_scale=r_scale,v_max=v_max,r_max=r_max,mass_density=mass_density,enclosed_mass=enclosed_mass,vcirc=vcirc,potential=potential,phi0=phi0)
    elif model=='cnfwt':
        return dmhalo(model=model,triangle=params['triangle'],h=params['h'],m_triangle=params['m_triangle'],c_triangle=params['c_triangle'],r_triangle=r_triangle,r_core=params['r_core'],n_core=params['n_core'],r_tide=params['r_tide'],delta=params['delta'],rho_scale=rho_scale,r_scale=r_scale,v_max=v_max,r_max=r_max,mass_density=mass_density,enclosed_mass=enclosed_mass,vcirc=vcirc,potential=potential,phi0=phi0)
    else:
        raise TypeError('DM halo not properly specified!')
    
def get_tracer(model,**params):

    class tracer:

        def __init__(self,model=None,luminosity_tot=None,upsilon=None,r_scale=None,nu_scale=None,sigma0=None,lscalenorm=None,ltotnorm=None,alpha=None,beta=None,gamma=None,rhalf_2d=None,rhalf_3d=None,luminosity_density=None,luminosity_density_2d=None,enclosed_luminosity=None):

            self.model=model
            self.luminosity_tot=luminosity_tot
            self.upsilon=upsilon
            self.r_scale=r_scale
            self.nu_scale=nu_scale
            self.sigma0=sigma0
            self.lscalenorm=lscalenorm
            self.ltotnorm=ltotnorm
            self.alpha=alpha
            self.beta=beta
            self.gamma=gamma
            self.rhalf_2d=rhalf_2d
            self.rhalf_3d=rhalf_3d
            self.luminosity_density=luminosity_density
            self.luminosity_density_2d=luminosity_density_2d
            self.enclosed_luminosity=enclosed_luminosity

    if model=='plum':

        rhalf_2d,rhalf_3d,xxx,yyy=get_rhalf(model,params['r_scale'],bigsigma0=1.,ellipticity=0.)
        nu_scale,sigma0=get_plum_scale(params['luminosity_tot'],params['r_scale'])
        def luminosity_density(x):
            return plum_luminosity_density(x)
        def luminosity_density_2d(x):
            return plum_luminosity_density_2d(x)
        def enclosed_luminosity(x):
            return plum_enclosed_luminosity(x)

        return tracer(model=model,luminosity_tot=params['luminosity_tot'],r_scale=params['r_scale'],upsilon=params['upsilon'],nu_scale=nu_scale,sigma0=sigma0,lscalenorm=plum_lscalenorm(),ltotnorm=plum_ltotnorm(),rhalf_2d=rhalf_2d,rhalf_3d=rhalf_3d,luminosity_density=luminosity_density,luminosity_density_2d=luminosity_density_2d,enclosed_luminosity=enclosed_luminosity)

    if model=='exp':

        rhalf_2d,rhalf_3d,xxx,yyy=get_rhalf(model,params['r_scale'],bigsigma0=1.,ellipticity=0.)
        nu_scale,sigma0=get_exp_scale(params['luminosity_tot'],params['r_scale'])
        def luminosity_density(x):
            return exp_luminosity_density(x)
        def luminosity_density_2d(x):
            return exp_luminosity_density_2d(x)
        def enclosed_luminosity(x):
            return exp_enclosed_luminosity(x)
        
        return tracer(model=model,luminosity_tot=params['luminosity_tot'],r_scale=params['r_scale'],upsilon=params['upsilon'],nu_scale=nu_scale,sigma0=sigma0,lscalenorm=exp_lscalenorm(),ltotnorm=exp_ltotnorm(),rhalf_2d=rhalf_2d,rhalf_3d=rhalf_3d,luminosity_density=luminosity_density,luminosity_density_2d=luminosity_density_2d,enclosed_luminosity=enclosed_luminosity)
    
    if model=='a2bg':

        rhalf_2d,rhalf_3d,xxx,yyy=get_rhalf(model,params['r_scale'],bigsigma0=1.,ellipticity=0.,beta=params['beta'],gamma=params['gamma'])
        nu_scale,sigma0=get_a2bg_scale(params['luminosity_tot'],params['r_scale'],params['beta'],params['gamma'])
        def luminosity_density(x):
            return a2bg_luminosity_density(x,params['beta'],params['gamma'])
        def luminosity_density_2d(x):
            return a2bg_luminosity_density_2d(x,params['beta'],params['gamma'])
        def enclosed_luminosity(x):
            return a2bg_enclosed_luminosity(x,params['beta'],params['gamma'])
        
        return tracer(model=model,luminosity_tot=params['luminosity_tot'],r_scale=params['r_scale'],upsilon=params['upsilon'],nu_scale=nu_scale,sigma0=sigma0,lscalenorm=a2bg_lscalenorm(params['beta'],params['gamma']),ltotnorm=a2bg_ltotnorm(params['beta'],params['gamma']),beta=params['beta'],gamma=params['gamma'],rhalf_2d=rhalf_2d,rhalf_3d=rhalf_3d,luminosity_density=luminosity_density,luminosity_density_2d=luminosity_density_2d,enclosed_luminosity=enclosed_luminosity)
    
    if model=='abg':

        rhalf_2d,rhalf_3d,xxx,yyy=get_rhalf(model,params['r_scale'],bigsigma0=1.,ellipticity=0.,alpha=params['alpha'],beta=params['beta'],gamma=params['gamma'])
        nu_scale,sigma0=get_abg_scale(params['luminosity_tot'],params['r_scale'],params['alpha'],params['beta'],params['gamma'])
        def luminosity_density(x):
            return abg_luminosity_density(x,params['alpha'],params['beta'],params['gamma'])
        def luminosity_density_2d(x):
            return abg_luminosity_density_2d(x,params['alpha'],params['beta'],params['gamma'])
        def enclosed_luminosity(x):
            return abg_enclosed_luminosity(x,params['alpha'],params['beta'],params['gamma'])
        
        return tracer(model=model,luminosity_tot=params['luminosity_tot'],r_scale=params['r_scale'],upsilon=params['upsilon'],nu_scale=nu_scale,sigma0=sigma0,lscalenorm=abg_lscalenorm(params['alpha'],params['beta'],params['gamma']),ltotnorm=abg_ltotnorm(params['alpha'],params['beta'],params['gamma']),alpha=params['alpha'],beta=params['beta'],gamma=params['gamma'],rhalf_2d=rhalf_2d,rhalf_3d=rhalf_3d,luminosity_density=luminosity_density,luminosity_density_2d=luminosity_density_2d,enclosed_luminosity=enclosed_luminosity)

def get_anisotropy(model,**params):

    class anisotropy:

        def __init__(self,model=None,beta_0=None,beta_inf=None,r_beta=None,n_beta=None,f_beta=None,beta=None):

            self.model=model
            self.beta_0=beta_0
            self.beta_inf=beta_inf
            self.r_beta=r_beta
            self.n_beta=n_beta
            self.f_beta=f_beta
            self.beta=beta

    if model=='read':

        def beta(x):#x = r / r_beta
            return params['beta_0']+(params['beta_inf']-params['beta_0'])/(1.+x**(-params['n_beta']))
        def f_beta(x):# x = r / r_beta
            return x**(2.*params['beta_inf'])*(1.+x**(-params['n_beta']))**(2.*(params['beta_inf']-params['beta_0'])/params['n_beta'])
    
        return anisotropy(model=model,beta_0=params['beta_0'],beta_inf=params['beta_inf'],r_beta=params['r_beta'],n_beta=params['n_beta'],f_beta=f_beta,beta=beta)
    
    else:
        raise TypeError('anisotropy model not properly specified!')

def get_rhalf(model,r_scale,**params):

    if model=='plum':
        rhalf_2d=r_scale
        rhalf_3d=1.30476909*r_scale
        nu_scale=3*params['bigsigma0']/4/r_scale
        ntot=(1.-params['ellipticity'])*np.pi*r_scale**2*params['bigsigma0']
    elif model=='exp':
        rhalf_2d=1.67835*r_scale
        rhalf_3d=2.22352*r_scale
        nu_scale=params['bigsigma0']/np.pi/r_scale
        ntot=(1.-params['ellipticity'])*2.*np.pi*r_scale**2*params['bigsigma0']
    elif model=='a2bg':
        def rootfind_a2bg_2d(x,beta,gamma):
            return 0.5-np.sqrt(np.pi)*scipy.special.gamma((beta-gamma)/2)/2/scipy.special.gamma(beta/2)/scipy.special.gamma((3-gamma)/2)*x**(3-beta)*scipy.special.hyp2f1((beta-3)/2,(beta-gamma)/2,beta/2,-1/x**2)
        def rootfind_a2bg_3d(x,beta,gamma):
            return -0.5+2*scipy.special.gamma((beta-gamma)/2)/scipy.special.gamma((beta-3)/2)/scipy.special.gamma((3-gamma)/2)/(3-gamma)*x**(3-gamma)*scipy.special.hyp2f1((3-gamma)/2,(beta-gamma)/2,(5-gamma)/2,-x**2)
        low0=1.e-20
        high0=1.e+20
        rhalf_2d=r_scale*scipy.optimize.brentq(rootfind_a2bg_2d,low0,high0,args=(params['beta'],params['gamma']),xtol=1.e-12,rtol=1.e-6,maxiter=1000,full_output=False,disp=True)
        rhalf_3d=r_scale*scipy.optimize.brentq(rootfind_a2bg_3d,low0,high0,args=(params['beta'],params['gamma']),xtol=1.e-12,rtol=1.e-6,maxiter=100,full_output=False,disp=True)
        nu_scale=params['bigsigma0']*scipy.special.gamma(params['beta']/2)/np.sqrt(np.pi)/r_scale/scipy.special.gamma((params['beta']-1)/2)
        ntot=(1.-params['ellipticity'])*4.*np.sqrt(np.pi)*r_scale**2*params['bigsigma0']/(params['beta']-3)*scipy.special.gamma((3-params['gamma'])/2)*scipy.special.gamma(params['beta']/2)/scipy.special.gamma((params['beta']-params['gamma'])/2)

    elif model=='abg':
        a=(3.-params['gamma'])/params['alpha']
        b=(params['beta']-params['gamma'])/params['alpha']
        c=(3.-params['gamma']+params['alpha'])/params['alpha']
        d=(params['beta']-3.)/params['alpha']
        def rootfind_abg_2d(x,alpha,beta,gamma):
            min0=0.
            max0=x
            int1=scipy.integrate.quad(integrand_abg_scale,min0,max0,args=(alpha,beta,gamma))
            min0=0.
            max0=np.inf
            int2=scipy.integrate.quad(integrand_abg_scale,min0,max0,args=(alpha,beta,gamma))
            return -0.5+int1[0]/int2[0]#not computed yet, projection of abg model requires numerical integration
        def rootfind_abg_3d(x,alpha,beta,gamma):
            #a=(3.-gamma)/alpha
            #b=(beta-gamma)/alpha
            #c=(3.-gamma+alpha)/alpha
            #d=(beta-3.)/alpha
            z1=-x**alpha
            return -0.5+(x**(3.-gamma))*scipy.special.hyp2f1(a,b,c,z1)*scipy.special.gamma(b)/scipy.special.gamma(d)/scipy.special.gamma(c)
        low0=1.e-20
        high0=1.e+5
        rhalf_2d=r_scale*scipy.optimize.brentq(rootfind_abg_2d,low0,high0,args=(params['alpha'],params['beta'],params['gamma']),xtol=1.e-12,rtol=1.e-6,maxiter=100,full_output=False,disp=True)
        rhalf_3d=r_scale*scipy.optimize.brentq(rootfind_abg_3d,low0,high0,args=(params['alpha'],params['beta'],params['gamma']),xtol=1.e-12,rtol=1.e-6,maxiter=100,full_output=False,disp=True)
        nu_scale=params['bigsigma0']/2./r_scale
        ntot=4.*np.pi*nu_scale*(r_scale**3)*scipy.special.gamma(d)*scipy.special.gamma(a)/scipy.special.gamma(b)/params['alpha']#for this one use integral of 3d profile, which is analytic

    elif model=='captured_truncated':
        return
    else:
        raise ValueError('error in model specification')
    return rhalf_2d,rhalf_3d,nu_scale,ntot
    
def integrate(bigx,dmhalo,tracer,anisotropy,**params):
    
    if 'component' not in params:
        params['component']=['los','rad','tan','3d']#default is to calculate all three projected components and both 3D components (3D angular components are equal)
    if not 'upper_limit' in params:#default upper limit is infinity, common alternative is dmhalo.r_triangle
        params['upper_limit']=np.inf
    if not 'epsrel' in params:
        params['epsrel']=1.49e-8
    if not 'epsabs' in params:
        params['epsabs']=1.49e-8
    if not 'limit' in params:
        params['limit']=50

    class jeans_integral:
        def __init__(self,sigma_proj_los=None,sigma_proj_rad=None,sigma_proj_tan=None,sigma_rad=None,sigma_tan=None):
            self.sigma_proj_los=sigma_proj_los
            self.sigma_proj_rad=sigma_proj_rad
            self.sigma_proj_tan=sigma_proj_tan
            self.sigma_rad=sigma_rad
            self.sigma_tan=sigma_tan
        
    def integrand1(x_halo,dmhalo,tracer,anisotropy):
        x_beta=x_halo*dmhalo.r_triangle/tracer.r_scale/anisotropy.r_beta# r / r_beta
        x_tracer=x_halo*dmhalo.r_triangle/tracer.r_scale# r / r_scale
        enclosed_mass=dmhalo.enclosed_mass(x_halo)+tracer.enclosed_luminosity(x_tracer)*tracer.luminosity_tot*tracer.upsilon/dmhalo.m_triangle
        return enclosed_mass*tracer.luminosity_density(x_tracer)*anisotropy.f_beta(x_beta)/x_halo**2
    
    def integrand_los(x_halo,dmhalo,tracer,anisotropy):
        x_beta=x_halo*dmhalo.r_triangle/tracer.r_scale/anisotropy.r_beta# r / r_beta
        min0=x_halo
        max0=params['upper_limit']
        int1=scipy.integrate.quad(integrand1,min0,max0,args=(dmhalo,tracer,anisotropy),epsrel=params['epsrel'],epsabs=params['epsabs'])
        return (1.-anisotropy.beta(x_beta)*(bigx/x_halo)**2)/np.sqrt(1.-(bigx/x_halo)**2)/anisotropy.f_beta(x_beta)*int1[0]

    def integrand_rad(x_halo,dmhalo,tracer,anisotropy):
        x_beta=x_halo*dmhalo.r_triangle/tracer.r_scale/anisotropy.r_beta# r / r_beta
        min0=x_halo
        max0=params['upper_limit']
        int1=scipy.integrate.quad(integrand1,min0,max0,args=(dmhalo,tracer,anisotropy),epsrel=params['epsrel'],epsabs=params['epsabs'])
        return (1.-anisotropy.beta(x_beta)+anisotropy.beta(x_beta)*(bigx/x_halo)**2)/np.sqrt(1.-(bigx/x_halo)**2)/anisotropy.f_beta(x_beta)*int1[0]

    def integrand_tan(x_halo,dmhalo,tracer,anisotropy):
        x_beta=x_halo*dmhalo.r_triangle/tracer.r_scale/anisotropy.r_beta# r / r_beta
        min0=x_halo
        max0=params['upper_limit']
        int1=scipy.integrate.quad(integrand1,min0,max0,args=(dmhalo,tracer,anisotropy),epsrel=params['epsrel'],epsabs=params['epsabs'])
        return (1.-anisotropy.beta(x_beta))/np.sqrt(1.-(bigx/x_halo)**2)/anisotropy.f_beta(x_beta)*int1[0]
    
    min0=bigx
    max0=params['upper_limit']
    bigx_tracer=bigx*dmhalo.r_triangle/tracer.r_scale
    
    bigsigmasigmalos2,bigsigmasigmarad2,bigsigmasigmatan2,nusigmarad2,nusigmatan2,sigma_proj_los,sigma_proj_rad,sigma_proj_tan,sigma_rad,sigma_tan=np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan
    
    if min0>=max0:
        bigsigmasigmalos2,bigsigmasigmarad2,bigsigmasigmatan2,nusigmarad2,nusigmatan2,sigma_proj_los,sigma_proj_rad,sigma_proj_tan,sigma_rad,sigma_tan=0.,0.,0.,0.,0.,0.,0.,0.,0.,0.
        
    else:
        
        if '3d' in params['component']:
            x_halo=bigx#this is now the 3D radius, r/r_triangle, for purpose of the 3D integral
            x_beta=x_halo*dmhalo.r_triangle/tracer.r_scale/anisotropy.r_beta# r / r_beta
            if type(dmhalo.m_triangle) is ap.units.quantity.Quantity:
                nusigmarad2=g_dim*dmhalo.m_triangle/dmhalo.r_triangle/anisotropy.f_beta(x_beta)*scipy.integrate.quad(integrand1,min0,max0,args=(dmhalo,tracer,anisotropy),epsrel=params['epsrel'],epsabs=params['epsabs'])[0]#sigma^2_r(x) * nu(x) / nu_scale, sigma_r(x) is 3D radial velocity dispersion at x=r/r_triangle
            else:
                nusigmarad2=g*dmhalo.m_triangle/dmhalo.r_triangle/anisotropy.f_beta(x_beta)*scipy.integrate.quad(integrand1,min0,max0,args=(dmhalo,tracer,anisotropy),epsrel=params['epsrel'],epsabs=params['epsabs'])[0]#sigma^2_r(x) * nu(x) / nu_scale, sigma_r(x) is 3D radial velocity dispersion at x=r/r_triangle

            nusigmatan2=nusigmarad2*(1.-anisotropy.beta(x_beta))#sigma^2_t(x) * nu(x) / nu_scale, sigma_t(x) is 3D tangential velocity dispersion at x=r/r_triangle, equals both the theta component and the phi component
                
        if 'los' in params['component']:
            if type(dmhalo.m_triangle) is ap.units.quantity.Quantity:
                bigsigmasigmalos2=2.*g_dim*dmhalo.m_triangle*scipy.integrate.quad(integrand_los,min0,max0,args=(dmhalo,tracer,anisotropy),epsrel=params['epsrel'],epsabs=params['epsabs'])[0]#sigma^2_los(X) * Sigma(X) / nu_scale
            else:
                bigsigmasigmalos2=2.*g*dmhalo.m_triangle*scipy.integrate.quad(integrand_los,min0,max0,args=(dmhalo,tracer,anisotropy),epsrel=params['epsrel'],epsabs=params['epsabs'])[0]#sigma^2_los(X) * Sigma(X) / nu_scale
        if 'rad' in params['component']:
            if type(dmhalo.m_triangle) is ap.units.quantity.Quantity:
                bigsigmasigmarad2=2.*g_dim*dmhalo.m_triangle*scipy.integrate.quad(integrand_rad,min0,max0,args=(dmhalo,tracer,anisotropy),epsrel=params['epsrel'],epsabs=params['epsabs'])[0]#sigma^2_rad(X) * Sigma(X) / nu_scale
            else:
                bigsigmasigmarad2=2.*g*dmhalo.m_triangle*scipy.integrate.quad(integrand_rad,min0,max0,args=(dmhalo,tracer,anisotropy),epsrel=params['epsrel'],epsabs=params['epsabs'])[0]#sigma^2_rad(X) * Sigma(X) / nu_scale
        if 'tan' in params['component']:
            if type(dmhalo.m_triangle) is ap.units.quantity.Quantity:
                bigsigmasigmatan2=2.*g_dim*dmhalo.m_triangle*scipy.integrate.quad(integrand_tan,min0,max0,args=(dmhalo,tracer,anisotropy),epsrel=params['epsrel'],epsabs=params['epsabs'])[0]#sigma^2_tan(X) * Sigma(X) / nu_scale
            else:
                bigsigmasigmatan2=2.*g*dmhalo.m_triangle*scipy.integrate.quad(integrand_tan,min0,max0,args=(dmhalo,tracer,anisotropy),epsrel=params['epsrel'],epsabs=params['epsabs'])[0]#sigma^2_tan(X) * Sigma(X) / nu_scale
            
        sigma_proj_los=np.sqrt(bigsigmasigmalos2/(tracer.luminosity_density_2d(bigx_tracer)*tracer.sigma0/tracer.nu_scale))
        sigma_proj_rad=np.sqrt(bigsigmasigmarad2/(tracer.luminosity_density_2d(bigx_tracer)*tracer.sigma0/tracer.nu_scale))
        sigma_proj_tan=np.sqrt(bigsigmasigmatan2/(tracer.luminosity_density_2d(bigx_tracer)*tracer.sigma0/tracer.nu_scale))
        sigma_rad=np.sqrt(nusigmarad2/(tracer.luminosity_density(bigx_tracer)))
        sigma_tan=np.sqrt(nusigmatan2/(tracer.luminosity_density(bigx_tracer)))
    return jeans_integral(sigma_proj_los=sigma_proj_los,sigma_proj_rad=sigma_proj_rad,sigma_proj_tan=sigma_proj_tan,sigma_rad=sigma_rad,sigma_tan=sigma_tan)

def integrate_isotropic(bigx,dmhalo,tracer,**params):
    if not 'upper_limit' in params:#default upper limit is infinity, common alternative is dmhalo.r_triangle
        params['upper_limit']=np.inf
    if not 'epsrel' in params:
        params['epsrel']=1.49e-8
    if not 'epsabs' in params:
        params['epsabs']=1.49e-8
    if not 'limit' in params:
        params['limit']=50
        
    def integrand1(x_halo,dmhalo,tracer):
        x_tracer=x_halo*dmhalo.r_triangle/tracer.r_scale# r / r_scale
        enclosed_mass=dmhalo.enclosed_mass(x_halo)+tracer.enclosed_luminosity(x_tracer)*tracer.luminosity_tot*tracer.upsilon/dmhalo.m_triangle
        return np.sqrt(1.-(bigx/x_halo)**2)*enclosed_mass*tracer.luminosity_density(x_tracer)/x_halo
    
    min0=bigx
    max0=params['upper_limit']
    if type(m_triangle) is ap.units.quantity.Quantity:
        return 2.*g_dim*dmhalo.m_triangle*scipy.integrate.quad(integrand1,min0,max0,args=(dmhalo,tracer),epsrel=params['epsrel'],epsabs=params['epsabs'])[0]#sigma^2_LOS(X) * Sigma(X) / nu_scale
    else:
        return 2.*g*dmhalo.m_triangle*scipy.integrate.quad(integrand1,min0,max0,args=(dmhalo,tracer),epsrel=params['epsrel'],epsabs=params['epsabs'])[0]#sigma^2_LOS(X) * Sigma(X) / nu_scale

def projected_virial(x_halo,dmhalo,tracer):#computes integral for Wlos from Errani etal (2018)
    x_tracer=x_halo*dmhalo.r_triangle/tracer.r_scale
    totalmass=dmhalo.enclosed_mass(x_halo)+tracer.enclosed_luminosity(x_tracer)*tracer.luminosity_tot*tracer.upsilon/dmhalo.m_triangle
    return x_halo*tracer.luminosity_density(x_tracer)*totalmass

def get_virial(dmhalo,tracer,**params):
    if not 'lamb' in params:
        params['lamb']=1.
    if not 'epsrel' in params:
        params['epsrel']=1.e-13
    if not 'epsabs' in params:
        params['epsabs']=0.
    if not 'limit' in params:
        params['limit']=500

    min0=0.
    max0=np.inf
    val1=scipy.integrate.quad(projected_virial,min0,max0,args=(dmhalo,tracer),epsabs=params['epsabs'],epsrel=params['epsrel'],limit=params['limit'])
    if type(dmhalo.m_triangle) is ap.units.quantity.Quantity:
        vvar=val1[0]*4.*np.pi*g_dim/3.*dmhalo.m_triangle*(dmhalo.r_triangle**2)/tracer.ltotnorm/tracer.r_scale**3
        mu=g_dim*(dmhalo.enclosed_mass(params['lamb']*tracer.rhalf_2d/dmhalo.r_triangle)+tracer.enclosed_luminosity(params['lamb']*tracer.rhalf_2d/tracer.r_scale)*tracer.luminosity_tot*tracer.upsilon/dmhalo.m_triangle)*dmhalo.m_triangle/params['lamb']/tracer.rhalf_2d/vvar
        return np.sqrt(vvar),mu.value
    else:
        vvar=val1[0]*4.*np.pi*g/3.*dmhalo.m_triangle*(dmhalo.r_triangle**2)/tracer.ltotnorm/tracer.r_scale**3
        mu=g*(dmhalo.enclosed_mass(params['lamb']*tracer.rhalf_2d/dmhalo.r_triangle)+tracer.enclosed_luminosity(params['lamb']*tracer.rhalf_2d/tracer.r_scale)*tracer.luminosity_tot*tracer.upsilon/dmhalo.m_triangle)*dmhalo.m_triangle/params['lamb']/tracer.rhalf_2d/vvar
        return np.sqrt(vvar),mu
