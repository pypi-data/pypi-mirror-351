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
import time

from pycity_scheduling.classes import *
from pycity_scheduling.algorithms import *


# This is a simple power scheduling example integrating grid constraints. The central optimization algorithm is used to
# schedule an N branch scenario with five buildings (load/generation) per branch.


def main(do_plot=False):
    print("\n\n------ Example 30: Scheduling with Grid - N Branches ------\n\n")

    N = 2
    start_time = time.time()
    # Define timer, price, weather, and environment objects:
    nt = 24 * 7
    t = Timer(op_horizon=nt, step_size=3600)
    p = Prices(timer=t)
    w = Weather(timer=t)
    e = Environment(timer=t, weather=w, prices=p)
    # City district with district operator objective "price":
    cd = CityDistrict(environment=e)
    
    # Fixed load for buildings
    p_load = 0.03 * 1000  # kW
    
    building_list = []
    
    for i in range(5*N):
        bd = Building(e, objective='price')
        cd.addEntity(entity=bd, position=[0, 0])
        bes = BuildingEnergySystem(e)
        bd.addEntity(bes)
        ap = Apartment(e)
        bd.addEntity(ap)
        load = np.array([p_load] * nt)
        fi = FixedLoad(e, method=0, demand=load)
        ap.addEntity(fi)
        building_list.append(bd)

    # Define grid properties:
    P_ref = 1000  # kW
    Q_ref = 500  # kVar
    V_ref = 400  # V
    line_capacity = 3**0.5 * 0.242 * 400  # kW
    R_cable = 0.225  # Ohm/km
    X_cable = 0  # Ohm/km
    line_length = 0.05  # km
    
    cd.addElectricalGrid(e, P_ref, Q_ref, slack_V=0.99, ref_V=V_ref)

    # Add electrical grid:
    grid = cd.electrical_grid
    grid.update_cable_properties(R_cable, X_cable)

    # Add lines:
    for i in range(N):
        grid.connect_entities(grid.slack_node, building_list[5*i], line_capacity, line_length)
        grid.connect_entities(building_list[5*i], building_list[5*i+1], line_capacity, line_length)
        grid.connect_entities(building_list[5*i+1], building_list[5*i+2], line_capacity, line_length)
        grid.connect_entities(building_list[5*i+2], building_list[5*i+3], line_capacity, line_length)
        grid.connect_entities(building_list[5*i+3], building_list[5*i+4], line_capacity, line_length)

    # Perform the scheduling:
    opt = CentralOptimization(city_district=cd)
    building_time = time.time() - start_time
    results = opt.solve()
    solving_time = time.time() - building_time
    cd.copy_schedule("central")

    # Plot electrical grid's schedule:
    if do_plot:
        grid.plot_graph_results(t=1)
        

if __name__ == '__main__':
    # Run example:
    main(do_plot=True)
