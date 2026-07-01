import os
import time
from typing import List, Dict
from prettytable import PrettyTable

from classes import Student, Examiner, Question


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def build_students_table(students: List[Student], order: List[str]) -> PrettyTable:
    """
    Таблица студентов для вывода.
    Сортировка:
    - сначала "Очередь" в порядке очереди;
    - затем "Сдал";
    - затем "Провалил".
    """
    table = PrettyTable()
    table.field_names = ["Студент", "Статус"]

    status_priority = {"Очередь": 0, "Сдал": 1, "Провалил": 2}
    pos = {name: i for i, name in enumerate(order)}

    def sort_key(st: Student):
        return (
            status_priority.get(st.status, 3),
            pos.get(st.name, 10**9),
        )

    for st in sorted(students, key=sort_key):
        table.add_row([st.name, st.status])

    return table


def build_examiners_table(examiners: List[Examiner], exam_start: float) -> PrettyTable:
    """
    Таблица экзаменаторов для «живого» вывода.
    """
    table = PrettyTable()
    table.field_names = [
        "Экзаменатор",
        "Текущий студент",
        "Всего студентов",
        "Завалил",
        "Время работы",
    ]

    now = time.time()
    for ex in sorted(examiners, key=lambda e: e.name):
        # если экзаменатор сейчас кого-то принимает — показываем текущее время
        if ex.current_student is not None:
            work_time = now - exam_start - ex.lunch_duration
        # если уже закончил — фиксированное время окончания
        elif ex.end_time is not None:
            work_time = ex.end_time - ex.lunch_duration
        # если ещё никого не принимал, но экзамен идёт
        else:
            work_time = now - exam_start - ex.lunch_duration

        current = ex.current_student if ex.current_student is not None else "-"
        table.add_row(
            [
                ex.name,
                current,
                ex.total_students,
                ex.failed_students,
                f"{work_time:.2f}",
            ]
        )

    return table


def render_running_state_objects(
    students: List[Student],
    examiners: List[Examiner],
    exam_start: float,
    students_order: List[str],
) -> None:
    """
    Живой вывод во время экзамена: таблица студентов, экзаменаторов и краткая сводка.
    """
    clear_screen()

    elapsed = time.time() - exam_start

    st_table = build_students_table(students, students_order)
    print(st_table)
    print()

    ex_table = build_examiners_table(examiners, exam_start)
    print(ex_table)
    print()

    total = len(students)
    in_queue = sum(1 for s in students if s.status == "Очередь")
    print(f"Осталось в очереди: {in_queue} из {total}")
    print(f"Время с момента начала экзамена: {elapsed:.2f}")


def get_best_students(students: List[Student]) -> List[str]:
    """
    Лучшие студенты — те, кто быстрее всех сдал экзамен.
    """
    passed = [s for s in students if s.passed]
    if not passed:
        return []
    min_time = min(s.time for s in passed if s.time is not None)
    return [s.name for s in passed if s.time == min_time]


def get_best_examiners(examiners: List[Examiner]) -> List[str]:
    """
    Лучшие экзаменаторы — минимальный процент заваленных студентов.
    """
    rates = []
    for ex in examiners:
        if ex.total_students == 0:
            continue
        rate = ex.failed_students / ex.total_students
        rates.append((ex.name, rate))

    if not rates:
        return []

    min_rate = min(r for _, r in rates)
    return [name for name, r in rates if abs(r - min_rate) < 1e-9]


def get_expel_students(students: List[Student]) -> List[str]:
    """
    Студенты, которых отчислят: из проваливших — те, кто провалился раньше всех.
    """
    failed = [s for s in students if s.passed is False and s.time is not None]
    if not failed:
        return []
    min_time = min(s.time for s in failed)
    return [s.name for s in failed if s.time == min_time]


def get_best_questions(
    questions: List[Question], question_stats: Dict[int, int]
) -> List[str]:
    """
    Лучшие вопросы — на которые больше всего верных ответов.
    """
    if not question_stats:
        return []

    max_correct = max(question_stats.values())
    if max_correct <= 0:
        return []

    best: List[str] = []
    for q in questions:
        if question_stats.get(q.id, 0) == max_correct:
            best.append(q.text)
    return best


def is_exam_successful(students: List[Student]) -> bool:
    """
    Экзамен удался, если сдало больше 85% студентов.
    """
    total = len(students)
    if total == 0:
        return False
    passed_count = sum(1 for s in students if s.passed)
    return (passed_count / total) > 0.85


def get_total_exam_time(examiners: List[Examiner], exam_start: float) -> float:
    """
    Итоговое время экзамена — максимум времени окончания среди экзаменаторов.
    """
    times = [ex.end_time for ex in examiners if ex.end_time is not None]
    if not times:
        return time.time() - exam_start
    return max(times)


def build_final_students_table(students: List[Student]) -> PrettyTable:
    """
    Финальная таблица студентов: только Сдал/Провалил, нужная сортировка.
    """
    table = PrettyTable()
    table.field_names = ["Студент", "Статус"]

    status_priority = {"Сдал": 0, "Провалил": 1}

    def sort_key(st: Student):
        return (
            status_priority.get(st.status, 2),
            st.time if st.time is not None else 10**9,
        )

    for st in sorted(students, key=sort_key):
        table.add_row([st.name, st.status])

    return table


def build_final_examiners_table(examiners: List[Examiner]) -> PrettyTable:
    """
    Финальная таблица экзаменаторов.
    """
    table = PrettyTable()
    table.field_names = ["Экзаменатор", "Всего студентов", "Завалил", "Время работы"]

    for ex in sorted(examiners, key=lambda e: e.name):
        work_time = ex.end_time - ex.lunch_duration if ex.end_time is not None else 0.0
        table.add_row(
            [
                ex.name,
                ex.total_students,
                ex.failed_students,
                f"{work_time:.2f}",
            ]
        )

    return table


def render_final_state_objects(
    students: List[Student],
    examiners: List[Examiner],
    exam_start: float,
    questions: List[Question],
    question_stats: Dict[int, int],
) -> None:
    """
    Финальный вывод после завершения экзамена.
    """
    clear_screen()

    total_exam_time = get_total_exam_time(examiners, exam_start)

    st_table = build_final_students_table(students)
    print(st_table)
    print()

    ex_table = build_final_examiners_table(examiners)
    print(ex_table)
    print()

    print(
        "Время с момента начала экзамена и до момента и его завершения: "
        f"{total_exam_time:.2f}"
    )

    best_students_names = get_best_students(students)
    print(
        "Имена лучших студентов:",
        ", ".join(best_students_names) if best_students_names else "-",
    )

    best_examiners_names = get_best_examiners(examiners)
    print(
        "Имена лучших экзаменаторов:",
        ", ".join(best_examiners_names) if best_examiners_names else "-",
    )

    expel_students = get_expel_students(students)
    print(
        "Имена студентов, которых после экзамена отчислят: "
        + (", ".join(expel_students) if expel_students else "-")
    )

    best_questions = get_best_questions(questions, question_stats)
    print("Лучшие вопросы: " + (", ".join(best_questions) if best_questions else "-"))

    success = is_exam_successful(students)
    print("Вывод: экзамен " + ("удался" if success else "не удался"))
