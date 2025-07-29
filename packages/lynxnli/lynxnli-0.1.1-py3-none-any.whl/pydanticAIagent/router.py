from .state import AgentState

def router_agent(state: AgentState) -> str:
#    print(state)
    # state.add_llm_response(state.result)
    # print(state.get_full_context())

    if len(state.tasks)== 0:
        print("Not Task generted, now try again")
        return str(False)

    done = True
    for task in state.tasks:
        print(f"For Task: {task.name},\nTag     : {task.done},\n"+
              f"Solution: {task.solution}\n")
        done = done and task.done
        state.user_input += task.description
    print(f"Summarised input: {state.user_input}DONE\n")

    if done:
        print(f"User query is done!")
    else:
        print(f"User query is not done yet! new attempt is going on.")
#    print(f"the target is {state.target}\n")
    return str(done)