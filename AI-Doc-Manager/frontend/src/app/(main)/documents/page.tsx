const rows = [
  ["SOP-1004", "Incoming material inspection", "Quality", "Approved"],
  ["WI-2210", "Calibration workflow", "Maintenance", "In review"],
  ["POL-0092", "Data retention policy", "Compliance", "Approved"],
  ["FRM-0188", "Deviation intake form", "Operations", "Draft"]
];

export default function DocumentsPage() {
  return (
    <>
      <section className="page-header">
        <div>
          <h2>Documents</h2>
          <p>Browse controlled documents and review their lifecycle state.</p>
        </div>
        <a className="button" href="/documents/upload">
          Upload
        </a>
      </section>

      <section className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Code</th>
              <th>Title</th>
              <th>Owner</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([code, title, owner, status]) => (
              <tr key={code}>
                <td>
                  <a href={`/documents/${code}`}>{code}</a>
                </td>
                <td>{title}</td>
                <td>{owner}</td>
                <td>
                  <span className={`status ${status === "In review" ? "review" : "ready"}`}>
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
