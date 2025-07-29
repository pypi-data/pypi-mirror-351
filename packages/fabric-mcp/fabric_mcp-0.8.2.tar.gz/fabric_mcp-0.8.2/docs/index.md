# Fabric MCP Server Documentation Index

This document serves as the central catalog for all key documentation related to the Fabric MCP Server project.

## Core Project Documents

### [Product Requirements Document (PRD)](./PRD.md)

Defines the project goals, objectives, functional and non-functional requirements, user interaction goals, technical assumptions, and MVP scope.

### [Architecture Document](./architecture.md)

Outlines the overall project architecture, including components, patterns, technology stack, and key design decisions. *(This is the main source document before sharding)*

### [Developer Experience (DX) and Operational Experience (OpX) Interaction Specification](./DX-OPX-Interaction.md)

Details the command-line interface (CLI) design, Model Context Protocol (MCP) tool interaction conventions, target user personas, and overall usability goals.

## Architectural Granules (Sharded from Architecture Document)

### [API Reference](./api-reference.md)

Details the external APIs consumed by the server (primarily Fabric REST API) and the internal MCP tools provided by the server, including their endpoints, parameters, and schemas.

### [Component View](./component-view.md)

Describes the major logical components of the system, their responsibilities, interactions, and the architectural design patterns adopted. Includes component diagrams.

### [Core Workflows & Sequence Diagrams](./sequence-diagrams.md)

Illustrates key operational and interaction flows within the system using sequence diagrams, such as tool discovery, pattern execution (streaming and non-streaming), and server startup.

### [Data Models](./data-models.md)

Explains that the server is stateless and data models are primarily defined by the MCP tool schemas and Fabric API schemas, referencing the API Reference document for details.

### [Environment Variables](./environment-vars.md)

Lists and describes all environment variables used to configure the Fabric MCP Server (e.g., `FABRIC_BASE_URL`, `FABRIC_API_KEY`).

### [Infrastructure and Deployment Overview](./infra-deployment.md)

Details how the Fabric MCP Server is intended to be deployed, installed, and operated, including runtime environments and CI/CD.

### [Key Reference Documents (from Architecture)](./key-references.md)

Lists the primary documents that informed the architecture and are critical for understanding its context. *(Note: This refers to the sharded version of this section from the main architecture document).*

### [Operational Guidelines](./operational-guidelines.md)

Consolidates coding standards, the overall testing strategy, error handling strategy, and security best practices for the project.

### [Project Structure (from Architecture)](./project-structure.md)

Defines the project's folder and file structure, including key directories for source code, tests, and documentation.

### [Technology Stack](./tech-stack.md)

Provides the definitive list of technology choices for the project, including languages, frameworks, libraries, and development tooling, along with their versions.

## Contribution & Development Setup

### [Main Contribution Guidelines](./contributing.md)

Outlines the primary guidelines for contributing to the project, including development workflow and code style.

### [Detailed Contribution Guide](./contributing-detailed.md)

Provides an in-depth guide to contributing, covering advanced topics, tool configurations, and best practices.

### [Contributing Cheatsheet](./contributing-cheatsheet.md)

A micro-summary of the development workflow for quick reference.

### [Development Setup Guide](./development_setup.md)

Summarizes the project setup, including Python version, key development tools (`uv`, `ruff`, `pytest`, `hatch`, `pre-commit`, `pnpm` for MCP Inspector), and essential `make` commands.

## Other

### [Original High-Level Design Document](./design.md)

The initial design document that informed the PRD and subsequent planning.

### [Product Manager Checklist (Output)](./PM-checklist.md)

The completed checklist from the PM's review of the PRD.

### [Architect Checklist (Output)](./architect-checklist.md)

The completed checklist from the Architect's validation of the Architecture Document.
