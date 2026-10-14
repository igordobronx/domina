import { initialState } from "../data/demo";
import type { DemoState, Role, Activity } from "../types";
const KEY = "domina.demo.v1";
export function loadDemo(): DemoState {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return structuredClone(initialState);
    const parsed = JSON.parse(raw);
    if (
      !Array.isArray(parsed.activities) ||
      !Array.isArray(parsed.materials) ||
      !Array.isArray(parsed.completed) ||
      typeof parsed.name !== "string" ||
      !parsed.drafts ||
      typeof parsed.drafts !== "object" ||
      typeof parsed.goal !== "number"
    )
      return structuredClone(initialState);
    return parsed;
  } catch {
    return structuredClone(initialState);
  }
}
export function saveDemo(state: DemoState) {
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
    return true;
  } catch {
    return false;
  }
}
// Visibility is a demo UI rule. Real access control belongs in the API/database.
export function visibleResult(activity: Activity, role: Role) {
  return role !== "aluno" || activity.status === "aprovada";
}
export function validScores(
  scores: number[],
  kind: Activity["kind"] = "redacao",
) {
  if (kind === "matematica")
    return (
      scores.length === 1 &&
      Number.isFinite(scores[0]) &&
      scores[0] >= 0 &&
      scores[0] <= 10
    );
  return (
    scores.length === 5 &&
    scores.every(
      (n) => Number.isFinite(n) && n >= 0 && n <= 200 && n % 20 === 0,
    )
  );
}
export function approveActivity(
  activity: Activity,
  scores: number[],
  feedback: string,
): Activity {
  if (!validScores(scores, activity.kind) || !feedback.trim())
    throw new Error("Revise as notas e escreva o feedback.");
  return {
    ...activity,
    status: "aprovada",
    scores: [...scores],
    feedback: feedback.trim(),
  };
}
