export default function ChatPage() {
  return (
    <>
      <section className="page-header">
        <div>
          <h2>Document Chat</h2>
          <p>Ask questions against indexed procedures and controlled records.</p>
        </div>
      </section>

      <section className="panel chat-box">
        <div className="message assistant">
          Which document would you like to search?
        </div>
        <div className="message user">
          Find the acceptance criteria for incoming material inspection.
        </div>
        <div className="message assistant">
          I found matching criteria in SOP-1004. Connect the backend API to return
          live citations from indexed sources.
        </div>
        <div className="field">
          <label htmlFor="question">Question</label>
          <input id="question" placeholder="Ask about a document..." />
        </div>
      </section>
    </>
  );
}
