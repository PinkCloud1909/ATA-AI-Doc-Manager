const approvals = [
  ["WI-2210", "Calibration workflow", "QA Manager"],
  ["SOP-1180", "Supplier qualification", "Compliance Lead"],
  ["FRM-0188", "Deviation intake form", "Operations Lead"]
];

export default function ApprovalsPage() {
  return (
    <>
      <section className="page-header">
        <div>
          <h2>Approvals</h2>
          <p>Track documents waiting for review decisions.</p>
        </div>
      </section>

      <section className="panel">
        <ul className="list">
          {approvals.map(([code, title, owner]) => (
            <li key={code}>
              <div>
                <strong>{title}</strong>
                <p className="muted">{code} assigned to {owner}</p>
              </div>
              <span className="status review">Waiting</span>
            </li>
          ))}
        </ul>
      </section>
    </>
  );
}
