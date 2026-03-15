# Populated in F2 - Basic Q&A
# Extended in F4 - Agentic Multi-hop Reasoning

QA_PROMPT = """\
You are a helpful assistant. Answer the question using only the provided context.
Each context block is numbered. When you use information from a block, cite it inline as [Source N].
If the answer cannot be found in the context, say "I don't have enough information to answer that."

Context:
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