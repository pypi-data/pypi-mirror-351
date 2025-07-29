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


class ElectricalNode(ElectricalEntity):
    """
    Class ElectricalNode for scheduling purposes. Represents a building as a grid node inside an electrical grid within
    pycity_scheduling.

    Parameters
    ----------
    environment : pycity_scheduling.classes.Environment
        Common to all other objects. Includes time and weather instances.
    related_entity : Building, optional
        The entity coupled to the grid node.
    position : list, optional
         List of two floats specifying the position of the node inside the grid.
    min_V : float, optional
        Minimum voltage allowed for healthy operation in p.u.
    max_V : float, optional
        Maximum voltage allowed for healthy operation in p.u.
    ratio_pq_power : float, optional
        The fixed ratio of reactive power demand with respect to the active power demand, for the building connected
        to this node.
    """
    def __init__(self, environment, related_entity=None, position=None, min_V=0.95, max_V=1.05,
                 ratio_pq_power=1.0/3.0, *args, **kwargs):
        super().__init__(environment, *args, **kwargs)
        self._kind = "electricalnode"
        self._long_id = "EN_" + self._id_string
        self.related_entity = related_entity
        self.position = position
        self.min_V = min_V
        self.max_V = max_V
        self.ratio_pq_power = ratio_pq_power

        # Node power injection:
        self.new_var("p_node_el_vars")
        self.new_var("q_node_el_vars")

        # Square of node voltage:
        self.new_var("V_el_vars")

    def populate_model(self, model, mode='convex'):
        """
        Add electrical node block to pyomo ConcreteModel.

        Call parent's `populate_model` method and set variables lower bound to `None`.
        Set bound constraints on node voltage.
        
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

        # Introduce power injection of the node as an additional variable for readability
        m.p_node_el_vars = pyomo.Var(m.t, domain=pyomo.Reals, bounds=(None, None), initialize=1)

        def p_node_el_vars_rule(model, t):
            return m.p_node_el_vars[t] == m.p_el_vars[t]
        m.p_node_el_vars_constr = pyomo.Constraint(m.t, rule=p_node_el_vars_rule)

        # Power injection is negative when the node is consuming power and positive when the node is injecting power:
        m.p_el_vars.setlb(None)
        m.q_el_vars = pyomo.Var(m.t, domain=pyomo.Reals)

        # Bounded voltage for healthy operation:
        m.V_el_vars = pyomo.Var(m.t, domain=pyomo.Reals, bounds=(self.min_V**2, self.max_V**2), initialize=1)
