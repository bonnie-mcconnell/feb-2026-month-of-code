import { describe, it, expect } from "vitest";
import { analyzeCommits } from "../src/analyzers/commitAnalyzer.js";

const BASE_DATE = new Date("2026-02-01T00:00:00Z");

function daysAgo(days: number): Date {
  return new Date(
    BASE_DATE.getTime() - days * 24 * 60 * 60 * 1000
  );
}

describe("Commit Analyzer", () => {
  it("handles empty commit list", () => {
    const metrics = analyzeCommits([], {
      windowDays: 90,
      now: BASE_DATE
    });

    expect(metrics.commitsLast30Days).toBe(0);
    expect(metrics.commitsLast90Days).toBe(0);
    expect(metrics.avgCommitsPerWeek).toBe(0);
    expect(metrics.activityTrendRatio).toBe(0);
    expect(metrics.lastCommitDate).toBeNull();
  });

  it("ignores commits outside window", () => {
    const commits = [
      { authoredDate: daysAgo(120) }
    ];

    const metrics = analyzeCommits(commits, {
      windowDays: 90,
      now: BASE_DATE
    });

    expect(metrics.commitsLast90Days).toBe(0);
  });

  it("calculates even distribution correctly", () => {
    const commits = [
      { authoredDate: daysAgo(10) },
      { authoredDate: daysAgo(20) },
      { authoredDate: daysAgo(40) },
      { authoredDate: daysAgo(60) },
      { authoredDate: daysAgo(80) }
    ];

    const metrics = analyzeCommits(commits, {
      windowDays: 90,
      now: BASE_DATE
    });

    expect(metrics.commitsLast90Days).toBe(5);
    expect(metrics.commitsLast30Days).toBe(2);
    expect(metrics.avgCommitsPerWeek).toBeCloseTo(
      5 / (90 / 7),
      5
    );
    expect(metrics.activityTrendRatio).toBeGreaterThan(0);
  });

  it("detects recent spike in activity", () => {
    const commits = [
      { authoredDate: daysAgo(5) },
      { authoredDate: daysAgo(6) },
      { authoredDate: daysAgo(7) },
      { authoredDate: daysAgo(8) },
      { authoredDate: daysAgo(9) }
    ];

    const metrics = analyzeCommits(commits, {
      windowDays: 90,
      now: BASE_DATE
    });

    expect(metrics.commitsLast30Days).toBe(5);
    expect(metrics.commitsLast90Days).toBe(5);
    expect(metrics.activityTrendRatio).toBeGreaterThan(1);
  });

  it("computes lastCommitDate correctly", () => {
    const commits = [
      { authoredDate: daysAgo(20) },
      { authoredDate: daysAgo(5) },
      { authoredDate: daysAgo(40) }
    ];

    const metrics = analyzeCommits(commits, {
      windowDays: 90,
      now: BASE_DATE
    });

    expect(metrics.lastCommitDate).toEqual(daysAgo(5));
  });
});
