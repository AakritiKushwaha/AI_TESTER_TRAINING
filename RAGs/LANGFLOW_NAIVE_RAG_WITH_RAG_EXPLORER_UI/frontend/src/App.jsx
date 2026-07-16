import PipelineStepper from "./components/PipelineStepper";
import StatusPanel from "./components/StatusPanel";
import AskPanel from "./components/AskPanel";

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">RAG Explorer</h1>
        <p className="app-subtitle">
          E-Commerce Test Case Q&A · Langflow + Mistral + Chroma + Groq
        </p>
      </header>

      <PipelineStepper />

      <main className="main-layout">
        <aside className="left-col">
          <StatusPanel />
        </aside>
        <section className="right-col">
          <AskPanel />
        </section>
      </main>
    </div>
  );
}
