import React from 'react';
import './StrategyDisplay.css';

export default function StrategyDisplay({ strategy, jiraData }) {
  if (!strategy) return null;

  let parsedSections = strategy.sections || [];

  // 1. Parse and Render the JSON Sections (LLM output fallback)
  if (parsedSections.length === 1 && typeof parsedSections[0].content === 'string') {
    try {
      const cleanString = parsedSections[0].content.replace(/```json/gi, '').replace(/```/g, '').trim();
      const parsed = JSON.parse(cleanString);
      if (parsed && parsed.sections) {
        parsedSections = parsed.sections;
      }
    } catch (e) {
      console.warn("Failed to parse raw JSON section content", e);
    }
  }

  if (parsedSections.length === 0) return null;

  // 2. Dynamic Card Title Overwrite
  const summary = jiraData?.fields?.summary || jiraData?.summary || 'Unknown Issue';

  return (
    <section className="strategy-display">
      <h2 className="strategy-main-title">{summary}: Strategy Document</h2>
      {parsedSections.map((sec, idx) => (
        <div key={idx} className="section-item">
          <h3 className="section-title">{sec.title}</h3>
          <div className="strategy-content">{sec.content}</div>
        </div>
      ))}
    </section>
  );
}
