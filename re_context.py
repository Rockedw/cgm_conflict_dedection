import time

from main import *


class GptRespContext:
    pass


class BehavioralContext(GptRespContext):
    def __init__(self, value, subject, action, obj, content, time):
        self.value = value
        self.subject = subject
        self.action = action
        self.obj = obj
        self.time = time
        self.content = content

    def __str__(self):
        return f"Value: {self.value}, Subject: {self.subject}, Action: {self.action}, Object: {self.obj}, Time: {self.time}, Content: {self.content}"


class StateContext(GptRespContext):
    def __init__(self, value, entity, attribute, state, time, exclusivity):
        self.value = value
        self.entity = entity
        self.attribute = attribute
        self.state = state
        self.time = time
        self.exclusivity = exclusivity

    def __str__(self):
        return f"Value: {self.value}, Entity: {self.entity}, Attribute: {self.attribute}, State: {self.state}, Time: {self.time}, Exclusivity: {self.exclusivity}"


class Goal:
    def __init__(self, value: str = None, type: str = None, father=None, children=None, children_relation='and',
                 context=None,
                 so_that='', having_being_merged=False):
        if children is None:
            children = []
        self.value = value
        self.type = type
        self.father = father
        self.children = children
        self.children_relation = children_relation
        self.context = context
        self.so_that = so_that
        self.having_being_merged = having_being_merged

    def add_child(self, child):
        self.children.append(child)
        child.father = self

    def set_children_relation(self, relation):
        self.children_relation = relation

    # def __str__(self):
    #     children_str = ""
    #     for child in self.children:
    #         children_str += str(child) + ", "
    #     return f"Value: {self.value}, Type: {self.type}, Children: [{children_str[:-2]}], Children Relation: {self.children_relation} "
    def __str__(self):
        return self.value + ' '


class Context:
    def __init__(self, id: str, value: str = '', type: str = '', father=None, children=None, children_relation='and',
                 gpt_context_list=None):
        self.id = id
        if children is None:
            children = []
        self.value = value
        self.type = type
        self.father = father
        self.children = children
        self.children_relation = children_relation
        self.gpt_context_list = gpt_context_list

    def add_child(self, child):
        self.children.append(child)
        child.father = self

    def set_children_relation(self, relation):
        self.children_relation = relation

    def __str__(self):
        children_str = ""
        for child in self.children:
            children_str += str(child) + ", "
        return f"Value: {self.value}, Type: {self.type}, Children: [{children_str[:-2]}], Children Relation: {self.children_relation}"


def gpt_generate_context(context: Context):
    value = context.value
    rsp = ask_chatGPT(task=prompt_dict['ea_context'], content=value)
    print(rsp)
    json_response = json.loads(rsp)
    gpt_context_list = []

    for o in json_response:
        if o['context_type'] == 1:
            gpt_context_list.append(
                BehavioralContext(value=value, subject=o['subject'], action=o['action'], obj=o['object'],
                                  content=o['content'], time=o['time']))
        else:
            gpt_context_list.append(
                StateContext(value=value, entity=o['entity'], attribute=o['attribute'], state=o['state'],
                             time=o['time'], exclusivity=o['exclusivity']))
    return gpt_context_list


# 层序遍历Goal
def level_order_traversal_goal(root: Goal):
    if root is None:
        return
    queue = [root]
    while len(queue) > 0:
        node = queue.pop(0)
        if node.context is not None:
            level_order_traversal_context(node.context)
        print(node)
        for child in node.children:
            queue.append(child)


# 层序遍历Context
def level_order_traversal_context(root: Context):
    if root is None:
        return
    queue = [root]
    while len(queue) > 0:
        node = queue.pop(0)
        if node.value is not None:
            gpt_context_list = gpt_generate_context(node)
            node.gpt_context_list = gpt_context_list
            print(gpt_context_list)
        for child in node.children:
            queue.append(child)


def cal_similarity(sentence1, sentence2):
    return 0


def is_simular_attribute(context1: StateContext, context2: StateContext):
    return "True"


