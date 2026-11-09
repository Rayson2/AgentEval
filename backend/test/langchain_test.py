import time
from agents.langchain_agent import run_research


if __name__ == "__main__":

    question = """
    Explain how fuzzy logic can be used for autonomous rover navigation.
    """

    print("\nStarting Fast LangChain Research Agent...\n")

    start = time.perf_counter()

    try:
        response = run_research(question)

        elapsed = time.perf_counter() - start

        print("\n" + "=" * 50)
        print("LANGCHAIN RESEARCH REPORT")
        print("=" * 50)

        print(response)

        print("\n" + "=" * 50)
        print(f"TOTAL TIME: {elapsed:.2f} seconds")

        if elapsed <= 30:
            print("STATUS: TARGET ACHIEVED")
        else:
            print("STATUS: OPTIMIZATION REQUIRED")

    except Exception as error:
        print("\nAgent execution failed:")
        print(repr(error))
