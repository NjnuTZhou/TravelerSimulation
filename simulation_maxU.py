from tqdm import tqdm
import file_operation as fo
import GeoUtils as geo_utils
import math
import random
import copy


class Traveler:
    def __init__(self, index, traveler_type, start_node):
        self.index = index
        self.trails = [start_node]
        self.type = traveler_type
        self.target_node = ''
        self.coordinate = [0, 0]
        self.condition = 'start'
        self.current_route_section = []
        self.assigned_route = []
        self.if_assigned_route = False
        self.start_time = 0
        self.end_time = 0
        self.visited_view_point = []
        self.coord_trails = []
        self.stop_time = 0
        self.stop_node = ''

    def set_coordinate(self, coordinate):
        self.coordinate[0] = coordinate[0]
        self.coordinate[1] = coordinate[1]


class SimulationParams:
    def __init__(self, simulation_params):
        self.gate_list = simulation_params['gateList']
        self.traveler_type_probability = simulation_params['travelerTypeProbability']
        self.tourist_per_hour = simulation_params['touristPerHour']
        self.route_attributions = simulation_params['routeAttributions']
        self.view_point_in_route = simulation_params['viewPointInRoute']
        self.route_traveler_count = simulation_params['routeTravelerCount']
        self.route_points = simulation_params['routePoints']
        self.traveler_weights = simulation_params['travelerWeights']
        self.tourist_per_hour = simulation_params['touristPerHour']


class BaseParams:
    def __init__(self, data_type):
        self.date_type = data_type
        self.if_play = True
        self.total_simulation_time = 10
        self.if_add_traveler = True
        self.simulation_seconds = 0
        self.simulation_hour = 0
        self.gate_traveler_add_frequency = 0
        self.gate_traveler_last_add_time = 0
        self.traveler_index = 0
        self.in_list = []
        self.out_list = []
        self.total_traveler_count = []
        self.route_return_ratio = 0.1
        self.route_node_return_ratio = 0.3


def add_new_traveler(base_params, simulation_params):
    if base_params.gate_traveler_add_frequency == 0:
        return
    if base_params.simulation_seconds - base_params.gate_traveler_last_add_time >= base_params.gate_traveler_add_frequency:
        count = round((
                              base_params.simulation_seconds - base_params.gate_traveler_last_add_time) / base_params.gate_traveler_add_frequency)
        for m in range(0, len(simulation_params.gate_list)):
            for i in range(0, count):
                random_seed = random.random()
                traveler_type = 0
                for j in range(0, len(simulation_params.traveler_type_probability)):
                    if random_seed <= simulation_params.traveler_type_probability[j]:
                        traveler_type = j
                        break
                traveler = Traveler(base_params.traveler_index, traveler_type, simulation_params.gate_list[m])
                traveler.start_time = base_params.simulation_seconds
                base_params.in_list.append(traveler)
                base_params.traveler_index += 1
        base_params.gate_traveler_last_add_time = base_params.simulation_seconds


def move_travelers(base_params, simulation_params):
    for traveler in base_params.in_list:
        if traveler.condition == 'start':
            move_traveler_from_gate(traveler, base_params, simulation_params)
        if traveler.condition == 'playing':
            if if_stop_play(traveler, base_params):
                traveler.condition = 'readyOut'
                traveler.stop_time = base_params.simulation_seconds
                traveler.stop_node = traveler.target_node
                assign_traveler_route(traveler, base_params, simulation_params)
        if traveler.condition == 'playing':
            move_traveler_free(traveler, base_params, simulation_params)
        elif traveler.condition == 'readyOut':
            move_traveler_assigned(traveler, base_params, simulation_params)

        if traveler.condition == 'out':
            traveler.end_time = base_params.simulation_seconds
            base_params.in_list.remove(traveler)
            base_params.out_list.append(traveler)
        traveler.coord_trails.append(copy.deepcopy(traveler.coordinate))


