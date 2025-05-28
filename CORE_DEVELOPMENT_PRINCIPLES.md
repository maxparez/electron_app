# Core Development Principles & Mandates

**Purpose:** These are universal principles and mandatory rules applicable to ALL software development tasks, regardless of the specific phase or technology. These directives MUST be followed in conjunction with any domain-specific directives (Backend, Database, etc.).

## I. Foundational Philosophy

1. **KISS (Keep It Simple, Stupid):** Prioritize simplicity and clarity in all designs, code, and processes. Avoid unnecessary complexity.
2. **DRY (Don't Repeat Yourself):** Avoid code duplication. Abstract common logic into reusable functions, classes, or modules. Apply this principle also to configuration and documentation where applicable.
3. **YAGNI (You Ain't Gonna Need It):** Implement only the functionality required *now*. Do not add features or complexity based on speculation about future needs. Avoid premature optimization.

## II. Mandatory Procedures & Policies

4. **Development Checklist:** **MANDATORY.**
   * For every non-trivial task, create a detailed checklist *before* starting implementation.
   * The checklist must outline: Requirements/Features, Key Design Decisions, Applicable Principles from these directives, Implementation Steps, Testing Steps.
   * Regularly update the checklist and report progress against it. Adherence is critical.

5. **English-Only Policy:** **MANDATORY.**
   * ALL code artifacts MUST be written in English. This includes, but is not limited to:
     * File names
     * Directory names
     * Class names
     * Function/Method names
     * Variable names
     * Database table/column names
     * API endpoint names and parameters
     * Comments
     * Documentation strings (Docstrings)
     * Configuration keys
     * Commit messages (if applicable)
   * **EXCEPTION:** GUI text visible to end users will be in Czech for colleagues.

## III. Quality & Collaboration

6. **Code Review Principles (Apply during generation/self-correction):**
   * Strive for code that is readable, understandable, and maintainable.
   * Check for potential bugs, edge cases, and security vulnerabilities.
   * Ensure adherence to all applicable directives (Core, Backend, DB, etc.).
   * Verify that code aligns with the agreed-upon design and checklist.

7. **Logging & Monitoring Basics:**
   * Implement sufficient logging to understand application flow, diagnose errors, and track important events.
   * Consider what metrics might be needed for monitoring application health and performance.

## IV. Communication & Reporting

8. **Clarity and Proactivity:**
   * If requirements are unclear or ambiguous, ask for clarification *before* proceeding.
   * Report any significant roadblocks or deviations from the plan or directives promptly.
   * Provide clear explanations for design choices made.
   * When delivering code, include instructions for running and testing it.

## V. Guiding Influences

9. **Unix Philosophy:** Keep in mind the principles of designing small, focused tools that do one thing well and work together effectively.
10. **AI as an Assistant:** Leverage AI capabilities for analysis, code generation, documentation, and testing, but always ensure the final output adheres to these principles and quality standards. Human oversight (or simulation thereof based on these rules) is key.

## Project-Specific Application

### For Electron App Project:

1. **Code Language:** All code in English, GUI texts in Czech
2. **Modular Design:** Each tool (inv_vzd, zor_spec, plakat) as separate module
3. **Reusable Components:** Shared utilities for Excel operations, file handling
4. **Clear Separation:** Frontend (Electron) and Backend (Python) with defined API
5. **Incremental Development:** Start with core functionality, add features as needed