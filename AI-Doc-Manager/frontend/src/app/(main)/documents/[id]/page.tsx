export default function DocumentDetailPage() {
  return (
    <>
      <section className="page-header">
        <div>
          <h2>Document Details</h2>
          <p>Version history, metadata, and review state for the selected document.</p>
        </div>
        <div className="toolbar">
          <a className="button secondary" href="/documents">
            Back to documents
          </a>
          <a className="button" href="/approvals">
            Request approval
          </a>
        </div>
      </section>

      <section className="grid grid-2">
        <div className="panel">
          <h3>Metadata</h3>
          <ul className="list">
            <li>
              <span>Owner</span>
              <strong>Quality</strong>
            </li>
            <li>
              <span>Revision</span>
              <strong>3</strong>
            </li>
            <li>
              <span>Status</span>
              <span className="status review">In review</span>
            </li>
          </ul>
        </div>
        <div className="panel">
          <h3>Review notes</h3>
          <p className="muted">
            AI extraction is queued. Reviewers can validate sections, references, and
            approval routing once the document is indexed.
          </p>
        </div>
      </section>
    </>
  );
}
