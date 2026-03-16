# Populated in F2 - Basic Q&A
# Extended in F4 - Agentic Multi-hop Reasoning
# Extended in F7 - history block added so the LLM can use prior turns

QA_PROMPT = """\
You are a helpful assistant with access to document context and conversation history.

Rules:
- Use the conversation history to answer follow-up questions and remember facts the user told you.
- Use the document context to answer questions about the uploaded documents.
- When you use information from a numbered context block, cite it inline as [Source N].
- If neither history nor context contains the answer, say "I don't have enough information to answer that."

Conversation History:
{history}

Document Context:
{context}

Question: {question}

Answer:"""

ROUTER_PROMPT = """\
You are a query classifier. Decide whether the following question requires a single \
focused lookup ("simple") or needs to be broken into multiple sub-questions to be \
answered thoroughly ("complex").

Rules:
- "simple"  → one specific fact, definition, or direct lookup
- "complex" → comparisons, multi-part questions, cause-and-effect chains, or anything \
that needs information from more than one place

Respond with ONLY one word: simple  OR  complex

Question: {question}"""

DECOMPOSER_PROMPT = """\
You are a research planner. Break the following complex question into 2-4 focused \
sub-questions that together will provide enough information to answer the original.

Rules:
- Each sub-question must be self-contained and answerable independently.
- Output ONLY a numbered list, one sub-question per line, no extra text.
- Do NOT repeat the original question.

Question: {question}

Sub-questions:"""


# Extended in F6 - Summarize and Compare

SUMMARIZE_MAP_PROMPT = """\
Summarize the following document excerpt concisely in 3-5 sentences, \
preserving key facts, figures, and conclusions.

Excerpt:
{chunks}

Summary:"""

SUMMARIZE_REDUCE_PROMPT = """\
You are given several partial summaries of different sections of the same document.
Combine them into one coherent, well-structured final summary.
Do not repeat information. Write in clear, flowing prose.

Partial summaries:
{summaries}

Final summary:"""

COMPARE_PROMPT = """\
You are a research analyst. Compare the documents based on the provided context.
Each context block is numbered and tagged with its source document.
When you use information from a block, cite it inline as [Source N].
Highlight similarities, differences, and any notable contrasts.
If a point only appears in one document, say so explicitly.
If the answer cannot be determined from the context, say so.

Context:
{context}

Question: {question}

Comparison:"""
