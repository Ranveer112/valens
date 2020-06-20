#!/usr/bin/env python

import argparse
import datetime
import pathlib
import re
import statistics
import sys
from typing import Dict, Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd
import yaml

CONFIG_FILE = pathlib.Path.home() / ".config/valens/valens.yml"


config = {}


def main() -> Union[int, str]:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")

    parser_show = subparsers.add_parser("show", help="show exercise")
    sp_show = parser_show.add_subparsers(dest="subcommand")
    sp_show_wo = sp_show.add_parser("wo", help="show workouts")
    sp_show_wo.set_defaults(func=show_workouts)
    sp_show_ex = sp_show.add_parser("ex", help="show exercise")
    sp_show_ex.add_argument("exercise", metavar="NAME", type=str, help="exercise")
    sp_show_ex.set_defaults(func=show_exercise)
    sp_show_bw = sp_show.add_parser("bw", help="show bodyweight show")
    sp_show_bw.set_defaults(func=show_bodyweight)

    parser_list = subparsers.add_parser("list", help="list exercises")
    parser_list.add_argument(
        "--last", action="store_true", help="list only excercises of last workout"
    )
    parser_list.add_argument("--short", action="store_true", help="list only excercise names")
    parser_list.set_defaults(func=list_exercises)

    args = parser.parse_args(sys.argv[1:])

    if not args.subcommand:
        parser.print_usage()
        return 2

    parse_config()
    args.func(args)

    return 0


def parse_config() -> None:
    with open(CONFIG_FILE) as f:
        config.update(yaml.safe_load(f))


def list_exercises(args: argparse.Namespace) -> None:
    df = parse_log()

    if args.last:
        last_exercises = list(
            df.loc[lambda x: x["date"] == df["date"].iloc[-1]].groupby(["exercise"]).groups
        )
        df = df.loc[lambda x: x["exercise"].isin(last_exercises)]

    for exercise, log in df.groupby(["exercise"]):
        print(f"\n### {exercise}\n")
        for date, sets in log.groupby(["date"]):
            print(
                f"- {date}: "
                + "-".join(
                    format_set(set_tuple)
                    for set_tuple in sets.loc[:, ["reps", "time", "weight", "rpe"]].itertuples()
                )
            )


def format_set(set_tuple: Tuple[int, float, float, float, float]) -> str:
    _, reps, time, weight, rpe = set_tuple
    result = ""
    if not pd.isna(reps):
        result += f"{reps:.0f}"
    if not pd.isna(time):
        if result:
            result += "x"
        result += f"{time:.0f}s"
    if not pd.isna(weight):
        if result:
            result += "x"
        result += f"{weight:.1f}kg"
    if not pd.isna(rpe):
        result += f"@{rpe}"
    return result


def show_workouts(args: argparse.Namespace) -> None:
    # pylint: disable=unused-argument
    plot_workouts()
    plt.show()


def show_exercise(args: argparse.Namespace) -> None:
    plot_exercise(args.exercise)
    plt.show()


def show_bodyweight(args: argparse.Namespace) -> None:
    # pylint: disable=unused-argument
    plot_bodyweight()
    plt.show()


def plot_workouts() -> None:
    df = parse_log()
    r = df.groupby(["date"]).mean()
    r["volume"] = df.groupby(["date"]).sum()["reps"]
    r.plot(style="o-", ylim=(0, 200))


def plot_exercise(name: str) -> None:
    df = parse_log()
    df["reps+rir"] = df["reps"] + df["rir"]
    df_ex = df.loc[lambda x: x["exercise"] == name]
    r = df_ex.loc[:, ["date", "reps", "reps+rir", "weight", "time"]].groupby(["date"]).mean()
    r["volume"] = df_ex.groupby(["date"]).sum()["reps"]
    r.plot(style="o-")


def plot_bodyweight() -> None:
    xa = []
    ya = []

    with open(config["bodyweight_file"]) as f:
        for l in f:
            if ";" not in l:
                continue
            x, y = l.strip().split(";")
            xa.append(datetime.datetime.strptime(x, "%d.%m.%Y"))
            ya.append(float(y.replace(",", ".")))

    ya_mean = [
        *([None] * 4),
        *[statistics.mean(ya[i - 4 : i + 4]) for i in range(4, len(ya) - 4)],
        *([None] * 4),
    ]

    fig, ax = plt.subplots()
    fig.autofmt_xdate()
    ax.plot_date(xa, ya, "o-")
    ax.plot_date(xa, ya_mean, "-")

    ax.set(ylabel="Weight (kg)")
    ax.grid()


def parse_log() -> pd.DataFrame:
    cols: Dict[str, list] = {
        "date": [],
        "exercise": [],
        "reps": [],
        "time": [],
        "weight": [],
        "rpe": [],
    }

    with open(config["workout_file"]) as log_file:
        log = yaml.safe_load(log_file)

        for date, exercises in log.items():
            for exercise, sets in exercises.items():
                for s in sets:
                    for k, v in parse_set(str(s)).items():
                        if k in ["weight", "rpe"]:
                            cols[k].append(float(v) if v else None)
                        else:
                            cols[k].append(int(v) if v else None)
                    cols["date"].append(date)
                    cols["exercise"].append(exercise)

    df = pd.DataFrame(cols)
    df["rir"] = 10 - df["rpe"]

    return df


def parse_set(set_string: str) -> Dict[str, str]:
    m = re.match(
        r"^(?P<reps>\d+)?"
        r"(?:(?:^|x)(?P<time>\d+)s)?"
        r"(?:(?:^|x)(?P<weight>\d+(?:\.\d+)?)kg)?"
        r"(?:@(?P<rpe>\d+(?:\.\d+)?))?$",
        set_string,
    )
    if not m:
        raise Exception(f"unexpected format for set '{set_string}'")
    return m.groupdict()


if __name__ == "__main__":
    sys.exit(main())