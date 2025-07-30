# jeans

A package for calculating properties of (spherical) dark matter halos and embedded (spherical) stellar populations, including integration of the (spherical) Jeans equation in 2D (observed projections) and 3D.

Author: Matthew G. Walker (2024) 

# Instructions 

* Install jeans. You can either pip install the released version or install from github

```
pip install jeans
```
# Available Dark Matter Halo Models

The alpha/beta/gamma ('abg_triangle') halo has mass density profile $\rho(r)=\frac{\rho_s}{(r/r_s)^{\gamma}[1+(r/r_s)^{\alpha}]^{(\beta-\gamma)/\alpha}}$.

The Navarro-Frenk-White ('nfw') halo is a special case of the above, with $(\alpha,\beta,\gamma)=(1,3,1)$, but can be called directly. 

The Dehnen Cusp ('dehnen_cusp') halo is a special case of the 'abg' halo, with $(\alpha,\beta,\gamma)=(1,4,1)$, but can be called directly.

The Dehnen Core ('dehnen_core') halo is a special case of the 'abg' halo, with $(\alpha,\beta,\gamma)=(1,4,0)$, but can be called directly. 

The core-NFW ('cnfw') halo is by Read et al. (arXiv:1805.06934), defined in terms of the enclosed mass profile, $M_{\rm cNFW}(r)=M_{\rm NFW}(r)f^n$, where $M_{\rm NFW}(r)$ is the enclosed mass profile of the NFW halo and $f^n=[\tanh(r/r_c)]^n$, with $r_c$ a core radius.

The core-NFW-tides ('cnfwt') halo is by Read et al. (arXiv:1805.06934), with density profile $\rho_{\rm cNFWt}(r)=\rho_{\rm cNFW}(r)$ for $r<r_{\rm t}$ and $\rho_{\rm cNFWt}(r)=\rho_{\rm cNFW}(r_{\rm t})(r/r_{\rm t})^{-\delta}$, allowing for power-law decrease in density beyond `tidal' radius $r_{\rm t}$.

For cNFW and cNFWt models, the standard definitions of parameters $M_{\triangle}$, $c_{\triangle}$ and $r_{\triangle}$ apply to the density and mass profile of the corresponding NFW halo that would be obtained by setting $r_{\rm c}=0$ and $r_{\rm t}=\infty$.


# Available Models for Tracer component

The alpha/beta/gamma ('abg') model has number density profile $\nu(r)=\frac{\nu_0}{(r/r_s)^{\gamma}[1+(r/r_s)^{\alpha}]^{(\beta-\gamma)/\alpha}}$.

The Plummer model ('plum') is a special case of the 'abg' model, with $(\alpha,\beta,\gamma)=(2,5,0)$, but can be called directly.

The 'a2bg' model is a special case of the 'abg' model, with $\alpha=2$, but can be called directly.

The exponential model 'exp' is defined in terms of projected density, $\Sigma(R)=\Sigma_0\exp(-R/r_s)$.

# Available Models for velocity dispersion anisotropy of the tracer component

The only model currently implemented is that of Read et al. (arXiv:1805.06934): $\beta(r)\equiv 1-\sigma^2_{\rm t}/\sigma^2_{\rm r}=\beta_0+(\beta_{\infty}-\beta_0)/(1+(r/r_{\beta})^{-n})$, where $\sigma_{\rm r}$ is the radial component of the velocity dispersion and $\sigma_{\rm t}=\sigma_{\theta}=\sigma_{\phi}$ is the tangential component (the two angular components have equal magnitude in the absence of rotation).  

# Usage

See [notebook](examples/jeans_example1.ipynb) in the examples folder.

# Examples 

See [notebook](examples/jeans_example1.ipynb) in the examples folder.

# Acknowledgement

