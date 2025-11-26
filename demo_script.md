# Demo Video Script: Autonomous QA Agent
**Duration:** ~5-8 Minutes
**Tone:** Professional, clear, enthusiastic, and technically accurate.

---

## 0:00 - Introduction & The "Why"
**(Visual: Title Slide "Autonomous QA Agent: Building a Testing Brain")**

**Speaker:**
"Hello everyone! Welcome to the demo of my **Autonomous QA Agent**.

In modern software development, keeping test cases in sync with rapidly changing requirements is a massive challenge. We often have product specs in one place, UI designs in another, and the actual code somewhere else. Bridging these gaps manually is slow and error-prone.

**The Goal:**
My objective for this assignment was to build an intelligent agent that acts as a 'Testing Brain.' It doesn't just run tests; it *reads* your documentation, *understands* your application's structure, and *autonomously* generates comprehensive test cases and executable Selenium scripts.

Key requirements I’ve implemented include:
1.  **Strict Grounding:** No hallucinations. Every test case is backed by your actual support documents.
2.  **End-to-End Automation:** From reading a PDF to writing Python code.
3.  **Modern Stack:** Built with **FastAPI**, **Streamlit**, and **Vector Search**."

---

## 1:00 - Technical Architecture
**(Visual: High-level architecture diagram or showing the VS Code project structure)**

**Speaker:**
"Before we dive into the demo, let's look under the hood. The system is built on a modular architecture:

*   **The Backend:** I used **FastAPI** for high-performance, asynchronous processing. It handles all the heavy lifting—file parsing, vector storage, and agent logic.
*   **The Frontend:** The user interface is built with **Streamlit**, providing a clean, interactive way to control the agents.
*   **The Brain (RAG Pipeline):** This is the core. I use **ChromaDB** as a vector store to index documents. When the agent needs to answer a question or write a script, it uses **Retrieval Augmented Generation (RAG)** to fetch the exact paragraphs needed from the specs.
*   **The LLM:** I'm using **Groq** (powered by Llama 3) for incredibly fast inference, ensuring the UI feels responsive."

---

## 2:00 - Phase 1: Knowledge Base Ingestion
**(Visual: Streamlit UI "Knowledge Base" tab. Cursor hovering over upload buttons)**

**Speaker:**
"Let's see it in action. Phase 1 is **Ingestion**.

Imagine we are testing a new **E-Shop Checkout** page. We have three key assets:
1.  `product_specs.md`: Defines rules like 'SAVE15 gives 15% off'.
2.  `ui_ux_guide.txt`: Tells us error messages must be red and buttons green.
3.  `checkout.html`: The actual source code of the page we're testing.

**(Visual: Uploading files in the UI)**

I'll upload these documents into the system. When I click **'Build Knowledge Base'**, the backend is doing several things:
*   It parses the files (Markdown, Text, and HTML).
*   It chunks the text into semantic pieces.
*   It generates vector embeddings and stores them in ChromaDB.

**(Visual: Success message "Knowledge Base Built - 4 Documents Processed")**

And just like that, the agent has 'read' the manual. It now knows everything about our shipping rules and discount codes."

---

## 3:30 - Phase 2: Test Case Generation
**(Visual: Switching to "Test Case Agent" tab)**

**Speaker:**
"Now for Phase 2: **Test Case Generation**.

Instead of writing spreadsheets manually, I can simply ask the agent.
I'll enter the prompt: *'Generate positive and negative test cases for the discount code feature.'*

**(Visual: Clicking 'Generate', loading spinner, then results appearing)**

Look at the result. The agent has generated structured test cases. Let's look at **TC-001**:
*   **Scenario:** Apply valid code 'SAVE15'.
*   **Expected Result:** 15% discount applied.
*   **Grounded In:** `product_specs.md`.

**Crucial Point:** Notice the **'Grounded In'** field. The agent didn't guess 'SAVE15'; it found it in the document we uploaded. It also generated a *negative* test case for invalid codes, referencing the error message rules from the UI guide. This ensures 100% traceability."

---

## 5:30 - Phase 3: Selenium Script Generation
**(Visual: Switching to "Script Agent" tab, selecting TC-001 from a dropdown)**

**Speaker:**
"Finally, Phase 3: **Selenium Script Generation**. This is where we turn plans into code.

I'll select **TC-001** from the list. The agent now has a complex task:
1.  It takes the test steps (e.g., 'Enter code').
2.  It looks at the `checkout.html` file we uploaded to find the *real* ID, like `#discount-code-input`.
3.  It writes a Python script using Selenium.

**(Visual: Clicking 'Generate Script', code block appearing)**

Here is the generated code.
*   It imports `webdriver`.
*   It initializes the driver.
*   It finds the element `By.ID("discount-code")`. **This matches our HTML exactly.**
*   It even includes assertions to verify the 'Success' message appears in green, adhering to our `ui_ux_guide.txt`.

I can now download this script and run it immediately in my CI/CD pipeline."

---

## 7:00 - Conclusion & Wrap Up
**(Visual: Camera back to speaker or summary slide)**

**Speaker:**
"To summarize, this Autonomous QA Agent successfully bridges the gap between requirements and automation.

*   **Functionality:** It handles the full lifecycle—Ingestion, Planning, and Coding.
*   **Quality:** The scripts are runnable and use correct selectors.
*   **Reliability:** By using RAG, we eliminated hallucinations—if it's not in the docs, the agent won't test it.

This tool significantly reduces the time to start testing a new feature, allowing QA engineers to focus on strategy rather than boilerplate code.

Thank you for watching!"
