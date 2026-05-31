'use client';

import { useState } from 'react';

export default function Home() {
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    if (loading) return;
    setLoading(true);
    setAnswer('');
    setError('');
    try {
      const res = await fetch('https://ai-engineer-journey-0agd.onrender.com/agent-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: message,
          session_id: 'browser-1',
        }),
      });
      const data = await res.json();
      setAnswer(data.answer);
    } catch (err) {
  setError('Could not reach the agent. Please try again.');
    } finally {
      setLoading(false);
    }
  }
  function renderBold(text) {
  return text.split(/(\*\*.*?\*\*)/g).map((part, i) =>
    part.startsWith('**') && part.endsWith('**')
      ? <strong key={i}>{part.slice(2, -2)}</strong>
      : part
  );
}

  return (
    <main style={{ padding: 40, fontFamily: 'sans-serif', maxWidth: 600 }}>
      <h1>Agent Chat</h1>
      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Ask the agent something..."
        onKeyDown={(e) => { if (e.key === 'Enter') sendMessage(); }}
        style={{ width: '100%', padding: 8, fontSize: 16 }}
      />
      <button
        onClick={sendMessage}
        disabled={loading}
        style={{ marginTop: 10, padding: '8px 16px', fontSize: 16 }}
      >
        {loading ? 'Thinking...' : 'Send'}
      </button>
      <p style={{ marginTop: 20, whiteSpace: 'pre-wrap' }}>{renderBold(answer)}</p>
      {error && <p style={{ marginTop: 20, color: 'red' }}>{error}</p>}
    </main>
  );
}