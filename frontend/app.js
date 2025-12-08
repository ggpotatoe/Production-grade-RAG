// Application state
        let currentLanguage = 'hu';
        const API_BASE_URL = 'http://localhost:8000';

        // Language texts - MINDEN SZÖVEG
        const texts = {
            hu: {
                // AI Chat
                welcome: "Üdvözöllek! Kérdezz bármit az Óbudai Egyetem telefonkönyvéből. Például: \"Ki a mérnöki intézet dékánja?\" vagy \"Melyik a Györök György telefonszáma?\"",
                placeholder: "Kérdezz valamit...",
                sending: "Küldés...",
                
                // Toggle labels
                classicSearch: "Klasszikus keresés",
                aiAssistant: "AI Asszisztens",
                
                // Top Bar
                topGreen: "ZÖLD ÓE",
                topTender: "PÁLYÁZAT",
                topJob: "ÁLLÁS",
                topNeptun: "NEPTUN",
                topElearning: "E-LEARNING",
                topIntranet: "INTRANET",
                topPhonebook: "TELEFONKÖNYV",
                
                // Main Navigation
                navUniversity: "EGYETEMÜNK",
                navPrograms: "KÉPZÉSEINK",
                navStudents: "HALLGATÓKNAK",
                navApplicants: "FELVÉTELIZŐKNEK",
                navScience: "TUDOMÁNY",
                navResearch: "KUTATÁS",
                navInnovation: "INNOVÁCIÓ",
                navInternational: "NEMZETKÖZI PROFIL",
                
                // Page Title
                pageTitle: "Telefonkönyv",
                
                // Form Labels
                formName: "Név:",
                formPosition: "Beosztás:",
                formUnit: "Szervezeti egység:",
                formPhone: "Telefonszám:",
                formSubmit: "LEKÉRDEZÉS",
                
                // Calendar
                calendarTitle: "ESEMÉNYNAPTÁR",
                calendarMonth: "december 2025",
                dayMon: "H",
                dayTue: "K",
                dayWed: "SZE",
                dayThu: "CS",
                dayFri: "P",
                daySat: "SZO",
                daySun: "V",
                
                // Month names for dynamic calendar
                monthNames: ["január", "február", "március", "április", "május", "június", 
                            "július", "augusztus", "szeptember", "október", "november", "december"],
                
                // Footer
                footerHeadquarters: "SZÉKHELY",
                footerPhone: "Telefon:",
                footerRectorate: "REKTORI HIVATAL",
                footerPress: "SAJTÓSZOBA",
                footerPressContact: "Sajtókapcsolat",
                footerNewsletter: "Hírmondó",
                footerVideos: "Videótár",
                footerInfo: "INFORMÁCIÓK",
                footerContact: "Kapcsolat",
                footerPublicData: "Közérdekű adatok",
                footerPrivacy: "Adatvédelem",
                footerCookie: "Cookie nyilatkozat",
                footerImprint: "Impresszum",
                footerJob: "Állás",
                footerArchive: "Archívum",
                
                // Error messages
                errorMessage: "Hiba történt a kérés feldolgozása során. Kérlek, próbáld újra."
            },
            en: {
                // AI Chat
                welcome: "Welcome! Ask anything about Óbuda University's phonebook. For example: \"Who is the dean of the engineering institute?\" or \"What is Györök György's phone number?\"",
                placeholder: "Ask something...",
                sending: "Sending...",
                
                // Toggle labels
                classicSearch: "Classic Search",
                aiAssistant: "AI Assistant",
                
                // Top Bar
                topGreen: "GREEN ÓE",
                topTender: "TENDER",
                topJob: "JOB",
                topNeptun: "NEPTUN",
                topElearning: "E-LEARNING",
                topIntranet: "INTRANET",
                topPhonebook: "PHONEBOOK",
                
                // Main Navigation
                navUniversity: "OUR UNIVERSITY",
                navPrograms: "PROGRAMS",
                navStudents: "FOR STUDENTS",
                navApplicants: "FOR APPLICANTS",
                navScience: "SCIENCE",
                navResearch: "RESEARCH",
                navInnovation: "INNOVATION",
                navInternational: "INTERNATIONAL PROFILE",
                
                // Page Title
                pageTitle: "Phonebook",
                
                // Form Labels
                formName: "Name:",
                formPosition: "Position:",
                formUnit: "Organizational Unit:",
                formPhone: "Phone Number:",
                formSubmit: "SEARCH",
                
                // Calendar
                calendarTitle: "EVENT CALENDAR",
                calendarMonth: "December 2025",
                dayMon: "Mon",
                dayTue: "Tue",
                dayWed: "Wed",
                dayThu: "Thu",
                dayFri: "Fri",
                daySat: "Sat",
                daySun: "Sun",
                
                // Month names for dynamic calendar
                monthNames: ["January", "February", "March", "April", "May", "June", 
                            "July", "August", "September", "October", "November", "December"],
                
                // Footer
                footerHeadquarters: "HEADQUARTERS",
                footerPhone: "Phone:",
                footerRectorate: "RECTORATE OFFICE",
                footerPress: "PRESS ROOM",
                footerPressContact: "Press Contact",
                footerNewsletter: "Newsletter",
                footerVideos: "Video Archive",
                footerInfo: "INFORMATION",
                footerContact: "Contact",
                footerPublicData: "Public Data",
                footerPrivacy: "Privacy Policy",
                footerCookie: "Cookie Statement",
                footerImprint: "Imprint",
                footerJob: "Job",
                footerArchive: "Archive",
                
                // Error messages
                errorMessage: "An error occurred while processing your request. Please try again."
            }
        };

        // DOM elements
        const chatMessages = document.getElementById('chatMessages');
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');
        const welcomeMessage = document.getElementById('welcomeMessage');

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            setupEventListeners();

            const modeToggle = document.getElementById('modeToggle');
            const toggleLabel = document.getElementById('toggleLabel');
            const classicSearch = document.getElementById('classicSearch');
            const aiChat = document.getElementById('aiChat');

            modeToggle.checked = false;
            toggleLabel.textContent = 'Klasszikus keresés';
            classicSearch.style.display = 'grid';
            aiChat.classList.remove('active');

            // Initialize language UI
            updateLanguageUI();
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

            // Top bar language links
            const langHU = document.getElementById('langHU');
            const langEN = document.getElementById('langEN');

            if (langHU) {
                langHU.addEventListener('click', (e) => {
                    e.preventDefault();
                    setLanguage('hu');
                });
            }

            if (langEN) {
                langEN.addEventListener('click', (e) => {
                    e.preventDefault();
                    setLanguage('en');
                });
            }
        }

        function setLanguage(lang) {
            if (lang !== 'hu' && lang !== 'en') {
                return;
            }
            
            currentLanguage = lang;
            
            // Update welcome message
            updateLanguageUI();
        }

        function updateLanguageUI() {
            // Update AI Chat elements
            if (welcomeMessage) {
                welcomeMessage.textContent = texts[currentLanguage].welcome;
            }
            if (chatInput) {
                chatInput.placeholder = texts[currentLanguage].placeholder;
            }
            
            // Update toggle label
            const toggleLabel = document.getElementById('toggleLabel');
            const modeToggle = document.getElementById('modeToggle');
            if (toggleLabel && modeToggle) {
                toggleLabel.textContent = modeToggle.checked 
                    ? texts[currentLanguage].aiAssistant 
                    : texts[currentLanguage].classicSearch;
            }
            
            // Update send button aria-label
            if (sendButton) {
                sendButton.setAttribute('aria-label', texts[currentLanguage].sending);
            }
            
            // Update all data-translate elements
            updateTranslateElements();
            
            // Update language toggle active state
            const langHU = document.getElementById('langHU');
            const langEN = document.getElementById('langEN');
            if (langHU && langEN) {
                langHU.style.fontWeight = currentLanguage === 'hu' ? 'bold' : 'normal';
                langEN.style.fontWeight = currentLanguage === 'en' ? 'bold' : 'normal';
            }
            
            // Update HTML lang attribute
            document.documentElement.lang = currentLanguage === 'hu' ? 'hu-HU' : 'en-US';
        }

        function updateTranslateElements() {
            // Map data-translate keys to text values
            const translateMap = {
                // Top Bar
                'top-green': 'topGreen',
                'top-tender': 'topTender',
                'top-job': 'topJob',
                'top-neptun': 'topNeptun',
                'top-elearning': 'topElearning',
                'top-intranet': 'topIntranet',
                'top-phonebook': 'topPhonebook',
                
                // Main Navigation
                'nav-university': 'navUniversity',
                'nav-programs': 'navPrograms',
                'nav-students': 'navStudents',
                'nav-applicants': 'navApplicants',
                'nav-science': 'navScience',
                'nav-research': 'navResearch',
                'nav-innovation': 'navInnovation',
                'nav-international': 'navInternational',
                
                // Page Title
                'page-title': 'pageTitle',
                
                // Form
                'form-name': 'formName',
                'form-position': 'formPosition',
                'form-unit': 'formUnit',
                'form-phone': 'formPhone',
                'form-submit': 'formSubmit',
                
                // Calendar
                'calendar-title': 'calendarTitle',
                'calendar-month': 'calendarMonth',
                'day-mon': 'dayMon',
                'day-tue': 'dayTue',
                'day-wed': 'dayWed',
                'day-thu': 'dayThu',
                'day-fri': 'dayFri',
                'day-sat': 'daySat',
                'day-sun': 'daySun',
                
                // Footer
                'footer-headquarters': 'footerHeadquarters',
                'footer-phone': 'footerPhone',
                'footer-rectorate': 'footerRectorate',
                'footer-press': 'footerPress',
                'footer-press-contact': 'footerPressContact',
                'footer-newsletter': 'footerNewsletter',
                'footer-videos': 'footerVideos',
                'footer-info': 'footerInfo',
                'footer-contact': 'footerContact',
                'footer-public-data': 'footerPublicData',
                'footer-privacy': 'footerPrivacy',
                'footer-cookie': 'footerCookie',
                'footer-imprint': 'footerImprint',
                'footer-job': 'footerJob',
                'footer-archive': 'footerArchive'
            };
            
            // Update all elements with data-translate attribute
            Object.keys(translateMap).forEach(key => {
                const elements = document.querySelectorAll(`[data-translate="${key}"]`);
                const textKey = translateMap[key];
                elements.forEach(element => {
                    element.textContent = texts[currentLanguage][textKey];
                });
            });
        }



        function toggleLanguage() {
            currentLanguage = currentLanguage === 'hu' ? 'en' : 'hu';
            updateLanguageUI();
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




        // Toggle switch működés
        const modeToggle = document.getElementById('modeToggle');
        const toggleLabel = document.getElementById('toggleLabel');
        const classicSearch = document.getElementById('classicSearch');
        const aiChat = document.getElementById('aiChat');

        modeToggle.addEventListener('change', function() {
            if (this.checked) {
                // AI Asszisztens mód
                toggleLabel.textContent = 'AI Asszisztens';
                classicSearch.style.display = 'none';
                aiChat.classList.add('active');
            } else {
                // Klasszikus keresés mód
                toggleLabel.textContent = 'Klasszikus keresés';
                classicSearch.style.display = 'grid';
                aiChat.classList.remove('active');
            }
        });

        // Aktuális dátum beállítása
        const today = new Date();
        const currentDay = today.getDate();
        const currentMonth = today.getMonth();

        updateCalendarCurrentDay();

        function updateCalendarCurrentDay() {
            // Naptár frissítési logika ide jöhet
            const calendarDays = document.querySelectorAll('.calendar-day');
            calendarDays.forEach(day => {
                day.classList.remove('today');
                if (parseInt(day.textContent) == currentDay && day.classList.contains('other-month') === false) {
                    day.classList.add('today');
                }
            });
        }

        calendarEvents();
        function calendarEvents() {
            // Események kezelési logikája ide jöhet
            const eventItems = document.querySelectorAll('.event-item');
            eventItems.forEach(item => {
                // Esemény idő kezelési logika ide jöhet
                const eventtime = item.querySelector('.event-time').textContent;
                const eventmonth = eventtime.split('.')[0];
                const eventday = eventtime.split('.')[1];
                console.log(eventmonth, eventday);
                // Például kiemelhetjük az aktuális hónap eseményeit
                if (parseInt(eventmonth) - 1 === currentMonth) {
                    const calendaritem = document.querySelectorAll('.calendar-day');
                    calendaritem.forEach(calitem => {
                        if (parseInt(calitem.textContent) === parseInt(eventday)) {
                            calitem.style.opacity = '0.85';
                            calitem.style.color = '#fff';
                        }
                    });
                }
            });
        }