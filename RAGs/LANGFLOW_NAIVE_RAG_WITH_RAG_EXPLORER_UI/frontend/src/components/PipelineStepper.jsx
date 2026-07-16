const STAGES = [
  { num: 1, label: "CSV" },
  { num: 2, label: "Chunk" },
  { num: 3, label: "Embed (Mistral)" },
  { num: 4, label: "Store (Chroma)" },
  { num: 5, label: "Retrieve" },
  { num: 6, label: "Answer (Groq)" },
];

const ORANGE = "#f97316";

export default function PipelineStepper() {
  return (
    <div className="stepper">
      {STAGES.map((s, i) => (
        <span key={s.num} className="stepper-item">
          <span className="stepper-badge" style={{ background: ORANGE }}>
            {s.num}
          </span>
          <span className="stepper-label">{s.label}</span>
          {i < STAGES.length - 1 && (
            <span className="stepper-arrow">→</span>
          )}
        </span>
      ))}
    </div>
  );
}