def move_traveler_from_gate(traveler, base_params, simulation_params):
    gate_id = traveler.trails[-1]
    max_utility_node = get_route_chosen_probability(traveler, gate_id, base_params, simulation_params, '')
    traveler.current_route_section = copy.deepcopy(
        simulation_params.route_attributions[gate_id]['routes'][max_utility_node]['path'])
    traveler.set_coordinate(traveler.current_route_section.pop(0))
    traveler.condition = 'playing'
    traveler.target_node = max_utility_node

    route_id = geo_utils.get_route_id(gate_id, max_utility_node)
    if route_id in simulation_params.gate_list:
        traveler.visited_view_point.extend(simulation_params.view_point_in_route[route_id])
    simulation_params.route_traveler_count[route_id] += 1


def move_traveler_free(traveler, base_params, simulation_params):
    speed = get_traveler_speed(traveler, base_params, simulation_params)
    while speed > 0:
        from_node = traveler.trails[-1]
        target_node = traveler.target_node
        if len(traveler.current_route_section) > 0:
            distance_to_next_coordinate = geo_utils.distance(traveler.coordinate, traveler.current_route_section[0])
            if distance_to_next_coordinate >= speed:
                ratio = speed / distance_to_next_coordinate
                new_coord = [
                    ratio * (traveler.current_route_section[0][0] - traveler.coordinate[0]) + traveler.coordinate[0],
                    ratio * (traveler.current_route_section[0][1] - traveler.coordinate[1]) + traveler.coordinate[1]]
                traveler.set_coordinate(new_coord)
            else:
                traveler.set_coordinate(traveler.current_route_section.pop(0))
            speed -= distance_to_next_coordinate
        else:
            traveler.trails.append(target_node)
            route_id = geo_utils.get_route_id(from_node, target_node)
            simulation_params.route_traveler_count[route_id] -= 1
            # if traveler.condition=='readyOut':
            #     traveler.condition='out'
            #     break

            # if if_stop_play(traveler, target_node, base_params, simulation_params) == 'out':
            #     traveler.condition = 'out'
            #     break
            max_utility_node = get_route_chosen_probability(traveler, target_node, base_params, simulation_params,
                                                            from_node)
            traveler.target_node = max_utility_node
            traveler.current_route_section = copy.deepcopy(
                simulation_params.route_attributions[target_node]['routes'][max_utility_node]['path'])
            traveler.set_coordinate(traveler.current_route_section.pop(0))
            route_id = geo_utils.get_route_id(target_node, max_utility_node)
            if route_id in simulation_params.view_point_in_route:
                traveler.visited_view_point.extend(simulation_params.view_point_in_route[route_id])
            simulation_params.route_traveler_count[route_id] += 1


def move_traveler_assigned(traveler, base_params, simulation_params):
    speed = get_traveler_speed(traveler, base_params, simulation_params)
    while speed > 0:
        from_node = traveler.trails[-1]
        target_node = traveler.target_node
        if len(traveler.current_route_section) > 0:
            distance_to_next_coordinate = geo_utils.distance(traveler.coordinate, traveler.current_route_section[0])
            if distance_to_next_coordinate >= speed:
                ratio = speed / distance_to_next_coordinate
                new_coord = [
                    ratio * (traveler.current_route_section[0][0] - traveler.coordinate[0]) + traveler.coordinate[0],
                    ratio * (traveler.current_route_section[0][1] - traveler.coordinate[1]) + traveler.coordinate[1]]
                traveler.set_coordinate(new_coord)
            else:
                traveler.set_coordinate(traveler.current_route_section.pop(0))
            speed -= distance_to_next_coordinate
        else:
            traveler.trails.append(target_node)
            route_id = geo_utils.get_route_id(from_node, target_node)
            simulation_params.route_traveler_count[route_id] -= 1
            if target_node in simulation_params.gate_list:
                traveler.condition = 'out'
                break
            else:
                traveler.target_node = traveler.assigned_route.pop(0)
                traveler.current_route_section = copy.deepcopy(
                    simulation_params.route_attributions[target_node]['routes'][traveler.target_node]['path'])
                traveler.current_route_section.pop(0)


