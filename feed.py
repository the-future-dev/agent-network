import random


async def get_feed(
    board,
    agent_id: str,
    feed_size: int = 5,
    explore_ratio: float = 0.4,
) -> list[dict]:
    """
    Returns a mixed feed of posts for the agent to read.

    - explore_ratio  → fraction from unseen posts (novelty / anti-groupthink)
    - 1-explore_ratio → fraction from top-upvoted posts (quality signal)

    After assembly the agent's read positions are recorded in seen_posts so
    the next round's exploration set is always fresh.
    """
    n_explore = max(1, int(feed_size * explore_ratio))
    n_exploit = feed_size - n_explore

    # Exploration: posts this agent hasn't seen yet
    unseen = await board.get_unseen_posts(agent_id, limit=n_explore * 2)
    if not unseen:
        # Fallback if the agent has read everything
        unseen = await board.get_recent_posts(limit=n_explore * 2)

    # Exploitation: highest-signal posts across the board
    top = await board.get_top_posts(limit=n_exploit * 2)

    explore = random.sample(unseen, min(n_explore, len(unseen)))
    exploit = random.sample(top, min(n_exploit, len(top)))

    # Merge and deduplicate by post ID
    seen_ids: set[str] = set()
    feed: list[dict] = []
    for post in explore + exploit:
        if post["id"] not in seen_ids:
            seen_ids.add(post["id"])
            post["comments"] = await board.get_comments(post["id"])
            feed.append(post)

    feed = feed[:feed_size]

    # Mark as seen so next round's exploration is fresh
    await board.mark_seen(agent_id, [p["id"] for p in feed])

    return feed


def format_feed_for_prompt(feed: list[dict]) -> str:
    """Render the feed as readable plain text for the LLM context window."""
    if not feed:
        return "The board is empty. Be the first to post an idea!"

    lines = []
    for post in feed:
        lines.append(
            f"--- Post [{post['id']}] by {post['agent_id']} "
            f"(⬆ {post['upvotes']}) ---"
        )
        lines.append(post["content"])
        for c in post.get("comments", []):
            lines.append(f"  💬 {c['agent_id']}: {c['content']}")
        lines.append("")

    return "\n".join(lines)
