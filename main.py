# -*- coding: utf-8 -*-
from analysis import *
from update import *
from system_class import *
import os
import shutil

MIN_REVIEW = 6

while True:

    update_ = input("Would you like to update? (y/n) ")
    if update_ == 'y' or update_ == 'yes':

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        source_file = os.path.join(BASE_DIR, 'data', 'all_prof_data.json')
        backup_dir = os.path.join(BASE_DIR, 'data', 'data_copy')
        backup_file = os.path.join(backup_dir, 'all_prof_data.json')
        shutil.copy(source_file, backup_file)

        save_all_professor_data_to_json()

    elif update_ == 'n' or update_ == 'no':
        break

    else:
        print("Invalid input, please try again")

# read all data
try:
    with open("data/all_prof_data.json", "r", encoding="utf-8") as f:
        prof_data = json.load(f)
except JSONDecodeError:
    print("Failed to load local data, trying again...")
    save_all_professor_data_to_json()
    try:
        with open("data/all_prof_data.json", "r", encoding="utf-8") as f:
            prof_data = json.load(f)
    except:
        print("Error occurs, please report this")

# initialize
utm = University('utm', prof_data)
all_profs = [prof for dept in utm.departments.values() \
             for prof in dept.profs]

valid_profs = [prof for prof in all_profs \
               if prof.sample_size >= MIN_REVIEW]

# avg
C_rating = sum(p.get_avg_rate()[0] for p in valid_profs) / len(valid_profs)
C_difficulty = sum(p.get_avg_rate()[1] for p in valid_profs) / len(valid_profs)
m = sum(p.sample_size for p in valid_profs) / len(valid_profs)

# sorting: Bayesian Rating & Difficulty
sorted_by_rating = sorted(
    valid_profs,
    key=lambda p: bayesian_score(p.get_avg_rate()[0], p.sample_size, C_rating, m),
    reverse=False
)
sorted_by_difficulty = sorted(
    valid_profs,
    key=lambda p: bayesian_score(p.get_avg_rate()[1], p.sample_size, C_difficulty, m),
    reverse=True
)

# show <= 50 profs
top_n = 50
rating_names = [p.name for p in sorted_by_rating[:top_n]]
rating_scores = [
    bayesian_score(p.get_avg_rate()[0], p.sample_size, C_rating, m)
    for p in sorted_by_rating[:top_n]
]

difficulty_names = [p.name for p in sorted_by_difficulty[:top_n]]
difficulty_scores = [
    bayesian_score(p.get_avg_rate()[1], p.sample_size, C_difficulty, m)
    for p in sorted_by_difficulty[:top_n]
]

# plot
plot_prof_ranking(
    rating_names,
    rating_scores,
    f"Top worst {top_n} Professors by Bayesian Rating(accurate 2025-4) review > 5",
    "Bayesian Rating (0-5)"
)

plot_prof_ranking(
    difficulty_names,
    difficulty_scores,
    f"Top {top_n} Professors by Bayesian Difficulty(accurate 2025-4) review > 5",
    "Bayesian Difficulty (0-5)"
)

# department same logic
dept_stats = []
for dept in utm.departments.values():
    if dept.profs:
        avg_rating = sum(p.get_avg_rate()[0] for p in dept.profs) / len(dept.profs)
        avg_difficulty = sum(p.get_avg_rate()[1] for p in dept.profs) / len(dept.profs)
        dept_stats.append((dept.name, avg_rating, avg_difficulty))

# generate plots using data
sorted_by_rating = sorted(dept_stats, key=lambda x: x[1], reverse=True)
dept_names = [d[0] for d in sorted_by_rating]
dept_rating_avgs = [d[1] for d in sorted_by_rating]

plot_prof_ranking(
    dept_names,
    dept_rating_avgs,
    "Department Average Ratings",
    "Rating (0-5)"
)

sorted_by_difficulty = sorted(dept_stats, key=lambda x: x[2], reverse=True)
dept_names = [d[0] for d in sorted_by_difficulty]
dept_difficulty_avgs = [d[2] for d in sorted_by_difficulty]

plot_prof_ranking(
    dept_names,
    dept_difficulty_avgs,
    "Department Average Difficulty",
    "Difficulty (0-5)"
)

dept_input = input("Enter your department name：").strip()
plot_dept_professors_by_metric(dept_input, utm, metric="rating")
plot_dept_professors_by_metric(dept_input, utm, metric="difficulty")
