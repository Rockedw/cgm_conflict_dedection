import os
import json
import openai
import json
import openai
import backoff

# 目前需要设置代理才可以访问 api
os.environ["HTTP_PROXY"] = "http://localhost:10809"
os.environ["HTTPS_PROXY"] = "http://localhost:10809"

openai.api_key = "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"

prompt_is_state_or_behavior_context = """
[Context Type Identification Task]
You are an outstanding requirements analyst with excellent skills in contextual goal modeling. Below is a context statement that makes an assertion about the world. If the context does not emphasize time, the default is now.
[Task]
Identify the context type in the statement and give a brief reason.
Input:
{"statement": "Input statement"}
Output:
{"type": "state", "reason": "Reason for state context"}
Your answer must be in JSON format. DO NOT RESPOND WITH ANYTHING ELSE.

[Response Format]
{"type": "state" or "behavior"}

[Examples]
Input:
{"statement": "John opened the locked door."}
Output:
{"type": "behavior", "reason": "Describes an action of opening."}

Input:
{"statement": "The room temperature is cold"}
Output:
{"type": "state", "reason": "Describes property of room temperature."}

Please follow the format strictly and identify entity intersections from different contexts accurately based on the examples. Do not provide any other response or explanation.


"""

prompt_is_state_context_conflict = """


You are an excellent context conflict analyzer. Below are two state contexts. 
Context1: <Context1> 
Context1: <Context2> 
Determine the conflict types between contexts based on background knowledge. The conflict types are as follows:
State conflict - The two contexts describe conflicting states for the same attribute of an entity.  
Causality conflict - The two contexts provide inconsistent explanations for the cause of a state.
Constraint conflict - One context describes a state violating constraints specified in the other.
None - There is no conflict.


You must output the following judgment content：
Conflict - Whether the contexts conflict if simultaneous, possible values: True, False, Maybe
Types of conflict:  The four types of conflicts in the above definition, possible values: State conflict, Causality conflict, Constraint conflict, Time conflict, None
Reason - Detailed reasons for your judgment

Your answers must be in JSON format like below. DO NOT RESPOND WITH ANYTHING ELSE, like:
{"Conflict": "True" or "False" or "Maybe", "Reason": "reason for your answer", "Type": "type of conflict"}

Examples:
Input:
Context1: "John is in New York."
Context2: "John is in London."
Output:
{"Conflict": "True", "Reason": "The two contexts state John is in different locations at the same time.", "Type": "State conflict"}

Input:
Context1: "The plant died because it was not watered for a month."
Context2: "The plant died due to overwatering."
Output:
{"Conflict": "True", "Reason": "The two contexts provide contradictory reasons for the plant's death.", "Type": "Causality conflict"}

Input:
Context1: "The meeting is scheduled for 2 PM."
Context2: "All meetings must be held before noon."
Output:
{"Conflict": "True", "Reason": "The meeting time violates the constraint specified in Context2.", "Type": "Constraint conflict"}

Input:
Context1: "The package was delivered on Monday."
Context2: "The package arrived on Wednesday."
Output:
{"Conflict": "True", "Reason": "The two contexts specify different, incompatible delivery dates for the package.", "Type": "Time conflict"}


Input:
Context1: "The sky is blue."
Context2: "The bird is red."
Output:
{"Conflict": "False", "Reason": "The two contexts describe unrelated facts with no apparent conflict.", "Type": "None"}
"""

background_knowledge = """The patient care system supports daily tasks that patients with memory impairments may forget, 
such as eating meals on time, maintaining indoor air circulation, and taking medications. Another critical 
requirement is to facilitate rescue efforts, like promptly notifying the medical emergency center and requesting 
dispatch of a rescue team in case of health emergencies. In addition to memory impairments, dementia patients may 
also suffer from anxiety attacks. The smart home should handle these situations properly by avoiding unexpected 
events through smooth transitions and preventing patients from leaving home during dangerous moments. Afterward, 
the patient needs to be comforted, and caregivers should be called in promptly for treatment. Furthermore, 
the smart home supports other routine tasks, such as preventing potential house theft. To achieve this, it can create 
an atmosphere of occupancy when the patient is away for an extended period, increasing the level of protection.
"""

