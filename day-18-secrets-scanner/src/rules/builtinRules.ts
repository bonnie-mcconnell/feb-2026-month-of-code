import type { Rule } from "../types/rule.js";

export const BUILTIN_RULES: Rule[] = [
  {
    ruleId: "aws-access-key-id",
    description: "AWS Access Key ID",
    regex: /\bAKIA[0-9A-Z]{16}\b/g,
    severity: "high"
  },
  {
    ruleId: "private-key",
    description: "Private key block",
    regex: /-----BEGIN (RSA|EC|OPENSSH|DSA) PRIVATE KEY-----/g,
    severity: "high"
  },
  {
    ruleId: "bearer-token",
    description: "Bearer token",
    regex: /\bBearer\s+[A-Za-z0-9\-._~+/]{20,}={0,2}\b/g,
    severity: "medium"
  },
  {
    ruleId: "jwt",
    description: "JWT token",
    regex: /\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b/g,
    severity: "medium"
  },
  {
    ruleId: "generic-api-key",
    description: "Generic API key-like string",
    regex: /\b(?=[A-Za-z0-9]{32,})(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z0-9]+\b/g,
    severity: "low"
  },
  {
    ruleId: "github-token",
    description: "GitHub personal access token",
    regex: /\bghp_[A-Za-z0-9]{36}\b/g,
    severity: "high"
  },
  {
  ruleId: "stripe-secret-key",
    description: "Stripe secret key",
    regex: /\bsk_live_[A-Za-z0-9]{24,}\b/g,
    severity: "high"
  },
  {
    ruleId: "slack-token",
    description: "Slack token",
    regex: /\bxox[baprs]-[A-Za-z0-9-]{10,}\b/g,
    severity: "high"
    }
];
