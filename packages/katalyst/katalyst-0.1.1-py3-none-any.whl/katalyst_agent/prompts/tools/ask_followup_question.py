from textwrap import dedent

ASK_FOLLOWUP_QUESTION_PROMPT = dedent("""
# ask_followup_question Tool

Use this tool to ask the user a question to gather additional information needed to complete the task. This tool should be used when you encounter ambiguities, need clarification, or require more details to proceed effectively. It allows for interactive problem-solving by enabling direct communication with the user. Use this tool judiciously to maintain a balance between gathering necessary information and avoiding excessive back-and-forth.

Provide 2-4 suggested answers, each in its own <suggest> tag, that are actionable and complete (no placeholders). The user can choose from the suggested answers or provide their own answer.

Parameters:
- question: (required) The question to ask the user. This should be a clear, specific question that addresses the information you need.
- follow_up: (required) A list of 2-4 suggested answers that logically follow from the question, ordered by priority or logical sequence. Each suggestion must:
  1. Be provided in its own <suggest> tag
  2. Be specific, actionable, and directly related to the completed task
  3. Be a complete answer to the question - the user should not need to provide additional information or fill in any missing details. DO NOT include placeholders with brackets or parentheses.

## Usage
<ask_followup_question>
<question>Your question here</question>
<follow_up>
<suggest>Your suggested answer here</suggest>
<suggest>Another suggestion</suggest>
</follow_up>
</ask_followup_question>

## Example
<ask_followup_question>
<question>What is the path to the frontend-config.json file?</question>
<follow_up>
<suggest>./src/frontend-config.json</suggest>
<suggest>./config/frontend-config.json</suggest>
<suggest>./frontend-config.json</suggest>
</follow_up>
</ask_followup_question>
""") 