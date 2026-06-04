export default function GeneratePage() {
  return (
    <>
      <section className="page-header">
        <div>
          <h2>Generate</h2>
          <p>Create a draft document from approved templates and source context.</p>
        </div>
      </section>

      <section className="panel">
        <form className="form">
          <div className="field">
            <label htmlFor="template">Template</label>
            <select id="template" defaultValue="sop">
              <option value="sop">Standard operating procedure</option>
              <option value="work-instruction">Work instruction</option>
              <option value="form">Form</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="prompt">Draft brief</label>
            <textarea id="prompt" placeholder="Describe the document to draft..." />
          </div>
          <button className="button" type="button">
            Generate draft
          </button>
        </form>
      </section>
    </>
  );
}
