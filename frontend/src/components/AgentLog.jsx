export default function AgentLog({ steps }) {
  if (!steps?.length) return null;
  return (
    <details className="agent-log">
      <summary>⬡ ADK agent execution log ({steps.length} events)</summary>
      <div className="agent-steps">
        {steps.map((s, i) => <div key={i} className="agent-step">{s}</div>)}
      </div>
    </details>
  );
}
