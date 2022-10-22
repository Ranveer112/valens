from __future__ import annotations

from multiprocessing import Process
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

import pytest
from selenium import webdriver

import tests.data
import tests.utils
from valens import app

from .const import HOST, PORT
from .page import (
    BodyFatPage,
    BodyWeightPage,
    ExercisePage,
    ExercisesPage,
    HomePage,
    LoginPage,
    PeriodPage,
    RoutinePage,
    RoutinesPage,
    WorkoutPage,
    WorkoutsPage,
)

USERS = tests.data.users()
USER = USERS[0]
USERNAMES = [user.name for user in USERS]


@pytest.fixture(autouse=True)
def fixture_backend() -> Generator[None, None, None]:
    def run_app(tmp_path: Path) -> None:
        app.config["DATABASE"] = f"sqlite:///{tmp_path}/valens.db"
        app.config["SECRET_KEY"] = b"TEST_KEY"

        with app.app_context():
            tests.utils.init_db_data()
            app.run(HOST, PORT)

    with TemporaryDirectory() as tmp_path:
        p = Process(target=run_app, name="pytest-valens-backend", args=(tmp_path,))
        p.daemon = True
        p.start()
        yield
        p.terminate()


@pytest.fixture(name="driver_args")
def fixture_driver_args() -> list[str]:
    return ["--log-level=ALL"]


@pytest.fixture(name="session_capabilities", scope="session")
def fixture_session_capabilities(
    session_capabilities: webdriver.DesiredCapabilities.CHROME,
) -> Generator[webdriver.DesiredCapabilities.CHROME, None, None]:
    session_capabilities["loggingPrefs"] = {"browser": "ALL"}
    return session_capabilities


def login(driver: webdriver.Chrome) -> None:
    login_page = LoginPage(driver)
    login_page.load()
    login_page.login(USERNAMES[0])


def test_login(driver: webdriver.Chrome) -> None:
    login_page = LoginPage(driver)
    login_page.load()

    assert login_page.users() == USERNAMES

    login_page.login(USERNAMES[0])


def test_home(driver: webdriver.Chrome) -> None:
    login(driver)

    home_page = HomePage(driver, USERNAMES[0])

    home_page.click_workouts()
    workouts_page = WorkoutsPage(driver)
    workouts_page.wait_until_loaded()
    workouts_page.click_up_button()
    home_page.wait_until_loaded()

    home_page.click_routines()
    routines_page = RoutinesPage(driver)
    routines_page.wait_until_loaded()
    routines_page.click_up_button()
    home_page.wait_until_loaded()

    home_page.click_exercises()
    exercises_page = ExercisesPage(driver)
    exercises_page.wait_until_loaded()
    exercises_page.click_up_button()
    home_page.wait_until_loaded()

    home_page.click_body_weight()
    body_weight_page = BodyWeightPage(driver)
    body_weight_page.wait_until_loaded()
    body_weight_page.click_up_button()
    home_page.wait_until_loaded()

    home_page.click_body_fat()
    body_fat_page = BodyFatPage(driver)
    body_fat_page.wait_until_loaded()
    body_fat_page.click_up_button()
    home_page.wait_until_loaded()

    home_page.click_period()
    period_page = PeriodPage(driver)
    period_page.wait_until_loaded()
    period_page.click_up_button()
    home_page.wait_until_loaded()


def test_body_weight_add(driver: webdriver.Chrome) -> None:
    login(driver)
    page = BodyWeightPage(driver)
    page.load()
    page.click_fab()

    date = page.body_weight_dialog.get_date()
    weight = "123.4"

    page.body_weight_dialog.click_cancel()

    assert page.get_table_value(1) != date
    assert page.get_table_value(2) != weight

    page.click_fab()
    page.body_weight_dialog.set_weight(weight)

    assert page.get_table_value(1) != date
    assert page.get_table_value(2) != weight

    page.body_weight_dialog.click_save()

    page.wait_for_table_value(1, date)
    page.wait_for_table_value(2, weight)


