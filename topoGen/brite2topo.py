#! /usr/bin/python3
# -*- encoding:utf-8 -*-
import random

import pandas as pd
import re
from sklearn.cluster import KMeans
import networkx as nx
import fnss
from collections import defaultdict


def findEdgesLine(file_name: str) -> int:
    with open(file_name, 'r') as f:
        index = 0
        while not f.readline().startswith("Edges"):
            index += 1
    return index + 1


def findNodeLine(file_name: str) -> int:
    with open(file_name, 'r') as f:
        index = 0
        while not f.readline().startswith("Nodes"):
            index += 1
    return index + 1


def getNodesAndEdgesNumber(file_name: str) -> tuple:
    with open(file_name, 'r') as line:
        first_line = line.readline()
        if not first_line.startswith("Topology"):
            print("Get Nodes and Edges Number Error! Unknown format")
            return 0, 0
        numbers = re.findall("\d+", first_line)
        return numbers[0], numbers[1]


def dump_axis_from_brite(brite_file: str, node_type_file: str, out_file: str, node_n: int, cluster_n: int):
    """
    Get axis information from brite file
    :param cluster_n: controller number in each AS
    :param brite_file: input brite file name
    :param node_type_file: input layout file name
    :param out_file: output file name (layout file)
    :param node_n: total node number
    """
    # create and clear output file
    with open(out_file, 'w') as f:
        f.write("")
    node_line = findNodeLine(brite_file)
    # line describe: NodeID, x, y, in_degree, out_degree, as_id, type
    header = ["NodeID", "x", "y", "in_degree", "out_degree", "as_id", "type"]
    df = pd.read_csv(brite_file, skiprows=node_line, sep="\t", nrows=int(node_n), names=header)
    # get total as number
    as_n = df["as_id"].max() + 1
    # get all switches in node_type_file(line3)
    with open(node_type_file, 'r') as f:
        lines = f.readlines()
        switches = set(eval(lines[2].split(":")[1].strip()))
        clients = set(eval(lines[0].split(":")[1].strip()) + eval(lines[1].split(":")[1].strip()))

    # get access switch of each client, save to a dict
    topology = fnss.parse_brite(brite_file).to_undirected()
    topology = largest_connected_component_subgraph(topology)
    c2sw = {}
    for client in clients:
        c2sw[client] = list(topology.neighbors(client))[0]

    for i in range(as_n):
        # get axis of each AS
        axis_of_as = df[df["as_id"] == i][["NodeID", "x", "y", "as_id"]]
        # sieve NodeID in switches in df: axis_of_as
        axis_of_as_sw = axis_of_as[axis_of_as["NodeID"].isin(switches)].copy()
        axis_without_sw = axis_of_as[~axis_of_as["NodeID"].isin(switches | clients)].copy()
        # cluster axis of each AS
        kmeans = KMeans(n_clusters=cluster_n, random_state=0, n_init='auto').fit(axis_of_as_sw[["x", "y"]])
        # get cluster center
        cluster_center = kmeans.cluster_centers_
        # get cluster label
        axis_of_as_sw["ctrl_area"] = kmeans.labels_
        # dump axies to output file
        axis_of_as_sw.to_csv(out_file, sep=",", index=False, header=False, mode="a")
        # put other nodes(without switches and clients) into the right cluster use k-means
        axis_without_sw["ctrl_area"] = kmeans.predict(axis_without_sw[["x", "y"]])
        axis_without_sw.to_csv(out_file, sep=",", index=False, header=False, mode="a")
        # put clients into the right cluster use the same value of access switch's ctrl_area
        axis_of_as_cl = axis_of_as[axis_of_as["NodeID"].isin(clients)].copy()
        axis_of_as_cl["ctrl_area"] = axis_of_as_cl["NodeID"].map(c2sw).map(axis_of_as_sw.set_index("NodeID")["ctrl_area"])
        axis_of_as_cl.to_csv(out_file, sep=",", index=False, header=False, mode="a")

    print(">>> Dump axies from brite file success! output file: {}".format(out_file))


def largest_connected_component_subgraph(topology):
    """Returns the largest connected component subgraph

    Parameters
    ----------
    topology : fnss.Topology
        The topology object

    Returns
    -------
    largest_connected_component_sub-graphs : Topology
        The topology of the largest connected component
    """
    c = max(nx.connected_components(topology), key=len)
    return topology.subgraph(c)


