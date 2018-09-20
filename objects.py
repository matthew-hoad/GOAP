import random
import city
import copy
import pygame
from operator import itemgetter
import time

class Bank:
    def __init__(self, balance):
        self.balance = 0

class Action:
    def __init__(self, name, task, preconditions={}, costs={}):
        self.name = name
        self.costs = costs
        self.preconditions = preconditions # dict
        self.task = task # a function

    def benefit_type(self):
        for c_type, c in self.costs.items():
            if 'Add' in c:
                return c_type

    def cost_type(self):
        for c_type, c in self.costs.items():
            if 'Sub' in c:
                return c_type

    def precondition_type(self):
        for p_type, p in self.preconditions.items():
            if 'Min' in p:
                return p_type

    def __hash__(self):
        return hash((self.name,))

    def __eq__(self, other):
        return (self.name) == (other.name)

    def __ne__(self, other):
        return not(self == other)


class Goal:
    def __init__(self, name, preconditions):
        self.name = name
        self.preconditions = preconditions

    def precondition_type(self):
        for p_type, p in self.preconditions.items():
            if 'Min' in p:
                return p_type

        # keepHouse = Goal('Keep house', {'money':('Min', 1000), 'energy': ('Min', 1)})


class Ant:
    def __init__(self, seed, RS, WS, world=None):
        self.seed = seed
        self.randomgen = random.seed(seed)
        # self.mood = random.randint(0, numMoods)
        self.strength = random.randint(1, 10)
        self.perception = random.randint(1, 10)
        self.endurance = random.randint(1, 10)
        self.charisma = random.randint(1, 10)
        self.intelligence = random.randint(1, 10)
        self.agilty = random.randint(1, 10)
        self.luck = random.randint(1, 10)

        self.homex = RS.x
        self.homey = RS.y
        self.workx = WS.x
        self.worky = WS.y

        self.world = world

        self.money = 0# random.randint(50, 500)
        self.energy = 100# random.randint(0, 100)

        self.stateDict = self.set_state()

        self.target = ()
        self.next_point = ()

        self.x = self.homex
        self.y = self.homey

        self.path = None
        # self.xv = 0
        # self.yv = 0
        self.waiting = False
        self.actions = []
        self.goals = []
        self.actionStack = []
        self.set_state()
        self.action = None
        self.set_goals_and_actions()

    def get_action_from_name(self, name):
        for action in self.actions:
            if action.name == name:
                return action

    def set_state(self):
        self.stateDict = {'money': self.money, 'energy': self.energy}
        return 1

    def get_next_point(self):
        # print('movement path before get_next_point =', self.path)
        if self.path != None and self.path != []:
            next_tile = self.world.get_tile_from_id(self.path.pop())
            self.next_point = (next_tile.x, next_tile.y)
            # print('Next point =', self.next_point.x, self.next_point.y)
        else:
            self.path = city.get_shortest_path(self.world.G, self.world.get_tile_id((self.x, self.y)), self.world.get_tile_id((self.target[0], self.target[1])))
            self.path.reverse()
            next_tile = self.world.get_tile_from_id(self.path.pop())
            self.next_point = (next_tile.x, next_tile.y)
            # print('Next point =', self.next_point.x, self.next_point.y)
        # time.sleep(1)
        # print('movement path after get_next_point =', self.path)
        # print((self.x, self.y), city.ttc(path[0], self.rl), city.ttc(path[1], self.rl))
        # if path is not None:
        # 	self.next_point = city.ttc(path[1], self.rl)
        # else:
        # 	self.next_point = (self.x, self.y)

    def move(self):
        self.get_next_point()
        # print('current pos =', self.x, self.y)
        # print('next_point =', self.next_point)
        self.x, self.y = self.next_point[0], self.next_point[1]

    def do_work(self):
        # print(self.seed, 'in do_work function')
        energyToWork = 1
        wage = 5
        self.target = (self.workx+1, self.worky)
        current_action = self.get_action_from_name(self.action)
        next_action = self.get_action_from_name(self.action_stack[-1])
        if self.stateDict[next_action.cost_type()] > next_action.costs[next_action.cost_type()][1]:
            self.action = self.action_stack.pop()
            return True
        elif self.stateDict[current_action.cost_type()] < current_action.costs[current_action.cost_type()][1]:
            self.action = None
            self.action_stack = []
            return False
        else:
            if (self.x, self.y) != self.target:
                self.move()
                return True
            else:
                self.energy -= energyToWork
                self.money += wage
        # return True

    def do_recharge(self):
        # print(self.seed, 'in do_recharge function')
        rechargeAmount = 50
        costToRecharge = 25
        self.target = (self.homex, self.homey)
        current_action = self.get_action_from_name(self.action)
        next_action = self.get_action_from_name(self.action_stack[-1])
        if self.stateDict[next_action.cost_type()] > next_action.costs[next_action.cost_type()][1]:
            self.action = self.action_stack.pop()
            return True
        elif self.stateDict[current_action.cost_type()] < current_action.costs[current_action.cost_type()][1]:
            self.action = None
            self.action_stack = []
            return False
        else:
            if (self.x, self.y) != self.target:
                self.move()
                return True
            else:
                self.energy += rechargeAmount
                self.money -= costToRecharge

    def do_pay_rent(self):
        rentRate = 1000
        if self.money > rentRate:
            self.money -= rentRate
            self.world.bank += rentRate
            print('{} is paying rent'.format(self.seed))
            # time.sleep(3)
            # pygame.quit()
            # quit()
        self.action = None

    def do_sell_body(self):
        self.money += 250

    def set_goals_and_actions(self):
        energyToWork = 1
        wage = 5
        rechargeAmount = 50
        costToRecharge = 25
        rentRate = 1000
        work = Action('Work', self.do_work, {'energy': ('Min', energyToWork), 'money':('Not', 0)}, {'money': ('Add', wage), 'energy': ('Sub', energyToWork)})
        # sell_body = Action('Sell body', self.do_sell_body, {'energy': ('Min', energyToWork), 'money':('Not', 0)}, {'money': ('Add', rentRate), 'energy': ('Sub', 100)})
        recharge = Action('Recharge', self.do_recharge, {'energy': ('Not', 0), 'money': ('Min', costToRecharge)}, {'money': ('Sub', costToRecharge), 'energy': ('Add', rechargeAmount)})
        # idle = Action('Idle', {'energy': ('Min', 1), 'money':('Not', 0)}, {'energy': ('Sub', 1), 'money':('Not', 0)})
        payRent = Action('Pay Rent', self.do_pay_rent, {'energy': ('Not', 0), 'money': ('Min', rentRate)}, {'money': ('Sub', rentRate), 'energy': ('Not', 0)})
        keepHouse = Goal('Keep house', {'money': ('Min', rentRate), 'energy': ('Not', 0)})
        self.goals.append(keepHouse)
        self.actions.append(work)
        # self.actions.append(sell_body)
        self.actions.append(recharge)
        self.actions.append(payRent)

    def get_best_path(self, paths):
        path_cost_indices = []
        for path in paths:
            # print('action path =', path)
            path_cost_index = 0
            for action_name in path:
                # print('action name =', action_name)
                if action_name != 'end':
                    action = self.get_action_from_name(action_name)
                    if action.costs['energy'][0] == 'Add':
                        path_cost_index -= action.costs['energy'][1]
                    elif action.costs['energy'][0] == 'Sub':
                        path_cost_index += action.costs['energy'][1]
                    else:
                        pass
                    if action.costs['money'][0] == 'Add':
                        path_cost_index -= action.costs['money'][1]
                    elif action.costs['money'][0] == 'Sub':
                        path_cost_index += action.costs['money'][1]
                    else:
                        pass
            path_cost_indices.append((path_cost_index, path))
        # print(path_cost_indices)
        # if path_cost_indices != []:
        sorted_paths = sorted(path_cost_indices, key=itemgetter(0))
        # print(sorted_paths)
        best_path = sorted_paths[0][1]
        best_path.reverse()
        best_path.remove('end')
        # else:
            # best_path = [None,]
        # print(self.seed, 'Best path =', best_path)
        # print('best_path:', best_path)
        return best_path


    def goap(self, goal):
        # get the action(s) that fulfils the goal outcome
        # get the action that fulfils that/those action(s)'(s) requirement until
        #  (an) action(s) is/are reached for which the requirement is already satisfied
        # select the chain of the lowest cost
        # if self.stateDict[goal.precondition_type()] >= goal.preconditions[goal.precondition_type()][1]:
            # paths = ['Idle']
            # print(paths)
            # return True
        # print('ant id = ', self.seed, ', energy =', self.energy, ', money =', self.money)
        action_tree = {'end':{}}
        for action in self.actions:
            action_tree[action.name] = {}
        for action in self.actions:
            if action.cost_type() == goal.precondition_type() and action.costs[action.cost_type()][1] >= goal.preconditions[goal.precondition_type()][1]:
                action_tree[action.name]['end'] = action.costs[action.cost_type()][1]
        action_tree_incomplete = True
        while action_tree_incomplete:
            last_length = len(action_tree)
            dict_copy = copy.deepcopy(action_tree)
            for k, v in dict_copy.items():
                if k != 'end':
                    other_action = self.get_action_from_name(k)
                    for action in self.actions:
                        if action.benefit_type() == other_action.precondition_type():
                            action_tree[action.name][other_action.name] = action.costs[action.cost_type()][1]
            new_length = len(action_tree)
            if new_length == last_length:
                action_tree_incomplete = False
        possible_starts = []
        for k, v in action_tree.items():
            if k != 'end':
                action = self.get_action_from_name(k)
                if action.preconditions[action.precondition_type()][0] != 'Not':
                    if self.stateDict[action.precondition_type()] >= action.preconditions[action.precondition_type()][1]:
                        possible_starts.append(action.name)
        paths = []
        # print('action tree =', action_tree)
        # print('possible starts =', possible_starts)
        for start in possible_starts:
            path = city.get_shortest_path(action_tree, start, 'end')
            paths.append(path)
        while True:
            if None in paths:
                paths.remove(None)
            else:
                break
        # print('paths:', paths)
        # print('action tree:', action_tree)
        self.action_stack = self.get_best_path(paths)
        # print(self.action_stack)
        self.action = self.action_stack.pop()
        # print(self.action)
        return 1

    def perform_action(self):
        # print(self.seed, self.money, self.energy)
        for act in self.actions:
            # print(self.seed, act.name)
            if act.name == self.action:
                # print(self.seed, 'about to perform', act.name)
                act.task()
                break
        # print(self.seed, self.money, self.energy)

    def prioritise(self):
        priority_indices = []
        for goal in self.goals:
            cost, best_path = goap(goal)
            for factor in goal.affects:
                priority_indices.append((self.currencies[factor] - cost, cost, goal))
        data.sort(key=lambda priority_indices: priority_indices[0], reverse=True)
        self.goals = [priority[2] for priority in priority_indices]

# myAnt = Ant('abcdefgh', (0, 0), (0, 0))
# myAnt.money = 25
# myAnt.energy = 0
# myAnt.goap(myAnt.goals[0])