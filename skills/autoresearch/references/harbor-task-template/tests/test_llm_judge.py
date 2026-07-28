"""
LLM-as-judge scoring — for tasks where correctness isn't binary.
Calls an LLM to evaluate output quality on a rubric, writes 0.0–1.0 to /logs/reward.txt.

Usage: python tests/test_llm_judge.py
Requires: OPENAI_API_KEY in environment
"""

import json
from pathlib import Path

# Adjust import based on your LLM SDK
from openai import OpenAI

RUBRIC = """
Rate the agent's output on a scale of 0.0 to 1.0:

- 1.0: Fully correct, well-structured, meets all requirements
- 0.7: Mostly correct with minor issues
- 0.4: Partially correct, significant gaps
- 0.1: Attempted but largely wrong
- 0.0: No meaningful output or completely wrong

Respond with ONLY a JSON object: {"score": 0.X, "reason": "brief explanation"}
"""


def judge(instruction: str, output: str) -> float:
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": RUBRIC},
            {
                "role": "user",
                "content": f"## Task Instruction\n\n{instruction}\n\n## Agent Output\n\n{output}",
            },
        ],
        temperature=0,
    )
    result = json.loads(response.choices[0].message.content)
    return float(result["score"])


def main():
    Path("/logs").mkdir(exist_ok=True)

    instruction = Path("/task/instruction.md").read_text()
    output_path = Path("/task/output.txt")

    if not output_path.exists():
        Path("/logs/reward.txt").write_text("0.0")
        print("FAIL: No output file produced")
        return

    output = output_path.read_text()
    score = judge(instruction, output)
    Path("/logs/reward.txt").write_text(f"{score:.2f}")
    print(f"SCORE: {score:.2f}")


if __name__ == "__main__":
    main()
