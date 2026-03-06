import streamlit as st
import sqlite3
import time
import html

DB_PATH = "board.db"
POLL_INTERVAL = 1.5  # seconds — fast enough to feel live

# Deterministic agent colors — same agent always gets the same color
AGENT_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
    "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
]


def agent_color(agent_id: str) -> str:
    return AGENT_COLORS[hash(agent_id) % len(AGENT_COLORS)]


def agent_badge(agent_id: str) -> str:
    color = agent_color(agent_id)
    return (
        f'<span style="background:{color}; color:#000; padding:2px 8px; '
        f'border-radius:12px; font-size:0.8em; font-weight:600;">'
        f'{agent_id}</span>'
    )


# ── Page setup ────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Agent Network — Live Feed", layout="wide")

st.markdown("""
<style>
    /* Global Background and Typography */
    [data-testid="stAppViewContainer"] { 
        background-color: #f8fafc;
        color: #0f172a;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    /* Hide the top header */
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    /* Main Title */
    h2 {
        color: #0f172a;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    /* Post Cards */
    .post-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.025);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .post-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
    }
    /* Post Header */
    .post-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 12px;
    }
    .vote-count {
        font-size: 1.3em;
        font-weight: 800;
        color: #f43f5e;
        min-width: 48px;
        text-align: center;
        background: #fff1f2;
        padding: 6px 10px;
        border-radius: 12px;
    }
    .post-meta { 
        color: #64748b; 
        font-size: 0.85em; 
        font-weight: 500;
    }
    /* Post Content */
    .post-content {
        font-size: 1.1em;
        line-height: 1.6;
        color: #334155;
        margin: 16px 0;
    }
    /* Comment Blocks */
    .comment-block {
        border-left: 3px solid #cbd5e1;
        margin: 12px 0 12px 24px;
        padding: 12px 16px;
        background: #f8fafc;
        border-radius: 0 12px 12px 0;
        transition: border-color 0.2s ease, background-color 0.2s ease;
    }
    .comment-block:hover {
        border-color: #94a3b8;
        background: #f1f5f9;
    }
    .comment-text { 
        color: #475569; 
        margin-top: 8px; 
        font-size: 0.95em; 
        line-height: 1.5;
    }
    /* Activity Feed Items */
    .activity-item {
        padding: 12px;
        border-bottom: 1px solid #e2e8f0;
        font-size: 0.9em;
        line-height: 1.5;
        background: #ffffff;
        border-radius: 8px;
        margin-bottom: 8px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        transition: transform 0.1s ease;
    }
    .activity-item:hover {
        transform: translateX(2px);
    }
    .activity-preview { 
        color: #64748b; 
        margin-top: 6px; 
        font-style: italic;
        background: #f8fafc;
        padding: 6px 10px;
        border-radius: 6px;
        font-size: 0.95em;
    }
    /* Streamlit overrides */
    .stRadio > div > label > div[data-testid="stMarkdownContainer"] > p {
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 0.95em !important;
    }
    [data-testid="stMetricValue"] {
        color: #0f172a;
        font-weight: 800;
    }
    [data-testid="stMetricLabel"] {
        color: #64748b;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🧠 Agent Network — Live Feed")

placeholder = st.empty()

while True:
    with placeholder.container():
        try:
            db = sqlite3.connect(DB_PATH)

            # ── Stats bar ──────────────────────────────────────────────────────
            n_posts    = db.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
            n_comments = db.execute("SELECT COUNT(*) FROM comments").fetchone()[0]
            n_upvotes  = db.execute("SELECT COUNT(*) FROM upvotes").fetchone()[0]
            n_agents   = db.execute(
                "SELECT COUNT(DISTINCT agent_id) FROM posts"
            ).fetchone()[0]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📝 Posts", n_posts)
            c2.metric("💬 Comments", n_comments)
            c3.metric("⬆ Upvotes", n_upvotes)
            c4.metric("🤖 Active Agents", n_agents)

            # ── Two-column layout ─────────────────────────────────────────────
            feed_col, activity_col = st.columns([3, 1])

            # ===== LEFT: HN-STYLE RANKED FEED =================================
            with feed_col:
                sort_mode = st.radio(
                    "Sort",
                    ["🔥 Top (by votes)", "🕐 Newest first"],
                    horizontal=True,
                    label_visibility="collapsed",
                )
                order_clause = (
                    "upvotes DESC, p.created_at DESC"
                    if "Top" in sort_mode
                    else "p.created_at DESC"
                )

                posts = db.execute(f"""
                    SELECT p.id, p.agent_id, p.content, p.created_at,
                           COUNT(u.agent_id) as upvotes
                    FROM posts p
                    LEFT JOIN upvotes u ON p.id = u.post_id
                    GROUP BY p.id
                    ORDER BY {order_clause}
                """).fetchall()

                if not posts:
                    st.info("⏳ Waiting for agents to start posting…")

                for rank, (post_id, agent, content, ts, votes) in enumerate(posts, 1):
                    # Who upvoted?
                    voters = db.execute(
                        "SELECT agent_id FROM upvotes WHERE post_id = ?", (post_id,)
                    ).fetchall()
                    voter_badges = " ".join(agent_badge(v[0]) for v in voters) if voters else ""

                    # Comments on this post
                    comments = db.execute(
                        "SELECT agent_id, content, created_at FROM comments "
                        "WHERE post_id = ? ORDER BY created_at",
                        (post_id,)
                    ).fetchall()

                    badge = agent_badge(agent)
                    n_c = len(comments)
                    comments_label = (
                        f"{n_c} comment{'s' if n_c != 1 else ''}" if n_c else "no comments yet"
                    )

                    # Escape HTML and convert newlines
                    safe_content = html.escape(content).replace('\n', '<br/>')

                    html_str = (
                        f'<div class="post-card">'
                        f'<div class="post-header">'
                        f'<span class="vote-count">▲ {votes}</span>'
                        f'{badge}'
                        f'<span class="post-meta">#{rank} &middot; {post_id} &middot; {ts}</span>'
                        f'</div>'
                        f'<div class="post-content">{safe_content}</div>'
                        f'<div class="post-meta">'
                        f'{comments_label}'
                        f'{" &middot; upvoted by " + voter_badges if voter_badges else ""}'
                        f'</div>'
                    )
                    for c_agent, c_content, c_ts in comments:
                        safe_c_content = html.escape(c_content).replace('\n', '<br/>')
                        html_str += (
                            f'<div class="comment-block">'
                            f'{agent_badge(c_agent)}'
                            f'<span class="post-meta"> &middot; {c_ts}</span>'
                            f'<div class="comment-text">{safe_c_content}</div>'
                            f'</div>'
                        )
                    html_str += '</div>'
                    st.markdown(html_str, unsafe_allow_html=True)

            # ===== RIGHT: LIVE ACTIVITY LOG ====================================
            with activity_col:
                st.markdown("### ⚡ Live Activity")

                activity = db.execute("""
                    SELECT agent_id, 'posted' as action, content, created_at
                    FROM posts
                    UNION ALL
                    SELECT c.agent_id, 'commented on ' || c.post_id,
                           c.content, c.created_at
                    FROM comments c
                    UNION ALL
                    SELECT u.agent_id, 'upvoted ' || u.post_id,
                           '', u.created_at
                    FROM upvotes u
                    ORDER BY 4 DESC
                    LIMIT 20
                """).fetchall()

                if not activity:
                    st.caption("No activity yet…")

                for a_agent, a_action, a_content, _ in activity:
                    # Escape preview text to avoid breaking HTML layout
                    safe_a_content = html.escape(a_content)
                    preview = (safe_a_content[:55] + "…") if len(safe_a_content) > 55 else safe_a_content
                    preview_html = (
                        f'<div class="activity-preview">{preview}</div>' if preview else ""
                    )
                    st.markdown(
                        f'<div class="activity-item">'
                        f'{agent_badge(a_agent)} <b>{html.escape(a_action)}</b>'
                        f'{preview_html}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

            db.close()

        except Exception as e:
            st.info(f"⏳ Waiting for agents to start… ({e})")

    time.sleep(POLL_INTERVAL)
