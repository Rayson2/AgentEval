import time
from agents.crewai_agent import run_crewai_research


if __name__ == "__main__":

    question = """
    what is AI?
    """

    print("\nStarting CrewAI Research Agent...\n")

    start = time.perf_counter()

    try:
        response = run_crewai_research(question)

        elapsed = time.perf_counter() - start

        print("\n" + "=" * 60)
        print("CREWAI RESEARCH REPORT")
        print("=" * 60)

        print(response)

        print("\n" + "=" * 60)
        print(f"TOTAL TIME: {elapsed:.2f} seconds")

        if response.strip() and elapsed <= 30:
            print("STATUS: TARGET ACHIEVED")
        elif not response.strip():
            print("STATUS: FAILED - EMPTY RESPONSE")
        else:
            print("STATUS: OPTIMIZATION REQUIRED")

    except Exception as error:
        print("\nCrewAI execution failed:")
        print(repr(error))