prompt_is_beavioral_context_conflict = """
You are an excellent context conflict analyzer. Below are two behavior contexts.  
Context1: <Context1>
Context2: <Context2>

Determine the conflict types between contexts based on background knowledge. The conflict types are as follows:
Action conflict - The two contexts describe mutually exclusive actions of the same entity at the same time.
Causality conflict - The two contexts provide inconsistent explanations of preconditions or consequences of an action.
Resource conflict - The two contexts depict competing usage of a constrained resource by different agents. 
None - There is no conflict.


You must output the following judgment content：
Conflict - Whether the contexts conflict if simultaneous, possible values: True, False, Maybe 
Types of conflict: The four types of conflicts in the above definition, possible values: Action conflict, Causality conflict, Resource conflict, Time conflict, None
Reason - Detailed reasons for your judgment 

Your answers must be in JSON format like below. DO NOT RESPOND WITH ANYTHING ELSE, like:
{"Conflict": "True" or "False" or "Maybe", "Reason": "reason for your answer", "Type": "type of conflict"}

Examples:
Input:
Context1: "John is driving to the airport to catch a flight."
Context2: "John is at home cooking dinner for his family."
Output:
{"Conflict":"True","Reason":"John cannot be driving to the airport and cooking at home at the same time. The two contexts describe mutually exclusive actions.","Type":"Action conflict"}

Input:
Context1: "The printer is out of paper, so the document could not be printed."
Context2: "The document was successfully printed and is ready for pickup."
Output:
{"Conflict":"True","Reason":"The two contexts provide inconsistent explanations about the preconditions and outcome of the printing action. If the printer is out of paper, the document could not have printed successfully.","Type":"Causality conflict"}

Input:
Context1: "Team A is using the conference room for their weekly meeting from 2-3pm."
Context2: "Team B has booked the conference room for a client call from 2:30-3:30pm."
Output:
{"Conflict":"True","Reason":"The conference room is a constrained resource that cannot be used by both teams simultaneously for their respective meetings. The bookings are competing for the same resource at overlapping times.","Type":"Resource conflict"}

Input:
Context1: "The construction of the new highway will be completed in 2024, before the housing development project begins."
Context2: "The housing development project is already underway and is scheduled to be finished by the end of 2023, prior to the highway construction."
Output:
{"Conflict":"True","Reason":"The two contexts refer to the highway construction and housing development happening in an inconsistent order. They cannot both be completed before the other.","Type":"Time conflict"}

"""

prompt_is_beavioral_state_context_conflict = """
You are an excellent context conflict analyzer. Below is a behavior context followed by a state context related to the same goal. 
Behavior Context: <Context1>
State Context: <Context2>

Determine the conflict types between contexts based on background knowledge. The conflict types are as follows:
Result conflict - The behavior context depicts an action whose outcome conflicts with the entity state described in the state context.
Dependency conflict - The precondition or execution dependency specified in the behavior context contradicts the state information given in the state context.
None - There is no conflict.

Background knowledge : <Optional>

You must output the following judgment content：
Conflict - Whether the contexts conflict if simultaneous, possible values: True, False, Maybe
Types of conflict: The two types of conflicts in the above definition, possible values: Result conflict, Dependency conflict, None
Reason - Detailed reasons for your judgment

Your answers must be in JSON format like below. DO NOT RESPOND WITH ANYTHING ELSE, like:
{"Conflict": "True" or "False" or "Maybe", "Reason": "reason for your answer", "Type": "type of conflict"}

Examples:
Input:
Behavior Context: "The user must have administrator privileges to install the software"
State Context: "The user is logged in with a standard user account"
Output:
{"Conflict": "True", "Reason": "Administrator privileges dependency is not met by standard user account", "Type": "Dependency conflict"}

Input:
Behavior Context: "The application will write data to the database"
State Context: "The database is currently locked by another process performing updates"
Output:
{"Conflict": "True", "Reason": "Writing data may conflict with database locked for updates", "Type": "Result conflict"}
"""

prompt_dict = {
    "is_state_context_conflict": prompt_is_state_context_conflict,
    "is_behavior_context_conflict": prompt_is_beavioral_context_conflict,
    "is_behavior_state_context_conflict": prompt_is_beavioral_state_context_conflict,
    "is_state_or_behavior_context": prompt_is_state_or_behavior_context,
}

