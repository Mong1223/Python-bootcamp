import time
import os
import random
import queue as pyqueue
from multiprocessing import Process, Queue
from typing import List, Dict, Tuple

from classes import Student, Examiner, Question
from files import read_students, read_examiners, read_questions
from interface_events import render_running_state_objects, render_final_state_objects


def single_student_exam_event(
    student: Student,
    examiner: Examiner,
    exam_start: float,
    questions: List[Question],
) -> Tuple[bool, float, List[int]]:
    """Экзамен для одного студента.

    Возвращает:
    - passed: сдал или нет;
    - finish_time: время от начала экзамена;
    - correct_question_ids: id вопросов, на которые студент ответил верно.
    """
    correct_answers = 0
    incorrect_answers = 0
    correct_question_ids: List[int] = []

    chosen_questions = random.sample(questions, k=min(3, len(questions)))

    for q in chosen_questions:
        # студент выбирает слово по своей вероятностной модели
        student_idx = q.student_choice(student.gender)
        # экзаменатор выбирает набор верных слов по своей модели
        correct_indices = q.examiner_choice(examiner.gender)

        if student_idx in correct_indices:
            correct_answers += 1
            correct_question_ids.append(q.id)
        else:
            incorrect_answers += 1

    # экзаменатор принимает решение с учётом настроения
    passed = examiner.pass_or_no(correct_answers, incorrect_answers)

    # Время сдачи: зависит от длины имени экзаменатора
    duration = examiner.exam_duration
    time.sleep(duration)

    finish_rel = time.time() - exam_start
    return passed, finish_rel, correct_question_ids


def examiner_worker_event(
    name: str,
    gender: str,
    exam_start: float,
    task_queue: Queue,
    event_queue: Queue,
    questions: List[Question],
    lunch_taken: bool,
) -> None:
    """Процесс-экзаменатор.

    Берёт студентов из task_queue и присылает результаты в event_queue.
    Вся логика поведения экзаменатора инкапсулирована в Examiner.
    """
    examiner_obj = Examiner(name, gender)
    examiner_obj._lunch_taken = lunch_taken

    while True:
        # Обед между студентами: один раз после 30 секунд от начала экзамена.
        examiner_obj.maybe_take_lunch(exam_start)
        if examiner_obj._lunch_taken:
            event_queue.put(
                {
                    "type": "lunch_taken",
                    "examiner": name,
                    "lunch_duration": examiner_obj.lunch_duration,
                }
            )
        try:
            student: Student = task_queue.get_nowait()
        except pyqueue.Empty:
            break

        # Сигнал «студент зашёл к экзаменатору»
        event_queue.put(
            {
                "type": "student_started",
                "examiner": name,
                "student": student.name,
            }
        )

        passed, finish_rel, correct_q_ids = single_student_exam_event(
            student,
            examiner_obj,
            exam_start,
            questions,
        )

        # Сигнал «студент закончил экзамен»
        event_queue.put(
            {
                "type": "student_finished",
                "examiner": name,
                "student": student.name,
                "passed": passed,
                "finish_time": finish_rel,
                "correct_questions": correct_q_ids,
            }
        )

    # Экзаменатор завершил работу
    event_queue.put(
        {
            "type": "examiner_finished",
            "examiner": name,
            "end_time": time.time() - exam_start,
        }
    )


def handle_student_finished_event(
    event: Dict,
    students_by_name: Dict[str, Student],
    examiners_by_name: Dict[str, Examiner],
    question_stats: Dict[int, int],
) -> None:
    """Обновление объектов Student/Examiner/статистики по событию student_finished."""
    student_name = event["student"]
    examiner_name = event["examiner"]
    passed = event["passed"]
    finish_time = event["finish_time"]
    correct_questions = event["correct_questions"]

    student = students_by_name[student_name]
    examiner = examiners_by_name[examiner_name]

    # Обновляем студента
    student.passed = passed
    student.status = "Сдал" if passed else "Провалил"
    student.time = finish_time

    # Обновляем экзаменатора
    examiner.total_students += 1
    if not passed:
        examiner.failed_students += 1
    examiner.current_student = None
    if examiner.end_time is None or finish_time > examiner.end_time:
        examiner.end_time = finish_time

    # Обновляем статистику по вопросам
    for qid in correct_questions:
        question_stats[qid] = question_stats.get(qid, 0) + 1


