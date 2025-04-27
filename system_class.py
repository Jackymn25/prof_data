class CourseUnderProf:
    """
    A course class by a single prof.
    """
    course_code: str
    rating: int
    difficulty: int
    size: int

    def __init__(self, course_code) -> None:
        """
        Initializer
        """
        self.course_code = course_code
        self.rating = 0
        self.difficulty = 0
        self.size = 0

    def update(self, rate, difficulty):
        """
        Update by a single data(comment)
        """
        self.size += 1
        self.rating += rate
        self.difficulty += difficulty

    def get_avg_rate(self) -> tuple[float, float]:
        return (self.rating / self.size,
                self.difficulty / self.size)


class ProfData:
    """
    A prof data, including id, name, department...
    """
    course_map: dict[str, CourseUnderProf]
    rating: int
    difficulty: int
    sample_size: int
    name: str
    department: str
    comments: list

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.department = data['department']
        self.sample_size = len(data['comments'])
        self.rating = 0
        self.difficulty = 0
        self.comments = []
        self.course_map = {}
        # self.raw_comments = data['comments']

        for single_rate in data['comments']:
            clarity = single_rate["clarityRating"]
            difficulty = single_rate["difficultyRating"]
            self.rating += clarity
            self.difficulty += difficulty
            self.comments.append(single_rate["comment"])

            course_name = single_rate["class"][:7]
            if course_name not in self.course_map:
                self.course_map[course_name] = CourseUnderProf(course_name)
            self.course_map[course_name].update(clarity, difficulty)

        self.course = list(self.course_map.values())

    def get_avg_rate(self):
        if self.sample_size == 0:
            return 0.0, 0.0
        return self.rating / self.sample_size, self.difficulty / self.sample_size


class Department:
    """
    A department containing profs.
    """
    name: str
    profs: list[ProfData]
    def __init__(self, name):
        self.name = name
        self.profs = []

    def update_prof(self, prof_data):
        self.profs.append(ProfData(prof_data))


class University:
    """
    A university containing all departments.
    """
    name: str
    departments: dict[str, Department]

    def __init__(self, name, data):
        self.name = name
        self.departments = {}

        for prof in data:
            dept_name = prof['department']
            if dept_name not in self.departments:
                self.departments[dept_name] = Department(dept_name)
            self.departments[dept_name].update_prof(prof)

    def get_all_departments(self):
        return list(self.departments.values())
