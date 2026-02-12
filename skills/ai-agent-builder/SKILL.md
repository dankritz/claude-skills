---
name: ai-agent-builder
description: Use when building AI agents from Jira tickets. Reads ticket requirements, Confluence agent cards, creates implementation plans, and builds n8n workflows with Jira updates.
allowed-tools: AskUserQuestion,Read,Write,Bash,Skill
---

# AI Agent Builder

This skill guides the complete process of building AI agents from Jira tickets through to implementation and documentation.

## Prerequisites

This skill requires the following MCP servers to be available:
- **Atlassian MCP**: For reading Jira tickets, Confluence agent cards, and updating tickets
- **n8n MCP**: For creating and configuring workflows

If these servers are not available, abort and inform the user.

## Workflow

### Step 1: Gather Requirements

1. **Ask for Jira ticket number**
   - Use AskUserQuestion to get the ticket number from the user

2. **Read Jira ticket**
   - Use Atlassian MCP to read the full ticket
   - Pay special attention to the description and comments
   - Look for references to the Confluence agent card (usually mentioned in comments)

3. **Locate agent card**
   - Search ticket comments for Confluence page links
   - If found, note the agent card URL
   - If not found in ticket, ask the user for the agent card link

4. **Read agent card**
   - Use Atlassian MCP to read the Confluence agent card
   - The agent card typically contains more detailed specifications than the ticket
   - Understand the agent's purpose, inputs, outputs, and behavior

### Step 2: Clarify and Confirm

1. **Analyze requirements**
   - Review both the Jira ticket and agent card thoroughly
   - Identify the core functionality required
   - Note any dependencies or integrations needed

2. **Ask clarifying questions**
   - If there are gaps, ambiguities, or unclear requirements, use AskUserQuestion
   - Ask about:
     - Specific behavior not documented
     - Integration details
     - Error handling preferences
     - Any technical constraints
   - Only ask questions that aren't answered by the ticket or agent card

3. **Confirm understanding**
   - Ensure you have a complete picture before proceeding to planning

### Step 3: Create Implementation Plan

1. **Design the solution**
   - For n8n workflows (most common scenario):
     - List all nodes that will be used (by type and purpose)
     - Describe what each node does
     - Explain the flow and how nodes connect
     - Specify data transformations between nodes
     - Note where Openrouter will be used as the model provider
     - Identify any Code nodes needed and what they'll do
     - Plan error handling and branching logic

2. **Present the plan**
   - Provide a clear, detailed implementation plan
   - Use a structured format (numbered nodes, connections shown clearly)
   - Highlight key decisions and architectural choices
   - Example format:
     ```
     Workflow Plan:

     1. Webhook Trigger
        - Receives incoming requests with [data]

     2. Extract Data (Code node)
        - Extracts X, Y, Z from webhook payload
        - Validates required fields

     3. AI Agent (Openrouter)
        - Model: [specify model]
        - Prompt: [high-level description]
        - Processes [input] to generate [output]

     4. Transform Response (Code node)
        - Formats AI response for downstream use

     5. [Additional nodes...]

     Connections:
     Webhook → Extract Data → AI Agent → Transform Response → ...

     Error Handling:
     [Describe error paths]
     ```

3. **Wait for approval**
   - Explicitly ask: "Does this plan look good? Should I proceed with building it?"
   - **Do NOT proceed to Step 4 without explicit user approval**

### Step 4: Build the Agent

Once the user approves the plan:

1. **Create the workflow**
   - Use n8n MCP tools to create a new workflow
   - Use the workflow name from the agent card or ticket

2. **Configure nodes**
   - Use the `n8n-node-configuration` skill for node setup guidance
   - For each node in your plan:
     - Add the node to the workflow
     - Configure its properties
     - Set up credentials if needed (e.g., Openrouter API key)

3. **Configure Openrouter AI nodes**
   - **Always** use Openrouter as the model provider for AI agent nodes
   - Ensure proper credential configuration
   - Set the appropriate model
   - Configure system and user prompts

4. **Add Code nodes**
   - Use the `n8n-code-javascript` skill for JavaScript Code nodes
   - Use the `n8n-code-python` skill if Python is needed
   - Implement the logic described in your plan

5. **Configure expressions**
   - Use the `n8n-expression-syntax` skill for complex expressions
   - Set up data mappings between nodes

6. **Validate the workflow**
   - Use the `n8n-validation-expert` skill if available
   - Review the workflow structure
   - Ensure all nodes are properly connected

7. **Test if possible**
   - If you can test the workflow, do so
   - Verify basic functionality

### Step 5: Document and Update

1. **Prepare update summary**
   - Document what was built
   - Include the workflow ID or link
   - Note any important configuration details
   - Mention any deviations from the original plan (and why)
   - Include any known limitations or future improvements

2. **Update Jira ticket**
   - Use Atlassian MCP to add a comment to the ticket
   - Include:
     - "✅ Agent implementation completed"
     - Link to the n8n workflow
     - Brief summary of what was built
     - Any relevant notes or next steps
   - Update ticket status if appropriate (e.g., move to "In Review" or "Done")

3. **Confirm completion**
   - Inform the user that the agent has been built and documented
   - Provide the workflow link and any relevant details

## Key Principles

- **Thoroughness**: Understand requirements completely before building
- **Openrouter**: Always use Openrouter as the AI model provider
- **User approval**: Never build without explicit approval of the plan
- **MCP tools**: Use Atlassian MCP for Jira/Confluence, n8n MCP for workflows
- **Skills integration**: Leverage n8n-specific skills for implementation guidance
- **Documentation**: Always update Jira with results

## Error Handling

If at any point you encounter issues:
- Missing MCP servers → Abort and inform the user
- Cannot find agent card → Ask the user for the link
- Unclear requirements → Ask clarifying questions
- Build errors → Document the error and ask for guidance
- Cannot update Jira → Inform the user and provide the update text for manual posting

## Example Session

```
User: Build the customer support agent

Claude: I'll help you build this AI agent. Let me start by gathering the requirements.

What is the Jira ticket number for this agent?

User: PROJ-123

Claude: [Reads ticket using Atlassian MCP]
[Finds agent card link in comments]
[Reads agent card from Confluence]

I've reviewed the ticket and agent card. I have a few clarifying questions:
1. Should the agent escalate to a human if confidence is below a certain threshold?
2. What should happen if the customer's account cannot be found?

User: [Answers questions]

Claude: Thanks! Here's my implementation plan:

[Detailed plan with nodes and connections]

Does this plan look good? Should I proceed with building it?

User: Yes, looks good

Claude: Great! I'll build the workflow now.
[Creates workflow using n8n MCP]
[Configures nodes]
[Tests workflow]

✅ Agent built successfully!

Workflow: [link]
I've updated PROJ-123 with the implementation details.
```

## Notes

- This skill assumes you have appropriate access to Jira, Confluence, and n8n
- The agent card must exist before invoking this skill
- This skill focuses on n8n implementations but can be adapted for other platforms
- Always follow the user's approval before executing the build