def dump_node_type(file_name: str, out_file: str, recv_ratio: float):
    """
    Get node type information from brite file
    :param file_name: input brite file name
    :param out_file: output file name (node type file)
    :param recv_ratio: receiver ratio(0 ~ 1.0), choose receivers in which node degree == 1, the other is source
    """
    #  dump node type in: {"receiver", "source", "switch", "bgn"}
    topology = fnss.parse_brite(file_name).to_undirected()
    topology = largest_connected_component_subgraph(topology)
    # get node degree
    deg = nx.degree(topology)
    # print(min(deg))
    one_deg = [v for v in topology.nodes() if deg[v] == 1]
    # get receivers
    receiver = random.sample(one_deg, int(len(one_deg) * recv_ratio))
    # get sources
    source = [v for v in one_deg if v not in receiver]
    # get switches(nodes which connect to receivers and sources)
    switch = [list(topology.adj[v].keys())[0] for v in receiver + source]
    switch = list(set(switch))
    # get bgn nodes(nodes which has the type of RT_BORDER)
    bgn = [v for v in topology.nodes() if topology.nodes[v]["type"] == "RT_BORDER"]
    # get routers nodes
    router = [v for v in topology.nodes() if v not in receiver + source + switch + bgn]
    # dump node type to output file
    with open(out_file, 'w') as f:
        f.write("receiver: {}\n".format(receiver))
        f.write("source: {}\n".format(source))
        f.write("switch: {}\n".format(switch))
        f.write("bgn: {}\n".format(bgn))

    nodes_count = len(receiver) + len(switch) + len(source) + len(bgn) + len(router)
    print(">>> Dump {} nodes type from brite file success! output file: {}".format(nodes_count, out_file))


def dump_topology(file_name: str, out_file: str, node_n: int, edge_n: int):
    """
    Get topology information from brite file
    :param edge_n: edge number
    :param node_n: node number
    :param file_name: input brite file name
    :param out_file: output file name (topology file)
    """
    # create and clear output file
    with open(out_file, 'w') as f:
        f.write("")
    edge_line = findEdgesLine(file_name)
    # line describe: EdgeID, src, dst, weight, type
    df = pd.read_csv(file_name, skiprows=edge_line, sep="\t", header=None, skip_blank_lines=True)
    # format: edge_id, from_node, to_node, len, delay, capacity, from_as, to_as, type
    df[[6, 7]] += 1
    df = pd.DataFrame(df[[1, 2, 6, 7]])
    with open(out_file, "w") as f:
        f.write(str(node_n) + " " + str(edge_n) + "\n")
    df.to_csv(out_file, sep="\t", header=False, index=False, mode="a")
    print(">>> Generate topo done! nodes: {} / edges: {}, output to {}".format(node_n, edge_n, out_file))


def extent_brite_topo(file_name: str, out_file: str, one_deg_n: int, sw_ratio: float = 0.3):
    """
    Extend brite topology file, add receivers and sources which has degree one to the file
    :param sw_ratio: the first sw_ratio * node_n access switches will be random chosen
    :param one_deg_n: receiver number + source number
    :param file_name: input brite file name
    :param out_file: output file name (brite file with extend information)
    """
    with open(file_name, 'r') as f:
        lines = f.readlines()
    # The first line is: Topology: (xx Nodes, xx Edges), xx += one_deg_n
    n, e = re.findall(r"\d+", lines[0])
    lines[0] = "Topology: ( {} Nodes, {} Edges )\n".format(int(n) + one_deg_n, int(e) + one_deg_n)
    lines.append("\n")  # add a blank line to distinguish the extended lines information
    # parse topology
    topology = fnss.parse_brite(file_name).to_undirected()
    topology = largest_connected_component_subgraph(topology)
    # get node degree
    deg = nx.degree(topology)
    # change deg form [(node, degree)] to dict
    deg = dict(deg)
    # get number of nodes
    node_n = topology.number_of_nodes()
    # get max node id, max edge id and max as id
    max_node_id = max(topology.nodes())
    max_edge_id = int(lines[-2].split("\t")[0])
    max_as_n = topology.nodes[max_node_id].get("AS", 0)
    # print("max node id: {}, max edge id: {}, max as id: {}".format(max_node_id, max_edge_id, max_as_n))
    # ! >>> get node list in each AS group.
    # ! >>> The node has degree of the first 30% of the total nodes without bgn
    candidate_nodes = [v for v in topology.nodes() if topology.nodes[v]["type"] != "RT_BORDER"]
    candidate_nodes = sorted(candidate_nodes, key=lambda x: deg[x])
    candidate_list = [[] for _ in range(max_as_n + 1)]
    for v in candidate_nodes:
        candidate_list[topology.nodes[v].get("AS", 0)].append(v)
    # The first k entries from each group in candidate_list are taken equally to form a node list
    k = int(len(candidate_nodes) * sw_ratio) // (max_as_n + 1)
    node_list = []
    for i in range(max_as_n + 1):
        node_list.extend(candidate_list[i][:k])
    # print("node_list: {}".format(node_list))
    # get edge line, (insert row index is edge line - 1)
    edge_line = findEdgesLine(file_name) - 1
    for i in range(one_deg_n):
        new_node = max_node_id + 1 + i
        connect_node = random.choice(node_list)
        # print(connect_node, topology.nodes[connect_node])
        # construct new node line: NodeID, x, y, x-deg, y-deg, as_id
        new_node_line = str(new_node) + "\t" + str(random.randint(0, 1000)) + "\t" + str(
            random.randint(0, 1000)) + "\t" + "1" + "\t" + "1" + "\t" + str(
            topology.nodes[connect_node].get("AS", 0)) + "\t" + "RT_NODE" + "\n"
        lines.insert(edge_line - 1 + i, new_node_line)
        # construct new edge line: EdgeID, src, dst, distance, delay, capacity, from_as, to_as, type
        edge_id = max_edge_id + 1 + i
        from_as = to_as = topology.nodes[connect_node].get("AS", 0)
        new_edge_line = str(edge_id) + "\t" + str(new_node) + "\t" + str(connect_node) + "\t" + str(
            random.random() * 1000) + "\t" + str(0.5 + random.random() / 4) + "\t" + str(10.0) + "\t" + str(
            from_as) + "\t" + str(to_as) + "\t" + "E_RT" + "\t" + "U\n"
        lines.append(new_edge_line)

    # write to output file
    with open(out_file, 'w') as f:
        f.writelines(lines)


