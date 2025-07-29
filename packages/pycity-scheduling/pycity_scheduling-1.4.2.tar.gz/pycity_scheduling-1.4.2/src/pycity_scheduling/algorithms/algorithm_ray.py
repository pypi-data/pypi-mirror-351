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
import ray
import copy
import time

import pyomo.environ as pyomo

from pyomo.solvers.plugins.solvers.persistent_solver import PersistentSolver
from pyomo.opt import SolverStatus, TerminationCondition

from pycity_scheduling.classes import CityDistrict, Building
from pycity_scheduling.util import extract_pyomo_values
from pycity_scheduling.exceptions import NonoptimalError


def list_into_n_chunks(lst, n):
    for i in range(0, n):
        yield lst[i::n]


def get_beta(params, entity):
    """Returns the beta value for a specific entity"""
    beta = params["beta"]
    if isinstance(beta, dict):
        return beta.get(entity.id, 1.0)
    if isinstance(entity, CityDistrict):
        return 1.0
    return beta


class RaySolverNode():
    """Base class for a Ray Node which can be used to solve all entities provided to it with in a ray cluster.

    Provides an abstraction layer for algorithms, so entities can be
    assigned to nodes and optimized easily.

    Parameters
    ----------
    solver : str
        Solver to use for solving (sub)problems.
    solver_options : dict, optional
        Options to pass to calls to the solver. Keys are the name of
        the functions being called and are one of `__call__`, `set_instance_`,
        `solve`.
        - `__call__` is the function being called when generating an instance
          with the pyomo SolverFactory. In addition to the options provided,
          `node_ids` is passed to this call containing the IDs of the entities
          being optimized.
        - `set_instance` is called when a pyomo Model is set as an instance of
          a persistent solver.
        - `solve` is called to perform an optimization. If not set,
          `save_results` and `load_solutions` may be set to false to provide a
          speedup.
    entities : list
        List of entities which should be optimized by this node.
    mode : str, optional
        Specifies which set of constraints to use.

        - `convex`  : Use linear constraints
        - `integer`  : May use non-linear constraints
    robustness : tuple, optional
        Tuple of two floats. First entry defines how many time steps are
        protected from deviations. Second entry defines the magnitude of
        deviations which are considered.
    """
    def __init__(self, solver, solver_options, entities, node_index = 0, op_horizon=0, mode="convex", robustness=None):
        self.solvers = np.empty(len(entities), dtype=object)
        for i, entity in enumerate(entities):
            self.solvers[i] = pyomo.SolverFactory(solver,  **solver_options.get("__call__", {}))
        self.solver_options = solver_options
        self.is_persistent = False
        if len(self.solvers) > 0:
            self.is_persistent = isinstance(self.solvers[0], PersistentSolver)
        self.robustness = robustness
        self.entities = []
        for entity in entities:
            self.entities.append(copy.deepcopy(entity))
        self.mode = mode
        self.model = np.empty(len(entities), dtype=object)
        self.node_index = node_index
        self.op_horizon = op_horizon

        self._reset()
        self._prepare()

    def _reset(self):
        """Reset, i.e., 'unpopulate', the previous optimization model"""
        for entity in self.entities:
            if isinstance(entity, CityDistrict):
                city_district = entity
                city_district.model = None
                for bd in city_district.get_lower_entities():
                    bd.model = None
                    if isinstance(bd, Building) and bd.has_bes:
                        bd.bes.model = None
                        for e in bd.bes.get_lower_entities():
                            e.model = None
                    if isinstance(bd, Building) and len(bd.apartments) == 1:
                        bd.apartments[0].model = None
                        for e in bd.apartments[0].get_lower_entities():
                            e.model = None
                    elif isinstance(bd, Building) and len(bd.apartments) > 1:
                        for ap in bd.apartments:
                            ap.model = None
                            for e in ap.get_lower_entities():
                                e.model = None
        return

    def _prepare(self):
        """Create the pyomo model for the entities and populate it"""
        for i, entity in enumerate(self.entities):
            model = pyomo.ConcreteModel()
            self._prepare_model(entity, model, robustness=self.robustness)
            self.model[i] = model
        return

    def _prepare_model(self, entity, model, robustness=None):
        """Add a single entity to a model"""
        if isinstance(entity, Building):
            entity.populate_model(model, self.mode, robustness=robustness)
            entity.update_model(self.mode, robustness=robustness)
        else:
            entity.populate_model(model, self.mode)
            entity.update_model(self.mode)
        return

    def set_model_betas(self, params):
        """Sets the model betas for every entity on the remote node"""
        for i, entity in enumerate(self.entities): 
            beta = get_beta(params, entity)
            self.model[i].beta = beta

    def full_update(self, robustness=None):
        """Execute the update_model function and propagate other model changes.

        Parameters
        ----------
        robustness : tuple, optional
            Tuple of two floats. First entry defines how many time steps are
            protected from deviations. Second entry defines the magnitude of
            deviations which are considered.
        """
        for i, entity in enumerate(self.entities):
            if isinstance(entity, Building):
                entity.update_model(mode=self.mode, robustness=robustness)
            else:
                entity.update_model(mode=self.mode)
            if self.is_persistent:
                self.solvers[i].set_instance(self.model[i], **self.solver_options.get("set_instance", {}))
        return

    def constr_update(self):
        """Only propagate the constraints update of the model"""
        for i, entity in enumerate(self.entities):
            if self.is_persistent:
                self.solvers[i].set_instance(self.model[i], **self.solver_options.get("set_instance", {}))
            else:
                pass
        return

    def obj_update(self, index):
        """Only propagate the objective value update of the model"""
        if self.is_persistent:
            self.solvers[index].set_objective(self.model[index].o)
        else:
            pass
        return

    def postsolve(self):
        """In this step other post-processing can be done"""
        # Updates the schedules of each asset and entity on the node
        for entity in self.entities:
            entity.update_schedule()
        return

    def get_all_schedules(self):
        """Retrives all schedules of each entity and asset on the node"""
        local_schedules = dict()
        for entity in self.entities:
            # only update the child entities when the entity is not a city district
            if isinstance(entity, CityDistrict):
                if hasattr(entity, "id") and hasattr(entity, "schedules"):
                    local_schedules.update({entity.id: entity.schedules})
            else:  
                for asset in entity.get_all_entities(): 
                    if hasattr(asset, "id") and hasattr(asset, "schedules"):
                        local_schedules.update({asset.id: asset.schedules})
        return local_schedules    

    def get_objective(self):
        obj_value = 0
        for i, entity in enumerate(self.entities):
            obj_value += pyomo.value(entity.get_objective())
        return obj_value

    def exit(self):
        ray.actor.exit_actor()
        return


