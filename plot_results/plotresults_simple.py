import collections
import math
import os
import argparse
import logging
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Logger object
logger = logging.getLogger("plot")
sns.set_context("paper", font_scale=1.25)
# set font family
# sns.set(font="Arial")
# sns.set_style("whitegrid")
sns.set_style("ticks")
# sns.set_palette("pastel")
sns.set_palette("Set2")
# sns.set_palette("Blues")
MARKER_BASE = ["o", "^", "X", "s", "p", "P", ">", "*", "h", "H", "D", "d", "v", "<", "8", "x", "+",
               "|", "_", "."]
COLOR_BASE = ["r", "b", "g", "c", "m", "y", "k", "#FFA500", "#FFC0CB", "#FFD700", "#FF00FF", "#FF1493", "#FF4500", ]
HATCH_BASE = ["", "//", "XX", "++", "\\\\", "-", "||", "o", "O", ".", "*"]


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


def get_seq_hit_ratio(doc):
    seq_hit_ratio_pattern = r"\* SEQ_HIT_RATIO: \[(.*)\]"
    seq_hit_ratio_match = re.search(seq_hit_ratio_pattern, doc)
    if seq_hit_ratio_match:
        seq_hit_ratio_str = seq_hit_ratio_match.group(1)
        seq_hit_ratio = eval(seq_hit_ratio_str)
        return seq_hit_ratio
    else:
        print("No SEQ_HIT_RATIO data found in doc")


def get_avg_cache_hit_ratio(doc):
    avg_chr_pattern = r"MEAN: .*"
    avg_chr_match = re.search(avg_chr_pattern, doc)
    if avg_chr_match:
        avg_chr_str = avg_chr_match.group(0).split(":")[1].strip()
        avg_chr = eval(avg_chr_str)
        return avg_chr
    else:
        print("No average Cache hit ratio found in doc")