def is_time_conflict(time1: str, time2: str):
    d = {"time1": time1, "time2": time2}
    d_json = json.dumps(d)
    response = ask_chatGPT("is_time_conflict", d_json)
    return response


def is_state_conflict(context1: StateContext, context2: StateContext):
    entity1 = context1.entity
    attr1 = context1.attribute
    entity2 = context2.entity
    attr2 = context2.attribute

    pass


def is_behavioral_context_conflict(context1: BehavioralContext, context2: BehavioralContext):
    if is_time_conflict(context1.time, context2.time) == "False":
        return False
    pass


def is_state_context_conflict(context1: StateContext, context2: StateContext):
    time_conflict = is_time_conflict(context1.time, context2.time)
    if time_conflict == "False":
        return "False"
    simular_attribute = is_simular_attribute(context1.attribute, context2.attribute)
    if simular_attribute == "False":
        return "False"

    state_conflict = is_state_conflict(context1, context2)
    if state_conflict == "False":
        return "False"

    if time_conflict == "Maybe" or simular_attribute == "Maybe" or state_conflict == "Maybe":
        return "Maybe"

    return "True"


def is_conflict_context(context1: GptRespContext, context2: GptRespContext):
    if isinstance(context1, BehavioralContext) and isinstance(context2, BehavioralContext):
        return is_behavioral_context_conflict(context1, context2)
    elif isinstance(context1, StateContext) and isinstance(context2, StateContext):
        return is_state_context_conflict(context1, context2)
    else:
        return False


def conflict_group_judge(root: Goal):
    result = []
    dfs_goal(root, [root], result)
    detected = {}
    states = []
    behavs = []
    for l in result:
        context_list = []
        s = ""
        for g in l:
            s += (g.value + " ")
            if g.context is not None and len(g.context.id) > 0:
                context_list.append(g.context)
        test4(context_list, detected=detected, states=states, behavs=behavs)
        # test5(context_list,detected)
        # print(context_list)
        # print(s)
    print("-------------------------------------------------------------------")
    print("可能存在冲突的上下文对数量为: " + str(len(detected)))
    for key in detected:
        result, rsp = detected[key]
        if result['Conflict'] == 'True' or result['Conflict'] == 'Maybe' and result['Type'] != 'None':
            print(key + ' | ' + rsp)
    print("-------------------------------------------------------------------")


def dfs_goal(goal: Goal, l: list, result: list):
    if goal.children is None or len(goal.children) == 0:
        result.append(l)
        return
    children = goal.children
    if goal.children_relation == 'and':
        for child in children:
            l.append(child)
        for child in children:
            dfs_goal(child, l, result)
    else:
        for child in children:
            newl = l.copy()
            newl.append(child)
            dfs_goal(child, newl, result)


def dfs_context(context: Context, l: list, contexts: list):
    if context.children is None or len(context.children) == 0:
        contexts += l
        return contexts
    children = context.children
    if context.children_relation == 'and':
        for child in children:
            l += child
        for child in children:
            dfs_context(child, l, contexts)
    else:
        for child in children:
            newl = l.copy()
            newl += child
            dfs_context(child, l, contexts)


def context_group_list(goals: list):
    for i in range(0, len(goals)):
        goal1: Goal = goals[i]
        for j in range(i + 1, len(goals)):
            goal2: Goal = goals[j]
            goal1_contexts = dfs_context(goal1.context, [], [])
            goal2_contexts = dfs_context(goal2.context, [], [])
            contexts = goal1_contexts + goal2_contexts
            judge_contexts_conflict(contexts)


def judge_contexts_conflict(context_list):
    state_contexts = []
    behav_contexts = []
    for context in context_list:
        rsp = ask_chatGPT("is_state_or_behavior_context", json.dumps({"statement": context}))
        print(rsp)
        d = json.loads(rsp)
        if d["type"] == "state":
            state_contexts.append(context)
        else:
            behav_contexts.append(context)
    for i in range(0, len(state_contexts)):
        for j in range(i + 1, len(state_contexts)):
            test_is_conflict(state_contexts[i], state_contexts[j])
    for i in range(0, len(behav_contexts)):
        for j in range(i + 1, len(behav_contexts)):
            test_is_conflict(behav_contexts[i], behav_contexts[j])
    for i in range(0, len(state_contexts)):
        for j in range(0, len(behav_contexts)):
            test_is_conflict(behav_contexts[j], state_contexts[i])


