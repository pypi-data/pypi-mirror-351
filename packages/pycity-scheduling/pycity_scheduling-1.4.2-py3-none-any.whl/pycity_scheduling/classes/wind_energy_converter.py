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


import numpy as np
import pyomo.environ as pyomo
import pycity_base.classes.supply.wind_energy_converter as wec

from pycity_scheduling.classes.electrical_entity import ElectricalEntity


class WindEnergyConverter(ElectricalEntity, wec.WindEnergyConverter):
    """
    Extension of pyCity_base class WindEnergyConverter for scheduling purposes.

    Parameters
    ----------
    environment : Environment
        Common Environment instance.
    velocity : numpy.ndarray
        Wind speeds in [m/s].
    power : numpy.ndarray
        Power for given velocities in [kW].
    hub_height : float, optional
        Height of the wind energy converter in [m].
    roughness : float, optional
        Roughness of landscape in [m].
    force_renewables : bool, optional
        `True` if generation may not be reduced for optimization purposes.


    Notes
    -----
    - The following constraint is added for removing the bounds from EE:

    .. math::
        p_{el} &=& -p_{el\\_supply}, & \\quad \\text{if force_renewables} \\\\
        0 \\geq p_{el} &\\geq& -p_{el\\_supply} , & \\quad \\text{else}
    """

    def __init__(self, environment, velocity, power,
                 hub_height=70, roughness=0.1, force_renewables=True):
        super(WindEnergyConverter, self).__init__(environment, velocity, power, hub_height, roughness)
        self._long_id = "WEC_" + self._id_string

        self.force_renewables = force_renewables
        self.p_el_supply = self._get_power_supply()

    def _get_power_supply(self):
        # Base class cannot compute values for the whole simulation horizon
        wheather_forecast = self.environment.weather.getWeatherForecast
        (full_wind,) = wheather_forecast(getVWind=True)
        ts = self.timer.time_in_year(from_init=True)
        total_wind = full_wind[ts:ts + self.simu_horizon]
        log_wind = self._logWindProfile(total_wind)
        return np.interp(log_wind, self.velocity, self.power, right=0)

    def populate_model(self, model, mode="convex"):
        super().populate_model(model, mode)
        m = self.model
        timestep = self.timestep

        def p_el_vars_lb_rule(model, t):
            return model.p_el_vars[t] >= -self.p_el_supply[timestep + t]

        m.p_el_vars_lb_constr = pyomo.Constraint(m.t, rule=p_el_vars_lb_rule)

        def p_el_vars_ub_rule(model, t):
            if self.force_renewables:
                return model.p_el_vars[t] <= -self.p_el_supply[timestep + t]
            else:
                return model.p_el_vars[t] <= 0.0

        m.p_el_vars_ub_constr = pyomo.Constraint(m.t, rule=p_el_vars_ub_rule)

        return

    def update_model(self, mode=""):
        m = self.model
        timestep = self.timestep

        p_el_vars_lb_constr_active = m.p_el_vars_lb_constr.active

        def p_el_vars_lb_rule(model, t):
            return model.p_el_vars[t] >= -self.p_el_supply[timestep + t]
        try:
            m.del_component(m.p_el_vars_lb_constr)
        except AttributeError:
            pass
        m.p_el_vars_lb_constr = pyomo.Constraint(m.t, rule=p_el_vars_lb_rule)

        if p_el_vars_lb_constr_active is False:
            m.p_el_vars_lb_constr.deactivate()

        p_el_vars_ub_constr_active = m.p_el_vars_ub_constr.active

        def p_el_vars_ub_rule(model, t):
            if self.force_renewables:
                return model.p_el_vars[t] <= -self.p_el_supply[timestep + t]
            else:
                return model.p_el_vars[t] <= 0.0
        try:
            m.del_component(m.p_el_vars_ub_constr)
        except AttributeError:
            pass
        m.p_el_vars_ub_constr = pyomo.Constraint(m.t, rule=p_el_vars_ub_rule)

        if p_el_vars_ub_constr_active is False:
            m.p_el_vars_ub_constr.deactivate()
        return

    def get_objective(self, coeff=1):
        """
        Objective function of the WindEnergyConverter.

        Return the objective function of the wind energy converter weighted
        with `coeff`. Depending on `self.force_renewables` leave objective
        function empty or build quadratic objective function to minimize
        discrepancy between available power and produced power.

        Parameters
        ----------
        coeff : float, optional
            Coefficient for the objective function.

        Returns
        -------
        ExpressionBase :
            Objective function.
        """
        m = self.model

        s = 0
        for t in self.op_time_vec:
            s += m.p_el_vars[t] * m.p_el_vars[t]
            s -= 2 * self.p_el_supply[self.op_slice][t] * m.p_el_vars[t]
        return coeff * s

    def get_decision_var(self):
        return self.model.p_el_vars
