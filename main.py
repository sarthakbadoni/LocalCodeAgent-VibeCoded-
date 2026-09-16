from agent.agent import run_agent


def main():
    print("LocalCodeAgent")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("> ")

            if user_input.lower() in {"exit", "quit"}:
                break

            if not user_input.strip():
                continue

            response = run_agent(user_input)

            print(f"\n{response}\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break

        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()