export default function ReportsPage() {
  return (
    <>
      <section className="page-header">
        <div>
          <h2>Reports</h2>
          <p>Document throughput and compliance activity summaries.</p>
        </div>
      </section>

      <section className="grid grid-3">
        <div className="panel metric">
          <span>Approved this month</span>
          <strong>34</strong>
        </div>
        <div className="panel metric">
          <span>Returned for edits</span>
          <strong>6</strong>
        </div>
        <div className="panel metric">
          <span>Expired documents</span>
          <strong>2</strong>
        </div>
      </section>
    </>
  );
}
