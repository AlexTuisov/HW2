import time
import ex2


def timeout_exec(func, args=(), kwargs={}, timeout_duration=10, default=None):
    """This function will spawn a thread and run the given function
    using the args, kwargs and return the given default value if the
    timeout_duration is exceeded.
    """
    import threading

    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = default

        def run(self):
            # remove try if you want program to abort at error
            # try:
            self.result = func(*args, **kwargs)
            # except Exception as e:
            #    self.result = (-3, -3, e)

    it = InterruptableThread()
    it.start()
    it.join(timeout_duration)
    if it.is_alive():
        return default
    else:
        return it.result


def solve_problems(problems):
    for problem in problems:
        timeout = 300
        t1 = time.time()
        result = timeout_exec(ex2.solve_problem, args=[problem], timeout_duration=timeout)
        t2 = time.time()
        print(f'Your answer is {result}, achieved in {t2-t1} seconds')
        


def main():
    print(ex2.ids)
    """Here goes the input you want to check"""
    problems = [
        {
            "police": 0,
            "medics": 0,
            "observations": [
                (
                    ('H', '?'),
                    ('H', 'H')
                ),

                (
                    ('S', '?'),
                    ('?', 'S')
                ),
            ],

            "queries": [
                [((0, 1), 0, "H"), ((1, 0), 1, "S")]
            ]
        },

        {
            "police": 1,
            "medics": 0,
            "observations": [
                (
                    ('H', 'S'),
                    ('?', 'H')
                ),

                (
                    ('S', '?'),
                    ('?', 'S')
                ),
            ],

            "queries": [
                [((0, 1), 1, "H"), ((1, 0), 1, "S")]
            ]
        },

        {
            "police": 0,
            "medics": 0,
            "observations": [
                    (
                        ('H', '?', 'H'),
                        ('H', 'H', 'H'),
                        ('H', 'H', 'S'),
                    ),

                    (
                        ('H', 'H', 'H'),
                        ('?', 'H', 'S'),
                        ('H', 'S', 'S'),
                    ),

                    (
                        ('H', 'H', 'S'),
                        ('H', '?', 'S'),
                        ('S', 'S', 'S'),
                    ),

                    (
                        ('?', 'S', 'S'),
                        ('S', 'S', 'S'),
                        ('S', 'S', 'H'),
                    ),
                ],

            "queries": [
                ((0, 1), 0, 'H'), ((1, 0), 1, 'S'), ((1, 1), 2, 'H'), ((0, 0), 3, 'S')
            ],
        },

        {
            "police": 1,
            "medics": 0,
            "observations": [
                (
                    ('S', 'H', 'U'),
                    ('H', 'H', 'H'),
                    ('U', 'H', 'S'),
                ),

                (
                    ('S', 'S', 'U'),
                    ('S', 'H', 'S'),
                    ('U', 'S', 'Q'),
                ),

                (
                    ('?', 'S', 'U'),
                    ('S', 'S', 'S'),
                    ('U', 'S', 'Q'),
                ),
            ],

            "queries": [
                ((0, 0), 2, 'H')
            ],

        },

        {
            "police": 0,
            "medics": 0,
            "observations": [
                (
                    ('H', 'H', 'H', 'H'),
                    ('H', 'S', 'U', 'H'),
                    ('H', 'H', 'H', '?'),
                    ('H', 'H', 'S', 'S'),
                ),

                (
                    ('H', 'S', 'H', 'H'),
                    ('S', 'S', 'U', 'H'),
                    ('H', 'S', 'S', 'U'),
                    ('?', 'S', 'S', 'S'),
                ),
            ],

            "queries": [
                ((2, 3), 0, 'H'), ((3, 0), 1, 'H')
            ],
        },

        {
            "police": 0,
            "medics": 1,
            "observations": [
                (
                    ('H', 'H', 'H', 'H'),
                    ('H', 'S', 'U', 'H'),
                    ('U', 'S', 'S', 'U'),
                    ('H', 'S', 'H', 'H'),
                ),

                (
                    ('H', 'S', 'H', 'I'),
                    ('S', 'S', 'U', 'H'),
                    ('U', '?', 'S', 'U'),
                    ('S', 'S', 'S', 'H'),
                ),

                (
                    ('H', 'S', 'I', 'I'),
                    ('S', 'S', 'U', '?'),
                    ('U', 'S', 'S', 'U'),
                    ('?', 'S', 'S', 'S')
                ),

            ],

            "queries": [
                ((2, 1), 1, 'U'), ((1, 3), 2, 'I'), ((3, 0), 2, 'S')
            ],
        },

        {
            "police": 0,
            "medics": 0,
            "observations": [
                (
                    ('H', 'S'),
                    ('H', 'H'),
                ),

                (
                    ('S', 'S'),
                    ('H', 'S'),
                ),

                (
                    ('S', 'S'),
                    ('S', 'S'),
                ),

                (
                    ('S', 'H'),
                    ('S', 'S'),
                ),

                (
                    ('?', '?'),
                    ('?', '?'),
                ),

            ],

            "queries": [
                ((0, 0), 4, 'H'), ((1, 0), 4, 'S')
            ],
        },
        ########################################
        {
            "police": 0,
            "medics": 0,
            "observations": [

                (
                    ('?', 'H'),
                    ('H', 'H'),
                ),

                (
                    ('H', 'H'),
                    ('H', 'H'),
                ),

            ],
            "queries": [((0, 0), 0, 'S'), ],
        },

        {
            "police": 0,
            "medics": 0,
            "observations": [
                (
                    ('S', '?', 'S'),
                    ('H', 'S', 'H'),
                    ('H', 'H', 'H'),
                ),

                (
                    ('S', 'S', 'S'),
                    ('S', 'S', 'S'),
                    ('H', 'S', 'H'),
                ),
            ],
            "queries": [((0, 1), 0, 'S'), ],
        },

        {
            "police": 1,
            "medics": 0,
            "observations": [
                (
                    ('H', 'H', 'S'),
                    ('S', 'H', 'S'),
                    ('H', 'H', 'H'),
                ),

                (
                    ('S', 'S', 'S'),
                    ('S', 'S', '?'),
                    ('S', 'H', 'H'),
                ),

                (
                    ('S', 'Q', 'S'),
                    ('S', 'S', '?'),
                    ('?', 'S', 'H'),
                ),
            ],
            "queries": [((1, 2), 1, 'S'), ((2, 0), 2, 'S')],
        },

        {
            "police": 0,
            "medics": 1,
            "observations": [

                (
                    ('?', '?'),
                    ('?', '?'),
                ),

                (
                    ('H', 'H'),
                    ('I', 'H'),
                ),

            ],
            "queries": [((0, 0), 0, 'H'), ((0, 1), 0, 'H'), ((1, 0), 0, 'H'), ((1, 1), 0, 'H')],
        },

        {
            "police": 0,
            "medics": 1,
            "observations": [
                (
                    ('S', 'H', 'S'),
                    ('H', 'H', 'H'),
                    ('?', 'H', 'S'),
                ),

                (
                    ('S', 'S', 'S'),
                    ('S', 'I', 'S'),
                    ('?', 'S', 'S'),
                ),
            ],
            "queries": [((2, 0), 1, 'S'), ],
        },

        {
            "police": 1,
            "medics": 1,
            "observations": [
                (
                    ('S', 'S', 'H', 'H'),
                    ('H', 'H', 'H', '?'),
                    ('H', 'S', 'H', 'H'),
                ),

                (
                    ('S', 'S', 'S', 'H'),
                    ('S', 'S', 'H', '?'),
                    ('S', 'Q', 'H', 'H'),
                ),
            ],
            "queries": [((1, 3), 0, 'H'), ((1, 3), 1, 'H')],
        },






    ]
    solve_problems(problems)


if __name__ == '__main__':
    main()