def test_body_weight_edit(driver: webdriver.Chrome) -> None:
    date = str(USER.body_weight[-1].date)
    weight = str(USER.body_weight[-1].weight)
    new_weight = "123.4"

    login(driver)
    page = BodyWeightPage(driver)
    page.load()

    page.wait_for_table_value(1, date)
    page.wait_for_table_value(2, weight)

    page.click_edit(0)
    page.body_weight_dialog.set_weight(new_weight)
    page.body_weight_dialog.click_cancel()

    page.wait_for_table_value(1, date)
    page.wait_for_table_value(2, weight)

    page.click_edit(0)
    page.body_weight_dialog.set_weight(new_weight)
    page.body_weight_dialog.click_save()

    page.wait_for_table_value(1, date)
    page.wait_for_table_value(2, new_weight)


def test_body_weight_delete(driver: webdriver.Chrome) -> None:
    date_1 = str(USER.body_weight[-1].date)
    weight = str(USER.body_weight[-1].weight)
    date_2 = str(USER.body_weight[-2].date)

    login(driver)
    page = BodyWeightPage(driver)
    page.load()

    page.wait_for_table_value(1, date_1)
    page.wait_for_table_value(2, weight)

    page.click_delete(0)
    page.delete_dialog.click_no()

    page.wait_for_table_value(1, date_1)
    page.wait_for_table_value(2, weight)

    page.click_delete(0)
    page.delete_dialog.click_yes()

    page.wait_for_table_value(1, date_2)


def test_body_fat_add(driver: webdriver.Chrome) -> None:
    login(driver)
    page = BodyFatPage(driver)
    page.load()
    page.click_fab()

    date = page.body_fat_dialog.get_date()
    values = ("1", "2", "3", "4", "5", "6", "7")

    page.body_fat_dialog.click_cancel()

    assert page.get_table_value(1) != date
    for i, v in enumerate(values, start=4):
        assert page.get_table_value(i) != v

    page.click_fab()
    page.body_fat_dialog.set_jp7(values)

    assert page.get_table_value(1) != date
    for i, v in enumerate(values, start=4):
        assert page.get_table_value(i) != v

    page.body_fat_dialog.click_save()

    page.wait_for_table_value(1, date)
    for i, v in enumerate(values, start=4):
        page.wait_for_table_value(i, v)


def test_body_fat_edit(driver: webdriver.Chrome) -> None:
    body_fat = USER.body_fat[-1]
    date = str(body_fat.date)
    values = (
        str(body_fat.tricep) if body_fat.tricep else "-",
        str(body_fat.suprailiac) if body_fat.suprailiac else "-",
        str(body_fat.tigh) if body_fat.tigh else "-",
        str(body_fat.chest) if body_fat.chest else "-",
        str(body_fat.abdominal) if body_fat.abdominal else "-",
        str(body_fat.subscapular) if body_fat.subscapular else "-",
        str(body_fat.midaxillary) if body_fat.midaxillary else "-",
    )
    new_values = ("1", "2", "3", "4", "5", "6", "7")

    login(driver)
    page = BodyFatPage(driver)
    page.load()

    page.wait_for_table_value(1, date)
    for i, v in enumerate(values, start=4):
        page.wait_for_table_value(i, v)

    page.click_edit(0)
    page.body_fat_dialog.set_jp7(new_values)
    page.body_fat_dialog.click_cancel()

    page.wait_for_table_value(1, date)
    for i, v in enumerate(values, start=4):
        page.wait_for_table_value(i, v)

    page.click_edit(0)
    page.body_fat_dialog.set_jp7(new_values)
    page.body_fat_dialog.click_save()

    page.wait_for_table_value(1, date)
    for i, v in enumerate(new_values, start=4):
        page.wait_for_table_value(i, v)