def assign_traveler_route(traveler, base_params, simulation_params):
    rand_seed = math.floor(random.random() * len(simulation_params.gate_list))
    assigned_route = get_shortest_route_out(traveler.target_node, simulation_params.gate_list[rand_seed], base_params,
                                            simulation_params)
    traveler.assigned_route = assigned_route
    traveler.if_assigned_route = True


def get_shortest_route_out(start_node, end_node, base_params, simulation_params):
    visited = []
    queue = []
    result_queue = []
    queue.append(start_node)
    result_queue.append([])
    while len(queue) > 0:
        node = queue.pop(0)
        result_array = result_queue.pop(0)
        if node in visited:
            continue
        else:
            current_node = simulation_params.route_attributions[node]
            visited.append(node)
            for n in current_node['routes']:
                if n == end_node:
                    result_array.append(n)
                    return result_array
            for next_node in current_node['routes']:
                if next_node not in visited:
                    tmp_result = copy.deepcopy(result_array)
                    tmp_result.append(next_node)
                    result_queue.append(tmp_result)
                    queue.append(next_node)
    return []


def get_route_chosen_probability(traveler, current_id, base_params, simulation_params, from_id):
    probability = {}
    sum_view = 0
    sum_flow = 0
    for to_id in simulation_params.route_attributions[current_id]['routes']:
        if to_id in simulation_params.gate_list:
            continue
        angle_point = 0 if from_id == '' else simulation_params.route_points['anglePoint'][current_id][from_id][to_id]
        view_point = get_view_point_point(traveler, current_id, to_id, base_params, simulation_params)
        flow_point = get_flow_point(traveler, current_id, to_id, base_params, simulation_params)
        probability[to_id] = [
            simulation_params.route_points['levelPoint'][current_id][to_id],
            simulation_params.route_points['gradientPoint'][current_id][to_id],
            angle_point,
            simulation_params.route_points['routeViewPoint'][current_id][to_id],
            view_point,
            simulation_params.route_points['servicePoint'][current_id][to_id],
            flow_point
        ]
        sum_view += view_point
        sum_flow += flow_point

    for to_id in probability:
        if sum_view != 0:
            probability[to_id][4] /= sum_view
        if sum_flow != 0:
            probability[to_id][6] /= sum_flow

    max_utility = -999999
    max_utility_node = ''
    for to_id in probability:
        utility = 0
        for i in range(0, 7):
            utility += probability[to_id][i] * simulation_params.traveler_weights[traveler.type][i]
        if to_id == from_id:
            utility *= base_params.route_return_ratio
        elif to_id in traveler.trails:
            utility *= base_params.route_node_return_ratio

        if max_utility < utility:
            max_utility = utility
            max_utility_node = to_id

    return max_utility_node


def get_view_point_point(traveler, current_id, to_id, base_params, simulation_params):
    point = 0
    for view_point_name in simulation_params.route_points['viewPointPoint'][current_id][to_id]:
        if view_point_name not in traveler.visited_view_point:
            point += simulation_params.route_points['viewPointPoint'][current_id][to_id][view_point_name]
    return math.exp(point)


def get_flow_point(traveler, current_id, to_id, base_params, simulation_params):
    route_id = geo_utils.get_route_id(current_id, to_id)
    traveler_count = simulation_params.route_traveler_count[route_id]
    capacity = simulation_params.route_attributions[current_id]['routes'][to_id]['capacity']
    flow = traveler_count / capacity
    if flow <= 0.22:
        return math.sin(5.4 * math.pi * flow / 2.4)
    else:
        return math.sin((5.4 * math.pi * flow + 0.9 * math.pi) / 4.2)


def get_traveler_speed(traveler, base_params, simulation_params):
    from_node = traveler.trails[-1]
    target_node = traveler.target_node
    attribution = simulation_params.route_attributions[from_node]['routes'][target_node]

    route_id = geo_utils.get_route_id(from_node, target_node)
    level = attribution['level']
    gradient = attribution['gradient']
    flow = simulation_params.route_traveler_count[route_id] / attribution['capacity']
    view = attribution['view']
    init_speed = random.random() / 5 + 1
    speed = init_speed * get_level_ratio(level) * get_gradient_ratio(gradient) * get_view_ratio(view)
    if flow > 0.22:
        speed *= get_flow_ratio(flow)

    rand_seed = random.random()
    speed *= 1 - (rand_seed / 10 - 0.05)
    return speed


