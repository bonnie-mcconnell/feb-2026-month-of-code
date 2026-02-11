Uptime Monitor (SQLite-backed CLI)

A minimal, production-oriented uptime monitoring tool built around deterministic checks, typed results, and persistent history.

Designed to demonstrate:

Clean architecture separation (checker / monitor / storage / cli)

Typed domain models

Transition detection logic

SQLite-backed persistence

Testable, mock-friendly design

What It Does

Performs HTTP health checks

Classifies status as: UP, DEGRADED, DOWN

Persists results to SQLite

Detects status transitions

Calculates uptime statistics

Provides CLI access to:

run

report

history

Architecture

checker.py
Responsible only for performing HTTP checks and classifying results.

monitor.py
Orchestrates checks, detects transitions, writes to storage.

storage.py
SQLite persistence layer. Returns domain models, not dicts.

models.py
Typed domain entities (CheckResult).

cli.py
User interface layer. No business logic.

This separation keeps the system:

Testable

Replaceable (swap SQLite → Postgres easily)

Clear in responsibility boundaries

Status Logic

UP
HTTP < 500 and under degraded threshold.

DEGRADED
HTTP < 500 but slower than configured threshold.

DOWN
HTTP >= 500 or network error.

Usage

Run checks:

monitor run


Generate report:

monitor report https://example.com


Show history:

monitor history https://example.com

Testing
pytest


Tests cover:

Classification logic

Transition detection

Storage correctness

Summary math

CLI smoke test

Design Philosophy

Deterministic logic

No external monitoring services

No background threads

No async complexity

No overengineering

Focused on core signal.