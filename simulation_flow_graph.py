#! /usr/bin/python3
# -*- encoding:utf-8 -*-
from pyecharts import options as opts
from pyecharts.charts import Graph
import numpy as np
import pandas as pd


def g_render(nodes, links, categories):
    c = (
        Graph(opts.InitOpts(width="1440px", height="720px", page_title="FlowGraph"))
            .add(
            "",
            nodes,
            links,
            categories=categories,
            repulsion=1000,
            is_draggable=True,
            # edge_label=opts.LabelOpts(
            #     is_show=True, position="middle", formatter="flow speed:{c} kpps"
            # ),
            edge_symbol="arrow",
            edge_symbol_size=5,
            # itemstyle_opts=opts.ItemStyleOpts(color="rgb(230,73,74)", border_color="rgb(255,148,149)", border_width=3)
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="Simulation_Flow_Graph")
        )
            .render("Simulation_Flow_Graph.html")
    )


def load_flow_data(file: str):
    flow_arr = np.loadtxt(file, delimiter=" ", dtype=int)
    return flow_arr


def load_topology_data(file: str):
    topo_arr = np.loadtxt(file, delimiter="\t", dtype=int, skiprows=1)
    return topo_arr


def dataHandler(flow_arr: np.ndarray, topo_arr: np.ndarray):
    """
    根据节点流数据和节点拓扑文件生成最终数据表
    数据表共7列数据，的格式为：
    [Node1 Node2 Category1 Category2 load_val1 load_val2 link_val]
    :param flow_arr: 节点的流数组
    :param topo_arr: 节点拓扑数组
    :return:  整合之后的数组
    """
    topo_arr = np.hstack((topo_arr, np.zeros((len(topo_arr), 3), dtype=int)))
    # 使用flow_arr中的每一行更新topo_arr
    for flow_line in flow_arr:
        for topo_line in topo_arr:
            if flow_line[0] == topo_line[0]:
                topo_line[4] = flow_line[2]
            if flow_line[1] == topo_line[1]:
                topo_line[5] = flow_line[3]
            if flow_line[0] == topo_line[0] and flow_line[1] == topo_line[1]:
                topo_line[6] = flow_line[4]
            if flow_line[0] == topo_line[1]:
                topo_line[5] = flow_line[2]
            if flow_line[1] == topo_line[0]:
                topo_line[4] = flow_line[3]
            if flow_line[0] == topo_line[1] and flow_line[1] == topo_line[0]:
                topo_line[6] = flow_line[4]

    return topo_arr


def run():
    flow_data = load_flow_data("flow_data.txt")
    topo_data = load_topology_data("community_small.txt")
    all_data = dataHandler(flow_data, topo_data)
    nodes_data = []
    links_data = []
    category_data = []
    nodes = {}
    # 创建节点
    for line in all_data:
        startNode, endNode, s_cat, e_cat, s_val, e_val, link_val = line
        nodes[startNode] = (s_val, s_cat)
        nodes[endNode] = (e_val, e_cat)
        # if startNode == 13:
        #     print(line)
    for key in nodes.keys():
        nodes_data.append(
            opts.GraphNode(name=str(key), symbol_size=20 + int(nodes[key][0]) * 10, value=str(nodes[key][0]),
                           category=int(nodes[key][1]-1),
                           label_opts=opts.LabelOpts(position="bottom", font_size=14, font_weight="bold")
                           )
        )
    # print(nodes)
    # 创建边
    for line in all_data:
        startNode, endNode, s_cat, e_cat, s_val, e_val, link_val = line
        # color_r = str(150 - link_val)
        # color = "rgb(" + color_r + "," + color_r + "," + color_r + ")"
        if int(link_val) == 0:
            links_data.append(
                opts.GraphLink(source=str(startNode), target=str(endNode), value=int(link_val),
                               linestyle_opts=opts.LineStyleOpts(width=1)
                               )
            )
        else:
            links_data.append(
                opts.GraphLink(source=str(startNode), target=str(endNode), value=int(link_val),
                               linestyle_opts=opts.LineStyleOpts(width=1 + int(link_val) * 2, type_="solid",
                                                                 color="orange"),
                               label_opts=opts.LabelOpts(is_show=True, position="middle", formatter="{c} kpps",
                                                         distance=1)
                               )
            )
    # 创建类别
    category_set = set(list(all_data[:, 2]) + list(all_data[:, 3]))
    for cate in category_set:
        print(cate)
        category_data.append(
            opts.GraphCategory(name="社区" + str(cate))
        )
    # 生成关系图
    g_render(nodes_data, links_data, category_data)


if __name__ == '__main__':
    run()
