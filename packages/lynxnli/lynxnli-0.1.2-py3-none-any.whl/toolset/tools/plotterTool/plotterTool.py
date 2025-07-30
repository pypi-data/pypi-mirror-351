import matplotlib.pyplot as plt
import os
import uuid
from content.state import ToolResult

def run(prompt) -> ToolResult:
    try:
        values = [float(x.strip()) for x in prompt.split(":")[-1].strip().split(",")]
        fig_id = uuid.uuid4().hex
        path = f"outputs/plot_{fig_id}.png"
        os.makedirs("outputs", exist_ok=True)
        plt.plot(values)
        plt.title("Line Plot")
        plt.savefig(path)
        plt.close()

        return ToolResult(
            output=f"Plot saved to {path}",
            stop=False
        )

    except Exception as e:
        return ToolResult(
            output=f"Error creating plot: {e}",
            stop=False
        )
