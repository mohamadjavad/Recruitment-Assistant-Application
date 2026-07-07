---
description: Run the AAMAD Phase 1 discovery process to generate Market Research and Product Requirements Document for a multi-agent system concept.
agent: product-mgr
---

> NOTE: This prompt is used to generate the Market Research and Product Requirements Document in the Phase 1 of the AAMAD framework.
> Use Perplexity Pro with Deep Research for optimal results.

You will help the user build 2 key documents during the initial Design stage of a Multiagent System Application:

1. A detailed Deep Research on the market for the product the user intends to build
2. A detailed Product Requirement Document to define the product to build

The process is performed in 3 steps:
1. When the user enters: {{input}} - use the generate-mr template to create a complete Market Research
2. Use the Market Research from step 1 to create the Product Requirement Document using the generate-prd template
3. Share the Market Research file (mr.md) and Product Requirements Document (prd.md) in Markdown format

Execute the three steps in series and output the final documents as markdown files in project-context/1.define/.
