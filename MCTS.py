import random
import math
from collections import defaultdict

from constants import DAYS_WEEK_ABB, DAYS_WEEK
import penalty


class NurseSchedulerMCTS:
    def __init__(self, scenario, week_data, history_data=None):
        self.scenario = scenario
        self.week_data = week_data
        self.history_data = history_data
        
        # 初始化基本參數
        self.nurses = scenario["nurses"]
        self.shift_types = [s["id"] for s in scenario["shiftTypes"]]
        self.forbidden_successions = scenario["forbiddenShiftTypeSuccessions"]
        
        # 初始化其他必要參數
        self.shift_requirements = self._build_shift_requirements()
        self.nurse_history = self._build_nurse_history()
        self.off_requests = self._build_off_requests()

    def _build_shift_requirements(self):
        """Build requirements for the number of persons needed per day per skill per shift"""
        shift_requirements = {day: {} for day in DAYS_WEEK_ABB}
        for req in self.week_data["requirements"]:
            shift = req["shiftType"]
            skill = req["skill"]
            for day in DAYS_WEEK:
                day_key = f"requirementOn{day}"
                if day_key in req:
                    minimum_required = req[day_key]["minimum"]
                    if minimum_required > 0:
                        shift_requirements[day[:3]][(shift, skill)] = minimum_required
        print("Finish building shift_requirements")
        return shift_requirements

    def _build_nurse_history(self):
        """Build nurse history from history data"""
        nurse_history = []
        nurses_lastday_from_lastweek = dict()
        if self.history_data:
            nurse_history = self.history_data["nurseHistory"]
            nurses_lastday_from_lastweek = {
                data["nurse"]: data["lastAssignedShiftType"]
                for data in self.history_data["nurseHistory"]
            }
        print("Finish building nurse_history")
        return nurse_history, nurses_lastday_from_lastweek

    def _build_off_requests(self):
        """Build off requests for S4"""
        off_requests = set()
        for req in self.week_data.get("shiftOffRequests", []):
            off_requests.add((req["nurse"], req["day"][0:3], req["shiftType"]))
        print("Finish building off_requests")
        return off_requests

    def calculate_state_penalty(self, state):
        """Calculate penalty for current state"""
        if not state["schedule"]:
            return float('inf')
        
        # Convert schedule to assignments format
        assignments = []
        for nurse_id, schedule in state["schedule"].items():
            for day, shift in schedule.items():
                # Find a valid skill for this shift
                nurse = next(n for n in self.nurses if n["id"] == nurse_id)
                valid_skills = [s for s in nurse["skills"] if (shift, s) in self.shift_requirements.get(day, {})]
                if valid_skills:
                    assignments.append({
                        "nurse": nurse_id,
                        "day": day,
                        "shiftType": shift,
                        "skill": valid_skills[0]
                    })

        # Calculate penalties
        h1 = penalty.calculate_h1_penalty(assignments)
        h3 = penalty.calculate_h3_penalty(assignments, self.forbidden_successions, self.nurse_history[1])
        s2_s3_s5 = penalty.calculate_s2_s3_s5_penalty(assignments, self.nurses, self.scenario, self.nurse_history[0])
        s4 = penalty.calculate_s4_penalty(assignments, self.week_data)
        
        print(f"h1: {h1}, h3: {h3}, s2_s3_s5: {s2_s3_s5}, s4: {s4}")
        return h1 + h3 + s2_s3_s5 + s4

    class MCTSNode:
        def __init__(self, state, parent=None, action=None, scheduler=None):
            self.state = state
            self.parent = parent
            self.action = action
            self.scheduler = scheduler  # 添加對 NurseSchedulerMCTS 實例的引用
            self.children = []
            self.visits = 0
            self.value = 0
            self.untried_actions = self.get_untried_actions()

        def get_untried_actions(self):
            """
            Get all possible actions(feasible combinations of shift type and skill) next day 
            from current state (based on current day and nurse).
            """
            actions = []
            nurse_id = self.state["current_nurse"]
            current_day = self.state["current_day"]
            
            # Get nurse's skills
            nurse = next(n for n in self.scheduler.nurses if n["id"] == nurse_id)
            nurse_skills = nurse["skills"]
            
            # Get previous shift for H3 check
            prev_shift = None
            if current_day == "Mon" and self.scheduler.history_data:
                prev_shift = self.scheduler.nurse_history[1].get(nurse_id)
            elif current_day != "Mon":
                prev_day_idx = DAYS_WEEK_ABB.index(current_day) - 1
                prev_day = DAYS_WEEK_ABB[prev_day_idx]
                prev_shift = self.state["schedule"].get(nurse_id, {}).get(prev_day)

            # Check each possible shift and skill combination
            for shift in self.scheduler.shift_types:
                # Check H3: Forbidden successions
                if prev_shift:
                    forbidden = any(
                        rule["precedingShiftType"] == prev_shift
                        and shift in rule["succeedingShiftTypes"]
                        for rule in self.scheduler.forbidden_successions
                    )
                    if forbidden:
                        continue

                # Check if shift is needed
                for skill in nurse_skills:
                    if (shift, skill) in self.scheduler.shift_requirements.get(current_day, {}):
                        # Check S4: Preferences
                        if (nurse_id, current_day, shift) in self.scheduler.off_requests or (nurse_id, current_day, "Any") in self.scheduler.off_requests:
                            continue
                        actions.append((current_day, shift, skill))
            
            return actions

        def select_child(self, exploration_weight=1.4):
            """Select child using UCB1(Upper Confidence Bound for 1-ply) formula"""
            return max(self.children, key=lambda c: c.value/c.visits + 
                      exploration_weight * math.sqrt(2 * math.log(self.visits) / c.visits))

        def expand(self):
            """Expand the tree by adding a new child"""
            action = random.choice(self.untried_actions)
            self.untried_actions.remove(action)
            
            # Create new state
            new_state = self.state.copy()
            new_state["schedule"] = self.state["schedule"].copy()
            new_state["schedule"].setdefault(self.state["current_nurse"], {})[action[0]] = action[1]
            
            # Move to next day or next nurse
            if action[0] == DAYS_WEEK_ABB[-1]:  # Last day of week
                nurse_idx = self.scheduler.nurses.index(next(n for n in self.scheduler.nurses if n["id"] == self.state["current_nurse"]))
                if nurse_idx == len(self.scheduler.nurses) - 1:  # Last nurse
                    new_state["current_nurse"] = None
                else:
                    new_state["current_nurse"] = self.scheduler.nurses[nurse_idx + 1]["id"]
                new_state["current_day"] = DAYS_WEEK_ABB[0]
            else:
                new_state["current_day"] = DAYS_WEEK_ABB[DAYS_WEEK_ABB.index(action[0]) + 1]
            
            # 創建子節點時，傳入 scheduler 實例
            child = self.scheduler.MCTSNode(new_state, self, action, self.scheduler)
            self.children.append(child)
            return child

        def update(self, value):
            """Update node statistics"""
            self.visits += 1
            self.value += value

    def mcts_search(self, nurse_id, max_iterations=3):
        """
        Perform MCTS search for a single nurse
        """
        root_state = {
            "current_nurse": nurse_id,
            "current_day": DAYS_WEEK_ABB[0],
            "schedule": defaultdict(dict)
        }
        # 創建根節點時傳入 scheduler 實例
        root = self.MCTSNode(root_state, scheduler=self)
        
        for i in range(max_iterations):
            print("-"*100)
            print(f"Iteration {i+1}/{max_iterations}")
            node = root

            # 1. Selection
            while node.untried_actions == [] and node.children != []:
                # Walk through the tree to find the node with untried actions
                node = node.select_child()

            # 2. Expansion
            # If the node has untried actions, expand it
            if node.untried_actions:
                node = node.expand()

            current_state = node.state.copy()
            # e.g., 
            # current_state =
            # { 
            #   "current_nurse": "n002",
            #   "current_day": "Tue",
            #   "schedule": {
            #     "n002": {"Mon": "D"}
            #   }
            # }
            
            # 3. Simulation
            while True:
                print(">> Simulating.......................................................................")
                # Break if all nurses are scheduled
                if current_state["current_nurse"] is None:
                    break
                print(f"Current state: {current_state}")
                    
                # Get current day and nurse
                current_day = current_state["current_day"]
                current_nurse = current_state["current_nurse"]
                
                # Get nurse's skills
                nurse = next(n for n in self.nurses if n["id"] == current_nurse)
                nurse_skills = nurse["skills"]
                
                # Get previous shift
                prev_shift = None
                if current_day == "Mon" and self.history_data:
                    prev_shift = self.nurse_history[1].get(current_nurse)
                elif current_day != "Mon":
                    prev_day_idx = DAYS_WEEK_ABB.index(current_day) - 1
                    prev_day = DAYS_WEEK_ABB[prev_day_idx]
                    prev_shift = current_state["schedule"].get(current_nurse, {}).get(prev_day)
                
                # 生成可用動作: 
                available_actions = []
                for shift in self.shift_types:
                    # 檢查 H3: 禁止的班次連續
                    if prev_shift:
                        forbidden = any(
                            rule["precedingShiftType"] == prev_shift
                            and shift in rule["succeedingShiftTypes"]
                            for rule in self.forbidden_successions
                        )
                        if forbidden:
                            continue
                    
                    # 檢查是否需要這個班次
                    for skill in nurse_skills:
                        if (shift, skill) in self.shift_requirements.get(current_day, {}):
                            # 檢查 S4: 偏好
                            if (current_nurse, current_day, shift) in self.off_requests or (current_nurse, current_day, "Any") in self.off_requests:
                                continue
                            available_actions.append((current_day, shift, skill))
                
                if not available_actions:
                    break
                print(f"Available actions: {available_actions}")
                
                # 隨機選擇一個動作
                action = random.choice(available_actions)
                print(f"Action: {action}")
                
                action_day = action[0]
                action_shift = action[1]
                
                # 更新排班
                if current_nurse not in current_state["schedule"]:
                    current_state["schedule"][current_nurse] = {}
                current_state["schedule"][current_nurse][action_day] = action_shift
                
                # 更新下一天
                if action_day == DAYS_WEEK_ABB[-1]:  # 如果是週末
                    # 找到下一個護士
                    current_nurse_idx = next(i for i, n in enumerate(self.nurses) 
                                          if n["id"] == current_nurse)
                    if current_nurse_idx == len(self.nurses) - 1:  # 最後一個護士
                        current_state["current_nurse"] = None
                    else:
                        current_state["current_nurse"] = self.nurses[current_nurse_idx + 1]["id"]
                    current_state["current_day"] = DAYS_WEEK_ABB[0]
                else:
                    current_state["current_day"] = DAYS_WEEK_ABB[DAYS_WEEK_ABB.index(action_day) + 1]
                
                print()
            
            print(">> (Break the simulation loop)")
            print(f"Final state: {current_state}")

            # 4. Backpropagation
            print("Start backpropagation...")
            value = -self.calculate_state_penalty(current_state)  # Negative because we want to minimize penalty
            current_node = node
            # debug?
            while current_node is not None:
                current_node.update(value)
                current_node = current_node.parent
        
        # Return best child's schedule
        if root.children:
            best_child = max(root.children, key=lambda c: c.value/c.visits)
            return best_child.state["schedule"][nurse_id]
        return {}

    def schedule(self):
        """Generate schedule for all nurses"""
        final_schedule = defaultdict(dict)
        for nurse in self.nurses:
            print("-"*100)
            print(f"\nScheduling nurse {nurse['id']}")
            nurse_schedule = self.mcts_search(nurse["id"])
            if nurse_schedule:  # 只有當有排班結果時才更新 debug: 這邊應該要改成 min nurse_schedule penalty
                final_schedule[nurse["id"]].update(nurse_schedule)

        # Convert schedule to assignments format
        assignments = []
        for nurse_id, schedule in final_schedule.items():
            for day, shift in schedule.items():
                # Find a valid skill for this shift
                nurse = next(n for n in self.nurses if n["id"] == nurse_id)
                valid_skills = [s for s in nurse["skills"] if (shift, s) in self.shift_requirements.get(day, {})]
                if valid_skills:
                    assignments.append({
                        "nurse": nurse_id,
                        "day": day,
                        "shiftType": shift,
                        "skill": valid_skills[0]
                    })

        return assignments