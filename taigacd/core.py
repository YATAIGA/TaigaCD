from __future__ import annotations
import contextlib
import sys

import asyncio
import io
import logging
from dataclasses import dataclass
from typing import Literal

from agents import Agent, ItemHelpers, Runner, TResponseInputItem, trace, FunctionTool

@dataclass
class EvalFeedback:
    feedback: str
    score: Literal["pass", "needs_improvement", "fail"]

# Worker: Generate simulation python code
worker = Agent(
    name="worker",
    instructions=(
        "You are a materials simulation code generator. "
        "Given the user's prompt and any feedback, generate a complete Python code snippet that performs a materials simulation calculation. "
        "The code should check if the structure file from 'user_uploads/structure.cif' exists if don't you should generate the scructure in the python code"
        "Use appropriate libraries such as ASE, GPAW, M3GNet, or MACE based on the simulation needs. "
        "Store output file under ./outputs/code_gen/."
        "If feedback is provided, use it to improve the code."
    )
)

# Evaluator: Evaluate simulation results
evaluator = Agent[None](
    name="evaluator",
    instructions=(
        "You are a material scientists. Evaluate the provided simulation result. "
        "If the simulation results is correct, respond with a score of 'pass'. "
        "If errors occur or the output is not as expected, provide feedback on what should be improved and respond with a score of 'needs_improvement'."
    ),
    output_type=EvalFeedback
)

def extract_python_code(mixed_text: str) -> str:
    """Extract code block from markdown-style output or return raw text."""
    if "```python" in mixed_text:
        try:
            return mixed_text.split("```python")[1].split("```")[0].strip()
        except IndexError:
            pass  # fallback below
    return mixed_text.strip()

def run_code_safely(code: str) -> str:
    """Executes code and captures output."""
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            exec(code, {})  # Run in a fresh global namespace
    except Exception as e:
        return f"Error during execution: {e}"
    return buffer.getvalue().strip()

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
            history = f"[Iteration {iteration}] latest_sim_code:\n{latest_sim_code}\n"
            taiga407_history.append(history)

            # Execute simulation code
            code = extract_python_code(latest_sim_code)
            exe_results = run_code_safely(code)
            with open(f"outputs/code_itr_{iteration}.py", "w", encoding="utf-8") as f:
                f.write(code)
            with open(f"outputs/output_itr_{iteration}.txt", "w", encoding="utf-8") as f:
                f.write(exe_results)

            # Check the output and give feedback
            input_items.extend([
                {"content": latest_sim_code, "role": "assistant"},
                {"content": exe_results, "role": "user"}
            ])
            print(input_items)
            eval_result = await Runner.run(evaluator, input_items)
            feedback = eval_result.final_output
            print("eval_result: ", eval_result)
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
            
    with open("logs/taiga407_history.log", "w", encoding="utf-8") as f:
        for history in taiga407_history:
            f.write(history + "\n\n")
    print("Trace output saved to taiga407_history.log")

if __name__ == "__main__":
    asyncio.run(main())
