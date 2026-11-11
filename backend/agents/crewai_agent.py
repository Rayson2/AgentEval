import time
from dotenv import load_dotenv
from crewai import Agent, Crew, LLM, Process, Task
from tools.websearch_tool import WebSearchSession, requires_web_search
load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "qwen3:1.7b"
OLLAMA_URL = "http://localhost:11434"
MAX_OUTPUT_TOKENS = 1600

# ============================================================
# CREWAI RESEARCH FUNCTION
# ============================================================

def run_crewai_research(question: str) -> str:

    start_time = time.perf_counter()
    search_session = WebSearchSession()

    print("\n[1/3] Initializing CrewAI...", flush=True)

    # --------------------------------------------------------
    # QUERY ANALYSIS
    # --------------------------------------------------------

    search_required, search_reason = requires_web_search(question)

    print("\n========== QUERY ANALYSIS ==========")
    print(f"Question: {question}")
    print(f"Search required: {search_required}")
    print(f"Reason: {search_reason}")
    print("====================================\n")

    # --------------------------------------------------------
    # LLM CONFIGURATION
    # --------------------------------------------------------

    llm = LLM(
        model=f"ollama/{MODEL_NAME}",
        base_url=OLLAMA_URL,
        temperature=0.2,
        max_tokens=MAX_OUTPUT_TOKENS,
        context_window_size=8192,
    )

    # --------------------------------------------------------
    # MANDATORY INITIAL SEARCH
    # --------------------------------------------------------

    search_results = (
        "Web search was not required for this query."
    )

    if search_required:
        print(
            "[WEB] Search required. Performing initial search...",
            flush=True,
        )

        # IMPORTANT:
        # Call the normal Python function, NOT the CrewAI Tool.
        search_results = search_session.execute_search(question)

    else:
        print(
            "[WEB] Search not required. Skipping Serper.",
            flush=True,
        )

    # --------------------------------------------------------
    # AGENT CONFIGURATION
    # --------------------------------------------------------

    print(
        "[2/3] Creating research agent and task...",
        flush=True,
    )

    researcher = Agent(

        role="Academic Research Analyst",

        goal=(
            "Produce accurate, structured and evidence-based "
            "research reports. Use web evidence when required "
            "and established knowledge when sufficient."
        ),

        backstory=(
            "You are an academic research analyst specializing "
            "in computer science, artificial intelligence, "
            "emerging technologies and technical research. "

            "A Python-based query analyzer determines whether "
            "external information is required. "

            "When web search is required, analyze the retrieved "
            "evidence and perform additional searches only "
            "when necessary. "

            "When web search is not required, rely on established "
            "technical knowledge. "

            "Never fabricate facts, references or statistics."
        ),

        llm=llm,

        # No search tool is exposed for ordinary queries.
        tools=(
            [search_session.tool]
            if search_required
            else []
        ),

        verbose=False,
        allow_delegation=False,
        max_iter=3,
    )

    # --------------------------------------------------------
    # RESEARCH TASK
    # --------------------------------------------------------

    research_task = Task(

        description="""

        Research question:
        {question}

        ==================================================
        SEARCH DECISION
        ==================================================

        Search required: {search_decision}

        Reason: {search_reason}

        Initial web search results:
        {search_results}

        ==================================================
        RESEARCH INSTRUCTIONS
        ==================================================

        1. Follow the Python query analyzer's search decision.

        2. If SEARCH DECISION is TRUE:

           - Analyze the initial search results.
           - The initial search has already been performed.
           - Use the search tool for additional information
             only when necessary.
           - Maximum two total searches.
           - Prioritize academic papers, IEEE, NIST,
             official documentation and government sources.
           - Check publication dates and source relevance.
           - Distinguish recent findings from older research.

        3. If SEARCH DECISION is FALSE:

           - Do not perform web searches.
           - Use established technical knowledge.
           - Do not invent current facts or references.

        ==================================================
        EVIDENCE REQUIREMENTS
        ==================================================

        - Never fabricate authors, dates or statistics.
        - Use only source information actually retrieved.
        - Clearly distinguish evidence from interpretation.
        - If information is insufficient, state this explicitly.
        - Do not treat search snippets as definitive proof.
        - Do not claim information is current without evidence.

        ==================================================
        REPORT REQUIREMENTS
        ==================================================

        Produce a focused academic research report.

        Adapt the report to the actual research question.
        Avoid irrelevant sections when they do not apply.
        Keep the report concise enough to complete every applicable
        section. Never stop in the middle of a sentence or bullet.

        """,

        expected_output="""

        A focused academic research report containing:

        1. Executive Summary
        2. Key Findings
        3. Advantages and Limitations
        4. Potential Attacks (if applicable)
        5. Alternative Mechanisms
        6. Research Gaps
        7. Conclusion
        8. References

        References must contain actual source titles and URLs
        retrieved through web search.

        If no search was performed, do not fabricate references.
        Explicitly indicate that no external sources were retrieved.

        """,

        agent=researcher,
    )

    # --------------------------------------------------------
    # CREW CONFIGURATION
    # --------------------------------------------------------

    crew = Crew(

        agents=[researcher],
        tasks=[research_task],
        process=Process.sequential,
        verbose=False,
    )

    # --------------------------------------------------------
    # EXECUTION
    # --------------------------------------------------------

    print(
        "[3/3] Starting CrewAI research...",
        flush=True,
    )

    result = crew.kickoff(
        inputs={
            "question": question,
            "search_decision": str(
                search_required
            ).upper(),
            "search_reason": search_reason,
            "search_results": search_results,
        }
    )

    # --------------------------------------------------------
    # RESULTS AND METRICS
    # --------------------------------------------------------

    report = str(result.raw).strip()
    elapsed = time.perf_counter() - start_time

    print("\n========== CREWAI EXECUTION ==========")
    print(f"Model: {MODEL_NAME}")
    print("Framework: CrewAI")
    print(f"Search required: {search_required}")
    print(f"Search reason: {search_reason}")
    print(
        f"Search calls: {search_session.search_count}/"
        f"{search_session.max_search_calls}"
    )
    print(f"Search time: {search_session.search_time:.2f} seconds")
    print(f"Total execution time: {elapsed:.2f} seconds")
    print("======================================\n")

    if not report:

        raise RuntimeError(
            "CrewAI returned an empty report."
        )
    return report
