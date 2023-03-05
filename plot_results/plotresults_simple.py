import os
import argparse
import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Logger object
logger = logging.getLogger("plot")
sns.set_context("paper", font_scale=1.5)


def plot_mean_delay_chart(df, xlabel, ylabel, title, output, show=True):
    sns.set_style("whitegrid")
    fig, ax = plt.subplots()
    ax.grid(linestyle="--")
    x, y1, y2, y3, z3 = df["nodes"], df[0.65], df[0.75], df[0.85], df["0.85.1"]
    # ax.plot(x, y1, label="DINNRS α=0.65", color="b", marker="o", markersize=8)
    # ax.plot(x, y2, label="DINNRS α=0.75", color="g", marker="^", markersize=8)
    ax.plot(x, y3, label="DINNRS α=0.85", color="r", marker=">", markersize=8)
    ax.plot(x, z3, label="MDHT α=0.85", color="b", marker="X", markersize=8)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_title(title)
    ax.legend()
    fig.savefig(output)
    if show:
        plt.show()


def plot_load_rate_chart(df, xlabel, ylabel, title, output, show=True):
    sns.set_style("whitegrid")
    fig, ax = plt.subplots()
    ax.grid(linestyle="--")
    x, y1, y2 = df["rate"], df["total"], df["total.1"]
    # y use scientific notation
    ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
    ax.plot(x, y1, label="DINNRS α=0.85", color="r", marker="o", markersize=8)
    ax.plot(x, y2, label="MDHT α=0.85", color="b", marker="^", markersize=8)
    # ax.plot(x, y3, label="DINNRS α=0.85", color="r", marker=">", markersize=8)
    # ax.plot(x, z3, label="MDHT α=0.85", color="b", marker="X", markersize=8)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_title(title)
    ax.legend()
    fig.savefig(output)
    if show:
        plt.show()


def plot_internal_ratio(df, xlabel, ylabel, title, output, show=True):
    sns.set_style("whitegrid")
    fig, ax = plt.subplots()
    ax.grid(linestyle="--")
    x, y1, y2 = df["rate"], df["internal-ratio"], df["internal-ratio.1"]
    # y use scientific notation
    # ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
    ax.plot(x, y1, label="DINNRS α=0.85", color="r", marker="o", markersize=8)
    ax.plot(x, y2, label="MDHT α=0.85", color="b", marker="^", markersize=8)
    # ax.plot(x, y3, label="DINNRS α=0.85", color="r", marker=">", markersize=8)
    # ax.plot(x, z3, label="MDHT α=0.85", color="b", marker="X", markersize=8)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_title(title)
    ax.legend()
    fig.savefig(output)
    if show:
        plt.show()


def plot_bar_chart(data, title, output, show=True):
    sns.set_style("white")
    # x_labels = ["Control", "Management", "Intermediary"]
    x_labels = ["level-1", "level-2", "level-3"]
    fig, ax = plt.subplots()
    # set figure size
    fig.set_size_inches(8, 6)
    x = [1, 2, 3]
    y = data
    ax.grid(linestyle="--", axis="y")
    ax.bar(x, y, width=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("Domain type", fontsize=14)
    ax.set_ylabel("Resolve numbers in domains", fontsize=14)
    ax.set_title(title)
    fig.savefig(output)
    if show:
        plt.show()


def run(input_file, output_path):
    # name = "mean_delay.pdf"
    logger.info("Reading results from %s", input_file)
    #  ========= plot mean delay line chart =========
    # input a xlsx file, read from excel to pandas dataframe
    # df = pd.read_excel(input_file, sheet_name="delay", skiprows=1, dtype="float")
    # plot_mean_delay_chart(df, "Node number", "delay(ms)", "", output_path + "/mean_delay.pdf")
    #  ========= plot bar chart =========
    data = [9917, 8968, 4516]  # DINNRS
    plot_bar_chart(data, "", output_path + "/DINNRS-domain-hit.pdf")
    # data = [89, 513, 4498]  # MDHT
    # plot_bar_chart(data, "", output_path + "/MDHT-level-hit.pdf")
    # ========== plot load-rate line chart =========
    # df = pd.read_excel(input_file, sheet_name="load", skiprows=1, dtype="float")
    # plot_load_rate_chart(df, "Request rate(/s)", "Average link load (KB)", "",
    #                      output_path + "/load_rate.pdf")
    # # ========== plot internal ratio chart =========
    # df = pd.read_excel(input_file, sheet_name="load", skiprows=1, dtype="float")
    # plot_internal_ratio(df, "Request rate(/s)", "Internal ratio", "",
    #                     output_path + "/internal_ratio.pdf")


def main():
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True, help="input file")
    parser.add_argument("-o", "--output", type=str, required=True, help="output path")
    args = parser.parse_args()
    run(args.input, args.output)


if __name__ == '__main__':
    main()