@ray.remote(scheduling_strategy="SPREAD", num_cpus=1, num_gpus=0)
class RayDualDecompositionSolverNode(RaySolverNode):
    """Ray Node which can be used to solve all entities provided to it with in a ray cluster using the Dual
    Decompositon method.

    Provides an abstraction layer for algorithms, so entities can be
    assigned to nodes and optimized easily.

    Parameters
    ----------
    solver : str
        Solver to use for solving (sub)problems.
    solver_options : dict, optional
        Options to pass to calls to the solver. Keys are the name of
        the functions being called and are one of `__call__`, `set_instance_`,
        `solve`.
        - `__call__` is the function being called when generating an instance
          with the pyomo SolverFactory. In addition to the options provided,
          `node_ids` is passed to this call containing the IDs of the entities
          being optimized.
        - `set_instance` is called when a pyomo Model is set as an instance of
          a persistent solver.
        - `solve` is called to perform an optimization. If not set,
          `save_results` and `load_solutions` may be set to false to provide a
          speedup.
    entities : list
        List of entities which should be optimized by this node.
    mode : str, optional
        Specifies which set of constraints to use.

        - `convex`  : Use linear constraints
        - `integer`  : May use non-linear constraints
    robustness : tuple, optional
        Tuple of two floats. First entry defines how many time steps are
        protected from deviations. Second entry defines the magnitude of
        deviations which are considered.
    """
    def __init__(self, solver, solver_options, entities, node_index = 0, op_horizon=0, mode="convex", robustness=None):
        super().__init__(solver, solver_options, entities, node_index, op_horizon, mode, robustness)
        self.calc_model_params()

    def calc_model_params(self):
        """ Create the model parameters locally on the actor """
        for i, entity in enumerate(self.entities): 
            beta = pyomo.Param(mutable=True, initialize=1)
            lambdas = pyomo.Param(entity.model.t, mutable=True, initialize=0)
            self.model[i].beta = beta
            self.model[i].lambdas = lambdas

    def _set_model_lambdas(self, lambdas, index):
        """Sets the model lambdas for every entity on the remote node"""
        for t in range(self.op_horizon):
            self.model[index].lambdas[t] = lambdas[t]

    def add_objective(self, global_entity_indices):
        """Adds the objective to all models of every entity on the remote node"""
        for i, entity in enumerate(self.entities):
            global_index = global_entity_indices[entity.id]
            obj = self.model[i].beta * entity.get_objective()
            if global_index == 0:
                # penalty term is expanded and constant is omitted
                # invert sign of p_el_schedule and p_el_vars (omitted for quadratic term)
                for t in range(self.op_horizon):
                    obj -= self.model[i].lambdas[t] * entity.model.p_el_vars[t]
            else:
                for t in range(self.op_horizon):
                   obj += self.model[i].lambdas[t] * entity.model.p_el_vars[t]
            self.model[i].o = pyomo.Objective(expr=obj)
        return

    def _solve_single(self, lambdas, index, debug=True):
        """Call the solver to solve this nodes optimization problem for a single entity"""
        self._set_model_lambdas(lambdas, index)
        self.obj_update(index)
        model = self.model[index]
        entity = self.entities[index]
        solver = self.solvers[index]

        solve_options = self.solver_options.get("solve", {})
        if self.is_persistent:
            result = solver.solve(**solve_options)
        else:
            result = solver.solve(model, **solve_options)
        if (not (result.solver.termination_condition == TerminationCondition.optimal or
                result.solver.termination_condition == TerminationCondition.maxTimeLimit or
                result.solver.termination_condition == TerminationCondition.maxIterations) or
                not (result.solver.status == SolverStatus.ok or
                     result.solver.status == SolverStatus.warning or
                     result.solver.status == SolverStatus.aborted)):
            if debug:
                import pycity_scheduling.util.debug as debug
                debug.analyze_model(model, solver, result)
            raise NonoptimalError("Could not retrieve schedule from model.")

        entity.update_schedule()

        return self.entities[index].model.p_el_vars 

    def solve(self, lambdas_ref, debug=True):
        """Call the solver to solve this nodes optimization problem for every entity on the node"""
        p_el_var_list = []
        indices_list = []
        lambdas = ray.get(lambdas_ref[0])
        for i, entity in enumerate(self.entities): 
            p_el_vars = self._solve_single(lambdas, i, debug)
            p_el_var_list.append(p_el_vars)
            indices_list.append(entity.id)

        # return p_el_vars with other method or cast pyomo vars on the side of the node
        numpy_vars = np.array([extract_pyomo_values(var, float) for var in p_el_var_list])
        numpy_indices = np.array(indices_list)

        obj_value = self.get_objective()

        return [numpy_indices, numpy_vars, obj_value]

    def postsolve(self):
        """ Updates the schedules of each asset and entity on the node"""
        super().postsolve()


