import { describe, it, expect } from "vitest";
import { analyzeContributors } from "../src/analyzers/contributorAnalyzer.js";

describe("Contributor Analyzer", () => {
  it("handles empty commit list", () => {
    const metrics = analyzeContributors([]);

    expect(metrics.totalContributors).toBe(0);
    expect(metrics.topContributorShare).toBe(0);
    expect(metrics.concentrationIndex).toBe(0);
  });

  it("detects single contributor", () => {
    const commits = [
      { authorId: "alice" },
      { authorId: "alice" },
      { authorId: "alice" }
    ];

    const metrics = analyzeContributors(commits);

    expect(metrics.totalContributors).toBe(1);
    expect(metrics.topContributorShare).toBe(1);
    expect(metrics.concentrationIndex).toBe(1);
  });

  it("detects distributed contributors", () => {
    const commits = [
      { authorId: "alice" },
      { authorId: "bob" },
      { authorId: "charlie" },
      { authorId: "alice" }
    ];

    const metrics = analyzeContributors(commits);

    expect(metrics.totalContributors).toBe(3);
    expect(metrics.topContributorShare).toBeLessThan(1);
    expect(metrics.concentrationIndex).toBeLessThan(1);
  });
});
