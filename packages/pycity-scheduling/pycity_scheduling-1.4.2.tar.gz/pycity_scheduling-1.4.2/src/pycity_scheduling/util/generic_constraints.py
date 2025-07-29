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
import pyomo.core
import pyomo.environ as pyomo

from pycity_scheduling import constants


class Constraint:
    """
    Base class for all generic constraints.

    This class provides functionality common to all generic constraints.
    Generic constraints can be easily added to an entity block.
    """
    def apply(self, model, mode=""):
        """
        Apply constraint to block during populate_model method call.

        Parameters
        ----------
        model : pyomo.Block
            The block corresponding to the entity the constraint should
            be applied to.
        mode : str, optional
            Specifies which set of constraints to use.

            - `convex`  : Use linear constraints
            - `integer`  : May use integer variables
        """
        raise NotImplementedError()


class LowerActivationLimit(Constraint):
    """
    Constraint Class for adding lower activation limits

    This class provides functionality to add lower activation limits
    to entities. Adds no new constraints and variables if not in integer
    mode or if not required. A new state schedule is also created for
    the entity.

    Notes
    -----
    - In `integer` mode the following constraints are added:

    .. math::
        State  \\geq \\frac{var}{var\\_nom} \\geq State * lower\\_activation\\_limit

    """
    def __init__(self, o, var_name, lower_activation_limit, var_nom, min_off_time=1, min_on_time=1):
        """
        Initialize Constraint for a specific entity and create the new
        state schedule.


        Parameters
        ----------
        o : OptimizationEntity
            The entity to add the constraint to.
        var_name : str
            The variable name the constraint should be applied to.
        lower_activation_limit : float (0 <= lowerActivationLimit <= 1)
            Defines the lower activation limit. For example, heat pumps
            are typically able to operate between 50% part load and rated
            load. In this case, lowerActivationLimit would be 0.5
            Two special cases:

            - Linear behaviour: lowerActivationLimit = 0.0
            - Two-point controlled: lowerActivationLimit = 1.0
        var_nom : float
            The maximum or minimum value the variable takes when operating
            under maximum load.
        min_off_time : int, optional
            Minimum number of consecutive time steps the entity must remain turned off, once it has been decided that it
            should turn off. Defaults to '1', i.e., not limited to a consecutive number of time steps.
        min_on_time : int, optional
            Minimum number of consecutive time steps the entity must remain turned on, once it has been decided that it
            should turn on. Defaults to '1', i.e., not limited to a consecutive number of time steps.
        """
        self.var_name = var_name
        self.lower_activation_limit = lower_activation_limit
        self.var_nom = var_nom
        self.min_off_time = min_off_time
        self.min_on_time = min_on_time

        o.new_var(var_name+"_state", dtype=np.bool_, func=lambda model:
                  abs(o.schedule[self.var_name][o.op_slice]) > abs(0.01 * var_nom))

    def apply(self, m, mode=""):
        if mode == "integer" and self.lower_activation_limit != 0.0 and self.var_nom != 0.0:
            # Add additional binary variables representing operating state
            if hasattr(m, self.var_name + "_state"):
                raise ValueError("model already has a component named: {}".format(self.var_name + "_state"))

            var = pyomo.Var(m.t, domain=pyomo.Binary, initialize=0)
            m.add_component(self.var_name + "_state_vars", var)

            # Couple state to operating variable
            if self.lower_activation_limit == 1.0:
                def p_activation_rule(model, t):
                    orig_var = getattr(m, self.var_name + "_vars")
                    var = getattr(m, self.var_name + "_state_vars")
                    return orig_var[t] == var[t] * self.var_nom

                if hasattr(m, self.var_name + "_activation_constr"):
                    raise ValueError("model already has a component named: {}".
                                     format(self.var_name + "_activation_constr"))
                m.add_component(self.var_name + "_activation_constr", pyomo.Constraint(m.t,
                                                                                       rule=p_activation_rule))
            else:
                def p_state_rule(model, t):
                    orig_var = getattr(m, self.var_name + "_vars")
                    var = getattr(m, self.var_name + "_state_vars")
                    if self.var_nom > 0:
                        return orig_var[t] <= var[t] * self.var_nom
                    else:
                        return orig_var[t] >= var[t] * self.var_nom

                if hasattr(m, self.var_name + "_state_constr"):
                    raise ValueError("model already has a component named: {}".format(self.var_name + "_state_constr"))
                m.add_component(self.var_name + "_state_constr", pyomo.Constraint(m.t, rule=p_state_rule))

                def p_activation_rule(model, t):
                    orig_var = getattr(m, self.var_name + "_vars")
                    var = getattr(m, self.var_name + "_state_vars")
                    if self.var_nom > 0:
                        return orig_var[t] >= var[t] * self.var_nom * self.lower_activation_limit
                    else:
                        return orig_var[t] <= var[t] * self.var_nom * self.lower_activation_limit

                if hasattr(m, self.var_name + "_activation_constr"):
                    raise ValueError("model already has a component named: {}".
                                     format(self.var_name + "_activation_constr"))
                m.add_component(self.var_name + "_activation_constr", pyomo.Constraint(m.t,
                                                                                       rule=p_activation_rule))

            # minimum off-time constraint
            if self.min_off_time > 1:
                m.t_min_off = pyomo.RangeSet(0, m.t.last()-self.min_off_time)

                indicator_1_to_0 = pyomo.Var(m.t_min_off, domain=pyomo.Reals,
                                             bounds=(-constants.INFINITY, constants.INFINITY), initialize=0)
                m.add_component(self.var_name + "_indicator_1_to_0_vars", indicator_1_to_0)

                def indicator_1_to_0_lb_rule(model, t):
                    count_var_1_to_0 = getattr(m, self.var_name + "_indicator_1_to_0_vars")
                    return count_var_1_to_0[t] >= -constants.INFINITY

                if hasattr(m, self.var_name + "_indicator_1_to_0_lb_constr"):
                    raise ValueError("model already has a component named: {}".
                                     format(self.var_name + "_indicator_1_to_0_lb_constr"))
                m.add_component(self.var_name + "_indicator_1_to_0_lb_constr",
                                pyomo.Constraint(m.t_min_off, rule=indicator_1_to_0_lb_rule))

                def indicator_1_to_0_ub_rule(model, t):
                    count_var_1_to_0 = getattr(m, self.var_name + "_indicator_1_to_0_vars")
                    return count_var_1_to_0[t] <= constants.INFINITY

                if hasattr(m, self.var_name + "_indicator_1_to_0_ub_constr"):
                    raise ValueError("model already has a component named: {}".
                                     format(self.var_name + "_indicator_1_to_0_ub_constr"))
                m.add_component(self.var_name + "_indicator_1_to_0_ub_constr",
                                pyomo.Constraint(m.t_min_off, rule=indicator_1_to_0_ub_rule))

                def indicator_1_to_0_rule(model, t):
                    var = getattr(m, self.var_name + "_state_vars")
                    count_var_1_to_0 = getattr(m, self.var_name + "_indicator_1_to_0_vars")
                    if t == 0:
                        return count_var_1_to_0[t] == 0
                    else:
                        return count_var_1_to_0[t] == var[t-1] - var[t]

                if hasattr(m, self.var_name + "_indicator_1_to_0_constr"):
                    raise ValueError("model already has a component named: {}".
                                     format(self.var_name + "_indicator_1_to_0_constr"))
                m.add_component(self.var_name + "_indicator_1_to_0_constr",
                                pyomo.Constraint(m.t_min_off, rule=indicator_1_to_0_rule))

                def min_off_time_rule(model, t):
                    var = getattr(m, self.var_name + "_state_vars")
                    count_var_1_to_0 = getattr(m, self.var_name + "_indicator_1_to_0_vars")
                    return (sum(var[t+tau] for tau in range(self.min_off_time)) <= self.min_off_time *
                            (1.0-count_var_1_to_0[t]))

                if hasattr(m, self.var_name + "_min_off_time_constr"):
                    raise ValueError("model already has a component named: {}".
                                     format(self.var_name + "_min_off_time_constr"))
                m.add_component(self.var_name + "_min_off_time_constr", pyomo.Constraint(m.t_min_off,
                                                                                         rule=min_off_time_rule))

            # minimum on-time constraint
            if self.min_on_time > 1:
                m.t_min_on = pyomo.RangeSet(0, m.t.last() - self.min_on_time)

                indicator_0_to_1 = pyomo.Var(m.t_min_on, domain=pyomo.Reals,
                                             bounds=(-constants.INFINITY, constants.INFINITY), initialize=0)
                m.add_component(self.var_name + "_indicator_0_to_1_vars", indicator_0_to_1)

                def indicator_0_to_1_lb_rule(model, t):
                    count_var_0_to_1 = getattr(m, self.var_name + "_indicator_0_to_1_vars")
                    return count_var_0_to_1[t] >= -constants.INFINITY

                if hasattr(m, self.var_name + "_indicator_0_to_1_lb_constr"):
                    raise ValueError("model already has a component named: {}".
                                     format(self.var_name + "_indicator_0_to_1_lb_constr"))
                m.add_component(self.var_name + "_indicator_0_to_1_lb_constr",
                                pyomo.Constraint(m.t_min_on, rule=indicator_0_to_1_lb_rule))

                def indicator_0_to_1_ub_rule(model, t):
                    count_var_0_to_1 = getattr(m, self.var_name + "_indicator_0_to_1_vars")
                    return count_var_0_to_1[t] <= constants.INFINITY

                if hasattr(m, self.var_name + "_indicator_0_to_1_ub_constr"):
                    raise ValueError("model already has a component named: {}".
                                     format(self.var_name + "_indicator_0_to_1_ub_constr"))
                m.add_component(self.var_name + "_indicator_0_to_1_ub_constr",
                                pyomo.Constraint(m.t_min_on, rule=indicator_0_to_1_ub_rule))

                def indicator_0_to_1_rule(model, t):
                    var = getattr(m, self.var_name + "_state_vars")
                    count_var_0_to_1 = getattr(m, self.var_name + "_indicator_0_to_1_vars")
                    if t == 0:
                        return count_var_0_to_1[t] == 0
                    else:
                        return count_var_0_to_1[t] == var[t] - var[t-1]

                if hasattr(m, self.var_name + "_indicator_0_to_1_constr"):
                    raise ValueError("model already has a component named: {}".
                                     format(self.var_name + "_indicator_0_to_1_constr"))
                m.add_component(self.var_name + "_indicator_0_to_1_constr",
                                pyomo.Constraint(m.t_min_on, rule=indicator_0_to_1_rule))

                def min_on_time_rule(model, t):
                    var = getattr(m, self.var_name + "_state_vars")
                    count_var_0_to_1 = getattr(m, self.var_name + "_indicator_0_to_1_vars")
                    return (sum(var[t+tau] for tau in range(self.min_on_time)) >= self.min_on_time *
                            count_var_0_to_1[t])

                if hasattr(m, self.var_name + "_min_on_time_constr"):
                    raise ValueError("model already has a component named: {}".
                                     format(self.var_name + "_min_on_time_constr"))
                m.add_component(self.var_name + "_min_on_time_constr", pyomo.Constraint(m.t_min_off,
                                                                                        rule=min_on_time_rule))