class P1(object):
    def __init__(self, input_path, out_path):
        self.input_path = input_path
        self.out_path = out_path
        self.df = pd.read_csv(self.input_path, header=0, index_col=None)
        # Remove leading and trailing spaces from each field in the header.
        self.df.columns = self.df.columns.str.strip()

    def plot_link_load_rate_line_chart(self, title=""):
        REQ_PKT_SIZE = 150
        fig, ax = plt.subplots()
        # set resolution to 300 dpi
        fig.set_dpi(300)
        ax.grid(linestyle="--")
        # use sci format, fonts and size
        ax.ticklabel_format(style="sci", scilimits=(-2, 2))
        ax.tick_params(labelsize=12)
        # sieve out the data from dataframe, alpha=0.85, cache=10.0
        df = self.df[(self.df["alpha"] == 0.85) & (self.df["cache"] == 0.1)]
        x = df["rate"].sort_values(ascending=True).unique()
        i = 0
        for wl_name in ("LEVEL_PROBABILITY", "STATIONARY"):
            for strategy in ("SEANRS", "MDHT"):
                line_style = "--" if strategy == "SEANRS" else "-"
                if wl_name == "LEVEL_PROBABILITY":
                    temp = df[(df["workload_name"] == wl_name) & (df["strategy"] == strategy) & (df["lp"] == 0.7)]
                    y = (temp["intra_link_load"] + temp["inter_link_load"]) * REQ_PKT_SIZE
                    ax.plot(x, y,
                            label="{}_{}={}".format("DINNRS" if strategy == "SEANRS" else "MDHT",
                                                    "LP" if wl_name == "LEVEL_PROBABILITY" else "ST",
                                                    0.7),
                            color=COLOR_BASE[i], marker=MARKER_BASE[i], markersize=8, linestyle=line_style)
                    i += 1
                else:
                    temp = df[(df["workload_name"] == wl_name) & (df["strategy"] == strategy)]
                    y = (temp["intra_link_load"] + temp["inter_link_load"]) * REQ_PKT_SIZE
                    ax.plot(x, y,
                            label="{}_{}".format("DINNRS" if strategy == "SEANRS" else "MDHT",
                                                 "LP" if wl_name == "LEVEL_PROBABILITY" else "ST"),
                            color=COLOR_BASE[i], marker=MARKER_BASE[i], markersize=8, linestyle=line_style)
                    i += 1
        # y use scientific notation
        ax.set_xlabel("Request rate", fontsize=16)
        ax.set_ylabel("Average link load", fontsize=16)
        ax.set_title(title, fontsize=16)
        # legend can't obstruct the image
        ax.legend()
        fig.savefig(self.out_path + "/link_load_rate_new.pdf")
        plt.show()

    def plot_intra_ratio_line_chart(self, title=""):
        fig, ax = plt.subplots()
        # set resolution to 300 dpi
        fig.set_dpi(300)
        ax.grid(linestyle="--")
        # use sci format, fonts and size
        ax.ticklabel_format(style="sci", scilimits=(-2, 2))
        ax.tick_params(labelsize=12)
        # sieve out the data from dataframe, alpha=0.85, cache=10.0
        df = self.df[(self.df["alpha"] == 0.85) & (self.df["cache"] == 0.1)]
        x = df["rate"].sort_values(ascending=True).unique()
        i = 0
        for wl_name in ("LEVEL_PROBABILITY", "STATIONARY"):
            for strategy in ("SEANRS", "MDHT"):
                line_style = "--" if strategy == "SEANRS" else "-"
                if wl_name == "LEVEL_PROBABILITY":
                    temp = df[(df["workload_name"] == wl_name) & (df["strategy"] == strategy) & (df["lp"] == 0.7)]
                    y = temp["intra_link_load"] / (temp["intra_link_load"] + temp["inter_link_load"])
                    ax.plot(x, y,
                            label="{}_{}={}".format("DINNRS" if strategy == "SEANRS" else "MDHT",
                                                    "LP" if wl_name == "LEVEL_PROBABILITY" else "ST",
                                                    0.7),
                            color=COLOR_BASE[i], marker=MARKER_BASE[i], markersize=8, linestyle=line_style)
                    i += 1
                else:
                    temp = df[(df["workload_name"] == wl_name) & (df["strategy"] == strategy)]
                    y = temp["intra_link_load"] / (temp["intra_link_load"] + temp["inter_link_load"])
                    ax.plot(x, y,
                            label="{}_{}".format("DINNRS" if strategy == "SEANRS" else "MDHT",
                                                 "LP" if wl_name == "LEVEL_PROBABILITY" else "ST"),
                            color=COLOR_BASE[i], marker=MARKER_BASE[i], markersize=8, linestyle=line_style)
                    i += 1
        # y use scientific notation
        ax.set_xlabel("Request rate", fontsize=16)
        ax.set_ylabel("Internal ratio", fontsize=16)
        ax.set_title(title, fontsize=16)
        # legend can't obstruct the image
        ax.legend()
        fig.savefig(self.out_path + "/internal_ratio_new.pdf")
        plt.show()

    def plot_cache_size_to_avg_latency_line_chart(self, title=""):
        fig, ax = plt.subplots()
        fig.set_dpi(300)
        ax.grid(linestyle="--")
        ax.ticklabel_format(style="sci", scilimits=(-2, 2))
        ax.tick_params(labelsize=12)
        # sieve out the data from dataframe, alpha=0.85, cache=10.0
        df = self.df[(self.df["alpha"] == 0.85) & (self.df["rate"] == 100000)]
        # plot DINNRS
        x = df[(df["lp"] == 0.7)]["cache"].unique() * 10 ** 4
        i = 0
        for strategy in ("SEANRS", "MDHT"):
            line_style = "--" if strategy == "SEANRS" else "-"
            for lp in (0.3, 0.7):
                y = df[(df["workload_name"] == "LEVEL_PROBABILITY") &
                       (df["lp"] == lp) &
                       (df["strategy"] == strategy)]["avg_latency"]
                ax.plot(x, y, label="{}_LP_{}".format("DINNRS" if strategy == "SEANRS" else "MDHT", lp),
                        color=COLOR_BASE[i], marker=MARKER_BASE[i], markersize=8, linestyle=line_style)
                i += 1
            y2 = df[(df["workload_name"] == "STATIONARY") & (df["strategy"] == strategy)]["avg_latency"]
            ax.plot(x, y2, label="{}_ST".format("DINNRS" if strategy == "SEANRS" else "MDHT"), color=COLOR_BASE[i],
                    marker=MARKER_BASE[i], markersize=8, linestyle=line_style)
            i += 1
        ax.set_xlabel("Cache size", fontsize=16)
        ax.set_ylabel("Average latency (ms)", fontsize=16)
        ax.set_title(title, fontsize=16)
        # legend can't obstruct the image
        ax.legend(bbox_to_anchor=(0.5, 1.17), loc="upper center", borderaxespad=0.5, ncol=3)
        fig.savefig(self.out_path + "/cache_size_avg_latency_new.pdf")
        plt.show()

    def plot_resolve_num_levels_bar_chart(self, title=""):
        fig, ax = plt.subplots()
        fig.set_dpi(300)
        ax.grid(linestyle="--", axis="y")
        ax.tick_params(labelsize=12)
        ax.ticklabel_format(style="sci", scilimits=(-2, 2))
        # sieve out the data from dataframe, alpha=0.85, cache=10.0
        df = self.df[(self.df["alpha"] == 0.85) & (self.df["rate"] == 100000) & (self.df["cache"] == 1)]
        x = ["level-1", "level-2", "level-3"]
        i = 0
        for strategy in ("SEANRS", "MDHT"):
            for wl_name in ("LEVEL_PROBABILITY", "STATIONARY"):
                if wl_name == "LEVEL_PROBABILITY":
                    df_n = df[df["lp"] == 0.7]
                    y1 = df_n[(df_n["strategy"] == strategy) & (df_n["workload_name"] == wl_name)]["resolve_ctrl"]
                    y2 = df_n[(df_n["strategy"] == strategy) & (df_n["workload_name"] == wl_name)]["resolve_ibgn"]
                    y3 = df_n[(df_n["strategy"] == strategy) & (df_n["workload_name"] == wl_name)]["resolve_ebgn"]
                else:
                    y1 = df[(df["strategy"] == strategy) & (df["workload_name"] == wl_name)]["resolve_ctrl"]
                    y2 = df[(df["strategy"] == strategy) & (df["workload_name"] == wl_name)]["resolve_ibgn"]
                    y3 = df[(df["strategy"] == strategy) & (df["workload_name"] == wl_name)]["resolve_ebgn"]

                y = [y1.values[0], y2.values[0], y3.values[0]]
                workload_name = "LP" if wl_name == "LEVEL_PROBABILITY" else "ST"
                ax.bar(np.arange(len(x)) + 0.2 * i, y, width=0.2,
                       label=f"DINNRS-{workload_name}" if strategy == "SEANRS" else f"MDHT-{workload_name}",
                       align="center", hatch=HATCH_BASE[i])
                # 设置x轴的刻度标签为x, 标记位置在x轴上居中
                ax.set_xticks(np.arange(len(x)) + 0.1 * i)
                ax.set_xticklabels(x)
                i += 1
        ax.set_xlabel("Domain type", fontsize=16)
        ax.set_ylabel("Resolve number in domains", fontsize=16)
        ax.set_title(title, fontsize=16)
        ax.legend()
        fig.savefig(self.out_path + "/resolve_num_levels_new.pdf")
        plt.show()