def generate_cgm():
    g0 = Goal(children_relation='and', value='g0')
    g1 = Goal(children_relation='or', value='g1')
    g2 = Goal(value='g2')
    g3 = Goal(value='g3')
    g4 = Goal(value='g4')
    g5 = Goal(value='g5')
    g6 = Goal(value='g6')
    g7 = Goal(value='g7')
    g12 = Goal(value='g12')
    t4 = Goal(value='t4')
    t5 = Goal(value='t5')
    t6 = Goal(value='t6')
    # t7 = Goal()
    t8 = Goal(value='t8')
    t9 = Goal(value='t9')
    t12 = Goal(value='t12')
    sg1 = Goal(value='sg1')
    sg2 = Goal(value='sg2')
    g14 = Goal(value='g15')
    g15 = Goal(value='g15')
    t15 = Goal(value='t15')

    g0.children.append(g1)
    g0.children.append(g2)
    g0.children.append(g3)
    g0.children.append(g15)
    g15.children.append(t15)

    g1.children.append(g4)
    g1.children.append(g5)
    g2.children.append(t8)
    g2.children.append(t9)
    g3.children.append(g6)
    g3.children.append(g7)
    g5.children.append(t4)
    g5.children.append(t5)
    t8.children.append(sg1)
    t9.children.append(sg2)
    g7.children.append(g12)

    g12.children_relation = 'or'
    g12.children.append(g14)
    g12.children.append(t12)

    g5.children.append(t6)

    c0 = Context(id='c0',
                 value='The home is lived in, and the patient is expected to have some dementia problems, and there '
                       'is no awaken caregiver or healthy relative at home')
    c1 = Context(id='c1', value='The patient is at home and anxious')
    c2 = Context(id='c2',
                 value='The humidity level is high, or home windows and doors haven’t been opened for a long time')
    c3 = Context(id='c3', value='The patient dementia disease is not in an advanced stage or he is moderately anxious.')
    c4 = Context(id='c4', value='The patient suffers of advanced dementia, and he seems to be extremely anxious')
    c5 = Context(id='c5', value='It is sunny and not very windy')
    c6 = Context(id='c6', value='Patients sleeping in the yard.')
    c7 = Context(id='c7', value='The patient is outside home since a long time and it is night time')
    c8 = Context(id='c8',
                 value='A stranger is trying to get into the yard in a suspicious way (e.g., enter from a place '
                       'different from the main gate)')
    c9 = Context(id='c9', value=' The phone is free and the caregiver is not using his phone for a call')
    c10 = Context(id='c10', value='It is not night time')
    c11 = Context(id='c11', value='The light level at the patient’s location is too low or too high')
    c12 = Context(id='c12', value='It is too dark inside home')
    c13 = Context(id='c13',
                  value='The neighbour is healthy, is at home, and can see or reach easily the patient’s home')
    c14 = Context(id='c14', value='The patient health turns bad or he has fallen down')
    c15 = Context(id='c15', value='The Medical Emergency Rescue Centre is reachable and online')
    g0.context = c0
    g1.context = c1
    g2.context = c2
    g4.context = c3
    g5.context = c4
    t8.context = c5
    sg1.context = c6
    sg2.context = c5
    g6.context = c7
    g7.context = c8
    t4.context = c9
    t5.context = c10
    t6.context = c11
    t12.context = c12
    g14.context = c13
    g15.context = c14
    t15.context = c15
    return g0


if __name__ == '__main__':
    # print(is_time_conflict("1pm to 3pm", "2pm to 4pm"))
    time_start_1 = time.time()
    root = generate_cgm()
    conflict_group_judge(root)
    time_end_1 = time.time()
    print("运行时间：" + str(time_end_1 - time_start_1) + "秒")

    # ans = ask_chatGPT("is_state_or_behavior_context", json.dumps({"Context": "It`s sunny today."}))
    # print(ans)


