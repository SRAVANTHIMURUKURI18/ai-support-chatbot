const themeToggle = document.getElementById('themeToggle');
const chatWindow = document.getElementById('chatWindow');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const themeIcon = document.getElementById('themeIcon');

const aiAvatarSVG = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect></svg>`;

const currentTheme = localStorage.getItem('theme') || 'dark';
document.documentElement.setAttribute('data-theme', currentTheme);
updateThemeIcon(currentTheme);

themeToggle.addEventListener('click', () => {
    let theme = document.documentElement.getAttribute('data-theme');
    let newTheme = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
});

function updateThemeIcon(theme) {
    if (theme === 'dark') {
        themeIcon.innerHTML = `<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>`;
    } else {
        themeIcon.innerHTML = `<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>`;
    }
}

userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    sendBtn.disabled = this.value.trim() === '';
});
sendBtn.disabled = true;

function sendSuggested(text) {
    userInput.value = text;
    userInput.style.height = 'auto';
    sendBtn.disabled = false;
    sendMessage();
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage('user', text);
    userInput.value = '';
    userInput.style.height = 'auto';
    sendBtn.disabled = true;

    const loadingId = appendLoading();

    try {
        const response = await fetch('http://127.0.0.1:8000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, session_id: 'vit_student_session' })
        });

        if (!response.ok) throw new Error('API Request Failed');

        const data = await response.json();
        document.getElementById(loadingId).remove();
        appendMessage('ai', data.reply);

    } catch (error) {
        document.getElementById(loadingId).remove();
        appendMessage('ai', 'Error: Unable to connect to the server. (Make sure your FastAPI backend is running).');
    }
}

function appendMessage(sender, text) {
    const isUser = sender === 'user';
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    
    let avatarHTML = isUser ? '' : `<div class="avatar">${aiAvatarSVG}</div>`;
    
    messageDiv.innerHTML = `
        ${avatarHTML}
        <div class="bubble">${escapeHTML(text)}</div>
    `;
    
    chatWindow.appendChild(messageDiv);
    scrollToBottom();
}

function appendLoading() {
    const id = 'loading-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ai-message`;
    messageDiv.id = id;
    
    messageDiv.innerHTML = `
        <div class="avatar">${aiAvatarSVG}</div>
        <div class="bubble">
            <div class="typing-indicator">
                <div class="dot"></div><div class="dot"></div><div class="dot"></div>
            </div>
        </div>
    `;
    
    chatWindow.appendChild(messageDiv);
    scrollToBottom();
    return id;
}

function scrollToBottom() {
    chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: 'smooth' });
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, tag => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[tag]));
}

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!sendBtn.disabled) sendMessage();
    }
});
sendBtn.addEventListener('click', sendMessage);