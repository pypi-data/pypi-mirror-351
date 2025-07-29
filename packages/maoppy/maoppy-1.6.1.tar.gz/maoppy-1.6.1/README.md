# MAOPPY

**M**odelization of the
**A**daptive
**O**ptics
**P**sf in
**PY**thon

Parsimonious modelization of the PSF for astronomy applications.
It includes the `Moffat` model (Moffat 1969) and the `Psfao` model (Fétick+2019b, see full reference below) dedicated to the AO corrected PSF.

The instruments ELT/HARMONI, VLT/SPHERE/ZIMPOL, VLT/MUSE and OHP/PAPYRUS are already implemented.
Feel free to add yours, and do not hesitate to contact me if you wish to contribute to the library.

## Quick start

[Repository](https://gitlab.lam.fr/lam-grd-public/maoppy)

[Documentation](https://gitlab.lam.fr/lam-grd-public/maoppy/-/wikis/home)

## Author

Romain JL. Fétick (romain.fetick@lam.fr)

Laboratoire d'Astrophysique de Marseille / ONERA Salon-de-Provence

38 rue Frédéric Joliot Curie, 13388 Marseille (France)

## Scientific references

Full description and validation of the `Psfao` model:

* [Fétick et al., August 2019, Astronomy and Astrophysics, Vol.628](https://www.aanda.org/articles/aa/abs/2019/08/aa35830-19/aa35830-19.html)

Scientific applications:

* STARFINDER2 [Schreiber et al., Dec. 2020, SPIE proceedings, Vol.11448](https://www.spiedigitallibrary.org/conference-proceedings-of-spie/11448/114480H/Starfinder2--a-software-package-for-identification-and-analysis-of/10.1117/12.2564105.full)
* photometry [Massari et al., Dec. 2020, SPIE proceedings, Vol.11448](https://www.spiedigitallibrary.org/conference-proceedings-of-spie/11448/114480G/Precise-photometry-and-astrometry-in-the-core-of-the-globular/10.1117/12.2560938.full)
* deconvolution [Fétick et al., July 2020, MNRAS, Vol.496](https://academic.oup.com/mnras/article-abstract/496/4/4209/5871799)
* PSF extraction in crowded field [Gottgens et al., Aug. 2021, MNRAS, Vol.507](https://doi.org/10.1093/mnras/stab2449)

More developments on the `Psfao` model:

* [Beltramo-Martin et al., Nov. 2020, Astronomy and Astrophysics, Vol.643](https://www.aanda.org/articles/aa/abs/2020/11/aa38679-20/aa38679-20.html)

## License

See the [LICENSE file](LICENSE)
