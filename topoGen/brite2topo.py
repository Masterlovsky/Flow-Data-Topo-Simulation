import pandas as pd
import re


def findEdgesLine(file_name: str) -> int:
    with open(file_name, 'r') as f:
        index = 0
        while not f.readline().startswith("Edges"):
            index += 1
    return index + 1


def getNodesAndEdgesNumber(file_name: str) -> tuple:
    with open(file_name, 'r') as f:
        first_line = f.readline()
        if not first_line.startswith("Topology"):
            print("Get Nodes and Edges Number Error! Unknown format")
            return 0, 0
        numbers = re.findall("\d+", first_line)
        return numbers[0], numbers[1]


if __name__ == '__main__':
    input_file = "test.brite"
    output_file = "test_topo.txt"
    startLine = findEdgesLine(input_file)
    node_num, edges_num = getNodesAndEdgesNumber(input_file)
    df = pd.read_csv(input_file, skiprows=startLine, sep="\t", skipinitialspace=True, header=None,
                     index_col=0)
    if df.loc[0, 6] == -1:
        df[6] = 1
    if df.loc[0, 7] == -1:
        df[7] = 1
    df = pd.DataFrame(df[[1, 2, 6, 7]])
    with open(output_file, "w") as f:
        f.write(node_num + " " + edges_num + "\n")
    df.to_csv(output_file, sep="\t", header=False, index=False, mode="a")
    print("Generate topo done! nodes: {} / edges: {}".format(node_num, edges_num))
