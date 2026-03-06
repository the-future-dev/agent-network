import { useState } from "react";
import { usePolling } from "./usePolling";
import type {
  SessionData,
  FeedData,
  ActivityData,
  SortMode,
} from "../types";

const POLL_INTERVAL = 2000;

export function useAgora() {
  const [sortMode, setSortMode] = useState<SortMode>("top");

  const session = usePolling<SessionData>("/api/sessions", POLL_INTERVAL);

  const feed = usePolling<FeedData>(
    `/api/feed?sort=${sortMode}&limit=50`,
    POLL_INTERVAL,
  );

  const activity = usePolling<ActivityData>(
    "/api/activity?limit=30",
    POLL_INTERVAL,
  );

  return { session, feed, activity, sortMode, setSortMode };
}
