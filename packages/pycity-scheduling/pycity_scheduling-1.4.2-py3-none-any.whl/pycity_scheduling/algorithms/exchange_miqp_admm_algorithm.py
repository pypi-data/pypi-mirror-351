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

from pycity_scheduling.classes import (CityDistrict, Building, Photovoltaic, WindEnergyConverter)
from pycity_scheduling.algorithms.algorithm import IterationAlgorithm, DistributedAlgorithm, SolverNode
from pycity_scheduling.solvers import DEFAULT_SOLVER, DEFAULT_SOLVER_OPTIONS


class ExchangeMIQPADMM(IterationAlgorithm, DistributedAlgorithm):
    """Implementation of the Exchange MIQP ADMM algorithm.

    Implements the Exchange MIQP ADMM algorithm described in [1], [2], and [3].

    Parameters
    ----------
    city_district : CityDistrict
    solver : str, optional
        Solver to use for solving (sub)problems.
    solver_options : dict, optional
        Options to pass to calls to the solver. Keys are the name of
        the functions being called and are one of `__call__`, `set_instance_`,
        `solve`.
        `__call__` is the function being called when generating an instance
        with the pyomo SolverFactory. In addition to the options provided,
        `node_ids` is passed to this call containing the IDs of the entities
        being optimized.
        `set_instance` is called when a pyomo Model is set as an instance of
        a persistent solver. `solve` is called to perform an optimization. If
        not set, `save_results` and `load_solutions` may be set to false to
        provide a speedup.
    mode : str, optional
        Specifies which set of constraints to use.
        - `convex`  : Use linear constraints
        - `integer`  : May use non-linear constraints
    eps_exch_primal : float, optional
        Primal stopping criterion for the ADMM algorithm.
    eps_exch_dual : float, optional
        Dual stopping criterion for the ADMM algorithm.
    gamma : float, optional
        Exchange MIQP ADMM scaling parameter
    gamma_incr : float, optional
        Varying scaling parameter scheme increase parameter
    rho : float, optional
        Stepsize for the ADMM algorithm.
    varying_penalty_parameter : bool, optional
        Apply a varying penalty parameter scheme, see [3] - chapter 3.4.1
    tau_incr : float, optional
        Varying penalty parameter scheme increase parameter
    tau_decr : float, optional
        Varying penalty parameter scheme decrease parameter
    mu : float, optional
        Varying penalty parameter scheme conditional change parameter
    max_iterations : int, optional
        Maximum number of ADMM iterations.
    robustness : tuple, optional
        Tuple of two floats. First entry defines how many time steps are
        protected from deviations. Second entry defines the magnitude of
        deviations which are considered.

    References
    ----------
    [1] "Alternating Direction Method of Multipliers for Decentralized
    Electric Vehicle Charging Control" by Jose Rivera, Philipp Wolfrum,
    Sandra Hirche, Christoph Goebel, and Hans-Arno Jacobsen
    Online: https://mediatum.ub.tum.de/doc/1187583/1187583.pdf (accessed on 2020/09/28)

    [2] "A simple effective heuristic for embedded mixed-integer quadratic programming" by Reza Takapoui,
    Nicholas Moehle, Stephen Boyd, and Alberto Bemporad
    Online: https://web.stanford.edu/~boyd/papers/pdf/miqp_admm.pdf (accessed on 2023/09/06)

    [3] "Distributed Optimization and Statistical Learning via the Alternating Direction Method of Multipliers" by
    Stephen Boyd, Neal Parikh, Eric Chu, Borja Peleato, and Jonathan Eckstein
    Online: https://web.stanford.edu/~boyd/papers/pdf/admm_distr_stats.pdf (accessed on 2023/10/09)
    """
    def __init__(self, city_district, solver=DEFAULT_SOLVER, solver_options=DEFAULT_SOLVER_OPTIONS, mode="convex",
                 x_update_mode="constrained", eps_exch_primal=0.01, eps_exch_dual=0.1, gamma=1.0, gamma_incr=1.0,
                 rho=2.0, varying_penalty_parameter=False, tau_incr=2.0, tau_decr=2.0, mu=10.0,
                 max_iterations=10000, robustness=None):
        super(ExchangeMIQPADMM, self).__init__(city_district, solver, solver_options, mode)

        self.x_update_mode = x_update_mode
        self.eps_exch_primal = eps_exch_primal
        self.eps_exch_dual = eps_exch_dual
        self.gamma = gamma
        self.gamma_incr = gamma_incr
        self.rho = rho
        self.varying_penalty_parameter = varying_penalty_parameter
        self.tau_incr = tau_incr
        self.tau_decr = tau_decr
        self.mu = mu
        self.max_iterations = max_iterations
        self.op_horizon = self.city_district.op_horizon
        self.number_constraints = 0
        self.number_binaries = 0

        # Only consider entities of type CityDistrict, Building, Photovoltaic, WindEnergyConverter
        self._entities = [entity for entity in self.entities if
                          isinstance(entity, (CityDistrict, Building, Photovoltaic, WindEnergyConverter))]

        # Create solver nodes for each entity
        self.nodes = [
            SolverNode(solver, solver_options, [entity], mode, robustness=robustness)
            for entity in self._entities
        ]

        # Create pyomo parameters for each entity
        for node, entity in zip(self.nodes, self._entities):
            node.model.gamma_ = pyomo.Param(mutable=True, initialize=self.gamma)
            node.model.rho_ = pyomo.Param(mutable=True, initialize=self.rho)
            node.model.beta = pyomo.Param(mutable=True, initialize=1)
            node.model.xs_ = pyomo.Param(entity.model.t, mutable=True, initialize=0)
            node.model.us = pyomo.Param(entity.model.t, mutable=True, initialize=0)
            node.model.last_p_el_schedules = pyomo.Param(entity.model.t, mutable=True, initialize=0)

        # Additions to the Exchange ADMM algorithm in order to obtain Exchange MIQP ADMM
        self.feasible = False
        self.district_binaries, self.district_bin_values, self.district_x_k_values, \
            self.district_u_k_values = self._get_binaries()
        self.district_equalities_t, self.district_equalities_n, \
            self.district_inequalities_t, self.district_inequalities_n = self._get_constraints()
        self._set_parameters()
        self._add_objective(exchange_admm_obj_terms=True, miqp_admm_obj_terms=True)

    # Function to get the binary variables from the model, to store them and to change their domain to reals
    def _get_binaries(self):
        district_binaries_list = []
        district_bin_values_list = []
        district_x_k_values_list = []
        district_u_k_values_list = []
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            node_binaries_list = []
            node_bin_values_list = []
            node_x_k_values_list = []
            node_u_k_values_list = []
            if i != 0:
                for en in entity.get_all_entities():
                    for variable in en.model.component_objects(pyomo.Var):
                        if variable[0].domain is pyomo.Binary:
                            bin_index_list = []
                            x_k_index_list = []
                            u_k_index_list = []
                            # change domain
                            variable.domain = pyomo.Reals
                            variable.setlb(0)
                            variable.setub(1)
                            node_binaries_list.append(variable)
                            for index in variable:
                                variable[index].fixed = False
                            for t in range(self.op_horizon):
                                x_value_array = np.zeros(self.max_iterations+1)
                                x_k_value_array = np.zeros(self.max_iterations+1)
                                u_k_value_array = np.zeros(self.max_iterations+1)
                                bin_index_list.append(x_value_array)
                                x_k_index_list.append(x_k_value_array)
                                u_k_index_list.append(u_k_value_array)
                            self.number_binaries += self.op_horizon
                            node_bin_values_list.append(bin_index_list)
                            node_x_k_values_list.append(x_k_index_list)
                            node_u_k_values_list.append(u_k_index_list)
            district_binaries_list.append(node_binaries_list)
            district_bin_values_list.append(node_bin_values_list)
            district_x_k_values_list.append(node_x_k_values_list)
            district_u_k_values_list.append(node_u_k_values_list)
        return np.array(district_binaries_list, dtype=object), np.array(district_bin_values_list, dtype=object),\
            np.array(district_x_k_values_list, dtype=object), np.array(district_u_k_values_list, dtype=object)

    def _get_constraints(self):
        # There are time indexed and none indexed constraints. They all need be stored in separate lists.
        district_equalities_list_t = []
        district_equalities_list_n = []
        district_inequalities_list_t = []
        district_inequalities_list_n = []
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            equalities_list_t = []
            inequalities_list_t = []
            equalities_list_n = []
            inequalities_list_n = []
            equality = False
            inequality = False
            none_index = False
            if i != 0:
                for en in entity.get_all_entities():
                    for constraint in en.model.component_objects(pyomo.Constraint):
                        if self.x_update_mode == "unconstrained":
                            constraint.deactivate()
                        for index in constraint:
                            self.number_constraints += 1
                            if index is None:
                                none_index = True
                            # check if the constraint is an equality constraint and write it in the form Ax-b=0
                            # for each index
                            if pyomo.value(constraint[index].lower) == pyomo.value(constraint[index].upper):
                                expr = constraint[index].body - constraint[index].lower
                                constraint[index].set_value(expr == 0)
                                equality = True

                            # if the constraint is not an equality constraint it has to be an inequality constraint;
                            # the next three checks are about to write that constraint in the form Cx-d >= 0
                            elif pyomo.value(constraint[index].upper) is None:
                                expr = constraint[index].body - constraint[index].lower
                                constraint[index].set_value(expr >= 0)
                                inequality = True

                            elif pyomo.value(constraint[index].lower) is None:
                                expr = -constraint[index].body + constraint[index].upper
                                constraint[index].set_value(expr >= 0)
                                inequality = True
                            else:
                                expr = -constraint[index].body + constraint[index].upper
                                expr = constraint[index].body - constraint[index].lower
                                print("WARNING: This constraint has a lb and ub and is hence not deactivated!")
                                inequality = True
                        if equality:
                            if none_index:
                                equalities_list_n.append(constraint)
                                none_index = False
                            else:
                                equalities_list_t.append(constraint)
                            equality = False
                        if inequality:
                            if none_index:
                                inequalities_list_n.append(constraint)
                                none_index = False
                            else:
                                inequalities_list_t.append(constraint)
                            inequality = False
            district_equalities_list_t.append(equalities_list_t)
            district_equalities_list_n.append(equalities_list_n)
            district_inequalities_list_t.append(inequalities_list_t)
            district_inequalities_list_n.append(inequalities_list_n)
        return np.array(district_equalities_list_t, dtype=object), np.array(district_equalities_list_n, dtype=object),\
            np.array(district_inequalities_list_t, dtype=object), np.array(district_inequalities_list_n, dtype=object)

    def _set_parameters(self):
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            # Create parameters for each binary variable
            length = len(self.district_binaries[i])
            if length != 0:
                node.model.bin_set = pyomo.RangeSet(0, length - 1)
                node.model.x_k = pyomo.Param(node.model.bin_set, entity.model.t, mutable=True, initialize=0)
                node.model.u_xk = pyomo.Param(node.model.bin_set, entity.model.t, mutable=True, initialize=0)
            if self.x_update_mode == "unconstrained":
                # Create parameters for each constraint
                length = len(self.district_equalities_t[i])
                if length != 0:
                    node.model.eq_t_set = pyomo.RangeSet(0, length - 1)
                    node.model.u_eq_t = pyomo.Param(node.model.eq_t_set, entity.model.t, mutable=True,
                                                    initialize=0)

                length = len(self.district_equalities_n[i])
                if length != 0:
                    node.model.eq_n_set = pyomo.RangeSet(0, length-1)
                    node.model.u_eq_n = pyomo.Param(node.model.eq_n_set, mutable=True, initialize=0)

                length = len(self.district_inequalities_t[i])
                if length != 0:
                    node.model.ineq_t_set = pyomo.RangeSet(0, length - 1)
                    node.model.u_ineq_t = pyomo.Param(node.model.ineq_t_set, entity.model.t, mutable=True,
                                                      initialize=0)
                    node.model.v_k_t = pyomo.Param(node.model.ineq_t_set, entity.model.t, mutable=True,
                                                   initialize=0)

                length = len(self.district_inequalities_n[i])
                if length != 0:
                    node.model.ineq_n_set = pyomo.RangeSet(0, length - 1)
                    node.model.u_ineq_n = pyomo.Param(node.model.ineq_n_set, mutable=True, initialize=0)
                    node.model.v_k_n = pyomo.Param(node.model.ineq_n_set, mutable=True, initialize=0)
        return

    # Returns True, if no constraint or binary variable violations occur
    def _check_violations(self, print_out=True, detailed_print_out=False):
        constr_counter = 0
        var_counter = 0
        fig_number = 0
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            length = len(self.district_binaries[i])
            if length != 0:
                for x, val, x_k, u_k in zip(self.district_binaries[i], self.district_bin_values[i],
                                            self.district_x_k_values[i], self.district_u_k_values[i]):
                    for t in range(self.op_horizon):
                        if abs(x[t].value) < 0.1 or (0.9 < x[t].value < 1.1):
                            pass
                        else:
                            var_counter += 1
                            if detailed_print_out:
                                x[t].pprint()
                                plot_name = x.name + str(t)
                                plt.figure(fig_number)
                                plt.plot(val[t], label='x')
                                plt.plot(x_k[t], label='x_k')
                                plt.plot(u_k[t], label='u_k')
                                plt.legend()
                                plt.title(plot_name)
                                plt.grid()
                                fig_number += 1

            length = len(self.district_equalities_t[i])
            if length != 0:
                for eq_constr in self.district_equalities_t[i]:
                    for t in range(len(eq_constr)):
                        if abs(pyomo.value(eq_constr[t].body)) > 0.05:
                            if detailed_print_out:
                                print(eq_constr[t].body, " ", pyomo.value(eq_constr[t].body))
                            constr_counter += 1

            length = len(self.district_equalities_n[i])
            if length != 0:
                for eq_constr in self.district_equalities_n[i]:
                    if abs(pyomo.value(eq_constr.body)) > 0.05:
                        if detailed_print_out:
                            print(eq_constr.body, " ", pyomo.value(eq_constr.body))
                        constr_counter += 1

            length = len(self.district_inequalities_t[i])
            if length != 0:
                for ineq_constr in self.district_inequalities_t[i]:
                    for t in range(len(ineq_constr)):
                        if pyomo.value(ineq_constr[t].body) < -0.05:
                            if detailed_print_out:
                                print(ineq_constr[t].body, " ", pyomo.value(ineq_constr[t].body))
                            constr_counter += 1

            length = len(self.district_inequalities_n[i])
            if length != 0:
                for ineq_constr in self.district_inequalities_n[i]:
                    if pyomo.value(ineq_constr.body) < -0.05:
                        if detailed_print_out:
                            print(ineq_constr.body, " ", pyomo.value(ineq_constr.body))
                        constr_counter += 1
        if print_out:
            print("Violated constraints:", constr_counter,  "of in total", self.number_constraints)
            print("Violated binaries:", var_counter, "of in total", self.number_binaries)
        if detailed_print_out:
            plt.show()
        if var_counter == 0 and constr_counter == 0:
            return True
        else:
            return False

    # Returns the objective value
    def _get_objective(self):
        obj_value = 0
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            obj_value += pyomo.value(entity.get_objective())
        return obj_value

    def _add_objective(self, exchange_admm_obj_terms=True, miqp_admm_obj_terms=True):
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            obj = node.model.beta * entity.get_objective()
            for t in range(entity.op_horizon):
                obj += node.model.rho_ / 2 * entity.model.p_el_vars[t] * entity.model.p_el_vars[t]

            # In the following, add the additional expressions to solve the sub-problems by Exchange ADMM.
            if exchange_admm_obj_terms:
                # penalty term is expanded and constant is omitted
                if i == 0:
                    # invert sign of p_el_schedule and p_el_vars (omitted for quadratic term)
                    penalty = [(-node.model.last_p_el_schedules[t] - node.model.xs_[t] - node.model.us[t])
                               for t in range(entity.op_horizon)]
                    for t in range(entity.op_horizon):
                        obj += node.model.rho_ * penalty[t] * entity.model.p_el_vars[t]
                else:
                    penalty = [(-node.model.last_p_el_schedules[t] + node.model.xs_[t] + node.model.us[t])
                               for t in range(entity.op_horizon)]
                    for t in range(entity.op_horizon):
                        obj += node.model.rho_ * penalty[t] * entity.model.p_el_vars[t]

            # In the following, add the additional expressions to solve the sub-problems by MIQP ADMM.
            if miqp_admm_obj_terms:
                # binary variables contribution
                length = len(self.district_binaries[i])
                if length != 0:
                    for x, k in zip(self.district_binaries[i], range(length)):
                        obj += node.model.rho_ / 2 * sum((x[t] - node.model.x_k[k, t] + node.model.gamma_ *
                                                          node.model.u_xk[k, t]) ** 2 for t in range(self.op_horizon))

                if self.x_update_mode == "unconstrained":
                    # add the contributions of the constraints (time and none indexed)
                    length = len(self.district_equalities_t[i])
                    if length != 0:
                        for eq_constr, k in zip(self.district_equalities_t[i], range(length)):
                            obj += node.model.rho_ / 2 * sum((eq_constr[t].body + node.model.u_eq_t[k, t]) ** 2
                                                             for t in range(len(eq_constr)))

                    length = len(self.district_equalities_n[i])
                    if length != 0:
                        for eq_constr, k in zip(self.district_equalities_n[i], range(length)):
                            obj += node.model.rho_ / 2 * (eq_constr.body + node.model.u_eq_n[k]) ** 2

                    length = len(self.district_inequalities_t[i])
                    if length != 0:
                        for ineq_constr, k in zip(self.district_inequalities_t[i], range(length)):
                            obj += node.model.rho_ / 2 * sum((ineq_constr[t].body + node.model.u_ineq_t[k, t] -
                                                              node.model.v_k_t[k, t]) ** 2
                                                             for t in range(len(ineq_constr)))

                    length = len(self.district_inequalities_n[i])
                    if length != 0:
                        for ineq_constr, k in zip(self.district_inequalities_n[i], range(length)):
                            obj += node.model.rho_ / 2 * (ineq_constr.body + node.model.u_ineq_n[k] -
                                                          node.model.v_k_n[k]) ** 2

            # if we want to redefine the objective for a certain node, then we should first reset the old objective
            try:
                node.model.del_component(node.model.o)
            except AttributeError:
                pass
            node.model.o = pyomo.Objective(expr=obj)
        return

    def _presolve(self, full_update, beta, robustness, debug):
        results, params = super()._presolve(full_update, beta, robustness, debug)

        for node, entity in zip(self.nodes, self._entities):
            node.model.beta = self._get_beta(params, entity)
            if full_update:
                node.full_update(robustness)
        results["r_norms"] = []
        results["s_norms"] = []
        results["gamma_value"] = []
        results["rho_value"] = []
        return results, params

    def _is_last_iteration(self, results, params, debug):
        if super(ExchangeMIQPADMM, self)._is_last_iteration(results, params, debug):
            self._check_violations()
            return True
        if results["r_norms"][-1] <= self.eps_exch_primal and results["s_norms"][-1] <= self.eps_exch_dual:
            if self.feasible:
                self._check_violations()
                return True
            else:
                return False

    def _iteration(self, results, params, debug):
        super(ExchangeMIQPADMM, self)._iteration(results, params, debug)
        op_horizon = self._entities[0].op_horizon

        # fill parameters if not already present
        if "p_el" not in params:
            params["p_el"] = np.zeros((len(self._entities), op_horizon))
        if "x_" not in params:
            params["x_"] = np.zeros(op_horizon)
        if "u" not in params:
            params["u"] = np.zeros(op_horizon)
        last_u = params["u"]
        last_p_el = params["p_el"]
        last_x_ = params["x_"]

        # --------------------------
        # 1) optimize all entities
        # --------------------------

        to_solve_nodes = []
        variables = []
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            for t in range(op_horizon):
                node.model.last_p_el_schedules[t] = last_p_el[i][t]
                node.model.xs_[t] = last_x_[t]
                node.model.us[t] = last_u[t]
            node.obj_update()
            to_solve_nodes.append(node)
            variables.append([entity.model.p_el_vars[t] for t in range(op_horizon)])
        self._solve_nodes(results, params, to_solve_nodes, variables=variables, debug=debug)

        # ----------------------------------------------
        # 2) incentive signal update (Exchange ADMM)
        # ----------------------------------------------

        p_el_schedules = np.stack([entity.p_el_schedule for entity in self._entities], axis=0)
        x_ = (-p_el_schedules[0] + sum(p_el_schedules[1:])) / len(self._entities)

        results["r_norms"].append(np.sqrt(len(self._entities)) * np.linalg.norm(x_))

        s = np.zeros_like(p_el_schedules)
        s[0] = - self.rho * (-p_el_schedules[0] + last_p_el[0] + last_x_ - x_)
        for i in range(1, len(self._entities)):
            s[i] = - self.rho * (p_el_schedules[i] - last_p_el[i] + last_x_ - x_)
        results["s_norms"].append(np.linalg.norm(s.flatten()))

        results["obj_value"].append(self._get_objective())

        # To check the latest solution for feasibility, fix all binary vars at either 0 or 1 and try to recalculate the
        # schedule based on an additional optimization. Of course, there are other and possibly more
        # straightforward ways to check for feasibility. This will be future work.
        if ((results["r_norms"][-1] <= self.eps_exch_primal) and (results["s_norms"][-1] <= self.eps_exch_dual)) or \
                (results["iterations"][-1] >= self.max_iterations):
            if results["iterations"][-1] >= self.max_iterations:
                print("Iteration " + str(results["iterations"][-1]) + ": " +
                      "Maximum iteration limit reached. Checking the current solution for feasibility.")
            else:
                print("Iteration " + str(results["iterations"][-1]) + ": " +
                      "Stopping criteria satisfied. Checking the current solution for feasibility.")
            self._add_objective(exchange_admm_obj_terms=True, miqp_admm_obj_terms=False)
            self.fix_variables()
            if self.x_update_mode == "unconstrained":
                self.activate_constraints()
            self.feasible = True
            for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
                to_solve_nodes = []
                variables = []
                node.obj_update()
                node.constr_update()
                to_solve_nodes.append(node)
                variables.append([entity.model.p_el_vars[t] for t in range(op_horizon)])
                try:
                    self._solve_nodes({}, {}, to_solve_nodes, variables=variables, debug=False)
                except:
                    self.feasible = False
            if self.feasible:
                print("Success. The solution is feasible!")
                self.release_variables()
                if self.x_update_mode == "unconstrained":
                    self.deactivate_constraints()
            else:
                print("Failure. The solution is infeasible, because at least one subsystem is (still) infeasible!")
                if results["iterations"][-1] >= self.max_iterations:
                    print("Attention: The final solution could be infeasible!")
                else:
                    self._add_objective(exchange_admm_obj_terms=True, miqp_admm_obj_terms=True)
                    self.release_variables()
                    if self.x_update_mode == "unconstrained":
                        self.deactivate_constraints()
                    to_solve_nodes = []
                    variables = []
                    for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
                        node.obj_update()
                        node.constr_update()
                        to_solve_nodes.append(node)
                        variables.append([entity.model.p_el_vars[t] for t in range(op_horizon)])
                    self._solve_nodes({}, {}, to_solve_nodes, variables=variables, debug=False)
                    # vary the gamma parameter (maximum value is 10e9 to avoid numerical issues):
                    self.gamma = min(float(self.gamma_incr)*self.gamma, 10e9)
                    for node, entity in zip(self.nodes, self._entities):
                        node.model.gamma_ = self.gamma
        results["gamma_value"].append(self.rho)

        # ----------------------------------------
        # 3) incentive signal update (MIQP ADMM)
        # ----------------------------------------

        # update all MIQP ADMM parameters (first the constraints then the variables)
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            if self.x_update_mode == "unconstrained":
                length = len(self.district_inequalities_t[i])
                if length != 0:
                    for ineq_constr, k in zip(self.district_inequalities_t[i], range(length)):
                        for t in range(len(ineq_constr)):
                            v_update = pyomo.value(ineq_constr[t].body) + node.model.u_ineq_t[k, t].value
                            if v_update > 0:
                                node.model.v_k_t[k, t] = v_update
                            else:
                                node.model.v_k_t[k, t] = 0

                length = len(self.district_inequalities_n[i])
                if length != 0:
                    for ineq_constr, k in zip(self.district_inequalities_n[i], range(length)):
                        v_update = pyomo.value(ineq_constr.body) + node.model.u_ineq_n[k].value
                        if v_update > 0:
                            node.model.v_k_n[k] = v_update
                        else:
                            node.model.v_k_n[k] = 0

                length = len(self.district_inequalities_t[i])
                if length != 0:
                    for ineq_constr, k in zip(self.district_inequalities_t[i], range(length)):
                        for t in range(len(ineq_constr)):
                            node.model.u_ineq_t[k, t] = node.model.u_ineq_t[k, t].value + \
                                                        pyomo.value(ineq_constr[t].body) - \
                                                        node.model.v_k_t[k, t].value

                length = len(self.district_inequalities_n[i])
                if length != 0:
                    for ineq_constr, k in zip(self.district_inequalities_n[i], range(length)):
                        node.model.u_ineq_n[k] = node.model.u_ineq_n[k].value + pyomo.value(ineq_constr.body) - \
                                                    node.model.v_k_n[k].value

                length = len(self.district_equalities_t[i])
                if length != 0:
                    for eq_constr, k in zip(self.district_equalities_t[i], range(length)):
                        for t in range(len(eq_constr)):
                            node.model.u_eq_t[k, t] = node.model.u_eq_t[k, t].value + pyomo.value(eq_constr[t].body)

                length = len(self.district_equalities_n[i])
                if length != 0:
                    for eq_constr, k in zip(self.district_equalities_n[i], range(length)):
                        node.model.u_eq_n[k] = node.model.u_eq_n[k].value + pyomo.value(eq_constr.body)

            # x_k update
            length = len(self.district_binaries[i])
            if length != 0:
                for x, k in zip(self.district_binaries[i], range(length)):
                    for t in range(op_horizon):
                        # Integer rounding:
                        node.model.x_k[k, t] = round(x[t].value + node.model.u_xk[k, t].value)
                        # Binary rounding:
                        # x_update = abs(x[t].value + node.model.u_xk[k, t].value)
                        # if x_update >= 0.5:
                        #    node.model.x_k[k, t] = 1
                        # else:
                        #    node.model.x_k[k, t] = 0
                        self.district_x_k_values[i][k][t][results["iterations"][-1]-1] = node.model.x_k[k, t].value

            # u_xk update
            length = len(self.district_binaries[i])
            if length != 0:
                for x, x_val, u_k, k in zip(self.district_binaries[i], self.district_bin_values[i],
                                            self.district_u_k_values[i], range(length)):
                    for t in range(op_horizon):
                        node.model.u_xk[k, t] = node.model.u_xk[k, t].value + x[t].value - \
                                                node.model.x_k[k, t].value
                        x_val[t][results["iterations"][-1]-1] = x[t].value
                        u_k[t][results["iterations"][-1]-1] = node.model.u_xk[k, t].value

        # if desired, vary the penalty parameter
        if self.varying_penalty_parameter:
            if results["r_norms"][-1] > self.mu * results["s_norms"][-1]:
                self.rho *= float(self.tau_incr)
                for node, entity in zip(self.nodes, self._entities):
                    node.model.rho_ = self.rho
            elif results["s_norms"][-1] > self.mu * results["r_norms"][-1]:
                self.rho /= float(self.tau_decr)
                for node, entity in zip(self.nodes, self._entities):
                    node.model.rho_ = self.rho
        results["rho_value"].append(self.rho)

        # save parameters for another iteration
        params["p_el"] = p_el_schedules
        params["x_"] = x_
        params["u"] += x_
        return

    def fix_variables(self):
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            length = len(self.district_binaries[i])
            if length != 0:
                for x, k in zip(self.district_binaries[i], range(length)):
                    for t in range(self.op_horizon):
                        x_k = node.model.x_k[k, t].value
                        x[t].fix(x_k)
        return

    def release_variables(self):
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            length = len(self.district_binaries[i])
            if length != 0:
                for x, k in zip(self.district_binaries[i], range(length)):
                    for t in range(self.op_horizon):
                        x[t].unfix()
        return

    def activate_constraints(self):
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            if i != 0:
                for en in entity.get_all_entities():
                    for constraint in en.model.component_objects(pyomo.Constraint):
                        constraint.activate()
        return

    def deactivate_constraints(self):
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            if i != 0:
                for en in entity.get_all_entities():
                    for constraint in en.model.component_objects(pyomo.Constraint):
                        constraint.deactivate()
        return

    def print_model(self):
        for i, node, entity in zip(range(len(self._entities)), self.nodes, self._entities):
            for en in entity.get_all_entities():
                for constraint in en.model.component_objects(pyomo.Constraint):
                    constraint.pprint()
                for x in self.district_binaries[i]:
                    x.pprint()
