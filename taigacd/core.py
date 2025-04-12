from __future__ import annotations

import asyncio
import io
import logging
from dataclasses import dataclass
from typing import Literal

from agents import Agent, ItemHelpers, Runner, TResponseInputItem, trace, FunctionTool

@dataclass
class EvalFeddback:
    feedback: str
    score: Literal["pass", "needs_improvement", "fail"]

# Worker: Generate simulation python code
worker = Agent(
    name="worker",
    instructions="Say Hello!"
)
'''
instructions=(
    "You are a materials simulation code generator. "
    "Given the user's prompt and any feedback, generate a complete Python code snippet that performs a materials simulation calculation. "
    "The code should read the structure file from 'user_uploads/structure.cif' and use appropriate libraries such as ASE, GPAW, M3GNet, or MACE based on the simulation needs. "
    "If feedback is provided, use it to improve the code."
)
'''

# Evaluator: Evaluate simulation results
evaluator = Agent[None](
    name="evaluator",
    instructions=(
        "Evaluate if the provided response is saying hello."
        "If the response are good, give it a score of 'pass'."
        "If its bad or need to improve, give it a score of 'needs_improvement' or 'fail'."
        "Do not pass in the first iteration."
    ),
    output_type=EvalFeddback
)
'''
instructions=(
    "You are a senior material simulation scientists."
)
'''

async def main() -> None:
    prompt = input("Enter your materials simulation request: ")
    input_items: list[TResponseInputItem] = [{"content": prompt, "role": "user"}]
    taiga407_history: list[str] = [f"[Prompt] \n{prompt}"]
    with trace("Taiga 407") as taiga407_trace:
        iteration = 0
        while True:
            # Generate simulation code
            print(input_items)
            sim_code = await Runner.run(worker, input_items)
            latest_sim_code = sim_code.final_output
            print("sim_code: ", sim_code)
            print("latest_sim_code: ", latest_sim_code)
            history = f"[Iteration {iteration}] latest_sim_code:\n{latest_sim_code}\n"
            taiga407_history.append(history)

            # Check the output and give feedback
            input_items.extend([
                {"content": latest_sim_code, "role": "assistant"},
            ])
            print(input_items)
            eval_result = await Runner.run(evaluator, input_items)
            feedback = eval_result.final_output
            print(f"Evaluator score: {feedback.score}")
            print(f"Evaluator feedback: {feedback.feedback}")
            history = f"[Iteration {iteration} - evaluation] feedback:\n{feedback}"
            taiga407_history.append(history)
            if feedback.score == "pass":
                print("Simulation code is accepted. Exiting iteration.")
                break
            else:
                print("Iteration did not pass. Rerunning with feedback.")
                input_items.append({"content": f"Feedback: {feedback.feedback}", "role": "user"})

                if iteration >= 1:
                    break
                else:
                    iteration += 1
            
    with open("taiga407_history.log", "w", encoding="utf-8") as f:
        for history in taiga407_history:
            f.write(history + "\n\n")
    print(taiga407_history)
    print("Trace output saved to taiga407_history.log")

if __name__ == "__main__":
    asyncio.run(main())
