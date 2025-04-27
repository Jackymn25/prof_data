from system_class import *
from update import *
import json
import difflib
import matplotlib.pyplot as plt


# bayesian method
def bayesian_score(avg, n, C, m):
    return (n / (n + m)) * avg + (m / (n + m)) * C


# ploting
def plot_prof_ranking(names, scores, title, xlabel):
    bar_height = 0.35
    height = max(6, bar_height * len(names))
    plt.figure(figsize=(12, height))
    plt.barh(names[:], scores[:])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.xlim(0, 5)
    plt.tight_layout()
    plt.show()


def get_department_by_fuzzy_name(utm, query):
    """Match department"""
    all_names = list(utm.departments.keys())
    matches = difflib.get_close_matches(query.lower(),
                                        [name.lower() for name in all_names],
                                        n=1,
                                        cutoff=0.4)

    # find the name
    for name in all_names:
        if name.lower() == matches[0]:
            return utm.departments[name]
    return None

def plot_dept_professors_by_difficulty(dept_name, utm, min_reviews=6):
    dept = get_department_by_fuzzy_name(utm, dept_name)
    if not dept:
        return

    profs_in_dept = [p for p in dept.profs if p.sample_size >= min_reviews]
    if not profs_in_dept:
        return

    C_difficulty = sum(p.get_avg_rate()[1] for p in profs_in_dept) / len(profs_in_dept)
    m = sum(p.sample_size for p in profs_in_dept) / len(profs_in_dept)

    # sorting
    sorted_profs = sorted(
        profs_in_dept,
        key=lambda p: bayesian_score(p.get_avg_rate()[1],
                                     p.sample_size, C_difficulty, m),
        reverse=True
    )
    names = [p.name for p in sorted_profs]
    scores = [bayesian_score(p.get_avg_rate()[1], p.sample_size,
                             C_difficulty, m) for p in sorted_profs]

    # plot
    plot_prof_ranking(
        names,
        scores,
        f"{dept.name} - Professors by Bayesian Difficulty (≥{min_reviews} reviews)",
        "Bayesian Difficulty (0-5)"
    )


def plot_dept_professors_by_metric(dept_name, utm, metric="difficulty",
                                   min_reviews=6):
    """
    metric: "difficulty" or "rating"
    """

    # Matches department
    all_names = list(utm.departments.keys())
    matches = difflib.get_close_matches(dept_name.lower(), [name.lower() for name in all_names], n=1, cutoff=0.4)
    if not matches:
        return

    matched_name = next(name for name in all_names if name.lower() == matches[0])
    dept = utm.departments[matched_name]

    # filtering
    profs_in_dept = [p for p in dept.profs if p.sample_size >= min_reviews]
    if not profs_in_dept:
        return

    if metric == "difficulty":
        C = sum(p.get_avg_rate()[1] for p in profs_in_dept) / len(profs_in_dept)
        key_fn = lambda p: p.get_avg_rate()[1]
        label = "Bayesian Difficulty (0-5)"
    elif metric == "rating":
        C = sum(p.get_avg_rate()[0] for p in profs_in_dept) / len(profs_in_dept)
        key_fn = lambda p: p.get_avg_rate()[0]
        label = "Bayesian Rating (0-5)"
    else:
        raise ValueError("metric peremetre can only be 'rating' or 'difficulty'")

    m = sum(p.sample_size for p in profs_in_dept) / len(profs_in_dept)
    if metric == "rating":

        sorted_profs = sorted(
            profs_in_dept,
            key=lambda p: bayesian_score(key_fn(p), p.sample_size, C, m),
            reverse=False
        )
    else:
        sorted_profs = sorted(
            profs_in_dept,
            key=lambda p: bayesian_score(key_fn(p), p.sample_size, C, m),
            reverse=True
        )
    names = [p.name for p in sorted_profs]
    scores = [bayesian_score(key_fn(p), p.sample_size, C, m) for p in sorted_profs]

    # plots
    plot_prof_ranking(
        names,
        scores,
        f"{matched_name} - Professors by Bayesian {metric.title()} (≥{min_reviews} reviews)",
        label
    )