import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="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",
)

message = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    temperature=0.0,
    system="Respond only in Yoda-speak.",
    messages=[
        {"role": "user", "content": "How are you today?"}
    ]
)


@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def ask_chatGPT(task: str, content: str):
    bg = prompt_dict[task]
    rsp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": bg},
            {"role": "user", "content": content}
        ]
    )
    return rsp.get("choices")[0]["message"]["content"]


@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def ask_chatGPT2(task: str, content: str):
    rsp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": task},
            {"role": "user", "content": content}
        ]
    )
    return rsp.get("choices")[0]["message"]["content"]


def test(context1, context2):
    rsp1 = ask_chatGPT("ea_context", context1)
    rsp2 = ask_chatGPT("ea_context", context2)
    print(rsp1)
    print(rsp2)
    rsp1 = json.loads(rsp1)
    rsp2 = json.loads(rsp2)
    entity1 = rsp1[0]["entity"]
    entity2 = rsp2[0]["entity"]
    print('Is the same entity : ' + ask_chatGPT("is_same_entity",
                                                json.dumps(
                                                    {"Entity1": entity1, "Entity2": entity2, "Context1": context1,
                                                     "Context2": context2})))
    attribute1 = rsp1[0]["attribute"]
    attribute2 = rsp2[0]["attribute"]
    print('Is_same_entity_attribute : ' + ask_chatGPT("is_same_entity_attribute", json.dumps(
        {"Context1": context1, "Entity1": entity1, "Attribute1": attribute1, "Context2": context2, "Entity2": entity2,
         "Attribute2": attribute2})))


def is_state_context_conflict(context1, context2):
    rsp = ask_chatGPT("is_state_context_conflict", json.dumps({"Context1": context1, "Context2": context2}))
    tmp = json.loads(rsp)
    return context1, context2, tmp, rsp


def is_behavior_context_conflict(context1, context2):
    rsp = ask_chatGPT("is_behavior_context_conflict", json.dumps({"Context1": context1, "Context2": context2}))
    tmp = json.loads(rsp)
    return context1, context2, tmp, rsp


def is_behavior_state_context_conflict(context1, context2):
    rsp = ask_chatGPT("is_behavior_state_context_conflict",
                      json.dumps({"BehaviorContext": context1, "StateContext": context2}))
    tmp = json.loads(rsp)
    return context1, context2, tmp, rsp


def test_is_conflict(context1, context2):
    rsp = ask_chatGPT("test", json.dumps({"context1": context1, "context2": context2}))
    print(context1 + "   " + context2 + "   " + rsp)
    rsp = ask_chatGPT("test2", json.dumps({"context1": context1, "context2": context2}))
    print(context1 + "   " + context2 + "   " + rsp)
    rsp = ask_chatGPT("test3", json.dumps({"context1": context1, "context2": context2}))
    print(context1 + "   " + context2 + "   " + rsp)


def test3(context_list):
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
            is_state_context_conflict(state_contexts[i], state_contexts[j])
    for i in range(0, len(behav_contexts)):
        for j in range(i + 1, len(behav_contexts)):
            is_behavior_context_conflict(behav_contexts[i], behav_contexts[j])
    for i in range(0, len(state_contexts)):
        for j in range(0, len(behav_contexts)):
            is_behavior_state_context_conflict(behav_contexts[j], state_contexts[i])


