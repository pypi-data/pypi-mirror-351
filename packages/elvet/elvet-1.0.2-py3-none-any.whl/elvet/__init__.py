import logging
import sys

# Useful tf accessors
from tensorflow import dtypes
from tensorflow import cast
from tensorflow import constant
from tensorflow import Variable

from elvet.bc import BC
from elvet.domains import box, cut_domain, ellipsoid
import elvet.math
from elvet.minimizer.minimizer import Minimizer, minimizer
from elvet.models import nn
from elvet.solver.fitter import fitter
from elvet.solver.solver import Solver, solver
from elvet.system import logger
from elvet.utils import callbacks, LRschedulers, loss_combinators, metrics, unstack

# Constants
pi = constant(3.141592653589793, name="Pi")
speed_of_light_m_s = constant(299792458.0, name="speed_of_light_m_s")
e = constant(2.718281828, name="natural_log_e")
hbar_eVs = constant(6.582119569e-16, name="hbar_eVs")
h_eVs = constant(4.135667696e-15, name="h_eVs")
hc_eVmum = constant(1.23984193, name="hc_eVmum")
hbarc_eVmum = constant(0.1973269804, name="hbarc_eVmum")

logger.init(LoggerStream=sys.stdout)
log = logging.getLogger("Elvet")
log.setLevel(logging.INFO)

__version__ = "1.0.1"

__all__ = [
    "BC",
    "box",
    "cut_domain",
    "ellipsoid",
    "Minimizer",
    "minimizer",
    "nn",
    "fitter",
    "Solver",
    "solver",
    "logger",
    "callbacks",
    "LRschedulers",
    "loss_combinators",
    "metrics",
    "unstack",
]

log.info("If you use Elvet in research, please cite arXiv:2103.14575")
# add citation when ready
cite_bibtex = "@article"
