# Test Strategy Builder Buddy (BLAST Framework)

## Objective
The primary goal of this application is to automate the extraction of feature details from a specific Jira ID, process those details using a Large Language Model (LLM), and generate a comprehensive Test Strategy document that adheres strictly to a predefined organizational format.

---

## Functional Requirements

### 1. Jira Data Extraction & Strategy Generation
* **Jira Integration:** Fetch the relevant issue/feature information using the provided Jira ID (e.g., Sample ID: `SCRUM-5`).
* **Document Reference:** The generated output must follow the structure, tone, and sections defined in the sample reference document: `Test Strategy for Ecommerce Website_Sample.docx`.
* **AI Processing:** Utilize an LLM via the GROQ API to analyze the Jira data and synthesize the formalized test strategy.

### 2. File Export Capability
* **Download Functionality:** Provide a dedicated **Download** button once the strategy has been successfully generated.
* **Export Format:** The downloaded file must be exported natively in Microsoft Word (`.docx`) format, preserving the structural layout of the sample document.

### 3. User Interface (UI) Requirements
The application must be a lightweight, single-page application built using **React** and **Vite**.

* **Home Page:**
  * Contains a prominent input field to accept the target Jira ID.
  * Contains a primary action button ("Generate Strategy") to trigger the workflow.
  * Displays the generated Test Strategy in a clean, readable format upon successful completion.
  * Includes the **Download (.docx)** action button post-generation.

* **Settings Configuration (Modal Dialog):**
  * Accessible globally to securely capture and temporarily store connection parameters.
  * **Jira Configuration Fields:**
    * Jira User Email ID
    * Jira API Token
    * Jira Base URL (Cloud instance)
  * **LLM Configuration Fields:**
    * GROQ Connection API Key
    * Target Model: `openai/gpt-oss-120b`

* **Theming & State Persistence:**
  * Implement a global toggle to switch between **Dark Mode** and **Light Mode**.
  * The user's theme preference must persist across browser sessions utilizing `localStorage`.

---

## Design & Aesthetics Guidelines
* **Styling:** No specific branding, corporate logos, or strict color palettes are mandated. 
* **Execution:** Use professional, clean, and modern design principles (e.g., Tailwind CSS or a minimalist component library) to ensure a high-quality user experience.
* **Tone:** The user interface copywriting and overall presentation should remain professional and production-ready.