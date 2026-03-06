import asyncio
import os
import sys
import uuid
from dotenv import load_dotenv
from google import genai
from board import Board
from agent import run_agent
from config import Config

load_dotenv()  # Load GOOGLE_API_KEY from .env if present


async def main():
    config = Config()

    # Single shared client — created once, reused by every agent every round
    client = genai.Client()

    # Allow overriding the model from CLI: python main.py --model gemini-2.5-pro
    if "--model" in sys.argv:
        idx = sys.argv.index("--model")
        config.model = sys.argv[idx + 1]

    # Accept prompt from CLI: python main.py --prompt "..."
    # Falls back to a default if not provided (useful for direct CLI runs)
    if "--prompt" in sys.argv:
        idx = sys.argv.index("--prompt")
        user_prompt = sys.argv[idx + 1]
    else:
        user_prompt = "Generate ad campaign concepts for a sustainable fashion brand's Super Bowl spot"

    # Create a new session for this run — no longer wipes the DB
    session_id = str(uuid.uuid4())

    board = Board(config.db_path, session_id)
    await board.init()

    # Register session in the DB
    await board.db.execute(
        "INSERT INTO sessions (id, prompt) VALUES (?, ?)",
        (session_id, user_prompt)
    )
    await board.db.commit()

    # Scandinavian agent personas
    AGENT_PERSONAS = [
        "Bjørn", "Sigrid", "Lars", "Astrid", "Erik",
        "Ingrid", "Sven", "Freya", "Gunnar", "Maja",
        "Ragnar", "Elsa", "Leif", "Karin", "Tor",
    ]
    agent_ids = [
        AGENT_PERSONAS[i % len(AGENT_PERSONAS)]
        if i < len(AGENT_PERSONAS)
        else f"{AGENT_PERSONAS[i % len(AGENT_PERSONAS)]}-{i // len(AGENT_PERSONAS) + 1}"
        for i in range(config.num_agents)
    ]

    print(f"\n🚀 Launching {config.num_agents} agents × {config.num_rounds} rounds")
    print(f"   Model: {config.model}  |  DB: {config.db_path}")
    print(f"   Session: {session_id}\n")
    print(f'   Challenge: "{user_prompt}"\n')
    print("─" * 60)

    # Run all agents concurrently — true swarm, no coordination
    tasks = [
        run_agent(agent_id, user_prompt, board, config, client)
        for agent_id in agent_ids
    ]
    await asyncio.gather(*tasks)

    # ── Final results ──────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"🏆  TOP {config.top_k} CONCEPTS (by upvotes)")
    print("=" * 60 + "\n")

    results = await board.get_results(config.top_k)
    if not results:
        print("No posts were created. Try increasing num_rounds.")
    else:
        for i, post in enumerate(results, 1):
            print(f"#{i}  ⬆ {post['upvotes']}  [{post['agent_id']}]")
            print(f"     {post['content']}")
            if post["comments"]:
                print("     Debate thread:")
                for c in post["comments"]:
                    print(f"       💬 {c['agent_id']}: {c['content']}")
            print()

    await board.close()


if __name__ == "__main__":
    asyncio.run(main())