def get_level_ratio(x):
    return 0.8 + math.pow(0.04 - math.pow((x - 5), 2) / 400, 0.5)


def get_gradient_ratio(x):
    return 0.9 * math.cos(x) + 0.1


def get_view_ratio(x):
    return 1 - 0.798 * x


def get_flow_ratio(x):
    return 1 - math.exp(-1.913 * (1 / (x * 5.4) - 1 / 5.4))


def if_stop_play(traveler, base_params):
    minimum_time = 7200 if base_params.if_add_traveler else 3600
    if base_params.simulation_seconds - traveler.start_time < minimum_time:
        return False
    else:
        pre_time = 7200 if base_params.if_add_traveler else 3600
        prob = (base_params.simulation_seconds - traveler.start_time - minimum_time) ** 2 / pre_time ** 2
        rand_seed = random.random()
        if rand_seed <= prob:
            return True
    return False


def save_simulation_data(base_params):
    traveler_trail_data = {}
    for traveler in base_params.out_list:
        traveler_trail_data[str(traveler.index)] = {
            "trails": traveler.trails,
            "startTime": traveler.start_time,
            "endTime": traveler.end_time,
            "type": traveler.type
        }

    fo.write_json_file(traveler_trail_data,
                       'simulationData_maxU/simulationData' + str(base_params.date_type) + ".json")
    fo.write_json_file(base_params.total_traveler_count,
                       'simulationData_maxU/timeData' + str(base_params.date_type) + ".json")


def save_hour_traveler_distribution(base_params):
    geojson = {
        "type": "FeatureCollection",
        "name": "mxl_route",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        'features': []
    }
    for traveler in base_params.in_list:
        geojson['features'].append({
            "type": "Feature",
            "properties": {
                "id": str(traveler.index),
            },
            "geometry": {
                "type": "Point",
                "coordinates": traveler.coordinate
            }
        })
    fo.write_json_file(geojson, 'simulationData_maxU/simulation_traveler_distribution/' + str(
        base_params.date_type) + "_" + str(base_params.simulation_hour) + ".geojson")


def simulation(base_params, simulation_params):
    base_params.gate_traveler_add_frequency = math.floor(
        3600 / (simulation_params.tourist_per_hour[base_params.date_type][0] / len(simulation_params.gate_list)))

    total = base_params.total_simulation_time * 3600
    p_bar = tqdm(total=total)

    while base_params.if_play:
        if base_params.simulation_seconds >= base_params.total_simulation_time * 3600:
            base_params.if_add_traveler = False

        if base_params.if_add_traveler:
            add_new_traveler(base_params, simulation_params)

        move_travelers(base_params, simulation_params)
        base_params.simulation_seconds += 1
        base_params.total_traveler_count.append(len(base_params.in_list))

        if base_params.if_add_traveler is False and len(base_params.in_list) == 0:
            base_params.if_play = False
            print('模拟完成')

        if base_params.simulation_seconds % 3600 == 0:
            base_params.simulation_hour = math.floor(base_params.simulation_seconds / 3600)
            save_hour_traveler_distribution(base_params)
            if base_params.simulation_hour < 10:
                base_params.gate_traveler_add_frequency = math.floor(3600 / (
                        simulation_params.tourist_per_hour[base_params.date_type][base_params.simulation_hour] / len(
                    simulation_params.gate_list)))
        p_bar.update(1)
    save_simulation_data(base_params)


def main():
    base_params = BaseParams(0)
    simulation_params = SimulationParams(fo.open_json_file('simulation_params_2.json'))
    base_params.date_type = 0
    print('------simulating workday...')
    simulation(base_params, simulation_params)

    base_params1 = BaseParams(1)
    print('------simulating holiday...')
    simulation(base_params1, simulation_params)


if __name__ == '__main__':
    main()
