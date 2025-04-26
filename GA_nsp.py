import numpy as np
import random


class NurseSchedulingProblem:
    """This class encapsulates the Nurse Scheduling problem"""

    def __init__(self, hardConstraintPenalty):
        """
        :param hardConstraintPenalty: the penalty factor for a hard-constraint violation
        """
        self.hardConstraintPenalty = hardConstraintPenalty

        # list of nurses:
        self.nurses = ["A", "B", "C", "D", "E", "F", "G", "H"]

        # nurses' respective shift preferences - morning, evening, night:
        self.shiftPreference = [
            [1, 0, 0],
            [1, 1, 0],
            [0, 0, 1],
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1],
            [0, 1, 1],
            [1, 1, 1],
        ]

        # min and max number of nurses allowed for each shift - morning, evening, night:
        self.shiftMin = [2, 2, 1]
        self.shiftMax = [3, 4, 2]

        # max shifts per week allowed for each nurse
        self.maxShiftsPerWeek = 5

        # number of weeks we create a schedule for:
        self.weeks = 1

        # useful values:
        self.shiftPerDay = len(self.shiftMin)
        self.shiftsPerWeek = 7 * self.shiftPerDay

    def __len__(self):
        """
        :return: the number of shifts in the schedule
        """
        return len(self.nurses) * self.shiftsPerWeek * self.weeks

    def getCost(self, schedule):
        """
        Calculates the total cost of the various violations in the given schedule
        ...
        :param schedule: a list of binary values describing the given schedule
        :return: the calculated cost
        """

        if len(schedule) != self.__len__():
            raise ValueError(
                "size of schedule list should be equal to ", self.__len__()
            )

        # convert entire schedule into a dictionary with a separate schedule for each nurse:
        nurseShiftsDict = self.getNurseShifts(schedule)

        # count the various violations:
        consecutiveShiftViolations = self.countConsecutiveShiftViolations(
            nurseShiftsDict
        )
        shiftsPerWeekViolations = self.countShiftsPerWeekViolations(nurseShiftsDict)[1]
        nursesPerShiftViolations = self.countNursesPerShiftViolations(nurseShiftsDict)[
            1
        ]
        shiftPreferenceViolations = self.countShiftPreferenceViolations(nurseShiftsDict)

        # calculate the cost of the violations:
        hardContstraintViolations = (
            consecutiveShiftViolations
            + nursesPerShiftViolations
            + shiftsPerWeekViolations
        )
        softContstraintViolations = shiftPreferenceViolations

        return (
            self.hardConstraintPenalty * hardContstraintViolations
            + softContstraintViolations
        )

    def getNurseShifts(self, schedule):
        """
        Converts the entire schedule into a dictionary with a separate schedule for each nurse
        :param schedule: a list of binary values describing the given schedule
        :return: a dictionary with each nurse as a key and the corresponding shifts as the value
        """
        shiftsPerNurse = self.__len__() // len(self.nurses)
        nurseShiftsDict = {}
        shiftIndex = 0

        for nurse in self.nurses:
            nurseShiftsDict[nurse] = schedule[shiftIndex : shiftIndex + shiftsPerNurse]
            shiftIndex += shiftsPerNurse

        return nurseShiftsDict

    def countConsecutiveShiftViolations(self, nurseShiftsDict):
        """
        Counts the consecutive shift violations in the schedule
        :param nurseShiftsDict: a dictionary with a separate schedule for each nurse
        :return: count of violations found
        """
        violations = 0
        # iterate over the shifts of each nurse:
        for nurseShifts in nurseShiftsDict.values():
            # look for two cosecutive '1's:
            for shift1, shift2 in zip(nurseShifts, nurseShifts[1:]):
                if shift1 == 1 and shift2 == 1:
                    violations += 1
        return violations

    def countShiftsPerWeekViolations(self, nurseShiftsDict):
        """
        Counts the max-shifts-per-week violations in the schedule
        :param nurseShiftsDict: a dictionary with a separate schedule for each nurse
        :return: count of violations found
        """
        violations = 0
        weeklyShiftsList = []
        # iterate over the shifts of each nurse:
        for nurseShifts in nurseShiftsDict.values():  # all shifts of a single nurse
            # iterate over the shifts of each weeks:
            for i in range(0, self.weeks * self.shiftsPerWeek, self.shiftsPerWeek):
                # count all the '1's over the week:
                weeklyShifts = sum(nurseShifts[i : i + self.shiftsPerWeek])
                weeklyShiftsList.append(weeklyShifts)
                if weeklyShifts > self.maxShiftsPerWeek:
                    violations += weeklyShifts - self.maxShiftsPerWeek

        return weeklyShiftsList, violations

    def countNursesPerShiftViolations(self, nurseShiftsDict):
        """
        Counts the number-of-nurses-per-shift violations in the schedule
        :param nurseShiftsDict: a dictionary with a separate schedule for each nurse
        :return: count of violations found
        """
        # sum the shifts over all nurses:
        totalPerShiftList = [sum(shift) for shift in zip(*nurseShiftsDict.values())]

        violations = 0
        # iterate over all shifts and count violations:
        for shiftIndex, numOfNurses in enumerate(totalPerShiftList):
            dailyShiftIndex = (
                shiftIndex % self.shiftPerDay
            )  # -> 0, 1, or 2 for the 3 shifts per day
            if numOfNurses > self.shiftMax[dailyShiftIndex]:
                violations += numOfNurses - self.shiftMax[dailyShiftIndex]
            elif numOfNurses < self.shiftMin[dailyShiftIndex]:
                violations += self.shiftMin[dailyShiftIndex] - numOfNurses

        return totalPerShiftList, violations

    def countShiftPreferenceViolations(self, nurseShiftsDict):
        """
        Counts the nurse-preferences violations in the schedule
        :param nurseShiftsDict: a dictionary with a separate schedule for each nurse
        :return: count of violations found
        """
        violations = 0
        for nurseIndex, shiftPreference in enumerate(self.shiftPreference):
            # duplicate the shift-preference over the days of the period
            preference = shiftPreference * (self.shiftsPerWeek // self.shiftPerDay)
            # iterate over the shifts and compare to preferences:
            shifts = nurseShiftsDict[self.nurses[nurseIndex]]
            for pref, shift in zip(preference, shifts):
                if pref == 0 and shift == 1:
                    violations += 1

        return violations

    def printScheduleInfo(self, schedule):
        """
        Prints the schedule and violations details
        :param schedule: a list of binary values describing the given schedule
        """
        nurseShiftsDict = self.getNurseShifts(schedule)

        print("Schedule for each nurse:")
        for nurse in nurseShiftsDict:  # all shifts of a single nurse
            print(nurse, ":", nurseShiftsDict[nurse])

        print(
            "consecutive shift violations = ",
            self.countConsecutiveShiftViolations(nurseShiftsDict),
        )
        print()

        weeklyShiftsList, violations = self.countShiftsPerWeekViolations(
            nurseShiftsDict
        )
        print("weekly Shifts = ", weeklyShiftsList)
        print("Shifts Per Week Violations = ", violations)
        print()

        totalPerShiftList, violations = self.countNursesPerShiftViolations(
            nurseShiftsDict
        )
        print("Nurses Per Shift = ", totalPerShiftList)
        print("Nurses Per Shift Violations = ", violations)
        print()

        shiftPreferenceViolations = self.countShiftPreferenceViolations(nurseShiftsDict)
        print("Shift Preference Violations = ", shiftPreferenceViolations)
        print()


# testing the class:
def main():
    # create a problem instance:
    nurses = NurseSchedulingProblem(10)

    randomSolution = np.random.randint(2, size=len(nurses))
    print("Random Solution = ")
    print(randomSolution)
    print(f"Size of schedule{len(randomSolution)}")
    print()

    nurses.printScheduleInfo(randomSolution)

    print("Total Cost = ", nurses.getCost(randomSolution))


class Genetic_Algorithm:
    """This class encapsulates the Genetic Algorithm"""

    def genetic_algorithm(
        problem,
        population_size=50,
        generations=100,
        crossover_rate=0.8,
        mutation_rate=0.01,
    ):
        """
        使用簡單的遺傳演算法來最佳化護理人員排班問題
        :param problem: NurseSchedulingProblem 物件
        :param population_size: 初始族群大小
        :param generations: 執行的世代數量
        :param crossover_rate: 執行交配的機率
        :param mutation_rate: 執行突變的機率
        :return: 最佳解與其成本
        """
        chromosome_length = len(problem)

        # 1. 初始化族群（隨機產生初始解）
        population = [
            np.random.randint(2, size=chromosome_length).tolist()
            for _ in range(population_size)
        ]

        for gen in range(generations):
            # 2. 評估每個解的成本（成本越低越好）
            population = sorted(population, key=lambda sol: problem.getCost(sol))
            best = population[0]
            best_cost = problem.getCost(best)
            print(f"Generation {gen + 1}: Best Cost = {best_cost}")

            # 3. 精英保留（保留最好的個體）
            new_population = [best]

            # 4. 交配產生下一代
            while len(new_population) < population_size:
                # 選擇兩個父母（使用輪盤選擇法或前幾名挑選）
                parent1 = Genetic_Algorithm.tournament_selection(
                    population, problem, k=3
                )
                parent2 = Genetic_Algorithm.tournament_selection(
                    population, problem, k=3
                )

                # 進行交配（crossover）
                if random.random() < crossover_rate:
                    child1, child2 = Genetic_Algorithm.single_point_crossover(
                        parent1, parent2
                    )
                else:
                    child1, child2 = parent1[:], parent2[:]

                # 突變（mutation）
                child1 = Genetic_Algorithm.mutate(child1, mutation_rate)
                child2 = Genetic_Algorithm.mutate(child2, mutation_rate)

                # 加入新族群
                new_population.extend([child1, child2])

            population = new_population[:population_size]  # 裁切到原本大小

        # 最終回傳最佳解
        best = min(population, key=lambda sol: problem.getCost(sol))
        return best, problem.getCost(best)

    # ✅ 輔助函數：單點交配
    def single_point_crossover(parent1, parent2):
        point = random.randint(1, len(parent1) - 2)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2

    # ✅ 輔助函數：突變（隨機翻轉位元）
    def mutate(solution, mutation_rate):
        return [bit if random.random() > mutation_rate else 1 - bit for bit in solution]

    # ✅ 輔助函數：錦標賽選擇法
    def tournament_selection(population, problem, k=3):
        candidates = random.sample(population, k)
        return min(candidates, key=lambda sol: problem.getCost(sol))


if __name__ == "__main__":
    main()