def test_body_fat_delete(driver: webdriver.Chrome) -> None:
    date_1 = str(USER.body_fat[-1].date)
    date_2 = str(USER.body_fat[-2].date)

    login(driver)
    page = BodyFatPage(driver)
    page.load()

    page.wait_for_table_value(1, date_1)

    page.click_delete(0)
    page.delete_dialog.click_no()

    page.wait_for_table_value(1, date_1)

    page.click_delete(0)
    page.delete_dialog.click_yes()

    page.wait_for_table_value(1, date_2)


def test_period_add(driver: webdriver.Chrome) -> None:
    login(driver)
    page = PeriodPage(driver)
    page.load()
    page.click_fab()

    date = page.period_dialog.get_date()
    period = "4"

    page.period_dialog.click_cancel()

    assert page.get_table_value(1) != date
    assert page.get_table_value(2) != period

    page.click_fab()
    page.period_dialog.set_period(period)

    assert page.get_table_value(1) != date
    assert page.get_table_value(2) != period

    page.period_dialog.click_save()

    page.wait_for_table_value(1, date)
    page.wait_for_table_value(2, period)


def test_period_edit(driver: webdriver.Chrome) -> None:
    period = USER.period[-1]
    date = str(period.date)
    intensity = str(period.intensity)
    new_intensity = "4"

    assert intensity != new_intensity

    login(driver)
    page = PeriodPage(driver)
    page.load()

    page.wait_for_table_value(1, date)
    page.wait_for_table_value(2, intensity)

    page.click_edit(0)
    page.period_dialog.set_period(new_intensity)
    page.period_dialog.click_cancel()

    page.wait_for_table_value(1, date)
    page.wait_for_table_value(2, intensity)

    page.click_edit(0)
    page.period_dialog.set_period(new_intensity)
    page.period_dialog.click_save()

    page.wait_for_table_value(1, date)
    page.wait_for_table_value(2, new_intensity)


def test_period_delete(driver: webdriver.Chrome) -> None:
    period = USER.period[-1]
    date_1 = str(period.date)
    intensity = str(period.intensity)
    date_2 = str(USER.period[-2].date)

    login(driver)
    page = PeriodPage(driver)
    page.load()

    page.wait_for_table_value(1, date_1)
    page.wait_for_table_value(2, intensity)

    page.click_delete(0)
    page.delete_dialog.click_no()

    page.wait_for_table_value(1, date_1)
    page.wait_for_table_value(2, intensity)

    page.click_delete(0)
    page.delete_dialog.click_yes()

    page.wait_for_table_value(1, date_2)


def test_workouts_add(driver: webdriver.Chrome) -> None:
    routine = USER.routines[-1].name

    login(driver)
    page = WorkoutsPage(driver)
    page.load()
    page.click_fab()

    date = page.workouts_dialog.get_date()

    page.workouts_dialog.click_cancel()

    assert page.get_table_value(1) != date
    assert page.get_table_value(2) != routine

    page.click_fab()
    page.workouts_dialog.set_routine(routine)

    assert page.get_table_value(1) != date
    assert page.get_table_value(2) != routine

    page.workouts_dialog.click_save()

    page.wait_for_table_value(1, date)
    page.wait_for_table_value(2, routine)


def test_workouts_delete(driver: webdriver.Chrome) -> None:
    workout = USER.workouts[-1]
    date_1 = str(workout.date)
    routine = (
        [r.name for r in USER.routines if r.id == workout.routine_id][0]
        if workout.routine_id
        else "-"
    )
    date_2 = str(USER.workouts[-2].date)

    login(driver)
    page = WorkoutsPage(driver)
    page.load()

    page.wait_for_table_value(1, date_1)
    page.wait_for_table_value(2, routine)

    page.click_delete(0)
    page.delete_dialog.click_no()

    page.wait_for_table_value(1, date_1)
    page.wait_for_table_value(2, routine)

    page.click_delete(0)
    page.delete_dialog.click_yes()

    page.wait_for_table_value(1, date_2)


