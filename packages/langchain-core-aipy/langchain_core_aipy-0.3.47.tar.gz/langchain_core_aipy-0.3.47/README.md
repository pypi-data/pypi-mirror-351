This project is a branch of [langchain-core](https://pypi.org/project/langchain-core/) on [QPython](https://www.qpython.org).

## What is it?

LangChain Core contains the base abstractions that power the rest of the LangChain ecosystem.

These abstractions are designed to be as modular and simple as possible. Examples of these abstractions include those for language models, document loaders, embedding models, vectorstores, retrievers, and more.

The benefit of having these abstractions is that any provider can implement the required interface and then easily be used in the rest of the LangChain ecosystem.

For full documentation see the [API reference](https://python.langchain.com/api_reference/core/index.html).

## 1️⃣ Core Interface: Runnables

The concept of a Runnable is central to LangChain Core – it is the interface that most LangChain Core components implement, giving them

- a common invocation interface (invoke, batch, stream, etc.)
- built-in utilities for retries, fallbacks, schemas and runtime configurability
- easy deployment with [LangServe](https://github.com/langchain-ai/langserve)

For more check out the [runnable docs](https://python.langchain.com/docs/expression_language/interface). Examples of components that implement the interface include: LLMs, Chat Models, Prompts, Retrievers, Tools, Output Parsers.

You can use LangChain Core objects in two ways:

1. **imperative**, ie. call them directly, eg. `model.invoke(...)`

2. **declarative**, with LangChain Expression Language (LCEL)

3. or a mix of both! eg. one of the steps in your LCEL sequence can be a custom function

| Feature   | Imperative                      | Declarative    |
| --------- | ------------------------------- | -------------- |
| Syntax    | All of Python                   | LCEL           |
| Tracing   | ✅ – Automatic                  | ✅ – Automatic |
| Parallel  | ✅ – with threads or coroutines | ✅ – Automatic |
| Streaming | ✅ – by yielding                | ✅ – Automatic |
| Async     | ✅ – by writing async functions | ✅ – Automatic |

## ⚡️ What is LangChain Expression Language?

LangChain Expression Language (LCEL) is a _declarative language_ for composing LangChain Core runnables into sequences (or DAGs), covering the most common patterns when building with LLMs.

LangChain Core compiles LCEL sequences to an _optimized execution plan_, with automatic parallelization, streaming, tracing, and async support.

For more check out the [LCEL docs](https://python.langchain.com/docs/expression_language/).

![Diagram outlining the hierarchical organization of the LangChain framework, displaying the interconnected parts across multiple layers.](https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/static/svg/langchain_stack_112024.svg "LangChain Framework Overview")

For more advanced use cases, also check out [LangGraph](https://github.com/langchain-ai/langgraph), which is a graph-based runner for cyclic and recursive LLM workflows.