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
from pycity_scheduling.classes import *
from pycity_scheduling.algorithms import *


# This is a simple power scheduling example integrating grid constraints. The central optimization algorithm is used to
# schedule an alternative four load branch scenario compared to 'example_24_scheduling_with_grid_four_load_branch.py'.


def main(do_plot=False):
    print("\n\n------ Example 26: Scheduling with Grid - Four Load Branch Out ------\n\n")
    
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
    
    # Building 1
    bd1 = Building(e, objective='price')
    cd.addEntity(entity=bd1, position=[0, 0])
    bes = BuildingEnergySystem(e)
    bd1.addEntity(bes)
    ap = Apartment(e)
    bd1.addEntity(ap)
    load = np.array([p_load] * nt)
    fi = FixedLoad(e, method=0, demand=load)
    ap.addEntity(fi)
    
    # Building 2
    bd2 = Building(e, objective='price')
    cd.addEntity(entity=bd2, position=[0, 0])
    bes = BuildingEnergySystem(e)
    bd2.addEntity(bes)
    ap = Apartment(e)
    bd2.addEntity(ap)
    load = np.array([p_load] * nt)
    fi = FixedLoad(e, method=0, demand=load)
    ap.addEntity(fi)
    
    # Building 3
    bd3 = Building(e, objective='price')
    cd.addEntity(entity=bd3, position=[0, 0])
    bes = BuildingEnergySystem(e)
    bd3.addEntity(bes)
    ap = Apartment(e)
    bd3.addEntity(ap)
    load = np.array([p_load] * nt)
    fi = FixedLoad(e, method=0, demand=load)
    ap.addEntity(fi)

    # Building 4
    bd4 = Building(e, objective='price')
    cd.addEntity(entity=bd4, position=[0, 0])
    bes = BuildingEnergySystem(e)
    bd4.addEntity(bes)
    ap = Apartment(e)
    bd4.addEntity(ap)
    load = np.array([p_load] * nt)
    fi = FixedLoad(e, method=0, demand=load)
    ap.addEntity(fi)
    
    # Define grid properties:
    P_ref = 1000  # kW
    Q_ref = 500  # kVar
    V_ref = 400  # V
    line_capacity = 3**0.5 * 0.242 * 400  # kW
    R_cable = 0.225  # Ohm/km
    X_cable = 0.08  # Ohm/km
    line_length = 0.05  # km
    
    cd.addElectricalGrid(e, P_ref, Q_ref, slack_V=0.998, ref_V=V_ref)

    # Add electrical grid:
    grid = cd.electrical_grid
    grid.update_cable_properties(R_cable, X_cable)

    # Add lines:
    bus3 = ElectricalNode(e, None, None)
    bus4 = ElectricalNode(e, None, None)
    bus5 = ElectricalNode(e, None, None)
    bus6 = ElectricalNode(e, None, None)

    grid.connect_entities(grid.slack_node, bus3, line_capacity, line_length)
    grid.connect_entities(bus3, bus4, line_capacity, line_length)
    grid.connect_entities(bus4, bus5, line_capacity, line_length)
    grid.connect_entities(bus5, bus6, line_capacity, line_length)

    grid.connect_entities(bus3, bd1, line_capacity, line_length)
    grid.connect_entities(bus4, bd2, line_capacity, line_length)
    grid.connect_entities(bus5, bd3, line_capacity, line_length)
    grid.connect_entities(bus6, bd4, line_capacity, line_length)

    # Perform the scheduling:
    opt = CentralOptimization(city_district=cd)
    results = opt.solve()
    cd.copy_schedule("central")
    
    # Print the building's schedules:
    print("Schedule building no. one:")
    print(list(bd1.p_el_schedule))
    print("Schedule building no. two:")
    print(list(bd2.p_el_schedule))
    print("Schedule building no. three:")
    print(list(bd2.p_el_schedule))
    print("Schedule building no. four:")
    print(list(bd2.p_el_schedule))
    
    # Print the district's schedule:
    print("Schedule of the city district:")
    print(list(cd.p_el_schedule))
    
    # Plot electrical grid's schedule:
    if do_plot:
        grid.plot_graph_results(t=1)
        

if __name__ == '__main__':
    # Run example:
    main(do_plot=True)
