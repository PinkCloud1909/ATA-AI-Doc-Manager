export default function UploadDocumentPage() {
  return (
    <>
      <section className="page-header">
        <div>
          <h2>Upload Document</h2>
          <p>Add a controlled document package for review and indexing.</p>
        </div>
      </section>

      <section className="panel">
        <form className="form">
          <div className="field">
            <label htmlFor="title">Document title</label>
            <input id="title" name="title" placeholder="Incoming material inspection" />
          </div>
          <div className="field">
            <label htmlFor="owner">Owner</label>
            <select id="owner" name="owner" defaultValue="quality">
              <option value="quality">Quality</option>
              <option value="operations">Operations</option>
              <option value="maintenance">Maintenance</option>
              <option value="compliance">Compliance</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="file">File</label>
            <input id="file" name="file" type="file" />
          </div>
          <button className="button" type="button">
            Queue upload
          </button>
        </form>
      </section>
    </>
  );
}