def test_workout_change_entries(driver: webdriver.Chrome) -> None:
    workout = USER.workouts[-1]
    sets = [
        [
            str(s.reps) if s.reps is not None else "",
            str(s.time) if s.time is not None else "",
            str(s.weight) if s.weight is not None else "",
            (str(int(s.rpe) if s.rpe % 1 == 0 else s.rpe)) if s.rpe is not None else "",
        ]
        for s in workout.sets
    ]
    new_values = ["1", "2", "3", "4"]

    login(driver)
    page = WorkoutPage(driver, workout.id)
    page.load()

    page.wait_for_title(str(workout.date))
    assert page.get_sets() == sets

    page.set_set(0, new_values)

    assert page.get_sets() == [new_values, *sets[1:]]

    page.load()

    page.wait_for_title(str(workout.date))
    assert page.get_sets() == sets

    page.set_set(0, new_values)

    assert page.get_sets() == [new_values, *sets[1:]]

    page.click_save()
    page.load()

    page.wait_for_title(str(workout.date))
    assert page.get_sets() == [new_values, *sets[1:]]


def test_workout_change_notes(driver: webdriver.Chrome) -> None:
    workout = USER.workouts[0]
    sets = [
        [
            str(s.reps) if s.reps is not None else "",
            str(s.time) if s.time is not None else "",
            str(s.weight) if s.weight is not None else "",
            (str(int(s.rpe) if s.rpe % 1 == 0 else s.rpe)) if s.rpe is not None else "",
        ]
        for s in workout.sets
    ]
    notes = workout.notes if workout.notes is not None else ""
    new_notes = "Test"

    assert notes != new_notes

    login(driver)
    page = WorkoutPage(driver, workout.id)
    page.load()

    page.wait_for_title(str(workout.date))
    assert page.get_sets() == sets
    assert page.get_notes() == notes

    page.set_notes(new_notes)

    assert page.get_sets() == sets
    assert page.get_notes() == new_notes

    page.load()

    page.wait_for_title(str(workout.date))
    assert page.get_sets() == sets
    assert page.get_notes() == notes

    page.set_notes(new_notes)

    assert page.get_sets() == sets
    assert page.get_notes() == new_notes

    page.click_save()
    page.load()

    page.wait_for_title(str(workout.date))
    assert page.get_sets() == sets
    assert page.get_notes() == new_notes


def test_routines_add(driver: webdriver.Chrome) -> None:
    name = USER.routines[-1].name
    new_name = "New Routine"

    assert name != new_name

    login(driver)
    page = RoutinesPage(driver)
    page.load()
    page.click_fab()
    page.routines_dialog.click_cancel()

    page.wait_for_table_value(1, name)

    page.click_fab()
    page.routines_dialog.set_name(new_name)
    page.routines_dialog.click_save()

    page.wait_for_table_value(1, new_name)


def test_routines_edit(driver: webdriver.Chrome) -> None:
    name = str(USER.routines[-1].name)
    new_name = "Changed Routine"

    assert name != new_name

    login(driver)
    page = RoutinesPage(driver)
    page.load()

    page.wait_for_table_value(1, name)

    page.click_edit(0)
    page.routines_dialog.set_name(new_name)
    page.routines_dialog.click_cancel()

    page.wait_for_table_value(1, name)

    page.click_edit(0)
    page.routines_dialog.set_name(new_name)
    page.routines_dialog.click_save()

    page.wait_for_table_value(1, new_name)


def test_routines_delete(driver: webdriver.Chrome) -> None:
    name_1 = str(USER.routines[-1].name)
    name_2 = str(USER.routines[-2].name)

    login(driver)
    page = RoutinesPage(driver)
    page.load()

    page.wait_for_table_value(1, name_1)

    page.click_delete(0)
    page.delete_dialog.click_no()

    page.wait_for_table_value(1, name_1)

    page.click_delete(0)
    page.delete_dialog.click_yes()

    page.wait_for_table_value(1, name_2)


