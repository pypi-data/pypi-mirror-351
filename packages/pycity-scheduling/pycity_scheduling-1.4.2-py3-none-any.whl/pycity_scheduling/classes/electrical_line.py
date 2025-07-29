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
from pycity_scheduling.classes.electrical_entity import ElectricalEntity
from pycity_scheduling.util import approximation as approx


class ElectricalLine(ElectricalEntity):
    """
    Class ElectricalLine for scheduling purposes. Represents a connecting line/cable for the interconnection of
    buildings in pycity_scheduling.

    Parameters
    ----------
    environment : pycity_scheduling.classes.Environment
        Common to all other objects. Includes time and weather instances.
    sending_node : Union[ElectricalNode, Building]
        First entity to connect, sending node of the line.
    receiving_node : Union[ElectricalNode, Building]
        Second entity to connect, receiving node of the line.
    resistance : float, optional
        Line resistance in Ohm.
    reactance : float, optional
        Line reactance in Ohm.
    max_capacity : float, optional
        Maximum line capacity (power) in kVA.
    """
    def __init__(self, environment, sending_node, receiving_node, resistance, reactance, max_capacity, *args, **kwargs):
        super().__init__(environment, *args, **kwargs)
        self._kind = "electricalline"
        self._long_id = "EL_" + self._id_string
        self.sending_node = sending_node
        self.receiving_node = receiving_node
        self.resistance = resistance
        self.reactance = reactance
        self.max_capacity = max_capacity

        # Power flow through line:
        self.new_var("p_line_el_vars")
        self.new_var("q_line_el_vars")

        # Approximated square of power flow:
        self.new_var("p_app_el_vars")
        self.new_var("q_app_el_vars")

        # Power losses through line:
        self.new_var("p_loss_el_vars")
        self.new_var("q_loss_el_vars")

        # Binary variables:
        self.new_var("x_p")
        self.new_var("x_q")

    def populate_model(self, model, mode='convex'):
        """
        Add electrical line block to pyomo ConcreteModel.

        Call parent's `populate_model` method.
        Set bounds on power flow according to line capacity.
        Perform max affine approximation for the square function. Coefficients of the approximation are used to set
        lower bounds on power square `p_app_el_vars`.
        Set disjunctive upper bounds constraints on `p_app_el_vars` using the big-M method.
        Set equality constraints to calculate power losses based on square power approximation.
        Add voltage drop constraint.
        
        Parameters
        ----------
        model : pyomo.ConcreteModel
        mode : str, optional
            Specifies which set of constraints to use.

            - `convex`  : Use linear constraints
            - `integer`  : Use same constraints as convex mode
        """
        super().populate_model(model, mode)
        m = self.model

        m.q_el_vars = pyomo.Var(m.t, domain=pyomo.Reals, initialize=0)

        # Introduce power flow through the line as an additional variable for readability
        m.p_line_el_vars = pyomo.Var(m.t, domain=pyomo.Reals, initialize=1)

        def p_line_el_vars_rule(model, t):
            return m.p_line_el_vars[t] == m.p_el_vars[t]
        m.p_line_el_vars_constr = pyomo.Constraint(m.t, rule=p_line_el_vars_rule)

        # Power flow can be positive or negative considering the arbitrary orientation of the line:
        m.p_el_vars.setlb(None)

        # Perform max-affine approximation of power square:
        square_function = lambda x: x**2
        inf_bound = [-np.max(self.max_capacity)]
        sup_bound = [np.max(self.max_capacity)]
        nb_samples = 1000
        nb_segments = 15

        # Calculate coefficients of affine functions:
        slopes, intercepts = approx.piecewise_linear_approx(square_function, inf_bound, sup_bound, nb_samples,
                                                            nb_segments)
        slopes = np.array(slopes, dtype=np.float32)
        intercepts = np.array(intercepts, dtype=np.float32)

        # Set constraints for max-affine approximation of power square:
        M = 1000  # for big-M method
        max_affine_index = pyomo.RangeSet(0, nb_segments-1)
        m.p_app_el_vars = pyomo.Var(m.t, domain=pyomo.Reals, bounds=(0, None), initialize=0)   # power square
        m.q_app_el_vars = pyomo.Var(m.t, domain=pyomo.Reals, bounds=(0, None), initialize=0)

        # x_p[i][t]=1 if p[t] is in the ith approximation segment, 0 otherwise:
        m.x_p = pyomo.Var(max_affine_index, m.t, domain=pyomo.Binary)
        m.x_q = pyomo.Var(max_affine_index, m.t, domain=pyomo.Binary)

        def p_lower_bounds_approx_rule(model, t, i):
            return m.p_app_el_vars[t] >= slopes[i] * m.p_el_vars[t] + intercepts[i]
        m.p_lower_bounds_approx_constr = pyomo.Constraint(m.t, max_affine_index,
                                                          rule=p_lower_bounds_approx_rule)

        def q_lower_bounds_approx_rule(model, t, i):
            return m.q_app_el_vars[t] >= slopes[i] * m.q_el_vars[t] + intercepts[i]
        m.q_lower_bounds_approx_constr = pyomo.Constraint(m.t, max_affine_index,
                                                          rule=q_lower_bounds_approx_rule)

        # Big-M method to set disjunctive upper bound constraints and handle saturation of lower bounds constraints:
        def p_upper_bounds_approx_rule(model, t, i):
            return m.p_app_el_vars[t] - (slopes[i] * m.p_el_vars[t] + intercepts[i]) <= M * (1-m.x_p[i, t])
        m.p_upper_bounds_approx_constr = pyomo.Constraint(m.t, max_affine_index,
                                                          rule=p_upper_bounds_approx_rule)
        
        def q_upper_bounds_approx_rule(model, t, i):
            return m.q_app_el_vars[t] - (slopes[i] * m.q_el_vars[t] + intercepts[i]) <= M * (1-m.x_q[i, t])
        m.q_upper_bounds_approx_constr = pyomo.Constraint(m.t, max_affine_index,
                                                          rule=q_upper_bounds_approx_rule)

        # At least one lower bound approx constraint is saturated (the corresponding upper bound constraint is active):
        def p_saturation_rule(model, t):
            return sum(m.x_p[i, t] for i in range(nb_segments)) >= 1
        m.p_saturation_constr = pyomo.Constraint(m.t, rule=p_saturation_rule)

        def q_saturation_rule(model, t):
            return sum(m.x_q[i, t] for i in range(nb_segments)) >= 1
        m.q_saturation_constr = pyomo.Constraint(m.t, rule=q_saturation_rule)

        # Power loss is positive and calculated from the max-affine approximation:
        m.p_loss_el_vars = pyomo.Var(m.t, domain=pyomo.Reals, bounds=(0, None), initialize=0)
        m.q_loss_el_vars = pyomo.Var(m.t, domain=pyomo.Reals, bounds=(0, None), initialize=0)

        def p_loss_rule(model, t):
            return m.p_loss_el_vars[t] == (m.p_app_el_vars[t] + m.q_app_el_vars[t]) * self.resistance
        m.p_loss_constr = pyomo.Constraint(m.t, rule=p_loss_rule)

        def q_loss_rule(model, t):
            return m.q_loss_el_vars[t] == (m.p_app_el_vars[t] + m.q_app_el_vars[t]) * self.reactance
        m.q_loss_constr = pyomo.Constraint(m.t, rule=q_loss_rule)

        # Bounded power flow for healthy operation
        def bounded_power_flow_rule(model, t):
            return m.p_app_el_vars[t] + m.q_app_el_vars[t] <= self.max_capacity**2
        m.bounded_power_flow_constr = pyomo.Constraint(m.t, rule=bounded_power_flow_rule)

        # Voltage drop across the line, calculated from power flow and power loss through the line:
        def voltage_drop_rule(model, t):
            return (self.sending_node.model.V_el_vars[t] - self.receiving_node.model.V_el_vars[t] ==
                    2 * self.resistance*m.p_el_vars[t] + 2 * self.reactance*m.q_el_vars[t] -
                    self.resistance*m.p_loss_el_vars[t] - self.reactance*m.q_loss_el_vars[t])
        m.voltage_drop_constr = pyomo.Constraint(m.t, rule=voltage_drop_rule)