@ray.remote(scheduling_strategy="SPREAD", num_cpus=1, num_gpus=0)
class RayADMMSolverNode(RaySolverNode):
    """Ray Node which can be used to solve all entities provided to it with in a ray cluster using the Exchange
    ADMM method.

    Provides an abstraction layer for algorithms, so entities can be
    assigned to nodes and optimized easily.

    Parameters
    ----------
    solver : str
        Solver to use for solving (sub)problems.
    solver_options : dict, optional
        Options to pass to calls to the solver. Keys are the name of
        the functions being called and are one of `__call__`, `set_instance_`,
        `solve`.
        - `__call__` is the function being called when generating an instance
          with the pyomo SolverFactory. In addition to the options provided,
          `node_ids` is passed to this call containing the IDs of the entities
          being optimized.
        - `set_instance` is called when a pyomo Model is set as an instance of
          a persistent solver.
        - `solve` is called to perform an optimization. If not set,
          `save_results` and `load_solutions` may be set to false to provide a
          speedup.
    entities : list
        List of entities which should be optimized by this node.
    mode : str, optional
        Specifies which set of constraints to use.

        - `convex`  : Use linear constraints
        - `integer`  : May use non-linear constraints
    robustness : tuple, optional
        Tuple of two floats. First entry defines how many time steps are
        protected from deviations. Second entry defines the magnitude of
        deviations which are considered.
    """
    def __init__(self, solver, solver_options, entities, rho, node_index = 0, op_horizon=0, mode="convex",
                 robustness=None):
        self.rho = rho
        super().__init__(solver, solver_options, entities, node_index, op_horizon, mode, robustness)
        self.calc_model_params()
      
    def calc_model_params(self):
        """ Create the model parameters localy on the actor """
        for i, entity in enumerate(self.entities): 
            beta = pyomo.Param(mutable=True, initialize=1)
            xs_ = pyomo.Param(entity.model.t, mutable=True, initialize=0)
            us = pyomo.Param(entity.model.t, mutable=True, initialize=0)
            last_p_el_schedules = pyomo.Param(entity.model.t, mutable=True, initialize=0)
            rho_ = pyomo.Param(mutable=True, initialize=self.rho)
            self.model[i].rho_ = rho_
            self.model[i].beta = beta
            self.model[i].xs_ = xs_
            self.model[i].us = us
            self.model[i].last_p_el_schedules = last_p_el_schedules

    def _set_model_variables(self, last_p_els, last_x_, last_u, local_index, global_index):
        """Sets the model vars for entity on the remote node"""
        for t in range(self.op_horizon):
            self.model[local_index].last_p_el_schedules[t] = last_p_els[global_index][t]
            self.model[local_index].xs_[t] = last_x_[t]
            self.model[local_index].us[t] = last_u[t]

    def add_objective(self, global_entity_indices):
        """Adds the objective to all models of every entity on the remote node"""
        for i, entity in enumerate(self.entities):
            global_index = global_entity_indices[entity.id]
            obj = self.model[i].beta * entity.get_objective()
            for t in range(self.op_horizon):
                obj += self.model[i].rho_ / 2 * entity.model.p_el_vars[t] * entity.model.p_el_vars[t]
            # penalty term is expanded and constant is omitted
            if global_index == 0:
                # invert sign of p_el_schedule and p_el_vars (omitted for quadratic term)
                penalty = [(-self.model[i].last_p_el_schedules[t] - self.model[i].xs_[t] - self.model[i].us[t])
                           for t in range(self.op_horizon)]
                for t in range(self.op_horizon):
                    obj += self.model[i].rho_ * penalty[t] * entity.model.p_el_vars[t]
            else:
                penalty = [(-self.model[i].last_p_el_schedules[t] + self.model[i].xs_[t] + self.model[i].us[t])
                           for t in range(self.op_horizon)]
                for t in range(self.op_horizon):
                    obj += self.model[i].rho_ * penalty[t] * entity.model.p_el_vars[t]
            self.model[i].o = pyomo.Objective(expr=obj)
        return

    def _solve_single(self, last_p_els, last_x_, last_u, local_index, global_index, debug=True):
        """Call the solver to solve this nodes optimization problem for a single entity"""
        self._set_model_variables(last_p_els, last_x_, last_u, local_index, global_index)
        self.obj_update(local_index)

        model = self.model[local_index]
        entity = self.entities[local_index]
        solver = self.solvers[local_index]

        solve_options = self.solver_options.get("solve", {})
        if self.is_persistent:
            result = solver.solve(**solve_options)
        else:
            result = solver.solve(model, **solve_options)
        if (not (result.solver.termination_condition == TerminationCondition.optimal or
                result.solver.termination_condition == TerminationCondition.maxTimeLimit or
                result.solver.termination_condition == TerminationCondition.maxIterations) or
                not (result.solver.status == SolverStatus.ok or
                     result.solver.status == SolverStatus.warning or
                     result.solver.status == SolverStatus.aborted)):
            if debug:
                import pycity_scheduling.util.debug as debug
                debug.analyze_model(model, solver, result)
            raise NonoptimalError("Could not retrieve schedule from model.")

        entity.update_schedule()

        return self.entities[local_index].model.p_el_vars 

    def solve(self, variable_refs, debug=True):
        """Call the solver to solve this nodes optimization problem for every entity on the node

        Parameters
        ----------
        variables : list of lists of variables, optional
            Can contain a list for each node in nodes to indicate to pyomo which
            variables should be loaded back into the model. Specifying this can
            lead to a significant speedup.
        debug : bool, optional
            Specify whether detailed debug information shall be printed. Defaults
            to true.
        """
        p_el_var_list = []
        indices_list = []

        last_p_els = ray.get(variable_refs[0])
        last_x_ = ray.get(variable_refs[1])
        last_u_ = ray.get(variable_refs[2])
        global_entity_indices = ray.get(variable_refs[3])

        for i, entity in enumerate(self.entities): 
            global_index = global_entity_indices[entity.id]
            p_el_vars = self._solve_single(last_p_els, last_x_, last_u_, i, global_index, debug)
            p_el_var_list.append(p_el_vars)
            indices_list.append(entity.id)

        # return p_el_vars with other method or cast pyomo vars on the side of the node
        numpy_vars = np.array([extract_pyomo_values(var, float) for var in p_el_var_list])
        numpy_indices = np.array(indices_list)

        obj_value = self.get_objective()

        return [numpy_indices, numpy_vars, obj_value]

    def postsolve(self):
        """ Updates the schedules of each asset and entity on the node """
        super().postsolve()

    def update_rho(self, new_rho):
        """Updates the rho parameter for all entities on the remote node"""
        self.rho = new_rho
        for i, entity in enumerate(self.entities):
            self.model[i].rho_ = new_rho
        return


