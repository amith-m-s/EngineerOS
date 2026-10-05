
## Repository Health

[![CI](https://github.com/amith-m-s/EngineerOS/actions/workflows/ci.yml/badge.svg)](https://github.com/amith-m-s/EngineerOS/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/amith-m-s/EngineerOS)](https://github.com/amith-m-s/EngineerOS)
[![Last Commit](https://img.shields.io/github/last-commit/amith-m-s/EngineerOS)](https://github.com/amith-m-s/EngineerOS/commits/main)
[![Code Size](https://img.shields.io/github/languages/code-size/amith-m-s/EngineerOS)](https://github.com/amith-m-s/EngineerOS)
[![Top Language](https://img.shields.io/github/languages/top/amith-m-s/EngineerOS)](https://github.com/amith-m-s/EngineerOS)
[![Issues](https://img.shields.io/github/issues/amith-m-s/EngineerOS)](https://github.com/amith-m-s/EngineerOS/issues)
[![Stars](https://img.shields.io/github/stars/amith-m-s/EngineerOS?style=social)](https://github.com/amith-m-s/EngineerOS/stargazers)

# EngineerOS

**Simulation-driven engineering command cockpit for practicing system design, incident response, and technical decision making.**

EngineerOS is a software-engineering training platform built with Next.js, FastAPI, SQLAlchemy, WebSockets, automated tests, and CI.

## What it demonstrates

- DDD-style separation of domain, repository, service, and transport concerns.
- JWT authentication and role-aware access control.
- Async in-process domain event bus.
- WebSocket-backed simulation updates.
- Incident-generation and command-evaluation workflows.
- Architecture/risk visualization.
- Backend unit/integration/security tests.
- Type checking, linting, CI and Docker build stages.

## Important implementation note

The incident and evaluation intelligence is **simulation/rule driven** in the current repository. It is not a machine-learning system that autonomously understands an arbitrary codebase or an engineer's behavior.

This distinction is intentional: the project demonstrates how a structured backend can host richer evaluation models later.

## Testing

The repository includes backend tests, frontend tests, coverage checks, type checking, linting, CI and end-to-end test configuration.

## Local execution

Follow GETTING_STARTED.md for the current setup. The default development stack uses a Next.js client and a FastAPI backend with SQLite in development.

## Scope

EngineerOS should be understood as an **engineering simulation/training platform**, not a production SRE command center.
