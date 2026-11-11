import time

from agents.autogen_agent import run_autogen_research


if __name__ == "__main__":

    question = """
    What is federated learning?
    and 
    weather in bilaspur, chhattisgarh, india
    """

    print("\nStarting AutoGen Research Agent...\n")

    start = time.perf_counter()

    try:
        response = run_autogen_research(question)

        elapsed = time.perf_counter() - start

        print("\n" + "=" * 60)
        print("AUTOGEN RESEARCH REPORT")
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
        print("\nAutoGen execution failed:")
        print(repr(error))
