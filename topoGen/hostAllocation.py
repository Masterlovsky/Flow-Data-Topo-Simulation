#! /usr/bin/python3
# -*- encoding:utf-8 -*-

def getHostIDs(totalNum: int) -> set:
    host_ids = set()
    input_str = input("Please input Host ID, option format:'1'/'1,2,3'/'1-3,5-6'\n")
    range_l = input_str.strip(",").strip(" ").split(",")
    for ran in range_l:
        ran = ran.strip()
        if "-" not in ran:
            if int(ran) > totalNum:
                raise ValueError("Error! Input number must lower than total node number<{}>".format(totalNum))
            host_ids.add(ran)
            continue
        start = ran.split("-")[0]
        end = ran.split("-")[1]
        for i in range(int(start), int(end) + 1):
            if int(i) > totalNum:
                raise ValueError("Error! Input number must lower than total node number<{}>".format(totalNum))
            host_ids.add(str(i))
    return host_ids


def getSwitchIDs(totalNum: int, hostids: set) -> set:
    switch_ids = set()
    for i in range(totalNum):
        if i not in hostids:
            switch_ids.add(str(i))
    return switch_ids


def getfirstLine(file_name: str) -> tuple:
    f = open(file_name, "r")
    nodes, lines = f.readline().strip().split(" ")
    return int(nodes), int(lines)


def writeToFile(file_name: str, host_ids: set, switch_ids: set):
    with open(file_name, "a") as f:
        f.write("host " + ",".join(host_ids) + "\n")
        f.write("switch " + ",".join(switch_ids) + "\n")


if __name__ == '__main__':
    topo_file = "test_topo.txt"
    n_num, l_num = getfirstLine(topo_file)
    hostids = getHostIDs(n_num)
    switchids = getSwitchIDs(n_num, hostids)
    writeToFile(topo_file, hostids, switchids)
    print("Host and switch generate success!")