class P2(object):
    """
    Plot result in paper 2
    """

    def __init__(self, input_path, out_path):
        self.input_path = input_path
        self.out_path = out_path
        self.legend_map = {"LCE": "LCE", "popularity": "AC-POP", "random": "AC-RAND", "recommend": "AC-REC",
                           "group": "AC-OPT"}

    def plot_cache_hit_ratio_seq_line_chart(self, xlabel, ylabel, title="", show=True, date="0610"):
        fig, ax = plt.subplots()
        ax.grid(linestyle="--")
        # read file from path and get label from file name
        real_path = os.path.join(self.input_path, date)
        result_files = [os.path.join(real_path, k) for k in os.listdir(real_path)]

        print("result_files: {}".format(result_files))
        i = 0
        for file in result_files:
            label_name = os.path.basename(file).split(".")[0].split("_")[1]
            if label_name == "group" or label_name == "optimal":
                continue
            if label_name in self.legend_map:
                label_name = self.legend_map[label_name]
            with open(file, "r") as f:
                sr = get_seq_hit_ratio(f.read())
                df = pd.DataFrame(sr, columns=["time", "hit_ratio"])
                x = df["time"][::5]
                y = df["hit_ratio"][::5]
                # y use scientific notation
                ax.ticklabel_format(style="sci", axis="y", scilimits=(-2, 2))
                ax.plot(x, y, label=label_name, color=COLOR_BASE[i], marker=MARKER_BASE[i], markersize=5)
            i += 1

        ax.legend()
        ax.set_title(title)
        ax.set_xlabel(xlabel, fontsize=14)
        ax.set_ylabel(ylabel, fontsize=14)
        fig.savefig(self.out_path + "/cache_hit_ratio_seq_{}.pdf".format(date))
        if show:
            plt.show()

    def plot_data_to_avg_CHR_bar_group_chart(self, title="", show=True):
        """
        Plot average cache hit ratio bar chart, x-axis is date, y-axis is average cache hit ratio,
        each bar is a group of four bars, each bar is a different algorithm
        """
        sns.set_palette("Set3")
        date_list = os.listdir(self.input_path)
        method_f_l = os.listdir(os.path.join(self.input_path, date_list[0]))
        res = collections.defaultdict(dict)
        for date in date_list:
            for method_f in method_f_l:
                method = os.path.basename(method_f).split(".")[0].split("_")[1]
                if method == "optimal":
                    continue
                if method in self.legend_map:
                    method = self.legend_map[method]
                with open(os.path.join(self.input_path, date, method_f), "r") as f:
                    avg_chr = get_avg_cache_hit_ratio(f.read())
                    res[date][method] = avg_chr

        # draw bar chart
        fig, ax = plt.subplots()
        ax.grid(linestyle="--")
        x = np.arange(len(date_list))
        width = 0.15
        i = 0
        for method in res[date_list[0]]:
            y = [res[date][method] for date in date_list]
            if method == "AC-OPT":
                # fill in blank
                ax.bar(x + width * i, y, width=width, label=method, hatch="///")
            else:
                ax.bar(x + width * i, y, width=width, label=method)
            i += 1
        ax.set_xticks(x + width * 2)
        ax.set_xticklabels(date_list)
        ax.set_xlabel("Date", fontsize=14)
        ax.set_ylabel("Average cache hit ratio", fontsize=14)
        ax.set_title(title)
        ax.legend()
        fig.savefig(self.out_path + "/avg_cache_hit_ratio_bar.pdf")
        if show:
            plt.show()

    def plot_alpha_to_CHR_bar_chart_multi_file(self, title="", show=True):
        sns.set_palette("Set2")
        fig, ax = plt.subplots()
        ax.grid(linestyle="--")
        path = self.input_path + "/alpha"
        file_list = os.listdir(path)
        res = collections.defaultdict(dict)
        for file in file_list:
            method = os.path.basename(file).split(".")[0].split("_")[1]
            alpha = eval(os.path.basename(file).split("_")[2].replace(".txt", ""))
            # plot bar group chart, x-axis is alpha, y-axis is average cache hit ratio, each bar is a different algorithm
            with open(os.path.join(path, file), "r") as f:
                avg_chr = get_avg_cache_hit_ratio(f.read())
                # print("method: {}, alpha: {}, avg_chr: {}".format(method, alpha, avg_chr))
                res[alpha][method] = avg_chr

        alpha_list = list(res.keys())
        x = np.arange(len(res))
        width = 0.15
        i = 0
        for method in res[list(res.keys())[0]]:
            y = [res[alpha][method] for alpha in alpha_list]
            ax.bar(x + width * i, y, width=width, label=method)
            i += 1

        ax.set_xticks(x + width * 1)
        ax.set_xticklabels(alpha_list)
        ax.set_xlabel("Alpha", fontsize=14)
        ax.set_ylabel("Average cache hit ratio", fontsize=14)
        ax.set_title(title)
        ax.legend()
        fig.savefig(self.out_path + "/alpha_to_avg_CHR_bar.pdf")
        if show:
            plt.show()

    def plot_alpha_to_avg_CHR_bar_chart(self, title="", show=True):
        fig, ax1 = plt.subplots()
        ax1.grid(linestyle="--")
        path = self.input_path + "/alpha"
        csvfile = os.path.join(path, "v_alpha_10x.csv")
        res = collections.defaultdict(dict)
        df = pd.read_csv(csvfile, header=0, index_col=None)
        # change methods name
        df["methods"] = df["methods"].apply(lambda x: self.legend_map[x])
        # draw bar chart, each bar is a different algorithm with different alpha, error bar only show the top
        b = sns.barplot(x="alpha", y="CHR", hue="methods", data=df, ax=ax1, errwidth=1, capsize=0.1,
                        errorbar=("ci", 90))
        # Set a different hatch for each alpha
        alpha_len = len(df["alpha"].unique())
        for i, bar in enumerate(b.patches):
            bar.set_hatch(HATCH_BASE[i // alpha_len])
        ax1.legend(bbox_to_anchor=(0.5, 1.1), loc="upper center", borderaxespad=0.0, ncol=df["methods"].nunique())
        ax1.set_xlabel("Alpha", fontsize=14, labelpad=0)
        ax1.set_ylabel("Average cache hit ratio", fontsize=14)
        ax1.set_title(title)
        fig.savefig(self.out_path + "/alpha_to_avg_CHR_bar.pdf")
        if show:
            plt.show()

    def plot_alpha_to_free_space_bar_chart(self, title="", show=True):
        fig, ax1 = plt.subplots()
        ax1.grid(linestyle="--")
        path = self.input_path + "/alpha"
        csvfile = os.path.join(path, "v_alpha_10x.csv")
        res = collections.defaultdict(dict)
        df = pd.read_csv(csvfile, header=0, index_col=None)
        # change methods name
        df["methods"] = df["methods"].apply(lambda x: self.legend_map[x])
        # use seaborn to draw bar chart, each bar is a different algorithm with different alpha,
        b = sns.barplot(x="alpha", y="free_space", hue="methods", data=df, ax=ax1, errwidth=1, capsize=0.1,
                        errorbar=("ci", 90))
        # Set a different hatch for each alpha
        alpha_len = len(df["alpha"].unique())
        for i, bar in enumerate(b.patches):
            bar.set_hatch(HATCH_BASE[i // alpha_len])
        ax1.legend(bbox_to_anchor=(0.5, 1.1), loc="upper center", borderaxespad=0.0, ncol=df["methods"].nunique())
        ax1.set_xlabel("Alpha", fontsize=14)
        ax1.set_ylabel("Space remaining ratio", fontsize=14)
        ax1.set_title(title)
        fig.savefig(self.out_path + "/alpha_to_avg_space_bar.pdf")
        if show:
            plt.show()

    def plot_alpha_mix_bar_chart(self, title="", show=True, in_f="v_alpha_main.csv", out_f="alpha_mix_bar.pdf"):
        """
        plot alpha to average cache hit ratio and average space remaining ratio bar chart in one figure
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        ax1.grid(linestyle="--")
        ax2.grid(linestyle="--")
        path = self.input_path + "/alpha"
        csvfile = os.path.join(path, in_f)
        res = collections.defaultdict(dict)
        df = pd.read_csv(csvfile, header=0, index_col=None)
        # change methods name
        df["methods"] = df["methods"].apply(lambda x: self.legend_map[x])
        df["used_space"] = 1 - df["free_space"]
        # use seaborn to draw bar chart, each bar is a different algorithm with different alpha,
        # Use the same single x-axis, flip the second y-axis top to bottom
        b1 = sns.barplot(x="alpha", y="CHR", hue="methods", data=df, ax=ax1, errwidth=1, capsize=0.1,
                         errorbar=("ci", 90))
        b2 = sns.barplot(x="alpha", y="used_space", hue="methods", data=df, ax=ax2, errwidth=1, capsize=0.1,
                         errorbar=("ci", 90))
        # Set a different hatch for each alpha
        alpha_len = len(df["alpha"].unique())
        for i, bar in enumerate(b1.patches):
            bar.set_hatch(HATCH_BASE[i // alpha_len])
        for i, bar in enumerate(b2.patches):
            bar.set_hatch(HATCH_BASE[i // alpha_len])
        # x-axis label and x-axis tick label should be in the middle of two subplots
        ax2.set_xlabel("Alpha", fontsize=16, labelpad=5)
        ax2.tick_params(axis="x", pad=1)
        ax1.set_xlabel("")
        ax2.xaxis.set_ticks_position("top")
        ax2.invert_yaxis()
        ax1.legend(bbox_to_anchor=(0.5, 1.2), loc="upper center", borderaxespad=0.0, ncol=df["methods"].nunique())
        # ax2.legend(bbox_to_anchor=(0.5, -0.05), loc="upper center", borderaxespad=0.0, ncol=df["methods"].nunique())
        ax2.legend().set_visible(False)
        ax1.set_ylabel("Average CHR", fontsize=16)
        ax2.set_ylabel("Space occupied", fontsize=16)
        ax1.set_title(title)
        fig.savefig(os.path.join(self.out_path, out_f))
        if show:
            plt.show()

    def plot_t0_to_avg_CHR_bar_chart(self, title="", show=True):
        fig, ax1 = plt.subplots()
        ax1.grid(linestyle="--")
        path = self.input_path + "/t0"
        csvfile = os.path.join(path, "v_t0_10x.csv")
        res = collections.defaultdict(dict)
        df = pd.read_csv(csvfile, header=0, index_col=None)
        # change methods name
        df["methods"] = df["methods"].apply(lambda x: self.legend_map[x])
        # use seaborn to draw line chart, smooth line
        b = sns.barplot(x="alpha", y="CHR", hue="methods", data=df, ax=ax1, errwidth=1, capsize=0.1,
                        errorbar=("ci", 90))
        t0_len = len(df["alpha"].unique())
        for i, bar in enumerate(b.patches):
            bar.set_hatch(HATCH_BASE[i // t0_len])
        # put legend outside the plot, tile on top of the graph
        # plt.legend(bbox_to_anchor=(0.5, 1.1), loc="upper center", borderaxespad=0.0, ncol=df["methods"].nunique())
        ax1.set_xlabel("T0", fontsize=14)
        ax1.set_ylabel("Average cache hit ratio", fontsize=14)
        ax1.set_title(title)
        fig.savefig(self.out_path + "/t0_to_avg_CHR_bar.pdf")
        if show:
            plt.show()

    def plot_t0_to_free_space_bar_chart(self, title="", show=True):
        fig, ax1 = plt.subplots()
        ax1.grid(linestyle="--")
        path = self.input_path + "/t0"
        csvfile = os.path.join(path, "v_t0_10x.csv")
        res = collections.defaultdict(dict)
        df = pd.read_csv(csvfile, header=0, index_col=None)
        # change methods name
        df["methods"] = df["methods"].apply(lambda x: self.legend_map[x])
        # use seaborn to draw line chart, smooth line
        b = sns.barplot(x="alpha", y="free_space", hue="methods", data=df, ax=ax1, errwidth=1, capsize=0.1,
                        errorbar=("ci", 90))
        t0_len = len(df["alpha"].unique())
        for i, bar in enumerate(b.patches):
            bar.set_hatch(HATCH_BASE[i // t0_len])
        # put legend outside the plot, tile on top of the graph
        plt.legend(bbox_to_anchor=(0.5, 1.1), loc="upper center", borderaxespad=0.0, ncol=df["methods"].nunique())
        ax1.set_xlabel("T0", fontsize=14)
        ax1.set_ylabel("Space remaining ratio", fontsize=14)
        ax1.set_title(title)
        fig.savefig(self.out_path + "/t0_to_avg_space_bar.pdf")
        if show:
            plt.show()

    def plot_t0_mix_bar_chart(self, title="", show=True, in_f="v_t0_main.csv", out_f="t0_mix_bar.pdf"):
        """
        plot t0 to average cache hit ratio and average space remaining ratio bar chart in one figure
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        ax1.grid(linestyle="--")
        ax2.grid(linestyle="--")
        path = self.input_path + "/t0"
        csvfile = os.path.join(path, in_f)
        res = collections.defaultdict(dict)
        df = pd.read_csv(csvfile, header=0, index_col=None)
        # change methods name
        df["methods"] = df["methods"].apply(lambda x: self.legend_map[x])
        df["used_space"] = 1 - df["free_space"]
        # use seaborn to draw bar chart, each bar is a different algorithm with different alpha,
        # Use the same single x-axis, flip the second y-axis top to bottom
        b1 = sns.barplot(x="alpha", y="CHR", hue="methods", data=df, ax=ax1, errwidth=1, capsize=0.1,
                         errorbar=("ci", 90))
        b2 = sns.barplot(x="alpha", y="used_space", hue="methods", data=df, ax=ax2, errwidth=1, capsize=0.1,
                         errorbar=("ci", 90))
        alpha_len = len(df["alpha"].unique())
        for i, bar in enumerate(b1.patches):
            bar.set_hatch(HATCH_BASE[i // alpha_len])
        for i, bar in enumerate(b2.patches):
            bar.set_hatch(HATCH_BASE[i // alpha_len])
        # x-axis label and x-axis tick label should be in the middle of two subplots
        ax2.set_xlabel("Default time-to-live ${t0}$", fontsize=16, labelpad=5)
        ax2.tick_params(axis="x", pad=1)
        ax1.set_xlabel("")
        ax2.xaxis.set_ticks_position("top")
        ax2.invert_yaxis()
        ax1.legend(bbox_to_anchor=(0.5, 1.2), loc="upper center", borderaxespad=0.0, ncol=df["methods"].nunique())
        # ax2.legend(bbox_to_anchor=(0.5, -0.05), loc="upper center", borderaxespad=0.0, ncol=df["methods"].nunique())
        ax2.legend().set_visible(False)
        ax1.set_ylabel("Average CHR", fontsize=16)
        ax2.set_ylabel("Space occupied", fontsize=16)
        ax1.set_title(title)
        fig.savefig(os.path.join(self.out_path, out_f))
        if show:
            plt.show()

    def plot_k_to_avg_CHR_bar_chart(self, title="", show=True):
        fig, ax1 = plt.subplots()
        ax1.grid(linestyle="--")
        path = self.input_path + "/k"
        csvfile = os.path.join(path, "v_k_10x.csv")
        res = collections.defaultdict(dict)
        df = pd.read_csv(csvfile, header=0, index_col=None)
        # change methods name
        df["methods"] = df["methods"].apply(lambda x: self.legend_map[x])
        # use seaborn to draw line chart, smooth line
        b = sns.barplot(x="alpha", y="CHR", hue="methods", data=df, ax=ax1, errwidth=1, capsize=0.1,
                        errorbar=("ci", 90))
        alpha_len = len(df["alpha"].unique())
        for i, bar in enumerate(b.patches):
            bar.set_hatch(HATCH_BASE[i // alpha_len])
        # put legend outside the plot, tile on top of the graph
        plt.legend(bbox_to_anchor=(0.5, 1.1), loc="upper center", borderaxespad=0.0, ncol=df["methods"].nunique())
        ax1.set_xlabel("Recommended candidate set size", fontsize=14)
        ax1.set_ylabel("Average cache hit ratio", fontsize=14)
        ax1.set_title(title)
        fig.savefig(self.out_path + "/k_to_avg_CHR_bar.pdf")
        if show:
            plt.show()

    def plot_k_to_free_space_bar_chart(self, title="", show=True):
        fig, ax1 = plt.subplots()
        ax1.grid(linestyle="--")
        path = self.input_path + "/k"
        csvfile = os.path.join(path, "v_k_10x.csv")
        res = collections.defaultdict(dict)
        df = pd.read_csv(csvfile, header=0, index_col=None)
        # change methods name
        df["methods"] = df["methods"].apply(lambda x: self.legend_map[x])
        # use seaborn to draw line chart, smooth line
        b = sns.barplot(x="alpha", y="free_space", hue="methods", data=df, ax=ax1, errwidth=1, capsize=0.1,
                        errorbar=("ci", 90))
        alpha_len = len(df["alpha"].unique())
        for i, bar in enumerate(b.patches):
            bar.set_hatch(HATCH_BASE[i // alpha_len])
        # put legend outside the plot, tile on top of the graph
        plt.legend(bbox_to_anchor=(0.5, 1.1), loc="upper center", borderaxespad=0.0, ncol=df["methods"].nunique())
        ax1.set_xlabel("Recommended candidate set size", fontsize=14)
        ax1.set_ylabel("Space remaining ratio", fontsize=14)
        ax1.set_title(title)
        fig.savefig(self.out_path + "/k_to_avg_space_bar.pdf")
        if show:
            plt.show()

    def plot_k_mix_bar_chart(self, title="", show=True, in_f="v_k_main.csv", out_f="k_mix_bar.pdf"):
        """
        plot k to average cache hit ratio and average space remaining ratio bar chart in one figure
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        ax1.grid(linestyle="--")
        ax2.grid(linestyle="--")
        path = self.input_path + "/k"
        csvfile = os.path.join(path, in_f)
        res = collections.defaultdict(dict)
        df = pd.read_csv(csvfile, header=0, index_col=None)
        # change methods name
        df["methods"] = df["methods"].apply(lambda x: self.legend_map[x])
        df["used_space"] = 1 - df["free_space"]
        # use seaborn to draw bar chart, each bar is a different algorithm with different alpha,
        # Use the same single x-axis, flip the second y-axis top to bottom
        bar1 = sns.barplot(x="alpha", y="CHR", hue="methods", data=df, ax=ax1, errwidth=1, capsize=0.1,
                           errorbar=("ci", 90))
        bar2 = sns.barplot(x="alpha", y="used_space", hue="methods", data=df, ax=ax2, errwidth=1, capsize=0.1,
                           errorbar=("ci", 90))
        # Set a different hatch for each alpha
        alpha_len = len(df["alpha"].unique())
        for i, bar in enumerate(bar1.patches):
            bar.set_hatch(HATCH_BASE[i // alpha_len])
        for i, bar in enumerate(bar2.patches):
            bar.set_hatch(HATCH_BASE[i // alpha_len])
        # x-axis label and x-axis tick label should be in the middle of two subplots
        ax2.set_xlabel("Recommended candidate set size ${k}$", fontsize=16, labelpad=5)
        ax2.tick_params(axis="x", pad=1)
        ax1.set_xlabel("")
        ax2.xaxis.set_ticks_position("top")
        ax2.invert_yaxis()
        ax1.legend(bbox_to_anchor=(0.5, 1.2), loc="upper center", borderaxespad=0.0, ncol=df["methods"].nunique())
        # ax2.legend(bbox_to_anchor=(0.5, -0.05), loc="upper center", borderaxespad=0.0, ncol=df["methods"].nunique())
        ax2.legend().set_visible(False)
        ax1.set_ylabel("Average CHR", fontsize=16)
        ax2.set_ylabel("Space occupied", fontsize=16)
        ax1.set_title(title)
        fig.savefig(os.path.join(self.out_path, out_f))
        if show:
            plt.show()


class P4(object):
    """
    draw pictures for paper 4
    """

    def __init__(self, input_path, out_path):
        self.input_path = input_path
        self.out_path = out_path
        self.title_map = {"data/movie_processed.csv": "The Movies Dataset",
                          "data/processed_data.csv": "The BSY Trace Dataset",
                          "data/zoo_processed.csv": "The Zoo Animals Dataset"}

    def read_excel(self, sheet_name, dtype=None):
        """
        read from excel to pandas dataframe
        """
        # read excel, skip empty rows
        df = pd.read_excel(self.input_path, sheet_name=sheet_name, dtype=dtype)
        df.dropna(axis=0, how="all", inplace=True)
        # 第一行为headers，去掉每个header的空格
        df.columns = df.columns.str.strip()
        return df

    def draw_speed_box_chart(self, show=True):
        """
        draw speed box chart
        """
        CATEGORY_MAP = {"r10w": "insert-10w", "q10w": "query-10w", "d10w": "delete-10w"}
        df_speed = self.read_excel("speed", dtype={"time": int, "set_num": int})

        # get filter category
        filter_category = df_speed["filter"].unique()
        for f in filter_category:
            fig, ax = plt.subplots()
            ax.grid(linestyle="--")
            df = df_speed[df_speed["filter"] == f].copy()
            df["category"] = df["category"].apply(lambda x: CATEGORY_MAP[x])
            # df["set_num"] = df["set_num"].apply(lambda x: math.log(x, 2))
            sns.boxplot(x="set_num", y="time", data=df, hue="category", ax=ax)
            ax.set_xlabel("Set number", fontsize=20)
            ax.set_ylabel("Job complete time(us)", fontsize=20)
            # y-axis use scientific notation to show
            ax.ticklabel_format(style="sci", axis="y", scilimits=(-2, 2))
            plt.tight_layout()
            ax.tick_params(labelsize=16)
            plt.legend(fontsize=16)
            fig.savefig(self.out_path + "/speed_box_{}.pdf".format(f))
        if show:
            plt.show()

    def draw_space_line_chart(self, xtype="set_num", show=True):
        """
        draw space line chart
        """
        sns.set_palette("muted")
        TYPE_MAP = {"emcf": "EMCF", "cf": "CFG", "hashmap": "HashTable"}
        fig, ax = plt.subplots()
        ax.grid(linestyle="--")
        df = self.read_excel("summary", dtype={"set_num": int, "mem_used": np.int64})
        if xtype == "set_num":
            df = df[df["capacity"] == 1000000].copy()
        elif xtype == "capacity":
            df = df[df["set_num"] == 16].copy()
        df["type"] = df["type"].apply(lambda x: TYPE_MAP[x])
        sns.lineplot(x=xtype, y="mem_used", hue="type", markers=True, data=df,
                     ax=ax, markersize=12, linewidth=2, dashes=False, style="type")
        # set line style
        ax.lines[0].set_linestyle("-")
        ax.lines[1].set_linestyle("--")
        ax.set_xlabel(xtype, fontsize=20)
        ax.set_ylabel("Space occupied", fontsize=20)
        # get rid of legend title
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles[:], labels=labels[:], fontsize=16)
        ax.tick_params(labelsize=16)
        # save figure
        plt.tight_layout()
        fig.savefig(self.out_path + "/space_with_{}.pdf".format(xtype))
        if show:
            plt.show()

    def draw_err_rate_line_chart(self, ds_name, show=True):
        """
        draw error rate line chart, y axixs is err_rate, x axis is memory used
        """
        df = self.read_excel("new",
                             dtype={"mem_used": int, "error_rate": np.float64, "tpr": np.float64, "query_num": int})
        fig, ax = plt.subplots()
        ax.grid(linestyle="--")
        df = df[df["dataset"] == ds_name].copy()
        # 按照不同的method画多条线
        for i, method in enumerate(df["method"].unique()):
            df_m = df[df["method"] == method].copy()
            if method == "emcf-v":
                df_m = df_m[(df_m["query_num"] == 10 ** 6) & (df_m["R"] == 3)].copy()
            x = df_m["mem_used"]
            y = df_m["error_rate"]
            ax.plot(x, y, label=method, markersize=8, color=COLOR_BASE[i], marker=MARKER_BASE[i])
        # ax.plot(x, y, label="error rate", color=COLOR_BASE[0], marker=MARKER_BASE[0], markersize=8)
        ax.set_xlabel("Memory used", fontsize=20)
        ax.set_ylabel("Error rate", fontsize=20)
        ax.set_title(self.title_map[ds_name], fontsize=20)
        ax.legend(fontsize=16)
        ax.tick_params(labelsize=16)
        out_name = ds_name.replace("/", "_").replace(".csv", "")
        # save figure use high resolution
        plt.tight_layout()
        fig.savefig(self.out_path + "/err_rate_{}.pdf".format(out_name), dpi=300)
        if show:
            plt.show()

    def draw_tpr_line_chart(self, ds_name, show=True):
        """
        draw query time line chart, y axixs is tpr, x axis is memory used
        """
        df = self.read_excel("new", dtype={"mem_used": int, "error_rate": np.float64, "tpr": np.float64})
        fig, ax = plt.subplots()
        ax.grid(linestyle="--")
        df = df[df["dataset"] == ds_name].copy()
        # 按照不同的method画多条线
        for i, method in enumerate(df["method"].unique()):
            df_m = df[df["method"] == method].copy()
            # if method == "ncf":
            #     continue
            if method == "emcf-v":
                df_m = df_m[(df_m["query_num"] == 10 ** 6) & (df_m["R"] == 3)].copy()
            x = df_m["mem_used"]
            y = df_m["tpr"]
            ax.plot(x, y, label=method, markersize=8, color=COLOR_BASE[i], marker=MARKER_BASE[i])
        # ax.plot(x, y, label="error rate", color=COLOR_BASE[0], marker=MARKER_BASE[0], markersize=8)
        ax.set_xlabel("Memory used", fontsize=20)
        ax.set_ylabel("Query Time (us)", fontsize=20)
        ax.set_title(self.title_map[ds_name], fontsize=20)
        ax.legend(fontsize=16)
        ax.tick_params(labelsize=16)
        out_name = ds_name.replace("/", "_").replace(".csv", "")
        # save figure use high resolution
        plt.tight_layout()
        fig.savefig(self.out_path + "/tpr_{}.pdf".format(out_name), dpi=300)
        if show:
            plt.show()

    def draw_tpr_K_R_line_chart(self, ds_name, show=True):
        """
        draw line chart, y axis is tpr, x axis is the parm K and R
        Exploring the impact of hyperparameters K and R on query time
        """
        df = self.read_excel("new", dtype={"mem_used": int, "error_rate": np.float64, "tpr": np.float64})
        fig, ax = plt.subplots()
        ax.grid(linestyle="--")
        df = df[df["dataset"] == ds_name].copy()
        df_m = df[(df["method"] == "emcf-v") & (df["query_num"] != 10 ** 6)].copy()
        df_m["K"] = df_m["K"].apply(lambda _x: int(_x))
        df_m["R"] = df_m["R"].apply(lambda _x: int(_x))
        df_k = df_m[df_m["R"] == 3].copy()
        df_r = df_m[df_m["K"] == 64].copy()
        xr = df_r["R"]
        yr = df_r["tpr"]
        ax.plot(xr, yr, label="emcf-v", color=COLOR_BASE[0], marker=MARKER_BASE[0], markersize=8)
        ax.set_xlabel("Replication number", fontsize=20)
        ax.set_ylabel("Query Time (us)", fontsize=20)
        ax.set_title(self.title_map[ds_name], fontsize=20)
        ax.tick_params(labelsize=16)
        ax.legend(fontsize=16)
        out_name = ds_name.replace("/", "_").replace(".csv", "")
        # save figure use high resolution
        plt.tight_layout()
        fig.savefig(self.out_path + "/tpr_R_{}.pdf".format(out_name), dpi=300)
        if show:
            plt.show()
        xk = df_k["K"]
        yk = df_k["tpr"]
        xk, yk = zip(*sorted(zip(xk, yk)))
        fig, ax = plt.subplots()
        ax.grid(linestyle="--")
        ax.plot(xk, yk, label="emcf-v", color=COLOR_BASE[0], marker=MARKER_BASE[0], markersize=8)
        ax.set_xlabel("Size of bit vector K (bit)", fontsize=20)
        ax.set_ylabel("Query Time (us)", fontsize=20)
        ax.set_title(self.title_map[ds_name], fontsize=20)
        ax.tick_params(labelsize=16)
        ax.legend(fontsize=16)
        out_name = ds_name.replace("/", "_").replace(".csv", "")
        # save figure use high resolution
        plt.tight_layout()
        fig.savefig(self.out_path + "/tpr_K_{}.pdf".format(out_name), dpi=300)
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
    # data = [9917, 8968, 4516]  # DINNRS
    # plot_bar_chart(data, "", output_path + "/DINNRS-domain-hit.pdf")
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
    # ---------------------------paper 1-------------------------------

    # p1 = P1(input_file, output_path)
    # p1.plot_link_load_rate_line_chart()
    # p1.plot_intra_ratio_line_chart()
    # p1.plot_cache_size_to_avg_latency_line_chart()
    # p1.plot_resolve_num_levels_bar_chart()

    # ---------------------------paper 2-------------------------------
    # plot_cache_hit_ratio_seq_line_chart
    # p2 = P2(input_file, output_path)
    # p2.plot_cache_hit_ratio_seq_line_chart("Time/s", "Average cache hit ratio", "", date="0616")
    # p2.plot_data_to_avg_CHR_bar_group_chart()
    # p2.plot_alpha_to_avg_CHR_bar_chart()
    # p2.plot_alpha_to_free_space_bar_chart()
    # p2.plot_alpha_mix_bar_chart(in_f="v_alpha_10x_v1.2.csv", out_f="alpha_mix_bar_v1.2.pdf")
    # p2.plot_t0_to_avg_CHR_bar_chart()
    # p2.plot_t0_to_free_space_bar_chart()
    # p2.plot_t0_mix_bar_chart(in_f="v_t0_10x_v1.2.csv", out_f="t0_mix_bar_v1.2.pdf")
    # p2.plot_k_to_avg_CHR_bar_chart()
    # p2.plot_k_to_free_space_bar_chart()
    # p2.plot_k_mix_bar_chart(in_f="v_k_10x_v1.2.csv", out_f="k_mix_bar_v1.2.pdf")

    # ---------------------------paper 4-------------------------------
    p4 = P4(input_file, output_path)
    # p4.draw_speed_box_chart()
    # p4.draw_space_line_chart("set_num")
    # p4.draw_space_line_chart("capacity")
    p4.draw_err_rate_line_chart("data/processed_data.csv")
    p4.draw_tpr_line_chart("data/processed_data.csv")
    # p4.draw_tpr_K_R_line_chart("data/movie_processed.csv")


def main():
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True, help="input file")
    parser.add_argument("-o", "--output", type=str, required=True, help="output path")
    args = parser.parse_args()
    run(args.input, args.output)


if __name__ == '__main__':
    main()
