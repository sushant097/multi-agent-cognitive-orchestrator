

# 🚀 **Multi-Agent Cognitive Orchestrator**

A modular, fully custom multi-agent architecture where specialized agents collaborate through a shared global state (“blackboard”) to turn user input into structured goals, adaptive plans, tool calls, critiques, memory updates, and final answers.

This project implements a **Coordinator-driven**, **role-separated**, and **plan-rewriting** system inspired by cognitive and distributed-AI design patterns.

---

## ⭐ 1. **Architecture Overview**

*under review*

This system is designed around a central **Coordinator** that manages six independent agents:

```
                          ┌─────────────────┐
                          │   Coordinator   │
                          └───────┬─────────┘
        ┌──────────────┬─────────┼───────────────┬──────────────┐
        ▼              ▼          ▼               ▼               ▼
┌────────────┐ ┌────────────┐ ┌──────────┐ ┌────────────┐ ┌─────────────┐
│ Perception │ │ Retriever   │ │ Critic   │ │ Memory     │ │ Decision     │
│   Agent    │ │   Agent     │ │  Agent   │ │   Agent    │ │   Agent      │
└──────┬─────┘ └──────┬──────┘ └────┬─────┘ └──────┬─────┘ └───────┬─────┘
       │               │             │              │               │
       │               │             │              │               │
       └──────────────▶─────────────▶──────────────▶───────────────▶
                              Plan / Rewrite
                                     │
                                     ▼
                              ┌────────────┐
                              │  Executor  │
                              │   Agent    │
                              └────────────┘
```

Each agent focuses on exactly one responsibility:

### **Perception Agent**

Extracts entities, goals, constraints, and structured understanding from input or tool results.

### **Retriever Agent**

Gathers external context through tools such as search, math evaluation, or document lookup.

### **Critic Agent**

Evaluates outputs for correctness, usefulness, and alignment with the user’s objective.

### **Memory Agent**

Maintains long-term memory:

* Facts discovered
* Tool performance logs
* Past failures
* Useful retrievals
  Supplies insights back into planning.

### **Decision Agent**

Creates or rewrites a **Plan**, which is a list of structured steps with explicit purposes.

### **Executor Agent**

Runs tools safely, logs usage, captures errors/latency, and returns execution results.

---

## ⭐ 2. **Core Concepts**

### **The Blackboard (Global State)**

All agents read/write to a shared JSON-like structure:

* `query`
* `objective`
* `entities`
* `constraints`
* `plan` (list of steps)
* `current_step_index`
* `memory`
* `tool_stats`
* `history` of steps and results
* `status` (`running`, `done`, `failed`)
* `flags.plan_rewrite_needed`

Agents **never call each other directly**.
They observe and update the blackboard, and the Coordinator routes control.

---

## ⭐ 3. **Plan Model**

A `Plan` is a list of `PlanStep` objects:

```json
{
  "id": 1,
  "description": "Search for background info",
  "agent": "retriever",
  "tool_name": "web_search",
  "input": "What is quantum computing?",
  "output": null,
  "status": "pending",
  "error": null
}
```

Each step expresses **who should act**, **why**, and **how**.

### **Plan Rewrite**

If a step fails or critic evaluation is negative:

* DecisionAgent receives full context
* Generates a revised plan:

  * Replace failing step
  * Add fallback step
  * Change strategy
  * Or conclude early

This rewrites only relevant parts, not the entire plan.

---

## ⭐ 4. **Coordinator Flow**

The Coordinator is the backbone:

1. Receive user query
2. Call **PerceptionAgent**
3. Call **DecisionAgent** to create initial plan
4. Enter loop:

   * Retrieve current step
   * Call the responsible agent (Retriever / Executor)
   * Run **CriticAgent**
   * Run **MemoryAgent**
   * If rewrite is needed → call DecisionAgent
   * Otherwise → go to next step
5. Stop when:

   * Goal achieved
   * No steps left
   * System reaches max step limits

---

## ⭐ 5. **Human-In-Loop Capabilities**

To ensure robustness:

### **When a Tool Fails**

* Executor marks failure after 3 retries
* Coordinator pauses
* Prompts human for direct input
* Incorporates input into the step and continues execution

### **When a Plan Fails**

* Critic sets `plan_rewrite_needed = true`
* DecisionAgent proposes an alternate plan
* Human may choose:

  * Accept plan
  * Provide a better plan
  * Skip failed steps
* DecisionAgent adapts immediately

This shows the system can **listen, adjust, and recover**.

---

## ⭐ 6. **Step Limits & Safety**

### `MAX_STEPS = 3`

Planning must stay within 3 high-level steps.

### `MAX_RETRIES = 3`

Each tool has three attempts before:

* Marking failure
* Triggering Human-In-Loop logic
* Logging the failure

---

## ⭐ 7. **Tool Performance Logging**

Every tool call generates a log entry:

```json
{
  "timestamp": "...",
  "tool": "web_search",
  "success": true,
  "latency_ms": 118,
  "error": null
}
```

Logs update in:

```
logs/tool_performance.jsonl
```

### **MemoryAgent uses this to influence planning**, e.g.:

* Prefer faster tools
* Avoid tools with repeated failures
* Recommend fallback methods

---

## ⭐ 8. **Simulator (100+ Test Runs)**

A simulator repeatedly triggers the agent with randomized prompts:

* Math
* Small research tasks
* Summaries
* Transformations
* Tool-based queries

Each test records:

* Steps taken
* Tools used
* Failures + retries
* Latency
* Whether plan was rewritten
* Whether Human-In-Loop was triggered

A `sleep()` is added between tests to avoid rate limits.

---

## ⭐ 9. **How This Architecture Evolves From a Single-Agent System**

### **Before**

* One agent handled perception → planning → execution
* No role separation
* No tool logs
* No plan rewrite system
* No critic
* No memory-driven planning

### **Now**

* Multiple specialized agents
* Transparent role boundaries
* Shared blackboard state
* Dynamic plan evolution
* Critic + Memory feedback loops
* Human-In-Loop safety
* Tool intelligence through performance logs
* A Coordinator that functions like a distributed OS

This transforms the system from **linear reasoning** into a **collaborative cognitive model**.

---

## ⭐ 10. **Project Structure**

```
src/
  state.py
  coordinator.py
  agents/
    perception_agent.py
    retriever_agent.py
    critic_agent.py
    memory_agent.py
    decision_agent.py
    executor_agent.py
  tools/
    web_search.py
    math_tools.py
    file_search.py
  simulator/
    simulator.py
tests/
logs/
```

---

## ⭐ 11. **Getting Started**

```
pip install -r requirements.txt
python src/simulator/simulator.py
```
