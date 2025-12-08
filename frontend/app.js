// Application state
let currentLanguage = 'hu';
const API_BASE_URL = 'http://localhost:8000';

// Language texts
const texts = {
    hu: {
        welcome: "Üdvözöllek! Kérdezz bármit az Óbudai Egyetem telefonkönyvéből. Például: \"Ki a mérnöki intézet dékánja?\" vagy \"Melyik a Györök György telefonszáma?\"",
        placeholder: "Kérdezz valamit...",
        sending: "Küldés..."
    },
    en: {
        welcome: "Welcome! Ask anything about Óbuda University's phonebook. For example: \"Who is the dean of the engineering institute?\" or \"What is Györök György's phone number?\"",
        placeholder: "Ask something...",
        sending: "Sending..."
    }
};

// DOM elements
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const languageToggle = document.getElementById('languageToggle');
const currentLang = document.getElementById('currentLang');
const loadingIndicator = document.getElementById('loadingIndicator');
const welcomeMessage = document.getElementById('welcomeMessage');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateLanguageUI();
    setupEventListeners();
});

function setupEventListeners() {
    // Send button click
    sendButton.addEventListener('click', handleSend);
    
    // Enter key press
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });
    
    // Language toggle
    languageToggle.addEventListener('click', toggleLanguage);
}

function toggleLanguage() {
    currentLanguage = currentLanguage === 'hu' ? 'en' : 'hu';
    updateLanguageUI();
    
    // Update welcome message
    welcomeMessage.textContent = texts[currentLanguage].welcome;
    chatInput.placeholder = texts[currentLanguage].placeholder;
}

function updateLanguageUI() {
    currentLang.textContent = currentLanguage.toUpperCase();
}

async function handleSend() {
    const query = chatInput.value.trim();
    
    if (!query) {
        return;
    }
    
    // Disable input
    chatInput.disabled = true;
    sendButton.disabled = true;
    
    // Add user message
    addMessage(query, 'user');
    
    // Clear input
    chatInput.value = '';
    
    // Show loading
    showLoading();
    
    try {
        // Call API
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                language: currentLanguage,
                top_k: 5
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Hide loading
        hideLoading();
        
        // Add bot message with formatted content
        addMessage(formatAnswer(data.answer), 'bot');
        
    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        
        const errorMessage = currentLanguage === 'hu' 
            ? 'Hiba történt a kérés feldolgozása során. Kérlek, próbáld újra.'
            : 'An error occurred while processing your request. Please try again.';
        
        addMessage(errorMessage, 'bot');
    } finally {
        // Re-enable input
        chatInput.disabled = false;
        sendButton.disabled = false;
        chatInput.focus();
    }
}

function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const p = document.createElement('p');
    p.innerHTML = text; // Use innerHTML to support links
    
    contentDiv.appendChild(p);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatAnswer(answer) {
    // Convert phone numbers to clickable links
    const phoneRegex = /(\+?\d{1,3}[\s\-\(\)]?\d{1,4}[\s\-\(\)]?\d{1,4}[\s\-\(\)]?\d{1,4}[\s\-\(\)]?\d{1,4})/g;
    answer = answer.replace(phoneRegex, (match) => {
        const cleanPhone = match.replace(/[\s\-\(\)]/g, '');
        return `<a href="tel:${cleanPhone}">${match}</a>`;
    });
    
    // Convert email addresses to clickable links
    const emailRegex = /([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/g;
    answer = answer.replace(emailRegex, (match) => {
        return `<a href="mailto:${match}">${match}</a>`;
    });
    
    // Convert line breaks to <br>
    answer = answer.replace(/\n/g, '<br>');
    
    return answer;
}

function showLoading() {
    loadingIndicator.style.display = 'block';
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideLoading() {
    loadingIndicator.style.display = 'none';
}