def check_layout_valid(layout_file: str, node_type_file: str, k: int):
    """
    Check the layout file is valid or not, if length of region set in switches is not k, return False.
    :param layout_file: (node, x, y, as_id, ctrl_id)
    :param node_type_file: line 3 represents the switches
    :param k: the number of regions
    :return: True or False
    """
    with open(node_type_file, 'r') as f:
        # skip 2 lines
        f.readline()
        f.readline()
        line = f.readline()
        if not line.startswith("switch"):
            raise ValueError("The third line of node type file should start with 'switch'")
        line = line.strip("switch: ").strip("\n[]")
        nodes = [int(v) for v in line.split(", ")]

    if not nodes:
        raise ValueError("'switch' is none in node type file")

    check_as_ctrl = defaultdict(set)
    with open(layout_file, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            node, x, y, as_id, ctrl_id = line.strip("\n").split(",")
            if int(node) in nodes:
                check_as_ctrl[int(as_id)].add(int(ctrl_id))

    total_ctrl = sum([len(v) for v in check_as_ctrl.values()])
    if total_ctrl != k * len(check_as_ctrl):
        print("[WARNING] Average regions ctrl number: {}, expected: {}; total number: {}, expected: {}".format(
            total_ctrl / len(check_as_ctrl), k, total_ctrl, k * len(check_as_ctrl)))
        return False
    return True


if __name__ == '__main__':
    RECV_RAT = 0.8  # The ratio of receiver nodes compared to source nodes
    SW_RAT = 0.8  # The ratio of switch candidates in all routers
    END_POINT_NUM = 7500  # The number of end points(source + receiver)
    CONTROLLER_NUM = 50  # The number of controllers in each AS
    path = "topology/seanrs_50x200/"  # brite file path
    # path = ""
    brite_file = path + "seanrs50x200.brite"
    extend_brite_file = path + "seanrs50x200_extend.brite"
    extent_brite_topo(brite_file, extend_brite_file, END_POINT_NUM, SW_RAT)
    topo_file = path + "topo50x200.txt"
    layout_file = path + "layout50x200.txt"
    node_type_file = path + "node_type50x200.txt"
    node_num, edges_num = getNodesAndEdgesNumber(extend_brite_file)
    dump_topology(extend_brite_file, topo_file, node_num, edges_num)  # Generate topology file
    dump_node_type(extend_brite_file, node_type_file, RECV_RAT)  # Generate node type file
    dump_axis_from_brite(extend_brite_file, node_type_file, layout_file, node_num,
                         CONTROLLER_NUM)  # Generate layout file
    print(">>> Check_layout_valid: ", check_layout_valid(layout_file, node_type_file, CONTROLLER_NUM))
