
import time

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    ToolMessage,
)

from core.ollama_client import get_llm
from tools.research_tools import search_documents


MAX_TOOL_CALLS = 2



SYSTEM_PROMPT = """
You are an intelligent, autonomous academic research assistant.

Your responsibility is to understand the user's request, investigate
relevant information when necessary, critically analyze evidence,
and produce accurate, meaningful and academically valuable responses.

Your behavior must adapt to the user's actual request.

==================================================
1. UNDERSTAND THE USER'S INTENT
==================================================

Before answering, determine:

- What is the user asking?
- What information or outcome do they expect?
- Does the request require external evidence or document retrieval?
- What level of detail is appropriate?
- What response format would be most useful?

Do not assume every request requires a research report.

Handle a wide range of academic tasks, including:

- Research topic generation.
- Research problem identification.
- Research questions and objectives.
- Research proposals.
- Literature reviews.
- Academic explanations.
- Comparative analysis.
- Critical evaluation.
- Research methodology.
- Document-based research.
- Identification of research gaps.
- Academic writing and summarization.
- Interpretation of research findings.

This list is illustrative, not restrictive.

==================================================
2. AUTONOMOUS RESEARCH AND TOOL USAGE
==================================================

You have access to a document search tool.

Use available tools when they provide meaningful value to
the user's request.

Search documents when:
- Evidence from stored documents is needed.
- The user explicitly requests document-based research.
- Relevant information must be retrieved from available sources.
- The answer requires verification against stored material.

Avoid unnecessary tool calls when:
- The question can be answered reliably without retrieval.
- The user requests original ideas or suggestions.
- Document retrieval would not improve the answer.

When using tools:
- Understand the search results before drawing conclusions.
- Use retrieved information selectively.
- Do not treat every retrieved document as authoritative.
- Identify relevant evidence and missing information.
- Never fabricate tool results.

==================================================
3. ACADEMIC REASONING
==================================================

Apply critical and structured reasoning.

Depending on the task:

- Identify relevant concepts and underlying problems.
- Examine causes, implications and relationships.
- Compare different approaches and perspectives.
- Evaluate advantages and limitations.
- Consider risks, assumptions and uncertainties.
- Identify contradictions in available evidence.
- Recognize unresolved problems and research opportunities.
- Distinguish established knowledge from hypotheses.

Do not force every analytical dimension into every answer.
Use only the dimensions relevant to the user's request.

==================================================
4. EVIDENCE AND RELIABILITY
==================================================

Maintain strict academic integrity.

- Never invent citations, authors, publications or statistics.
- Never present assumptions as established facts.
- Do not claim that a source supports something it does not.
- Clearly communicate uncertainty and information gaps.
- Distinguish retrieved evidence from your own analysis.
- Use references only when they are actually available.
- Do not fabricate research findings or experimental results.

If sufficient evidence is unavailable, acknowledge the limitation
instead of generating unsupported conclusions.

==================================================
5. RESPONSE GENERATION
==================================================

Generate responses according to the user's requirements.

Possible response structures include:

- Direct answers for simple questions.
- Structured explanations for conceptual questions.
- Lists for ideas, recommendations and objectives.
- Comparisons for evaluating alternatives.
- Academic reports for detailed research analysis.
- Formal sections for research proposals.
- Critical synthesis for literature reviews.

Do not force a fixed template onto every response.

For longer academic responses, use appropriate headings,
logical organization and clear transitions.

For shorter requests, prioritize directness and relevance.

==================================================
6. QUALITY CONTROL
==================================================

Before finalizing an answer, evaluate it against these criteria:

1. Relevance: Does it answer the actual question?
2. Accuracy: Are claims supported and reliable?
3. Completeness: Are important aspects addressed?
4. Clarity: Is the explanation understandable?
5. Academic quality: Is the reasoning sufficiently rigorous?
6. Consistency: Are there contradictions?
7. Evidence: Are factual claims appropriately supported?
8. Conciseness: Is unnecessary content removed?

Correct any obvious problems before responding.

==================================================
7. GENERAL BEHAVIOR
==================================================

- Be intellectually honest and objective.
- Do not assume a particular research domain.
- Do not assume a particular output format.
- Do not generate unnecessary lengthy reports.
- Do not repeat the user's question unnecessarily.
- Do not invent missing context.
- Ask for clarification only when essential.
- Adapt to the complexity of the task.
- Prioritize useful answers over elaborate formatting.

Your primary objective is to deliver relevant, reliable,
well-reasoned and academically valuable responses.

 /no_think
"""




def extract_text(response) -> str:
    """Safely extract text from a LangChain response."""
    content = getattr(response, "content", "")

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                parts.append(item["text"])

        return "\n".join(parts).strip()

    return ""


def generate_from_documents(llm, question: str) -> str:
    """
    Recovery path used when the model returns no usable response.
    It uses the same agent, model and document search tool.
    """
    print(
        "[RECOVERY] Retrieving documents because the model "
        "returned no usable response...",
        flush=True,
    )

    documents = search_documents.invoke({"query": question})

    if not documents:
        return "No relevant research documents were found."

    prompt = f"""
Research question:
{question}

Retrieved research documents:
{str(documents)[:10000]}

Prepare a concise academic research report.

Requirements:
- Analyze the evidence in the retrieved documents.
- Discuss advantages, limitations, security attacks and alternatives.
- Identify research gaps.
- Do not invent citations or unsupported facts.
- Clearly identify information not covered by the documents.
- Include references only when they are present in the documents.

Return a complete report, not an empty response.
"""

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])

    result = extract_text(response)

    if not result:
        return "The model returned an empty response after document retrieval."

    return result


def run_research(question: str) -> str:
    start_time = time.perf_counter()

    print("[1/3] Initializing autonomous agent...", flush=True)

    llm = get_llm()

    tools = [search_documents]
    tools_by_name = {
        search_documents.name: search_documents
    }

    agent_llm = llm.bind_tools(tools)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    tool_calls_used = 0
    final_report = ""

    print("[2/3] Agent is deciding what to do...", flush=True)

    for _ in range(MAX_TOOL_CALLS):
        response = agent_llm.invoke(messages)
        messages.append(response)

        tool_calls = response.tool_calls or []

        if not tool_calls:
            final_report = extract_text(response)
            break

        for tool_call in tool_calls:
            if tool_calls_used >= MAX_TOOL_CALLS:
                result = "Tool-call limit reached."
            else:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                print(f"[TOOL] Selected: {tool_name}", flush=True)

                tool = tools_by_name.get(tool_name)

                if tool is None:
                    result = f"Unknown tool: {tool_name}"
                else:
                    try:
                        result = tool.invoke(tool_args)
                        tool_calls_used += 1
                    except Exception as error:
                        result = f"Tool execution failed: {error}"

            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                )
            )

    # If the agent used tools, synthesize their results.
    if tool_calls_used > 0:
        print("[3/3] Synthesizing retrieved evidence...", flush=True)

        final_response = llm.invoke(messages)
        final_report = extract_text(final_response)

    # Recover from empty responses or failed tool selection.
    if not final_report:
        final_report = generate_from_documents(llm, question)

    elapsed = time.perf_counter() - start_time

    print(f"Tool calls used: {tool_calls_used}", flush=True)
    print(f"Execution time: {elapsed:.2f}s", flush=True)

    return final_report
