async function sendMessage() {
  const inputBox = document.getElementById('user-input');
  const message = inputBox.value.trim();
  if (!message) return;

  addMessage('user', message);
  inputBox.value = '';

  addMessage('bot', '...');

  try {
    const res = await fetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: message })
    });

    const data = await res.json();
    updateLastBotMessage(data.response || 'No answer.');
  } catch (e) {
    updateLastBotMessage('Error contacting backend.');
  }
}

function addMessage(sender, text) {
  const msg = document.createElement('div');
  msg.className = `message ${sender}`;
  msg.textContent = text;
  document.getElementById('chat-window').appendChild(msg);
  scrollToBottom();
}

function updateLastBotMessage(text) {
  const chatWindow = document.getElementById('chat-window');
  const last = chatWindow.querySelector('.message.bot:last-child');
  if (last) last.textContent = text;
  scrollToBottom();
}

function scrollToBottom() {
  const chatWindow = document.getElementById('chat-window');
  chatWindow.scrollTop = chatWindow.scrollHeight;
}