@pytest.mark.parametrize("position", [1, 2, 3])
def test_routine_add_exercise(driver: webdriver.Chrome, position: int) -> None:
    routine = USER.routines[0]
    exercise_1 = str(routine.exercises[0].exercise.name)
    exercise_2 = str(routine.exercises[1].exercise.name)
    new_exercise = str(USER.exercises[2].name)
    sets = "10"

    login(driver)
    page = RoutinePage(driver, routine.id)
    page.load()

    page.wait_for_title(routine.name)

    page.wait_for_link(exercise_1)
    page.wait_for_link(exercise_2)
    page.wait_for_link_not_present(new_exercise)

    page.click_fab()
    page.exercise_dialog.set_position("1")
    page.exercise_dialog.set_exercise(new_exercise)
    page.exercise_dialog.set_sets("20")
    page.exercise_dialog.click_cancel()

    page.wait_for_link(exercise_1)
    page.wait_for_link(exercise_2)
    page.wait_for_link_not_present(new_exercise)

    page.click_fab()
    page.exercise_dialog.set_position(str(position))
    page.exercise_dialog.set_exercise(new_exercise)
    page.exercise_dialog.set_sets(sets)
    page.exercise_dialog.click_save()

    page.wait_for_link(exercise_1)
    page.wait_for_link(exercise_2)
    page.wait_for_link(new_exercise)
    assert page.get_table_body()[position - 1][1:3] == [new_exercise, sets]


def test_routine_edit_exercise_position(driver: webdriver.Chrome) -> None:
    routine = USER.routines[0]
    exercise = [e.exercise.name for e in routine.exercises]
    table_entries = [[e.exercise.name, str(e.sets)] for e in routine.exercises]

    login(driver)
    page = RoutinePage(driver, routine.id)
    page.load()

    page.wait_for_title(routine.name)

    for i, e in enumerate(table_entries):
        page.wait_for_link(e[0])
        assert page.get_table_body()[i][1:3] == e

    page.click_edit(0)
    page.exercise_dialog.set_position("2")
    page.exercise_dialog.click_cancel()

    for i, e in enumerate(table_entries):
        page.wait_for_link(e[0])
        assert page.get_table_body()[i][1:3] == e

    order = [1, 2, 3]

    for position in range(1, 4):
        for new_position in range(1, 4):
            order.insert(new_position - 1, order.pop(position - 1))

            page.click_edit(position - 1)
            page.exercise_dialog.set_position(str(new_position))
            page.exercise_dialog.click_save()

            for i, j in enumerate(order):
                page.wait_for_link(exercise[i])
                assert page.get_table_body()[i][1:3] == table_entries[j - 1]


def test_routine_edit_exercise_values(driver: webdriver.Chrome) -> None:
    routine = USER.routines[0]
    exercise = [e.exercise.name for e in routine.exercises]
    sets = [str(e.sets) for e in routine.exercises]

    login(driver)
    page = RoutinePage(driver, routine.id)
    page.load()

    page.wait_for_title(routine.name)

    for i, (e, s) in enumerate(zip(exercise, sets)):
        page.wait_for_link(e)
        assert page.get_table_body()[i][1:3] == [e, s]

    page.click_edit(1)
    page.exercise_dialog.set_exercise(exercise[2])
    page.exercise_dialog.set_sets("20")
    page.exercise_dialog.click_cancel()

    for i, (e, s) in enumerate(zip(exercise, sets)):
        page.wait_for_link(e)
        assert page.get_table_body()[i][1:3] == [e, s]

    page.click_edit(1)
    page.exercise_dialog.set_exercise(exercise[0])
    page.exercise_dialog.set_sets("10")
    page.exercise_dialog.click_save()

    page.wait_for_link(exercise[0])
    page.wait_for_link(exercise[2])
    assert page.get_table_body()[0][1:3] == [exercise[0], sets[0]]
    assert page.get_table_body()[1][1:3] == [exercise[0], "10"]
    assert page.get_table_body()[2][1:3] == [exercise[2], sets[2]]


