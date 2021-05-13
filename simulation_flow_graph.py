#! /usr/bin/python3
# -*- encoding:utf-8 -*-
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from pyecharts.charts import Graph
import numpy as np
import pandas as pd


def g_render(nodes, links, categories):
    c = (
        Graph(opts.InitOpts(width="1600px", height="950px", page_title="FlowGraph", theme=ThemeType.WHITE))
            .add(
            "",
            nodes,
            links,
            categories=categories,
            repulsion=300,
            is_draggable=True,
            # layout="circular",
            tooltip_opts=opts.TooltipOpts(formatter="ID:{b}, Load:{c}"),
            # edge_label=opts.LabelOpts(
            #     is_show=True, position="middle", formatter="flow speed:{c} kpps"
            # ),
            # edge_symbol=["circle", "arrow"],
            # edge_symbol_size=10,
            # itemstyle_opts=opts.ItemStyleOpts(color="rgb(230,73,74)", border_color="rgb(255,148,149)", border_width=3)
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="Simulation_Flow_Graph"),
            legend_opts=opts.LegendOpts(legend_icon="circle"),
            toolbox_opts=opts.ToolboxOpts(is_show=True, feature=opts.ToolBoxFeatureOpts()),
        )
            .render("Simulation_Flow_Graph.html")
    )


def load_flow_data(file: str):
    flow_arr = np.loadtxt(file, delimiter=" ", dtype=int)
    return flow_arr


def load_topology_data(file: str):
    topo_arr = np.loadtxt(file, delimiter="\t", dtype=int, skiprows=1)
    return topo_arr


def load_type_data(file: str) -> dict:
    nodes_type_dict = {}
    with open(file, 'r') as f:
        lines_list = f.readlines()
    if len(lines_list) != 4:
        raise ValueError("wrong format in node_type.txt file!")
    else:
        for index, line in enumerate(lines_list):
            nodes_list = line.strip().split(",")
            for node in nodes_list:
                nodes_type_dict[node] = index + 1
    return nodes_type_dict


def load_axis_to_dict(file: str) -> dict:
    node_axis_dict = {}
    _x = None
    _y = None
    with open(file, 'r') as f:
        lines_list = f.readlines()
    for index, line in enumerate(lines_list):
        nodes_list = line.strip().split(",")
        if len(nodes_list) != 3:
            continue
        _x, _y = float(nodes_list[1]), float(nodes_list[2])
        node_axis_dict[nodes_list[0]] = (_x, _y)
    return node_axis_dict


