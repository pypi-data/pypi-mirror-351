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
import matplotlib.pyplot as plt
import networkx as nx

from pycity_scheduling.classes.electrical_entity import ElectricalEntity
from pycity_scheduling.classes.electrical_node import ElectricalNode
from pycity_scheduling.classes.electrical_line import ElectricalLine


class ElectricalGrid(ElectricalEntity):
    """
    Class ElectricalGrid for scheduling purposes. Connects buildings within pycity_scheduling via a shared electrical
    grid.

    Parameters
    ----------
    environment : pycity_scheduling.classes.Environment
        Common to all other objects. Includes time and weather instances.
    related_entity : CityDistrict
        City district object that 'maintains' the ElectricalGrid.
    max_p_slack : float
        Maximum active power that can be exchanged through slack node of the grid in kW.
    max_q_slack : float
        Maximum reactive power that can be exchanged through slack node of the grid in kVar.
    slack_V : float, optional
        If not `None`, voltage at which the slack node should be operated in V. Default is None.
    ref_V : float, optional
        Nominal voltage in the electrical grid in V. Default is 400V.
    V_min : float, optional
        Minimal per unit voltage allowed in the electrical grid. Default is 0.95.
    V_max : float, optional
        Maximal per unit voltage allowed in the electrical grid. Default is 1.05.
    """
    def __init__(self, environment, related_entity, max_p_slack, max_q_slack, slack_V=None, ref_V=400, min_V=0.95,
                 max_V=1.05, *args, **kwargs):
        super().__init__(environment, *args, **kwargs)
        self._kind = "electricalgrid"
        self._long_id = "EG_" + self._id_string
        self.environment = environment
        self.related_entity = related_entity

        self.lines = []
        self.nb_lines = 0

        self.slack_node = ElectricalNode(environment, None, None)
        self.slack_V = slack_V
        self.nodes = dict()
        self.nodes[self.slack_node] = 0
        self.nb_nodes = 1

        self.connected_entities = dict()
        self.connected_entities[self.slack_node] = self.slack_node

        self.min_V = min_V
        self.max_V = max_V
        self.max_p_slack = max_p_slack
        self.max_q_slack = max_q_slack

        # Per unit calculations:
        self.ref_V = ref_V  # V
        self.ref_S = max_p_slack  # kVA
        self.ref_Z = self.ref_V ** 2 / (self.ref_S * 1000.0)

        # Cable properties per unit length:
        self.R_cable = 0.25  # Ohm/km
        self.X_cable = 0.0  # Ohm/km

    def add_node(self, node):
        """
        Add a node to the electrical grid.

        Check whether the node is already in the grid. If not, the node is assigned a number in the node dictionary and
        the node number is incremented by 1.
        If the node has a related entity, this entity is added to the connected_entity dictionary.
        The nodes inherit the voltage bounds of the electrical grid to which it is added.

        Parameters
        ----------
        node : ElectricalNode
            The node that should be added to the network.
        """
        if node not in self.nodes:
            node.min_V = self.min_V
            node.max_V = self.max_V
            if node.related_entity is not None:
                self.connected_entities[node.related_entity] = node
            self.nodes[node] = self.nb_nodes
            self.nb_nodes += 1

    def add_line(self, line):
        """
        Add a line to the electrical grid.
        
        Check whether the sending and receiving nodes of the line are already in the electrical grid. If not they are
        added. The line is added to the lines list of the grid and the line number is incremented by 1.

        Parameters
        ----------
        line : ElectricalLine
            The line that should be added to the network.
        """
        s = line.sending_node
        r = line.receiving_node
        self.add_node(s)
        self.add_node(r)
        self.lines.append(line)
        self.nb_lines += 1

    def remove_line(self, line):
        """
        Remove a line from the electrical grid.
        
        Remove the line from the line list and decrement the line number by 1.

        Parameters
        ----------
        line : ElectricalLine
            The line that should be removed from the network.
        """
        self.lines.remove(line)
        self.nb_lines -= 1

    def update_cable_properties(self, R_cable, X_cable):
        """
        Update the resistance and reactance cable parameters of the electrical grid.
        
        Update the R_cable (ohm/km) and X_cable (ohm/km) attributes of the grid with the provided values.

        Parameters
        ----------
        R_cable : float
            Cable resistance in ohm/km.
        X_cable : float
            Cable reactance in ohm/km.
        """
        self.R_cable = R_cable
        self.X_cable = X_cable

    def connect_entities(self, entity1, entity2, line_capacity, line_length, R_line_per_km=None, X_line_per_km=None):
        """
        Add a line of specified length and capacity linking two entities in an electrical grid.
        
        Convert line capacity in per unit according to the electrical grid nominal power.
        Calculate per unit resistance and reactance of the line using the grid cable properties.
        Add a line to the electrical grid to connect two entities, that can be electrical nodes or buildings.

        Parameters
        ----------
        entity1 : Union[ElectricalNode, Building]
            First entity to connect, sending node of the line.
        entity2 : Union[ElectricalNode, Building]
            Second entity to connect, receiving node of the line.
        line_capacity : float
            Line capacity in kVA.
        line_length : float
            Line length in km.
        """
        # Per unit conversion:
        line_capacity = line_capacity / self.ref_S

        # Impedance calculation based on cable properties and conversion in per unit:
        if R_line_per_km is None:
            R_line_per_km = self.R_cable
        if X_line_per_km is None:
            X_line_per_km = self.X_cable
        R_line = R_line_per_km * line_length / self.ref_Z
        X_line = X_line_per_km * line_length / self.ref_Z

        # Find electrical nodes related to the entities to be connected:
        if isinstance(entity1, ElectricalNode):
            node1 = entity1
        else:
            node1 = self.connected_entities[entity1]
        if isinstance(entity2, ElectricalNode):
            node2 = entity2
        else:
            node2 = self.connected_entities[entity2]

        # Add line to the electrical grid:
        line = ElectricalLine(self.environment, node1, node2, R_line, X_line, line_capacity)
        self.add_line(line)

    def build_incidence_matrix(self):
        """
        Build the incidence matrix of the electrical grid.

        Returns
        -------
        A : np.ndarray
            Incidence matrix of the grid.
        """
        A = np.zeros((self.nb_lines, self.nb_nodes))
        for i, line in enumerate(self.lines):
            s = self.nodes[line.sending_node]
            r = self.nodes[line.receiving_node]
            A[i, s] = 1
            A[i, r] = -1
        return A

    def populate_model(self, model, mode="convex"):
        """
        Add electrical grid block to pyomo ConcreteModel.

        Call parent's `populate_model` method. Then call `populate_model` method of all contained electrical lines and
        electrical nodes. Add constraints on slack node operation; bounded exchange power and enforcement of specified
        slack voltage if any. Add coupling constraints between nodes and their related entities.
        Add power conservation constraint at each node.
        
        Parameters
        ----------
        model : pyomo.ConcreteModel
        mode : str, optional
            Specifies which set of constraints to use.

            - `convex`  : Use linear constraints
            - `integer`  : Use same constraints as convex mode
        """
        super().populate_model(model, mode)

        # Populate nodes:
        for node in self.nodes:
            node.populate_model(model)
        # Populate lines:
        for line in self.lines:
            line.populate_model(model)

        m = self.model
        node_index = pyomo.RangeSet(0, self.nb_nodes-1)
        nodes_list = list(self.nodes.keys())

        # Slack node operation constraints
        # Apply specified slack voltage if any provided:
        if self.slack_V is not None:
            def slack_V_rule(model, t):
                return self.slack_node.model.V_el_vars[t] == self.slack_V ** 2
            model.slack_V_constr = pyomo.Constraint(m.t, rule=slack_V_rule)

        # Bounded injection power at slack node for healthy operation:
        self.slack_node.model.p_el_vars.setlb(- self.max_p_slack)
        self.slack_node.model.p_el_vars.setub(self.max_p_slack)
        self.slack_node.model.q_el_vars.setlb(- self.max_q_slack)
        self.slack_node.model.q_el_vars.setub(self.max_q_slack)

        # Coupling constraint between buildings and nodes power:
        def p_linking_rule(model, t, n):
            node = nodes_list[n]
            if node.related_entity is not None:
                return node.model.p_el_vars[t] + node.related_entity.model.p_el_vars[t] / self.ref_S == 0
            elif self.nodes[node] == 0:
                return m.p_el_vars[t] == 0
            else:
                return node.model.p_el_vars[t] == 0
        model.p_linking_constr = pyomo.Constraint(m.t, range(0, self.nb_nodes), rule=p_linking_rule)

        def q_linking_rule(model, t, n):
            node = nodes_list[n]
            if self.nodes[node] != 0:
                return node.model.q_el_vars[t] == node.ratio_pq_power * node.model.p_el_vars[t]
            else:
                return m.p_el_vars[t] == 0
        model.q_linking_constr = pyomo.Constraint(m.t, range(0, self.nb_nodes), rule=q_linking_rule)

        # Power flow constraint
        # Build incidence matrix:
        A = self.build_incidence_matrix()

        # Modified matrix for handling of losses in power conservation:
        A_loss = A.copy()
        A_loss[A_loss == -1] = 0

        # Enforce power flow conservation at each node, power losses are taken into account:
        def p_flow_rule(model, t, n):
            return sum(A[i, n] * line.model.p_el_vars[t] + A_loss[i, n] * line.model.p_loss_el_vars[t]
                       for i, line in enumerate(self.lines)) == nodes_list[n].model.p_el_vars[t]
        m.p_flow_constr = pyomo.Constraint(m.t, node_index, rule=p_flow_rule)

        def q_flow_rule(model, t, n):
            return sum(A[i, n] * line.model.q_el_vars[t] + A_loss[i, n] * line.model.q_loss_el_vars[t]
                       for i, line in enumerate(self.lines)) == nodes_list[n].model.q_el_vars[t]
        m.q_flow_constr = pyomo.Constraint(m.t, node_index, rule=q_flow_rule)

    def plot_graph_results(self, t):
        """
        Plot the optimization results for the electrical grid in an oriented graph for one time step.
        
        Represented electrical nodes of the electrical grid as graph nodes and lines as edges.
        Display the optimal values of power flow, power injection or generation and node voltages in per unit.

        Parameters
        ----------
        t : int
            Time step for which results are plotted.
        """
        # Create the incidence matrix of the grid:
        A = self.build_incidence_matrix()
        # Create a directed graph from the incidence matrix using the networkx package:
        G = nx.DiGraph()
        edge_labels = {}

        # Collect optimal values of power flows through lines:
        p_l_opti = []
        q_l_opti = []
        for line in self.lines:
            p_l_opti.append(line.model.p_el_vars[t].value * self.ref_S)
            q_l_opti.append(line.model.q_el_vars[t].value * self.ref_S)

        # Collect optimal values of power injection or generation and node voltages:
        p_n_opti = []
        q_n_opti = []
        V_opti = []
        for node in self.nodes:
            p_n_opti.append(node.model.p_el_vars[t].value * self.ref_S) 
            q_n_opti.append(node.model.q_el_vars[t].value * self.ref_S)
            V_opti.append(node.model.V_el_vars[t].value**0.5)

        # Collect optimal slack power injection:
        p_slack_opti = self.slack_node.model.p_el_vars[t].value * self.ref_S
        q_slack_opti = self.slack_node.model.q_el_vars[t].value * self.ref_S

        # Build graph
        # Add nodes and edges based on the incidence matrix and write edge label including optimal power flows:
        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                if A[i, j] == 1:
                    s = j
                elif A[i, j] == -1:
                    r = j
            edge_label = format(p_l_opti[i], '.3f') + " + j " + format(q_l_opti[i], '.3f')
            edge_labels[f'Node_{s}', f'Node_{r}'] = edge_label
            G.add_edge(f'Node_{s}', f'Node_{r}')

        # Draw the graph:
        plt.figure(figsize=(15, 10))
        pos = nx.spring_layout(G)
        nx.nx.draw_networkx(G, pos, with_labels=True, node_size=1700, node_color='skyblue', font_size=10,
                            font_color='black')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

        # Add node labels with power injection or generation and node voltages:
        for i in range(self.nb_nodes):
            if i == self.nodes[self.slack_node]:
                colour = "blue"
                node_label = ("S_slack: " + format(p_slack_opti, '.3f') + " + j " + format(q_slack_opti, '.3f') +
                              "\n V_slack: " + format(V_opti[i], '.3f'))
            else:
                colour = "black"
                node_label = ("S: " + format(p_n_opti[i], '.3f') + " + j " + format(q_n_opti[i], '.3f') +
                              "\n V: " + format(V_opti[i], '.3f'))
            x, y = pos[f'Node_{i}']
            plt.text(x + 0.05, y, node_label, fontsize=10, color=colour)

        plt.show()