@ray.remote(scheduling_strategy="SPREAD", num_cpus=1, num_gpus=0)
class RayADMMMIQPSolverNode(RaySolverNode):
    """Ray Node which can be used to solve all entities provided to it with in a ray cluster using the Exchange
    MIQP ADMM method.

    Provides an abstraction layer for algorithms, so entities can be
    assigned to nodes and optimized easily.

    Parameters
    ----------
    solver : str
        Solver to use for solving (sub)problems.
    solver_options : dict, optional
        Options to pass to calls to the solver. Keys are the name of
        the functions being called and are one of `__call__`, `set_instance_`,
        `solve`.
        - `__call__` is the function being called when generating an instance
          with the pyomo SolverFactory. In addition to the options provided,
          `node_ids` is passed to this call containing the IDs of the entities
          being optimized.
        - `set_instance` is called when a pyomo Model is set as an instance of
          a persistent solver.
        - `solve` is called to perform an optimization. If not set,
          `save_results` and `load_solutions` may be set to false to provide a
          speedup.
    entities : list
        List of entities which should be optimized by this node.
    mode : str, optional
        Specifies which set of constraints to use.

        - `convex`  : Use linear constraints
        - `integer`  : May use non-linear constraints
    robustness : tuple, optional
        Tuple of two floats. First entry defines how many time steps are
        protected from deviations. Second entry defines the magnitude of
        deviations which are considered.
    """
    def __init__(self, solver, solver_options, entities, gamma, rho, node_index=0, max_iterations=1000, op_horizon=0,
                 mode="convex", x_update_mode="constrained", robustness=None):
        self.x_update_mode = x_update_mode
        self.gamma = gamma
        self.rho = rho
        self.max_iterations = max_iterations
        super().__init__(solver, solver_options, entities, node_index, op_horizon, mode, robustness)
        self.calc_model_params()

        self.feasible = False
        self.node_binaries, self.node_bin_values, self.node_x_k_values, \
             self.node_u_k_values = self._get_binaries()

        self.node_equalities_t, self.node_equalities_n, \
             self.node_inequalities_t, self.node_inequalities_n = self._get_constraints()

    def calc_model_params(self):
        """ Create the model parameters locally on the actor """
        for i, entity in enumerate(self.entities): 
            beta = pyomo.Param(mutable=True, initialize=1)
            xs_ = pyomo.Param(entity.model.t, mutable=True, initialize=0)
            us = pyomo.Param(entity.model.t, mutable=True, initialize=0)
            last_p_el_schedules = pyomo.Param(entity.model.t, mutable=True, initialize=0)
            gamma_ = pyomo.Param(mutable=True, initialize=self.gamma)
            rho_ = pyomo.Param(mutable=True, initialize=self.rho)
            self.model[i].gamma_ = gamma_
            self.model[i].rho_ = rho_
            self.model[i].beta = beta
            self.model[i].xs_ = xs_
            self.model[i].us = us
            self.model[i].last_p_el_schedules = last_p_el_schedules        

    def _get_binaries(self):
        local_binaries = []
        local_bin_values = []
        local_x_k_values = []
        local_u_k_values = []
        for i, entity in enumerate(self.entities):
            node_binaries_list = []
            node_bin_values_list = []
            node_x_k_values_list = []
            node_u_k_values_list = []
            if not isinstance(entity, CityDistrict):
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
                            node_bin_values_list.append(bin_index_list)
                            node_x_k_values_list.append(x_k_index_list)
                            node_u_k_values_list.append(u_k_index_list)
            local_binaries.append(node_binaries_list)
            local_bin_values.append(node_bin_values_list)
            local_x_k_values.append(node_x_k_values_list)
            local_u_k_values.append(node_u_k_values_list)

        if len(local_binaries) <= 1:
            local_binaries.append([])

        if len(local_bin_values) <= 1:
            local_bin_values.append([])

        if len(local_x_k_values) <= 1:
            local_x_k_values.append([])

        if len(local_u_k_values) <= 1:
            local_u_k_values.append([])

        return np.array(local_binaries, dtype=object), np.array(local_bin_values, dtype=object), \
            np.array(local_x_k_values, dtype=object), np.array(local_u_k_values, dtype=object),

    def _get_constraints(self):
        local_equalities_t = []
        local_equalities_n = []
        local_inequalities_t = []
        local_inequalities_n = []

        for i, entity in enumerate(self.entities):
            equalities_list_t = []
            inequalities_list_t = []
            equalities_list_n = []
            inequalities_list_n = []
            equality = False
            inequality = False
            none_index = False
            if not isinstance(entity, CityDistrict):
                for en in entity.get_all_entities():
                    for constraint in en.model.component_objects(pyomo.Constraint):
                        if self.x_update_mode == "unconstrained":
                            constraint.deactivate()
                        for index in constraint:
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
            local_equalities_t.append(equalities_list_t)
            local_equalities_n.append(equalities_list_n)
            local_inequalities_t.append(inequalities_list_t)
            local_inequalities_n.append(inequalities_list_n)

        if len(local_equalities_t) <= 1:
            local_equalities_t.append([])
            
        if len(local_equalities_n) <= 1:
            local_equalities_n.append([])

        if len(local_inequalities_t) <= 1:
            local_inequalities_t.append([])

        if len(local_inequalities_n) <= 1:
            local_inequalities_n.append([])

        return np.array(local_equalities_t, dtype=object), np.array(local_equalities_n, dtype=object),\
            np.array(local_inequalities_t, dtype=object), np.array(local_inequalities_n, dtype=object)

    def set_model_parameters(self):
        """Sets the model parameters for an entity on the remote node"""
        for i, entity in enumerate(self.entities):
            # Create parameters for each binary variable
            length = len(self.node_binaries[i])
            if length != 0:
                self.model[i].bin_set = pyomo.RangeSet(0, length - 1)
                self.model[i].x_k = pyomo.Param(self.model[i].bin_set, entity.model.t, mutable=True,
                                                initialize=0)
                self.model[i].u_xk = pyomo.Param(self.model[i].bin_set, entity.model.t, mutable=True,
                                                 initialize=0)
            if self.x_update_mode == "unconstrained":
                # Create parameters for each constraint
                length = len(self.node_equalities_t[i])
                if length != 0:
                    self.model[i].eq_t_set = pyomo.RangeSet(0, length - 1)
                    self.model[i].u_eq_t = pyomo.Param(self.model[i].eq_t_set, entity.model.t, mutable=True,
                                                       initialize=0)

                length = len(self.node_equalities_n[i])
                if length != 0:
                    self.model[i].eq_n_set = pyomo.RangeSet(0, length-1)
                    self.model[i].u_eq_n = pyomo.Param(self.model[i].eq_n_set, mutable=True, initialize=0)

                length = len(self.node_inequalities_t[i])
                if length != 0:
                    self.model[i].ineq_t_set = pyomo.RangeSet(0, length - 1)
                    self.model[i].u_ineq_t = pyomo.Param(self.model[i].ineq_t_set, entity.model.t,
                                                         mutable=True, initialize=0)
                    self.model[i].v_k_t = pyomo.Param(self.model[i].ineq_t_set, entity.model.t, mutable=True,
                                                      initialize=0)

                length = len(self.node_inequalities_n[i])
                if length != 0:
                    self.model[i].ineq_n_set = pyomo.RangeSet(0, length - 1)
                    self.model[i].u_ineq_n = pyomo.Param(self.model[i].ineq_n_set, mutable=True, initialize=0)
                    self.model[i].v_k_n = pyomo.Param(self.model[i].ineq_n_set, mutable=True, initialize=0)
        return

    def _set_model_variables(self, last_p_els, last_x_, last_u, local_index, global_index):
        """Sets the model vars for an entity on the remote node"""
        for t in range(self.op_horizon):
            self.model[local_index].last_p_el_schedules[t] = last_p_els[global_index][t]
            self.model[local_index].xs_[t] = last_x_[t]
            self.model[local_index].us[t] = last_u[t]

    def add_objective(self, exchange_admm_obj_terms=True, miqp_admm_obj_terms=True):
        """Adds the objective function for an entity on the remote node"""
        for i, entity in enumerate(self.entities):
            obj = self.model[i].beta * entity.get_objective()
            for t in range(entity.op_horizon):
                obj += self.model[i].rho_ / 2 * entity.model.p_el_vars[t] * entity.model.p_el_vars[t]

            # In the following, add the additional expressions to solve the sub-problems by Exchange ADMM.
            if exchange_admm_obj_terms:
                # penalty term is expanded and constant is omitted
                if isinstance(entity, CityDistrict):# i == 0:
                    # invert sign of p_el_schedule and p_el_vars (omitted for quadratic term)
                    penalty = [(-self.model[i].last_p_el_schedules[t] - self.model[i].xs_[t] - self.model[i].us[t])
                                for t in range(entity.op_horizon)]
                    for t in range(entity.op_horizon):
                        obj += self.model[i].rho_ * penalty[t] * entity.model.p_el_vars[t]
                else:
                    penalty = [(-self.model[i].last_p_el_schedules[t] + self.model[i].xs_[t] + self.model[i].us[t])
                                for t in range(entity.op_horizon)]
                    for t in range(entity.op_horizon):
                        obj += self.model[i].rho_ * penalty[t] * entity.model.p_el_vars[t]
            # In the following, add the additional expressions to solve the sub-problems by MIQP ADMM.
            if miqp_admm_obj_terms:
                # binary variables contribution
                length = len(self.node_binaries[i])
                if length != 0:
                    for x, k in zip(self.node_binaries[i], range(length)):
                        obj += self.model[i].rho_ / 2 * sum((x[t] - self.model[i].x_k[k, t] + self.model[i].gamma_ *
                                                             self.model[i].u_xk[k, t])**2
                                                            for t in range(self.op_horizon))

                if self.x_update_mode == "unconstrained":
                    # add the contributions of the constraints (time and none indexed)
                    length = len(self.node_equalities_t[i])
                    if length != 0:
                        for eq_constr, k in zip(self.node_equalities_t[i], range(length)):
                            obj += self.model[i].rho_ / 2 * sum((eq_constr[t].body + self.model[i].u_eq_t[k, t]) ** 2
                                                                for t in range(len(eq_constr)))

                    length = len(self.node_equalities_n[i])
                    if length != 0:
                        for eq_constr, k in zip(self.node_equalities_n[i], range(length)):
                            obj += self.model[i].rho_ / 2 * (eq_constr.body + self.model[i].u_eq_n[k]) ** 2

                    length = len(self.node_inequalities_t[i])
                    if length != 0:
                        for ineq_constr, k in zip(self.node_inequalities_t[i], range(length)):
                            obj += self.model[i].rho_ / 2 * sum((ineq_constr[t].body + self.model[i].u_ineq_t[k, t] -
                                                                 self.model[i].v_k_t[k, t]) ** 2
                                                                for t in range(len(ineq_constr)))

                    length = len(self.node_inequalities_n[i])
                    if length != 0:
                        for ineq_constr, k in zip(self.node_inequalities_n[i], range(length)):
                            obj += self.model[i].rho_ / 2 * (ineq_constr.body + self.model[i].u_ineq_n[k] -
                                                             self.model[i].v_k_n[k])**2

            # if we want to redefine the objective for a certain node, then we should first reset the old objective
            try:
                self.model[i].del_component(self.model[i].o)
            except AttributeError:
                pass
            self.model[i].o = pyomo.Objective(expr=obj)
        return

    def _solve_single(self, last_p_els, last_x_, last_u, local_index, global_index, debug=True):
        """Call the solver to solve this nodes optimization problem for a single entity"""
        self._set_model_variables(last_p_els, last_x_, last_u, local_index, global_index)
        self.obj_update(local_index)

        model = self.model[local_index]
        entity = self.entities[local_index]
        solver = self.solvers[local_index]

        solve_options = self.solver_options.get("solve", {})
        if self.is_persistent:
            result = solver.solve(**solve_options)
        else:
            result = solver.solve(model, **solve_options)
        if (not (result.solver.termination_condition == TerminationCondition.optimal or
                result.solver.termination_condition == TerminationCondition.maxTimeLimit or
                result.solver.termination_condition == TerminationCondition.maxIterations) or
                not (result.solver.status == SolverStatus.ok or
                     result.solver.status == SolverStatus.warning or
                     result.solver.status == SolverStatus.aborted)):
            if debug:
                import pycity_scheduling.util.debug as debug
                debug.analyze_model(model, solver, result)
            raise NonoptimalError("Could not retrieve schedule from model.")

        entity.update_schedule()

        return self.entities[local_index].model.p_el_vars 

    def solve(self, variable_refs, update_constr=False, debug=True):
        """Call the solver to solve this nodes optimization problem for every entity on the node"""
        p_el_var_list = []
        indices_list = []

        last_p_els = ray.get(variable_refs[0])
        last_x_ = ray.get(variable_refs[1])
        last_u_ = ray.get(variable_refs[2])
        global_entity_indices = ray.get(variable_refs[3])

        if update_constr:
            self.constr_update()

        is_feasible = True
        for i, entity in enumerate(self.entities): 
            global_index = global_entity_indices[entity.id]
            try:
                p_el_vars = self._solve_single(last_p_els, last_x_, last_u_, i, global_index, debug)
                p_el_var_list.append(p_el_vars)
                indices_list.append(entity.id)
            except:
                is_feasible = False

        # return p_el_vars with other method or cast pyomo vars on the side of the node
        numpy_vars = np.array([extract_pyomo_values(var, float) for var in p_el_var_list])
        numpy_indices = np.array(indices_list)

        obj_value = self.get_objective()
        return [numpy_indices, numpy_vars, obj_value, is_feasible]

    def incentive_signal_update(self, iteration_num):
        """Update all MIQP ADMM parameters (first the constraints then the variables) for every entity on the node"""
        for i, entity in enumerate(self.entities):
            if self.x_update_mode == "unconstrained":
                length = len(self.node_inequalities_t[i])
                if length != 0:
                    for ineq_constr, k in zip(self.node_inequalities_t[i], range(length)):
                        for t in range(len(ineq_constr)):
                            v_update = pyomo.value(ineq_constr[t].body) + self.model[i].u_ineq_t[k, t].value
                            if v_update > 0:
                                self.model[i].v_k_t[k, t] = v_update
                            else:
                                self.model[i].v_k_t[k, t] = 0

                length = len(self.node_inequalities_n[i])
                if length != 0:
                    for ineq_constr, k in zip(self.node_inequalities_n[i], range(length)):
                        v_update = pyomo.value(ineq_constr.body) + self.model[i].u_ineq_n[k].value
                        if v_update > 0:
                            self.model[i].v_k_n[k] = v_update
                        else:
                            self.model[i].v_k_n[k] = 0

                length = len(self.node_inequalities_t[i])
                if length != 0:
                    for ineq_constr, k in zip(self.node_inequalities_t[i], range(length)):
                        for t in range(len(ineq_constr)):
                            self.model[i].u_ineq_t[k, t] = self.model[i].u_ineq_t[k, t].value + \
                                                        pyomo.value(ineq_constr[t].body) - \
                                                        self.model[i].v_k_t[k, t].value

                length = len(self.node_inequalities_n[i])
                if length != 0:
                    for ineq_constr, k in zip(self.node_inequalities_n[i], range(length)):
                        self.model[i].u_ineq_n[k] = self.model[i].u_ineq_n[k].value + pyomo.value(ineq_constr.body) - \
                                                    self.model[i].v_k_n[k].value

                length = len(self.node_equalities_t[i])
                if length != 0:
                    for eq_constr, k in zip(self.node_equalities_t[i], range(length)):
                        for t in range(len(eq_constr)):
                            self.model[i].u_eq_t[k, t] = (self.model[i].u_eq_t[k, t].value +
                                                          pyomo.value(eq_constr[t].body))

                length = len(self.node_equalities_n[i])
                if length != 0:
                    for eq_constr, k in zip(self.node_equalities_n[i], range(length)):
                        self.model[i].u_eq_n[k] = self.model[i].u_eq_n[k].value + pyomo.value(eq_constr.body)

            # x_k update
            length = len(self.node_binaries[i])
            if length != 0:
                for x, k in zip(self.node_binaries[i], range(length)):
                    for t in range(self.op_horizon):
                        # Integer rounding:
                        self.model[i].x_k[k, t] = round(x[t].value + self.model[i].u_xk[k, t].value)
                        # Binary rounding:
                        # x_update = abs(x[t].value + node.model.u_xk[k, t].value)
                        # if x_update >= 0.5:
                        #    node.model.x_k[k, t] = 1
                        # else:
                        #    node.model.x_k[k, t] = 0
                        self.node_x_k_values[i][k][t][iteration_num] = self.model[i].x_k[k, t].value

            # u_xk update
            length = len(self.node_binaries[i])
            if length != 0:
                for x, x_val, u_k, k in zip(self.node_binaries[i],self.node_bin_values[i],
                                            self.node_u_k_values[i], range(length)):
                    for t in range(self.op_horizon):
                       
                        self.model[i].u_xk[k, t] = self.model[i].u_xk[k, t].value + x[t].value - \
                                                self.model[i].x_k[k, t].value
                        x_val[t][iteration_num] = x[t].value
                        u_k[t][iteration_num] = self.model[i].u_xk[k, t].value
        # Return local x_ks and u_ks to head to update district_x_k_values[i] and u_k[t] on head side
        return

    def fix_variables(self):
        """Fix the binary variables for all entities on the remote node"""
        for i, entity in enumerate(self.entities):
            length = len(self.node_binaries[i])
            if length != 0:
                for x, k in zip(self.node_binaries[i], range(length)):
                    for t in range(self.op_horizon):
                        x_k = self.model[i].x_k[k, t].value
                        x[t].fix(x_k)
        return

    def release_variables(self):
        """Release the binary variables for all entities on the remote node"""
        for i, entity in enumerate(self.entities):
            length = len(self.node_binaries[i])
            if length != 0:
                for x, k in zip(self.node_binaries[i], range(length)):
                    for t in range(self.op_horizon):
                        x[t].unfix()
        return

    def postsolve(self):
        """Updates the schedules of each asset and entity on the node"""
        super().postsolve()
        pass

    def update_gamma(self, new_gamma):
        """Updates the gamma parameter for all entities on the remote node"""
        self.gamma = new_gamma
        for i, entity in enumerate(self.entities):
            self.model[i].gamma_ = new_gamma
        return

    def update_rho(self, new_rho):
        """Updates the rho parameter for all entities on the remote node"""
        self.rho = new_rho
        for i, entity in enumerate(self.entities):
            self.model[i].rho_ = new_rho
        return

    def activate_constraints(self):
        """Activates all constraints for all entities on the remote node"""
        for i, entity in enumerate(self.entities):
            if not isinstance(entity, CityDistrict):
                for en in entity.get_all_entities():
                    for constraint in en.model.component_objects(pyomo.Constraint):
                        constraint.activate()
        return

    def deactivate_constraints(self):
        """Deactivates all constraints for all entities on the remote node"""
        for i, entity in enumerate(self.entities):
            if not isinstance(entity, CityDistrict):
                for en in entity.get_all_entities():
                    for constraint in en.model.component_objects(pyomo.Constraint):
                        constraint.deactivate()
        return

    # Returns True, if no constraint or binary variable violations occur
    def check_violations(self, detailed_print_out=False):
        """Checks constraint and binary variable violations for all entities on the remote node"""
        constr_counter = 0
        var_counter = 0
        number_constr = 0
        number_var = 0
        for i, entity in enumerate(self.entities):
            length = len(self.node_binaries[i])
            if length != 0:
                for x, val, x_k, u_k in zip(self.node_binaries[i], self.node_bin_values[i],
                                            self.node_x_k_values[i], self.node_u_k_values[i]):
                    for t in range(self.op_horizon):
                        if abs(x[t].value) < 0.1 or (0.9 < x[t].value < 1.1):
                            pass
                        else:
                            var_counter += 1
                            if detailed_print_out:
                                x[t].pprint()
                        number_var += 1

            length = len(self.node_equalities_t[i])
            if length != 0:
                for eq_constr in self.node_equalities_t[i]:
                    for t in range(len(eq_constr)):
                        if abs(pyomo.value(eq_constr[t].body)) > 0.05:
                            if detailed_print_out:
                                print(eq_constr[t].body, " ", pyomo.value(eq_constr[t].body))
                            constr_counter += 1
                        number_constr += 1

            length = len(self.node_equalities_n[i])
            if length != 0:
                for eq_constr in self.node_equalities_n[i]:
                    if abs(pyomo.value(eq_constr.body)) > 0.05:
                        if detailed_print_out:
                            print(eq_constr.body, " ", pyomo.value(eq_constr.body))
                        constr_counter += 1
                    number_constr += 1

            length = len(self.node_inequalities_t[i])
            if length != 0:
                for ineq_constr in self.node_inequalities_t[i]:
                    for t in range(len(ineq_constr)):
                        if pyomo.value(ineq_constr[t].body) < -0.05:
                            if detailed_print_out:
                                print(ineq_constr[t].body, " ", pyomo.value(ineq_constr[t].body))
                            constr_counter += 1
                        number_constr += 1

            length = len(self.node_inequalities_n[i])
            if length != 0:
                for ineq_constr in self.node_inequalities_n[i]:
                    if pyomo.value(ineq_constr.body) < -0.05:
                        if detailed_print_out:
                            print(ineq_constr.body, " ", pyomo.value(ineq_constr.body))
                        constr_counter += 1
                    number_constr += 1
        return constr_counter, var_counter, number_constr, number_var


