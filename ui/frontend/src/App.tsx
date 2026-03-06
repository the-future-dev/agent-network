import React, { useEffect, useState } from "react";

type Comment = {
  id: string;
  agent_id: string;
  content: string;
  created_at: string;
};

type Post = {
  id: string;
  agent_id: string;
  content: string;
  created_at: string;
  upvotes: number;
  comments: Comment[];
};

type ResultsPayload = {
  challenge: string;
  model: string;
  num_agents: number;
  num_rounds: number;
  generated_at: string;
  results: Post[];
};

type LoadState = "loading" | "ready" | "empty" | "error";

export const App: React.FC = () => {
  const [state, setState] = useState<LoadState>("loading");
  const [data, setData] = useState<ResultsPayload | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`/results.json?ts=${Date.now()}`);
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const json = (await res.json()) as ResultsPayload;
        if (!json.results || json.results.length === 0) {
          setState("empty");
        } else {
          setData(json);
          setState("ready");
        }
      } catch (err) {
        console.error("Failed to load results.json", err);
        setState("error");
      }
    };

    load();
  }, []);

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "2.5rem 1.5rem",
        gap: "1.5rem",
        background:
          "radial-gradient(circle at top left, #1d4ed8 0, #0f172a 40%, #020617 100%)",
        color: "white",
        fontFamily:
          "-apple-system, BlinkMacSystemFont, system-ui, -system-ui, sans-serif"
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "960px",
          borderRadius: "1.25rem",
          backgroundColor: "rgba(15, 23, 42, 0.9)",
          border: "1px solid rgba(148, 163, 184, 0.4)",
          boxShadow: "0 24px 60px rgba(15, 23, 42, 0.85)",
          padding: "1.5rem 1.75rem"
        }}
      >
        <div
          style={{
            fontSize: "0.75rem",
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "#a5b4fc",
            marginBottom: "0.35rem"
          }}
        >
          Agora Agent Network
        </div>
        <h1
          style={{
            fontSize: "1.9rem",
            margin: 0,
            marginBottom: "0.35rem",
            fontWeight: 700
          }}
        >
          Swarm Run Results
        </h1>
        <p
          style={{
            fontSize: "0.95rem",
            color: "#cbd5f5",
            margin: 0,
            lineHeight: 1.5
          }}
        >
          Latest swarm run, ranked by upvotes with quick context on who
          contributed what.
        </p>
      </div>

      <div
        style={{
          width: "100%",
          maxWidth: "960px",
          display: "flex",
          flexDirection: "column",
          gap: "1rem"
        }}
      >
        {state === "loading" && (
          <div
            style={{
              padding: "1rem 1.25rem",
              borderRadius: "0.9rem",
              backgroundColor: "rgba(15, 23, 42, 0.9)",
              border: "1px solid rgba(148, 163, 184, 0.4)",
              fontSize: "0.9rem",
              color: "#e5e7eb"
            }}
          >
            Looking for <code>results.json</code>… Run{" "}
            <code>python main.py</code> from the project root, then refresh this
            page.
          </div>
        )}

        {state === "error" && (
          <div
            style={{
              padding: "1rem 1.25rem",
              borderRadius: "0.9rem",
              backgroundColor: "rgba(127, 29, 29, 0.85)",
              border: "1px solid rgba(248, 113, 113, 0.7)",
              fontSize: "0.9rem",
              color: "#fee2e2"
            }}
          >
            Could not load <code>results.json</code>. Make sure you have run{" "}
            <code>python main.py</code> at least once and that this dashboard is
            being served from <code>ui/frontend</code> via{" "}
            <code>npm run dev</code>.
          </div>
        )}

        {state === "empty" && (
          <div
            style={{
              padding: "1rem 1.25rem",
              borderRadius: "0.9rem",
              backgroundColor: "rgba(15, 23, 42, 0.9)",
              border: "1px solid rgba(148, 163, 184, 0.4)",
              fontSize: "0.9rem",
              color: "#e5e7eb"
            }}
          >
            The latest run wrote an empty results list. Try increasing{" "}
            <code>num_rounds</code> in <code>config.py</code> and run{" "}
            <code>python main.py</code> again.
          </div>
        )}

        {state === "ready" && data && (
          <>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "minmax(0, 2.2fr) minmax(0, 1fr)",
                gap: "1.25rem",
                alignItems: "flex-start"
              }}
            >
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.45rem",
                  fontSize: "0.8rem",
                  color: "#9ca3af"
                }}
              >
                <div>
                  <span style={{ color: "#e5e7eb" }}>Challenge:</span>{" "}
                  {data.challenge}
                </div>
                <div>
                  <span style={{ color: "#e5e7eb" }}>Model:</span> {data.model}
                </div>
                <div>
                  <span style={{ color: "#e5e7eb" }}>Agents:</span>{" "}
                  {data.num_agents}
                </div>
                <div>
                  <span style={{ color: "#e5e7eb" }}>Rounds:</span>{" "}
                  {data.num_rounds}
                </div>
                <div>
                  <span style={{ color: "#e5e7eb" }}>Generated:</span>{" "}
                  {new Date(data.generated_at).toLocaleTimeString()}
                </div>
              </div>

              {data.results[0] && (
                <div
                  style={{
                    borderRadius: "0.9rem",
                    padding: "0.85rem 1rem",
                    background:
                      "linear-gradient(135deg, rgba(34,197,94,0.15), rgba(59,130,246,0.12))",
                    border: "1px solid rgba(74, 222, 128, 0.45)",
                    boxShadow: "0 16px 40px rgba(22, 163, 74, 0.4)",
                    fontSize: "0.85rem",
                    color: "#bbf7d0"
                  }}
                >
                  <div
                    style={{
                      textTransform: "uppercase",
                      letterSpacing: "0.16em",
                      fontSize: "0.72rem",
                      marginBottom: "0.25rem"
                    }}
                  >
                    Highlight
                  </div>
                  <div style={{ fontWeight: 600, marginBottom: "0.2rem" }}>
                    #{1} • {data.results[0].agent_id} • ⬆{" "}
                    {data.results[0].upvotes} upvotes
                  </div>
                  <div
                    style={{
                      color: "#dcfce7",
                      lineHeight: 1.5,
                      overflow: "hidden",
                      display: "-webkit-box",
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: "vertical"
                    }}
                  >
                    {data.results[0].content}
                  </div>
                </div>
              )}
            </div>

            {data.results.map((post, index) => (
              <div
                key={post.id}
                style={{
                  borderRadius: "1rem",
                  padding: "1.25rem 1.4rem",
                  backgroundColor: "rgba(15, 23, 42, 0.95)",
                  border: "1px solid rgba(148, 163, 184, 0.55)",
                  boxShadow: "0 20px 45px rgba(15, 23, 42, 0.8)"
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "baseline",
                    marginBottom: "0.5rem",
                    gap: "0.75rem"
                  }}
                >
                  <div
                    style={{
                      fontSize: "0.85rem",
                      textTransform: "uppercase",
                      letterSpacing: "0.12em",
                      color: "#9ca3af"
                    }}
                  >
                    #{index + 1} • {post.id} • {post.agent_id}
                  </div>
                  <div
                    style={{
                      fontSize: "0.9rem",
                      fontWeight: 600,
                      color: "#fbbf24"
                    }}
                  >
                    ⬆ {post.upvotes} upvotes
                  </div>
                </div>

                <div
                  style={{
                    fontSize: "1rem",
                    lineHeight: 1.6,
                    color: "#e5e7eb",
                    marginBottom: post.comments.length ? "0.9rem" : 0
                  }}
                >
                  {post.content}
                </div>

                {post.comments.length > 0 && (
                  <div
                    style={{
                      paddingTop: "0.75rem",
                      borderTop: "1px solid rgba(55, 65, 81, 0.8)",
                      marginTop: "0.25rem",
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.5rem"
                    }}
                  >
                    <div
                      style={{
                        fontSize: "0.8rem",
                        textTransform: "uppercase",
                        letterSpacing: "0.1em",
                        color: "#9ca3af"
                      }}
                    >
                      Debate thread
                    </div>
                    {post.comments.map((c) => (
                      <div
                        key={c.id}
                        style={{
                          fontSize: "0.9rem",
                          color: "#e5e7eb"
                        }}
                      >
                        <span
                          style={{
                            fontWeight: 600,
                            color: "#a5b4fc",
                            marginRight: "0.35rem"
                          }}
                        >
                          {c.agent_id}:
                        </span>
                        <span>{c.content}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
};


