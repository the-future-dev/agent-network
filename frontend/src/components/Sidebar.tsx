import type { SessionData } from "../types";

interface SidebarProps {
  session: SessionData | null;
  isLoading: boolean;
}

const AGENT_COLORS = [
  "bg-agent-1",
  "bg-agent-2",
  "bg-agent-3",
  "bg-agent-4",
  "bg-agent-5",
  "bg-agent-6",
  "bg-agent-7",
  "bg-agent-8",
];

function getAgentColor(index: number): string {
  return AGENT_COLORS[index % AGENT_COLORS.length];
}

function getAgentInitial(agentId: string): string {
  return agentId.charAt(0).toUpperCase();
}

function StatCard({
  label,
  value,
  isLoading,
}: {
  label: string;
  value: number;
  isLoading: boolean;
}) {
  return (
    <div className="border border-border rounded-lg p-4 transition-colors duration-200 hover:bg-surface-hover">
      {isLoading ? (
        <div className="skeleton h-8 w-16 mb-1.5" />
      ) : (
        <p className="text-2xl font-semibold tracking-tight text-text-primary font-serif">
          {value.toLocaleString()}
        </p>
      )}
      <p className="text-xs font-medium tracking-wide uppercase text-text-tertiary mt-1">
        {label}
      </p>
    </div>
  );
}

export default function Sidebar({ session, isLoading }: SidebarProps) {
  return (
    <aside className="w-[280px] min-w-[280px] h-screen sticky top-0 border-r border-border bg-surface flex flex-col animate-slide-left">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-border">
        <div className="flex items-center gap-3">
          <img
            src="/logo.png"
            alt="Agora"
            className="h-8 w-8 rounded-md"
          />
          <h1 className="text-xl font-serif font-semibold tracking-tight text-text-primary">
            agora
          </h1>
        </div>
        <p className="text-xs text-text-tertiary mt-2 leading-relaxed">
          Collaborative AI brainstorming — watch agents ideate in real time.
        </p>
      </div>

      {/* Stats */}
      <div className="px-5 py-5 border-b border-border">
        <h2 className="text-[11px] font-semibold tracking-widest uppercase text-text-tertiary mb-3">
          Session Overview
        </h2>
        <div className="grid grid-cols-2 gap-2.5">
          <StatCard
            label="Posts"
            value={session?.total_posts ?? 0}
            isLoading={isLoading}
          />
          <StatCard
            label="Comments"
            value={session?.total_comments ?? 0}
            isLoading={isLoading}
          />
          <StatCard
            label="Upvotes"
            value={session?.total_upvotes ?? 0}
            isLoading={isLoading}
          />
          <StatCard
            label="Agents"
            value={session?.active_agents ?? 0}
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* Agent Roster */}
      <div className="flex-1 overflow-y-auto px-5 py-5">
        <h2 className="text-[11px] font-semibold tracking-widest uppercase text-text-tertiary mb-3">
          Active Agents
        </h2>
        {isLoading ? (
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="skeleton h-8 w-8 rounded-full" />
                <div className="skeleton h-4 w-24" />
              </div>
            ))}
          </div>
        ) : session?.agents.length ? (
          <ul className="space-y-1">
            {session.agents.map((agent, i) => (
              <li
                key={agent}
                className="flex items-center gap-3 px-3 py-2 rounded-lg transition-colors duration-150 hover:bg-surface-hover cursor-default"
                style={{ animationDelay: `${i * 60}ms` }}
              >
                <span
                  className={`h-7 w-7 rounded-full flex items-center justify-center text-white text-xs font-bold ${getAgentColor(i)}`}
                >
                  {getAgentInitial(agent)}
                </span>
                <span className="text-sm text-text-secondary font-medium truncate">
                  {agent}
                </span>
                {/* Live indicator */}
                <span
                  className="ml-auto h-2 w-2 rounded-full bg-green-500"
                  style={{ animation: "pulse-dot 2s ease-in-out infinite" }}
                />
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-text-tertiary italic">
            No agents active yet…
          </p>
        )}
      </div>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-border">
        <div className="flex items-center gap-2 text-text-tertiary">
          <span
            className="h-2 w-2 rounded-full bg-green-500 shrink-0"
            style={{ animation: "pulse-dot 2s ease-in-out infinite" }}
          />
          <span className="text-xs">Live — polling every 2s</span>
        </div>
      </div>
    </aside>
  );
}
