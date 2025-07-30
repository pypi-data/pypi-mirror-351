# LynxNLI  `v.LynxNLI_0_0250201`
Project of Link-point for Linux using Natural-Language Interface (LynxNLI)  
Tool-Augmented LLM Inference System with Modular Agents

[![GitLab Repo](https://img.shields.io/badge/gitlab-gwdg--lynxnli-blue.svg)](https://gitlab-ce.gwdg.de/bidollahkhan/lynxnli) [📄 Presentation ](./README.html)

---

## Overview

**LynxNLI** (Lynx Natural Language Interface) is a research prototype designed to enhance Large Language Models (LLMs) with real-time tool execution and explainability. It combines language understanding with structured tool use through a system called the **Trinity**, consisting of three intelligent agents that handle:

![Workflow](./static/SpeculativeAgent.drawio.png)


- **Problem understanding: (Orchestration)** Analysis the problem of user, separate the problem into reasonable tasks and set the satisfaction conditions <span style="color:#1e90ff">-> with LLM</span>.
  
- **Tasks execution(for each task)**
  - **A. Tool Analysis**: find the corresponding tool according to the task description and rewrites freeform task into structured tool call <span style="color:#1e90ff">-> with LLM</span>.
  - **B. Tool Execution**: Call the tool for execution and recode the actions for rollback if change applied in system. 
  - **C. Output Evaluation**: Check the task output with desired target and determine if the task should be repeated with merged prompt for step A <span style="color:#1e90ff">-> with LLM</span>. 

- **Problem examine: (Summary):** Check the output of all tasks for satifaction conditions <span style="color:#1e90ff">-> with LLM</span>.
  -  Try new analysis for problem with tasks output <span style="color:#1e90ff">-> with LLM</span>.   
  -  Converts tasks output into human-friendly responses and stores results in XML.
  
To improve flexibility, LynxNLI now uses a fallback mechanism where the LLM itself can convert a freeform prompt into a structured JSON payload (e.g., a proper tool invocation), reducing reliance on rigid regex extraction.

---

## Project Structure

```
lynxnli/
│
├── main.py                # CLI entry point
├── main_form.py           # GUI interface with Tkinter
├── trinity.py             # Three-agent controller for LLM-tool reasoning
├── llm_engine.py          # Handles LLM API interaction
├── llm_context_manager.py # Manages chat and tool context
├── tool_executor.py       # Executes tools and saves results in XML
│
├── toolset/
│   ├── ini_tool_loader.py       # Loads .ini tool definitions
│   ├── tool_definition.py       # Tool schema (now includes extraction rules)
│   ├── tool_invocation_parser.py # Parses structured tool calls from LLM output
│   ├── tool_registry.py         # Central registry of available tools
│   └── tools/
│       ├── mathTool.ini
│       ├── plotterTool.ini
│       ├── imageAI.ini
│       └── runPython.ini
│
└── outputs/              # Stores XML logs and tool results
```

---

## 🛠 Features

- **Dynamic Tool Loading**: Tools are defined in `.ini` files and loaded at runtime.
- **Modular Agents**: Three agents (detection, triggering, and refinement) coordinate to select and execute tools.
- **Flexible Input Conversion**: 
  - Primary extraction uses configurable regex patterns defined in the INI files.
  - **LLM Fallback Conversion**: If regex extraction fails, the system leverages an LLM to convert freeform natural language into a structured JSON object.
- **Step-by-Step Trace & Explainability**: All tool invocations and outputs are saved in XML for traceability.
- **GUI and CLI Modes**: Use the interface that best fits your workflow.
- **Support for Positional & Keyword Arguments**: Tools can receive structured inputs in various formats.

---

## Running the Application

### Command-Line Interface

```bash
python main.py
```

### Graphical User Interface

```bash
python main_form.py
```

---

## LLM Backend (Configurable)

The default LLM API is set to:

```
https://synchange.com/sync.php
```

You can modify this in `llm_engine.py` when initializing `LLMEngine`.

---

## Sample Tool Call

When the LLM is prompted to convert a freeform instruction, it is expected to output a structured tool call. For example:

**User Input:**
```
run this python code: print("hello world")
```

**LLM Structured Output:**
```xml
<tool name="runPython">{"code": "print(\"hello world\")"}</tool>
```

Alternatively, you can directly provide the structured call:
```xml
<tool name="mathTool">{"expression": "sqrt(49 + 36)"}</tool>
```

---

## Requirements

- Python 3.9+
- Dependencies: `requests`, `tkinter`, `matplotlib`, `Pillow`, `numpy` (used by various tools)

Install all dependencies:

```bash
pip install -r requirements.txt
```

---

## Sample Tools

- **mathTool**: Evaluates mathematical expressions.
- **plotterTool**: Plots mathematical functions over a range.
- **imageAI**: Generates base64-encoded images from text prompts.
- **runPython**: Executes arbitrary Python code and returns the output.

Tool definitions are provided in INI format inside the `toolset/tools` directory.

---

## Logs & Results

All session outputs—including queries, conversions, tool results, and final output—are stored as XML files in:

```bash
outputs/session_<timestamp>.xml
```

---

## License

Research use only. © 2025 Michael B. Khani

---

## Repository

[LynxNLI GitLab Repo](https://gitlab-ce.gwdg.de/bidollahkhan/lynxnli.git)

---

## Developed By

**Michael B. Khani**  
AI Systems Researcher | UGOE and GWDG Göttingen