@ray.remote(scheduling_strategy="SPREAD", num_cpus=1, num_gpus=0)
class RayDerivativeFreeALADINSolverNode(RaySolverNode):
    """Ray Node which can be used to solve all entities provided to it with in a ray cluster using the derivative-free
     ALADIN method.

    Provides an abstraction layer for algorithms, so entities can be
    assigned to nodes and optimized easily.

    Parameters
    ----------
    solver : str
        Solver to use for solving (sub)problems.
    solver_options : dict, optional
        Options to pass to calls to the solver. Keys are the name of
        the functions being called and are one of `__call__`, `set_instance_`,
        `solve`.
        - `__call__` is the function being called when generating an instance
          with the pyomo SolverFactory. In addition to the options provided,
          `node_ids` is passed to this call containing the IDs of the entities
          being optimized.
        - `set_instance` is called when a pyomo Model is set as an instance of
          a persistent solver.
        - `solve` is called to perform an optimization. If not set,
          `save_results` and `load_solutions` may be set to false to provide a
          speedup.
    entities : list
        List of entities which should be optimized by this node.
    mode : str, optional
        Specifies which set of constraints to use.

        - `convex`  : Use linear constraints
        - `integer`  : May use non-linear constraints
    robustness : tuple, optional
        Tuple of two floats. First entry defines how many time steps are
        protected from deviations. Second entry defines the magnitude of
        deviations which are considered.
    """

    def __init__(self, solver, solver_options, entities, rho, hessian_scaling, node_index=0, op_horizon=0, mode="convex",
                 robustness=None):
        self.rho = rho
        self.hessian_scaling = hessian_scaling
        super().__init__(solver, solver_options, entities, node_index, op_horizon, mode, robustness)
        self.calc_model_params()

    def calc_model_params(self):
        """ Create the model parameters localy on the actor """
        for i, entity in enumerate(self.entities):
            beta = pyomo.Param(mutable=True, initialize=1)
            rho = pyomo.Param(mutable=True, initialize=self.rho)
            lambda_k = pyomo.Param(entity.model.t, mutable=True, initialize=0)
            x_k = pyomo.Param(entity.model.t, mutable=True, initialize=0)
            self.model[i].beta = beta
            self.model[i].rho = rho
            self.model[i].lambda_k = lambda_k
            self.model[i].x_k = x_k

    def _set_model_variables(self, lambda_k, x_k, local_index, global_index):
        """Sets the model vars for entity on the remote node"""
        for t in range(self.op_horizon):
            self.model[local_index].lambda_k[t] = lambda_k[t]
            self.model[local_index].x_k[t] = x_k[global_index, t]

    def add_objective(self):
        """Adds the objective to all models of every entity on the remote node"""
        for i, entity in enumerate(self.entities):
            obj = self.model[i].beta * entity.get_objective()
            # ToDo: Attention - Currently only defined for "price", "co2", "peak-shaving" and "least-squares"
            decision_vars = entity.get_decision_var()

            # lambda penalty term
            for t in range(self.op_horizon):
                obj += self.model[i].lambda_k[t] * decision_vars[t]

            # augmented penalty term
            # ToDo: Define custom scaling...
            scaling_i = self.hessian_scaling * np.eye(self.op_horizon)
            penalty = [decision_vars[t] - self.model[i].x_k[t] for t in range(self.op_horizon)]
            for j in range(self.op_horizon):
                for k in range(self.op_horizon):
                    if scaling_i[j][k] != 0.0:
                        obj += self.model[i].rho * (penalty[j] * scaling_i[j][k] * penalty[k])
            self.model[i].o = pyomo.Objective(expr=obj)
        return

    def _solve_single(self, lambda_k, x_k, local_index, global_index, debug=True):
        """Call the solver to solve this nodes optimization problem for a single entity

        Parameters
        ----------
        variables : list of lists of variables, optional
            Can contain a list for each node in nodes to indicate to pyomo which
            variables should be loaded back into the model. Specifying this can
            lead to a significant speedup.
        debug : bool, optional
            Specify whether detailed debug information shall be printed. Defaults
            to true.
        """
        self._set_model_variables(lambda_k, x_k, local_index, global_index)
        self.obj_update(local_index)

        model = self.model[local_index]
        entity = self.entities[local_index]
        solver = self.solvers[local_index]

        solve_options = self.solver_options.get("solve", {})
        if self.is_persistent:
            result = solver.solve(**solve_options)
        else:
            result = solver.solve(model, **solve_options)
        if result.solver.termination_condition != TerminationCondition.optimal or \
                result.solver.status != SolverStatus.ok:
            if debug:
                import pycity_scheduling.util.debug as debug
                debug.analyze_model(model, solver, result)
            raise NonoptimalError("Could not retrieve schedule from model.")

        entity.update_schedule()

        return self.entities[local_index].model.p_el_vars

    def solve(self, variable_refs, debug=True):
        """Call the solver to solve this nodes optimization problem for every entity on the node

        Parameters
        ----------
        variables : list of lists of variables, optional
            Can contain a list for each node in nodes to indicate to pyomo which
            variables should be loaded back into the model. Specifying this can
            lead to a significant speedup.
        debug : bool, optional
            Specify whether detailed debug information shall be printed. Defaults
            to true.
        """
        p_el_var_list = []
        indices_list = []
        sub_times_list = []

        lambda_k = ray.get(variable_refs[0])
        x_k = ray.get(variable_refs[1])
        global_entity_indices = ray.get(variable_refs[2])

        for i, entity in enumerate(self.entities):
            global_index = global_entity_indices[entity.id]
            t_0 = time.monotonic()
            p_el_vars = self._solve_single(lambda_k, x_k, i, global_index, debug)
            t_1 = time.monotonic()
            sub_times_list.append(t_1 - t_0)
            p_el_var_list.append(p_el_vars)
            indices_list.append(entity.id)

        # return p_el_vars with other method or cast pyomo vars on the side of the node
        numpy_vars = np.array([extract_pyomo_values(var, float) for var in p_el_var_list])
        numpy_indices = np.array(indices_list)
        numpy_times = np.array(sub_times_list)

        obj_value = self.get_objective()

        return [numpy_indices, numpy_vars, obj_value, numpy_times]

    def postsolve(self):
        """ Updates the schedules of each asset and entity on the node """
        super().postsolve()
