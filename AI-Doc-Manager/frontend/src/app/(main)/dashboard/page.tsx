const documents = [
  ["SOP-1004", "Incoming material inspection", "Ready"],
  ["WI-2210", "Calibration workflow", "Review"],
  ["FRM-0188", "Deviation intake form", "Ready"]
];

export default function DashboardPage() {
  return (
    <>
      <section className="page-header">
        <div>
          <h2>Dashboard</h2>
          <p>Current operational status for controlled documents.</p>
        </div>
        <div className="toolbar">
          <a className="button" href="/documents/upload">
            Upload document
          </a>
          <a className="button secondary" href="/reports">
            View reports
          </a>
        </div>
      </section>

      <section className="grid grid-3">
        <div className="panel metric">
          <span>Indexed documents</span>
          <strong>128</strong>
        </div>
        <div className="panel metric">
          <span>Pending approvals</span>
          <strong>7</strong>
        </div>
        <div className="panel metric">
          <span>Review cycle time</span>
          <strong>2.4d</strong>
        </div>
      </section>

      <section className="panel" style={{ marginTop: 16 }}>
        <h3>Recent documents</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Code</th>
              <th>Title</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {documents.map(([code, title, status]) => (
              <tr key={code}>
                <td>{code}</td>
                <td>{title}</td>
                <td>
                  <span className={`status ${status === "Review" ? "review" : "ready"}`}>
                    {status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </>
  );
}
