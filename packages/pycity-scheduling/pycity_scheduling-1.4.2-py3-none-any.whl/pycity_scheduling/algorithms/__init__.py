"""
The pycity_scheduling framework


Copyright (C) 2025,
Institute for Automation of Complex Power Systems (ACS),
E.ON Energy Research Center (E.ON ERC),
RWTH Aachen University

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


from .stand_alone_optimization_algorithm import StandAlone
from .local_optimization_algorithm import LocalOptimization
from .exchange_admm_algorithm import ExchangeADMM
from .exchange_admm_algorithm_mpi import ExchangeADMMMPI
from .exchange_admm_algorithm_ray import ExchangeADMMRay
from .central_optimization_algorithm import CentralOptimization
from .dual_decomposition_algorithm import DualDecomposition
from .dual_decomposition_algorithm_mpi import DualDecompositionMPI
from .dual_decomposition_algorithm_ray import DualDecompositionRay
from .exchange_miqp_admm_algorithm import ExchangeMIQPADMM
from .exchange_miqp_admm_algorithm_mpi import ExchangeMIQPADMMMPI
from .exchange_miqp_admm_algorithm_ray import ExchangeMIQPADMMRay
from .derivative_free_aladin_algorithm import DerivativeFreeALADIN
from .derivative_free_aladin_algorithm_ray import DerivativeFreeALADINRay
from .derivative_free_aladin_algorithm_ray_Hvet import DerivativeFreeALADINRay_Hvet


__all__ = [
    'StandAlone',
    'LocalOptimization',
    'ExchangeADMM',
    'ExchangeADMMMPI',
    'ExchangeADMMRay',
    'CentralOptimization',
    'DualDecomposition',
    'DualDecompositionMPI',
    'DualDecompositionRay',
    'ExchangeMIQPADMM',
    'ExchangeMIQPADMMMPI',
    'ExchangeMIQPADMMRay',
    'DerivativeFreeALADIN',
    'DerivativeFreeALADINRay',
    'DerivativeFreeALADINRay_Hvet',
    'algorithm',
    'algorithm_ray',
    'algorithms',
]


algorithms = {
    'stand-alone': StandAlone,
    'local': LocalOptimization,
    'exchange-admm': ExchangeADMM,
    'exchange-admm-mpi': ExchangeADMMMPI,
    'exchange-admm-ray': ExchangeADMMRay,
    'central': CentralOptimization,
    'dual-decomposition': DualDecomposition,
    'dual-decomposition-mpi': DualDecompositionMPI,
    'dual-decomposition-ray': DualDecompositionRay,
    'exchange-miqp-admm': ExchangeMIQPADMM,
    'exchange-miqp-admm-mpi': ExchangeMIQPADMMMPI,
    'exchange-miqp-admm-ray': ExchangeMIQPADMMRay,
    'derivative-free-aladin': DerivativeFreeALADIN,
    'derivative-free-aladin-ray': DerivativeFreeALADINRay,
    'derivative-free-aladin-ray-Hvet': DerivativeFreeALADINRay_Hvet
}