def dataHandler(flow_arr: np.ndarray, topo_arr: np.ndarray):
    """
    根据节点流数据和节点拓扑文件生成最终数据表
    数据表共7列数据，的格式为：
    [Node1 Node2 Community1 Category2 load_val1 load_val2 link_val]
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


def manual_set_node(key):
    if str(key) == "0":
        _is_fixed = True
        _x = 800
        _y = 100
    elif str(key) == "1":
        _is_fixed = True
        _x = 800
        _y = 150
    elif str(key) == "4":
        _is_fixed = True
        _x = 680
        _y = 376
    elif str(key) == "7":
        _is_fixed = True
        _x = 760
        _y = 376
    elif str(key) == "38":
        _is_fixed = True
        _x = 1000
        _y = 276
    elif str(key) == "40":
        _is_fixed = True
        _x = 900
        _y = 376
    elif str(key) == "44":
        _is_fixed = True
        _x = 1070
        _y = 376
    elif str(key) == "20":
        _is_fixed = True
        _x = 450
        _y = 636
    elif str(key) == "27":
        _is_fixed = True
        _x = 450
        _y = 536
    elif str(key) == "26":
        _is_fixed = True
        _x = 520
        _y = 470
    elif str(key) == "24":
        _is_fixed = True
        _x = 650
        _y = 536
    elif str(key) == "25":
        _is_fixed = True
        _x = 547
        _y = 670
    elif str(key) == "11":
        _is_fixed = True
        _x = 650
        _y = 893
    elif str(key) == "8":
        _is_fixed = True
        _x = 900
        _y = 893
    elif str(key) == "17":
        _is_fixed = True
        _x = 1150
        _y = 893
    elif str(key) == "9":
        _is_fixed = True
        _x = 750
        _y = 806
    elif str(key) == "15":
        _is_fixed = True
        _x = 1050
        _y = 806
    elif str(key) == "16":
        _is_fixed = True
        _x = 900
        _y = 750
    elif str(key) == "76":
        _is_fixed = True
        _x = 900
        _y = 636
    elif str(key) == "66":
        _is_fixed = True
        _x = 1237
        _y = 614
    elif str(key) == "57":
        _is_fixed = True
        _x = 1220
        _y = 582
    else:
        _is_fixed = False
        _x = None
        _y = None
    return _is_fixed, _x, _y
    # _is_fixed = False
    # _x = None
    # _y = None


def run():
    flow_data = load_flow_data("flow_data.txt")
    topo_data = load_topology_data("community_small.txt")
    type_data = load_type_data("node_type.txt")
    layout_data = load_axis_to_dict("layout.txt")
    all_data = dataHandler(flow_data, topo_data)
    nodes_data = []
    links_data = []
    category_data = []
    nodes = {}  # 存放所有节点的集合
    symbol_list = ["circle", "roundRect", "triangle", "rect", "diamond"]  # 分别代表普通节点,源节点，目的节点，叶节点，汇聚节点
    labels_tuple = ("源", "目的", "LN", "RP")
    # 创建节点 ===========================================================
    for line in all_data:
        startNode, endNode, s_cat, e_cat, s_val, e_val, link_val = line
        nodes[startNode] = (s_val, s_cat, type_data.get(str(startNode), 0))
        nodes[endNode] = (e_val, e_cat, type_data.get(str(endNode), 0))
    # print(nodes.keys())
    for key in nodes.keys():
        _name = str(key)
        _symbol_size = 12 + int(nodes[key][0]) * 3 if int(nodes[key][0]) else 10
        _x, _y = layout_data[str(key)]
        # 对特殊节点进行单独标识 ---------------------------------------
        if nodes[key][2] > 0:
            _formatter = labels_tuple[nodes[key][2] - 1] + ":{b},流量:{c}"
            _item_style_opts = opts.ItemStyleOpts(border_color="red", border_width=2)
            _label_opts = opts.LabelOpts(position="bottom", font_size=14, font_weight="bold", color="red",
                                         formatter=_formatter)
        # 普通节点标识 ------------------------------------------------
        else:
            _label_opts = opts.LabelOpts(position="bottom", font_size=12, font_weight="normal")
            _item_style_opts = None
            # _is_fixed = False
        # 添加节点
        # _is_fixed, _x, _y = manual_set_node(key)
        nodes_data.append(
            opts.GraphNode(name=_name,
                           x=_x,
                           y=_y,
                           symbol=str(symbol_list[nodes[key][2]]),
                           # symbol="image://pics/接入交换机.svg",
                           is_fixed=True,
                           symbol_size=_symbol_size,
                           value=str(nodes[key][0]),
                           category=int(nodes[key][1] - 1),
                           label_opts=_label_opts,
                           itemstyle_opts=_item_style_opts  # 如果没改源码需要把这行注释掉！
                           )
        )
    # 创建边 =============================================================
    for line in all_data:
        startNode, endNode, s_cat, e_cat, s_val, e_val, link_val = line
        # color_r = str(150 - link_val)
        # color = "rgb(" + color_r + "," + color_r + "," + color_r + ")"
        if int(link_val) == 0:
            links_data.append(
                opts.GraphLink(source=str(startNode), target=str(endNode), value=int(40 * link_val / 100),
                               linestyle_opts=opts.LineStyleOpts(width=0.5)
                               )
            )
        else:
            links_data.append(
                opts.GraphLink(source=str(startNode),
                               target=str(endNode),
                               value=int(link_val),
                               symbol=["none", "arrow"],
                               symbol_size=10 + int(link_val),
                               linestyle_opts=opts.LineStyleOpts(width=3 + 4 * link_val / 100, type_="solid",
                                                                 color="orange"),
                               label_opts=opts.LabelOpts(is_show=True, position="middle",
                                                         formatter=str(startNode) + " => " + str(
                                                             endNode) + " load: {c}",
                                                         distance=1,
                                                         horizontal_align="center"
                                                         )
                               )
            )
    # 创建类别 ===========================================================
    category_set = set(list(all_data[:, 2]) + list(all_data[:, 3]))
    for cate in category_set:
        category_data.append(
            opts.GraphCategory(name="社区" + str(cate))
        )
    # 生成关系图
    g_render(nodes_data, links_data, category_data)


if __name__ == '__main__':
    run()
    print("done!")
#   定时10s刷新html页面
#   <meta http-equiv="Refresh" content="10"/>