def load_initial_data() -> Tuple[
    List[Student],
    List[Examiner],
    List[Question],
    Dict[str, Student],
    Dict[str, Examiner],
    Dict[int, int],
    List[str],
]:
    """Читает файлы и готовит вспомогательные структуры."""

    # Вместо жестко заданных путей:
    data_dir = os.path.join("exercise1", "data")
    students_file = os.path.join(data_dir, "students.txt")
    examiners_file = os.path.join(data_dir, "examiners.txt")
    questions_file = os.path.join(data_dir, "questions.txt")

    students: List[Student] = read_students(students_file)
    examiners: List[Examiner] = read_examiners(examiners_file)
    questions: List[Question] = read_questions(questions_file)

    students_by_name: Dict[str, Student] = {s.name: s for s in students}
    examiners_by_name: Dict[str, Examiner] = {e.name: e for e in examiners}
    question_stats: Dict[int, int] = {q.id: 0 for q in questions}
    students_order: List[str] = [s.name for s in students]

    return (
        students,
        examiners,
        questions,
        students_by_name,
        examiners_by_name,
        question_stats,
        students_order,
    )


def handle_event(
    event: Dict,
    students: List[Student],
    examiners: List[Examiner],
    exam_start: float,
    students_order: List[str],
    students_by_name: Dict[str, Student],
    examiners_by_name: Dict[str, Examiner],
    question_stats: Dict[int, int],
    remaining_students: int,
    finished_examiners: int,
) -> Tuple[int, int]:
    """Обрабатывает одно событие из event_queue и возвращает обновлённые счётчики."""
    etype = event.get("type")

    if etype == "student_started":
        ex = examiners_by_name[event["examiner"]]
        ex.current_student = event["student"]

    elif etype == "student_finished":
        handle_student_finished_event(
            event,
            students_by_name,
            examiners_by_name,
            question_stats,
        )
        remaining_students -= 1

    elif etype == "examiner_finished":
        ex = examiners_by_name[event["examiner"]]
        end_time = event["end_time"]
        if ex.end_time is None or end_time > ex.end_time:
            ex.end_time = end_time
        ex.current_student = None
        finished_examiners += 1

    elif etype == "lunch_taken":
        ex = examiners_by_name[event["examiner"]]
        ex._lunch_taken = True
        ex.lunch_duration = event["lunch_duration"]

    # После обработки любого события обновляем вывод
    render_running_state_objects(students, examiners, exam_start, students_order)

    return remaining_students, finished_examiners


# --- 4. Главный цикл обработки событий ---


def event_loop(
    students: List[Student],
    examiners: List[Examiner],
    # questions: List[Question],
    students_by_name: Dict[str, Student],
    examiners_by_name: Dict[str, Examiner],
    question_stats: Dict[int, int],
    students_order: List[str],
    event_queue: Queue,
    exam_start: float,
) -> None:
    """
    Главный цикл: пока не отработали все студенты и все экзаменаторы.
    """
    remaining_students = len(students)
    finished_examiners = 0

    while remaining_students > 0 or finished_examiners < len(examiners):
        try:
            event = event_queue.get(timeout=0.5)
        except pyqueue.Empty:
            # Нет событий — просто перерисуем текущее состояние
            render_running_state_objects(
                students, examiners, exam_start, students_order
            )
            continue

        remaining_students, finished_examiners = handle_event(
            event,
            students,
            examiners,
            exam_start,
            students_order,
            students_by_name,
            examiners_by_name,
            question_stats,
            remaining_students,
            finished_examiners,
        )
        # После обработки каждого события обновляем вывод
        render_running_state_objects(students, examiners, exam_start, students_order)


def main() -> None:
    random.seed(1)

    (
        students,
        examiners,
        questions,
        students_by_name,
        examiners_by_name,
        question_stats,
        students_order,
    ) = load_initial_data()

    task_queue: Queue = Queue()
    event_queue: Queue = Queue()

    # Общая очередь задач: каждый студент один раз
    for s in students:
        task_queue.put(s)

    exam_start = time.time()

    processes: List[Process] = []
    for ex in examiners:
        p = Process(
            target=examiner_worker_event,
            args=(
                ex.name,
                ex.gender,
                exam_start,
                task_queue,
                event_queue,
                questions,
                ex.lunch_duration,
            ),
        )
        p.start()
        processes.append(p)

    # Главный цикл обработки событий
    event_loop(
        students,
        examiners,
        # questions,
        students_by_name,
        examiners_by_name,
        question_stats,
        students_order,
        event_queue,
        exam_start,
    )

    for p in processes:
        p.join()

    # Финальный вывод по объектам
    render_final_state_objects(
        students,
        examiners,
        exam_start,
        questions,
        question_stats,
    )


if __name__ == "__main__":
    main()
