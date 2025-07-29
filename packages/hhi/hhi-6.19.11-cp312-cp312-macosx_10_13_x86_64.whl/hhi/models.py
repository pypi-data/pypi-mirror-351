from __future__ import annotations

import sys
from functools import partial

import gplugins.sax.models as sm
from gplugins.sax.models import get_models

nm = 1e-3
straight = partial(sm.straight, wl0=1.55, neff=2.4, ng=4.2)
bend_euler_sc = bend_euler = partial(sm.bend, loss=0.03)

################
# MMIs
################
HHI_MMI1x2E1700 = partial(sm.mmi1x2, wl0=1.55, fwhm=0.2, loss_dB=1.0)
HHI_MMI1x2E600 = partial(sm.mmi1x2, wl0=1.55, fwhm=0.2, loss_dB=1.0)
HHI_MMI1x2ACT = partial(sm.mmi1x2, wl0=1.55, fwhm=0.2, loss_dB=1.0)

HHI_MMI2x2ACT = partial(sm.mmi2x2, wl0=1.55, fwhm=0.2, loss_dB=1.0)
HHI_MMI2x2E1700 = partial(sm.mmi2x2, wl0=1.55, fwhm=0.2, loss_dB=1.0)
HHI_MMI2x2E600 = partial(sm.mmi2x2, wl0=1.55, fwhm=0.2, loss_dB=1.0)

coupler = sm.coupler
models = get_models(sys.modules[__name__])
