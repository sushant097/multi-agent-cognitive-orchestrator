# Multi-agent-cognitive-orchestrator
A modular multi-agent cognitive system with a central Coordinator that manages Perception, Retriever, Critic, Memory, Decision, and Executor agents. The architecture uses a shared “blackboard” state, plan/step objects, and plan-rewrite loops to go from user query → plan → tools → critique → updated plan → final answer.