def test_routine_delete_exercise(driver: webdriver.Chrome) -> None:
    routine = USER.routines[0]
    table_entries = [[e.exercise.name, str(e.sets)] for e in routine.exercises]

    login(driver)
    page = RoutinePage(driver, routine.id)
    page.load()

    page.wait_for_title(routine.name)

    for i, e in enumerate(table_entries):
        page.wait_for_link(e[0])
        assert page.get_table_body()[i][1:3] == e

    page.click_delete(0)
    page.delete_dialog.click_no()

    for i, e in enumerate(table_entries):
        page.wait_for_link(e[0])
        assert page.get_table_body()[i][1:3] == e

    page.click_delete(0)
    page.delete_dialog.click_yes()

    for i, e in enumerate(table_entries[1:]):
        page.wait_for_link(e[0])
        assert page.get_table_body()[i][1:3] == e


def test_routine_delete_workout(driver: webdriver.Chrome) -> None:
    routine = USER.routines[0]
    workouts = sorted(
        {w for w in USER.workouts if w.routine_id == routine.id}, key=lambda x: x.date
    )
    workout_1 = str(workouts[-1].date)
    workout_2 = str(workouts[-2].date)
    offset = len(routine.exercises)

    login(driver)
    page = RoutinePage(driver, routine.id)
    page.load()

    page.wait_for_title(routine.name)

    page.wait_for_link(workout_1)
    page.wait_for_link(workout_2)

    page.click_delete(offset)
    page.delete_dialog.click_no()

    page.wait_for_link(workout_1)
    page.wait_for_link(workout_2)

    page.click_delete(offset)
    page.delete_dialog.click_yes()

    page.wait_for_link_not_present(workout_1)
    page.wait_for_link(workout_2)


def test_exercises_add(driver: webdriver.Chrome) -> None:
    exercise = sorted(USER.exercises, key=lambda x: x.name)[0]
    name = exercise.name
    new_name = "A Exercise"

    assert new_name < name

    login(driver)
    page = ExercisesPage(driver)
    page.load()
    page.click_fab()
    page.exercises_dialog.click_cancel()

    page.wait_for_table_value(1, name)

    page.click_fab()
    page.exercises_dialog.set_name(new_name)
    page.exercises_dialog.click_save()

    page.wait_for_table_value(1, new_name)


def test_exercises_edit(driver: webdriver.Chrome) -> None:
    exercise = sorted(USER.exercises, key=lambda x: x.name)[0]
    name = str(exercise.name)
    new_name = "Changed Exercise"

    assert name != new_name

    login(driver)
    page = ExercisesPage(driver)
    page.load()

    page.wait_for_table_value(1, name)

    page.click_edit(0)
    page.exercises_dialog.set_name(new_name)
    page.exercises_dialog.click_cancel()

    page.wait_for_table_value(1, name)

    page.click_edit(0)
    page.exercises_dialog.set_name(new_name)
    page.exercises_dialog.click_save()

    page.wait_for_table_value(1, new_name)


def test_exercises_delete(driver: webdriver.Chrome) -> None:
    exercises = sorted(USER.exercises, key=lambda x: x.name)
    name_1 = str(exercises[0].name)
    name_2 = str(exercises[1].name)

    login(driver)
    page = ExercisesPage(driver)
    page.load()

    page.wait_for_table_value(1, name_1)

    page.click_delete(0)
    page.delete_dialog.click_no()

    page.wait_for_table_value(1, name_1)

    page.click_delete(0)
    page.delete_dialog.click_yes()

    page.wait_for_table_value(1, name_2)


def test_exercise_delete_workout(driver: webdriver.Chrome) -> None:
    exercise = sorted(USER.exercises, key=lambda x: x.name)[1]
    workouts = sorted({ws.workout for ws in exercise.sets}, key=lambda x: x.date)
    workout_1 = str(workouts[-1].date)
    workout_2 = str(workouts[-2].date)

    login(driver)
    page = ExercisePage(driver, exercise.id)
    page.load()

    page.wait_for_table_value(1, workout_1)

    page.click_delete(0)
    page.delete_dialog.click_no()

    page.wait_for_table_value(1, workout_1)

    page.click_delete(0)
    page.delete_dialog.click_yes()

    page.wait_for_table_value(1, workout_2)