def test4(context_list, detected: {}, states: list, behavs: list):
    state_contexts = []
    behav_contexts = []
    for context in context_list:
        if context.id in states:
            state_contexts.append(context)
            continue
        if context.id in behavs:
            behav_contexts.append(context)
            continue
        else:
            rsp = ask_chatGPT("is_state_or_behavior_context", json.dumps({"statement": context.value}))
            # print(rsp)
            d = json.loads(rsp)
            if d["type"] == "state":
                state_contexts.append(context)
                states.append(context)
            else:
                behav_contexts.append(context)
                behavs.append(context)
    for i in range(0, len(state_contexts)):
        for j in range(i + 1, len(state_contexts)):
            c1 = state_contexts[i]
            c2 = state_contexts[j]
            id = c1.id + ':' + c2.id
            if id not in detected:
                _, _, result, rsp = is_state_context_conflict(c1.value, c2.value)
                detected[id] = result, rsp
            result, rsp = detected[id]
            if result['Conflict'] == 'True' or result['Conflict'] == 'Maybe' and result['Type'] != 'None':
                print(c1.value + ' | ' + c2.value + ' | ' + rsp)

    for i in range(0, len(behav_contexts)):
        for j in range(i + 1, len(behav_contexts)):
            c1 = behav_contexts[i]
            c2 = behav_contexts[j]
            id = c1.id + ':' + c2.id
            if id not in detected:
                _, _, result, rsp = is_behavior_context_conflict(c1.value, c2.value)
                detected[id] = result, rsp
            result, rsp = detected[id]
            if result['Conflict'] == 'True' or result['Conflict'] == 'Maybe' and result['Type'] != 'None':
                print(c1.value + ' | ' + c2.value + ' | ' + rsp)
    for i in range(0, len(state_contexts)):
        for j in range(0, len(behav_contexts)):
            c2 = state_contexts[i]
            c1 = behav_contexts[j]
            id = c1.id + ':' + c2.id
            if id not in detected:
                _, _, result, rsp = is_behavior_state_context_conflict(c1.value, c2.value)
                detected[id] = result, rsp
            result, rsp = detected[id]
            if result['Conflict'] == 'True' or result['Conflict'] == 'Maybe' and result['Type'] != 'None':
                print(c1.value + ' | ' + c2.value + ' | ' + rsp)


def test5(context_list, detected: {}):
    for i in range(0, len(context_list)):
        c1 = context_list[i]
        for j in range(i + 1, len(context_list)):
            c2 = context_list[j]
            id1 = c1.id + ':' + c2.id
            id2 = c2.id + ':' + c1.id
            if id1 not in detected and id2 not in detected:
                detected[id1] = 1


# while True:
#     content = input()
#     response = ask_chatGPT("ea_context", content)
#     print(response)
# json_response = json.loads(response)
# for o in json_response:
# context = GptRespContext(o['entity'], o['attribute'], o['state'], o['subject'], o['exclusivity'], o['time_varying'])
#     print(context)

# def gpt_generate_context(context: Context):
#     content = context.value
#     response = ask_chatGPT(content)
#     print(response)
#     json_response = json.loads(response)
#     gpt_context_list = []
#     for o in json_response:
#         gpt_context_list.append(GptRespContext(o['entity'], o['attribute'], o['state'], o['subject'], o['exclusivity'],
#                                                o['time_varying']))
#     return gpt_context_list

if __name__ == '__main__':
    # context_list = ["The room temperature is cold.", "Mary is dancing in the living room.",
    #                 "The box contains many heavy books."
    #     , "John opened the locked door with the key.", "The student is reading a book while listening to music.",
    #                 "The kitchen light is on and the window is open."
    #     , "Tom washed the dirty dishes after dinner.", "The dog is sleeping on the couch which has some stains.",
    #                 "Alice booked two flight tickets to London for her vacation."
    #     , "The manager approved the budget plan yesterday in the meeting."]

    context_list = [
        "The home is lived in, and the patient is expected to have some dementia problems, and there is no awaken caregiver or healthy relative at home",
        "The patient is at home and anxious",
        "The humidity level is high, or home windows and doors haven’t been opened for a long time",
        "The patient dementia disease is not in an advanced stage or he is moderately anxious.",
        "The patient suffers of advanced dementia, and he seems to be extremely anxious",
        "It is sunny and not very windy",
        "The patient is outside home since a long time and it is night time.",
        "A person is trying to get into the yard in a suspicious way",
        "The phone is free and the caregiver is not using his phone for a call",
        "It is not night time",
        "The light level at the patient’s location is too low or too high",
        "It is too dark inside home",
        "The neighbour is healthy, is at home, and can see or reach easily the patient’s home",
        "The patient health turns bad or he has fallen down",
        "The MERC is reachable and online",
        "The home has a screen that shows the patient’s medical record"
    ]

    # context_list = ["The system requires A to run", "The system cannot have B"]

    test3(context_list)
