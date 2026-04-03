const BACKEND_URL = 'http://127.0.0.1:5000';

// When deployed, change this to your actual backend URL e.g.:
// const BACKEND_URL = 'https://agenthub-backend.onrender.com';

let currentAgent = '';
let chatHistory = [];

// ── OPEN CHAT POPUP ─────────────────────────────────
// This runs when someone clicks a "Use" button
function openAgent(agentName) {

  // get user
  let user = localStorage.getItem("user");

  // SAVE AGENT
  let agents = JSON.parse(localStorage.getItem(user + "_agents")) || [];
  agents.push(agentName);
  localStorage.setItem(user + "_agents", JSON.stringify(agents));

  // EARNINGS
  let earnings = localStorage.getItem(user + "_earnings") || 0;
  earnings = parseInt(earnings) + 10;
  localStorage.setItem(user + "_earnings", earnings);

  currentAgent = agentName;
  chatHistory = [];

  document.getElementById('agentTitle').textContent = agentName;
  document.getElementById('chatMessages').innerHTML = '';

  addMessage('bot', `Hello! I'm the ${agentName} agent.`);

  document.getElementById('chatOverlay').classList.add('active');
}

// ── CLOSE CHAT POPUP ────────────────────────────────
function closeChat() {
  document.getElementById('chatOverlay').classList.remove('active');
}

// Close popup if user clicks the dark overlay (outside the box)
document.getElementById('chatOverlay').addEventListener('click', function(e) {
  if (e.target === this) closeChat();
});

// ── SEND MESSAGE ────────────────────────────────────
async function sendMessage() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();

  // Don't send empty messages
  if (!text) return;

  // Show user's message in the chat
  addMessage('user', text);

  // Add to history so AI remembers the conversation
  chatHistory.push({ role: 'user', content: text });
  let user = localStorage.getItem("user");

  let history = JSON.parse(localStorage.getItem(user + "_history")) || [];

  history.push({
    agent: currentAgent,
    message: text
  });

localStorage.setItem(user + "_history", JSON.stringify(history));
  // Clear the input box
  input.value = '';

  // Show "thinking..." indicator
  const thinkingId = addMessage('thinking', 'Agent is thinking...');

  try {
    // Send to your Python backend
    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent: currentAgent,
        message: text,
        history: chatHistory
      })
    });

    const data = await response.json();
    const reply = data.reply;

    // Remove "thinking..." and show real reply
    removeMessage(thinkingId);
    addMessage('bot', reply);

    // Add bot's reply to history too
    chatHistory.push({ role: 'assistant', content: reply });

  } catch (error) {
    removeMessage(thinkingId);
    addMessage('bot', '⚠️ Could not connect to backend. Make sure your Python server is running!');
  }
}

// ── HELPER: ADD A MESSAGE BUBBLE ───────────────────
function addMessage(type, text) {
  const messagesDiv = document.getElementById('chatMessages');
  const id = 'msg_' + Date.now();

  const div = document.createElement('div');
  div.className = `msg ${type}`;
  div.id = id;
  div.innerHTML = text;

  messagesDiv.appendChild(div);

  // Auto-scroll to bottom
  messagesDiv.scrollTop = messagesDiv.scrollHeight;

  return id;
}

// ── HELPER: REMOVE A MESSAGE ───────────────────────
function removeMessage(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function goDashboard() {
  window.location.href = "dashboard.html";
}
function logout() {
  localStorage.clear();
  window.location.href = "login.html";
}
// ── SEARCH FILTER ──────────────────────────────────
// Makes the search bar in the header filter cards live
document.querySelector('header input').addEventListener('input', function() {
  const query = this.value.toLowerCase();
  document.querySelectorAll('.card').forEach(card => {
    const text = card.textContent.toLowerCase();
    card.style.display = text.includes(query) ? '' : 'none';
  });
});
