#! /usr/bin/python3
# -*- encoding:utf-8 -*-
import random

import pandas as pd
import re
from sklearn.cluster import KMeans
import networkx as nx
import fnss


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


def dump_axies_from_brite(file_name: str, out_file: str, node_n: int, cluster_n: int):
    """
    Get axies information from brite file
    :param cluster_n: controller number in each AS
    :param file_name: input brite file name
    :param out_file: output file name (layout file)
    :param node_n: total node number
    """
    # create and clear output file
    with open(out_file, 'w') as f:
        f.write("")
    node_line = findNodeLine(file_name)
    # line describe: NodeID, x, y, in_degree, out_degree, as_id, type
    header = ["NodeID", "x", "y", "in_degree", "out_degree", "as_id", "type"]
    df = pd.read_csv(file_name, skiprows=node_line, sep="\t", nrows=int(node_n), names=header)
    # get x and y axies, zip to list, group by as_id
    axies = df[["NodeID", "x", "y"]].copy()
    # get total as number
    as_n = df["as_id"].max() + 1
    for i in range(as_n):
        # get axies of each AS
        axies_of_as = df[df["as_id"] == i][["NodeID", "x", "y"]].copy()
        # cluster axies of each AS
        kmeans = KMeans(n_clusters=cluster_n, random_state=0).fit(axies_of_as)
        # get cluster center
        cluster_center = kmeans.cluster_centers_
        # get cluster label
        axies_of_as["ctrl_area"] = kmeans.labels_
        # dump axies to output file
        axies_of_as.to_csv(out_file, sep=",", index=False, header=False, mode="a")

    print("Dump axies from brite file success! output file: {}".format(out_file))


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

    print("Dump node type from brite file success! output file: {}".format(out_file))


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
    df = pd.read_csv(input_file, skiprows=edge_line, sep="\t", skipinitialspace=True, header=None)
    # format: edge_id, from_node, to_node, len, delay, capacity, from_as, to_as, type
    df[[6, 7]] += 1
    df = pd.DataFrame(df[[1, 2, 6, 7]])
    with open(output_file, "w") as f:
        f.write(str(edge_n) + " " + str(edge_n) + "\n")
    df.to_csv(output_file, sep="\t", header=False, index=False, mode="a")
    print("Generate topo done! nodes: {} / edges: {}, output to {}".format(node_n, edge_n, output_file))


if __name__ == '__main__':
    input_file = "test_seanrs.brite"
    output_file = "test_topo.txt"
    out_layout_file = "test_layout.txt"
    out_node_type_file = "test_node_type.txt"
    startLine = findEdgesLine(input_file)
    node_num, edges_num = getNodesAndEdgesNumber(input_file)
    dump_topology(input_file, output_file, node_num, edges_num)  # Generate topology file
    dump_axies_from_brite(input_file, out_layout_file, node_num, 3)  # Generate layout file
    dump_node_type(input_file, out_node_type_file, 0.5)  # Generate node type file

