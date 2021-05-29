import datetime
from typing import Final

import pandas as pd

USERS: Final = {
    1: {"name": "U1", "sex": 0},
    2: {"name": "U2", "sex": 1},
}


USERS_DF: Final = pd.DataFrame(
    {
        "user_id": [1, 2],
        "name": ["U1", "U2"],
        "sex": [0, 1],
    }
)

SETS: Final = {
    datetime.date(2002, 2, 20): {"E1": ["12@8", "11@8", "10@8"], "E2": ["9@9", "8@9"]},
    datetime.date(2002, 2, 22): {"E4": ["7@8", "6@8", "5@8"], "E3": ["40s@9", "30s@9"]},
}

SETS_DF: Final = pd.DataFrame(
    {
        "date": [datetime.date(2002, 2, 20)] * 5 + [datetime.date(2002, 2, 22)] * 5,
        "exercise": ["E1", "E1", "E1", "E2", "E2", "E4", "E4", "E4", "E3", "E3"],
        "reps": list(map(float, range(12, 4, -1))) + [float("nan")] * 2,
        "time": [float("nan")] * 8 + [40, 30],
        "weight": [float("nan")] * 10,
        "rpe": [8.0, 8.0, 8.0, 9.0, 9.0, 8.0, 8.0, 8.0, 9.0, 9.0],
        "rir": [2.0, 2.0, 2.0, 1.0, 1.0, 2.0, 2.0, 2.0, 1.0, 1.0],
    }
)

WORKOUTS: Final = {
    datetime.date(2002, 2, 20): {"notes": "First"},
    datetime.date(2002, 2, 22): {"notes": "Second"},
}

WORKOUTS_DF: Final = pd.DataFrame(
    {
        "date": [datetime.date(2002, 2, 20), datetime.date(2002, 2, 22)],
        "notes": ["First", "Second"],
    }
)

BODYWEIGHT: Final = {datetime.date(2002, 2, 20): 81.2, datetime.date(2002, 2, 22): 82.4}

BODYWEIGHT_DF: Final = pd.DataFrame(
    {
        "date": [datetime.date(2002, 2, 20), datetime.date(2002, 2, 22)],
        "weight": [81.2, 82.4],
    }
)

BODYFAT: Final = {
    datetime.date(2002, 2, 20): [11, 13, 15, 17, 19, 21, 23],
    datetime.date(2002, 2, 22): [12, 14, 16, 18, 20, 22, 24],
}

BODYFAT_DF: Final = pd.DataFrame(
    {
        "date": [datetime.date(2002, 2, 20), datetime.date(2002, 2, 22)],
        "chest": [11, 12],
        "abdominal": [13, 14],
        "tigh": [15, 16],
        "tricep": [17, 18],
        "subscapular": [19, 20],
        "suprailiac": [21, 22],
        "midaxillary": [23, 24],
    }
)

PERIOD: Final = {datetime.date(2002, 2, 20): 81.2, datetime.date(2002, 2, 22): 82.4}

PERIOD_DF: Final = pd.DataFrame(
    {
        "date": [datetime.date(2002, 2, 20), datetime.date(2002, 2, 22)],
        "intensity": [2, 3],
    }
)

ROUTINE_SETS: Final = {
    "T1": {"E1": [None, None, None], "E2": [None, None]},
    "T2": {"E4": [None, None, None], "E3": [None, None]},
}

ROUTINE_SETS_DF: Final = pd.DataFrame(
    {
        "routine": ["T1"] * 5 + ["T2"] * 5,
        "exercise": ["E1", "E1", "E1", "E2", "E2", "E4", "E4", "E4", "E3", "E3"],
        "reps": [float("nan")] * 10,
        "time": [float("nan")] * 10,
        "weight": [float("nan")] * 10,
        "rpe": [float("nan")] * 10,
    }
)

ROUTINES: Final = {
    "T2": {"notes": "Second"},
}


ROUTINES_DF: Final = pd.DataFrame(
    {
        "routine": ["T2"],
        "notes": ["Second"],
    }
)
