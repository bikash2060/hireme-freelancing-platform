// Chat Application Class
class ChatApp {
    constructor() {
        this.chatSocket = null;
        this.currentRoom = null;
        this.currentUser = null;
        
        try {
            this.initElements();
            this.bindEvents();
            this.loadChatList();
        } catch (error) {
            console.error('Error initializing chat application:', error);
        }
    }
    
    initElements() {
        this.chatList = document.querySelector('.chat-list');
        if (!this.chatList) {
            console.error('Chat list element not found');
            return;
        }
        
        this.messageBox = document.getElementById('message-box');
        this.detailedChat = document.querySelector('.chat-container');
        this.messagesContainer = document.getElementById('messages');
        this.messageInput = document.getElementById('message-text');
        this.sendButton = document.getElementById('send-btn');
        this.messengerIcon = document.getElementById('messenger-icon');
        this.minimizeBtn = document.getElementById('minimize-btn');
        this.closeBtn = document.getElementById('close-btn');
    }
    
    bindEvents() {
        if (!this.chatList || !this.messengerIcon) {
            console.error('Required elements not found, cannot bind events');
            return;
        }
        
        const searchInput = document.querySelector('.message-box .search-bar input[type="text"]');
        if (searchInput) {
            console.log('Chat search input found, adding event listener');
            searchInput.addEventListener('input', (e) => this.filterChatList(e.target.value));
            
            // Add clear button functionality if present
            const searchButton = document.querySelector('.message-box .search-bar button');
            if (searchButton) {
                searchButton.addEventListener('click', () => {
                    searchInput.value = '';
                    this.loadChatList();
                });
            }
        } else {
            console.warn('Chat search input not found. Make sure the selector matches your HTML structure.');
            console.log('Available search inputs:', document.querySelectorAll('input[type="text"]'));
        }
        
        if (this.sendButton && this.messageInput) {
            // Remove any existing event listeners
            this.sendButton.removeEventListener('click', () => this.sendMessage());
            this.messageInput.removeEventListener('keypress', () => {});
            
            // Add new event listeners
            this.sendButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
            
            this.messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            
            // Add typing indicator
            this.messageInput.addEventListener('input', () => {
                // Auto-resize the textarea
                this.messageInput.style.height = 'auto';
                this.messageInput.style.height = (this.messageInput.scrollHeight) + 'px';
                
                // Send typing indicator
                if (this.chatSocket && this.chatSocket.readyState === WebSocket.OPEN) {
                    const typingData = JSON.stringify({
                        'type': 'typing',
                        'room_name': this.currentRoom
                    });
                    this.chatSocket.send(typingData);
                }
            });
        }
        
        if (this.minimizeBtn) {
            this.minimizeBtn.addEventListener('click', () => this.toggleMinimized());
        }
        
        if (this.closeBtn && this.detailedChat) {
            this.closeBtn.addEventListener('click', () => {
                this.detailedChat.classList.remove('visible');
                if (this.chatSocket) {
                    this.chatSocket.close();
                    this.chatSocket = null;
                }
                localStorage.removeItem('chatState');
            });
        }

        this.restoreChatState();

        // Add message filter tab functionality
        const allMessagesTab = document.querySelector('.message-filter-tab.active');
        const unreadMessagesTab = document.querySelector('.message-filter-tab.unread');
        
        if (allMessagesTab) {
            allMessagesTab.addEventListener('click', () => {
                this.activateTab(allMessagesTab, unreadMessagesTab);
                this.showAllMessages();
            });
        }
        
        if (unreadMessagesTab) {
            unreadMessagesTab.addEventListener('click', () => {
                this.activateTab(unreadMessagesTab, allMessagesTab);
                this.showUnreadMessages();
            });
        }

        // Improved chat header click for minimize
        const chatHeader = this.detailedChat.querySelector('.chat-header');
        if (chatHeader) {
            chatHeader.addEventListener('click', (e) => {
                // Only toggle if clicking the header itself, not its child buttons
                if (e.target === chatHeader || e.target.closest('.user-details')) {
                    this.toggleMinimized();
                }
            });
        }
    }
    
    // Helper function to get the language prefix from the current URL
    getLanguagePrefix() {
        const pathParts = window.location.pathname.split('/');
        if (pathParts.length > 1 && pathParts[1] && pathParts[1].length === 2) {
            return `/${pathParts[1]}`;
        }
        return '';
    }

    async loadChatList() {
        if (!this.chatList) {
            console.error('Chat list element not found, cannot load chats');
            return;
        }
        
        // Save current search term if any
        const searchInput = document.querySelector('.message-box .search-bar input[type="text"]');
        const searchTerm = searchInput ? searchInput.value.trim() : '';
        
        try {
            const languagePrefix = this.getLanguagePrefix();
            const url = `${languagePrefix}/chat/chats/`;
            console.log('Attempting to fetch chats from', url);
            
            const response = await fetch(url);
            if (!response.ok) {
                console.error(`HTTP error! status: ${response.status}, statusText: ${response.statusText}`);
                throw new Error(`HTTP error! status: ${response.status}, statusText: ${response.statusText}`);
            }
            const data = await response.json();
            console.log('Received chat data:', data);
            
            this.chatList.innerHTML = '';
            let unreadCount = 0;
            let existingChatCount = 0;
            
            if (data.chats && data.chats.length > 0) {
                data.chats.forEach(chat => {
                    const chatRow = this.createChatRow(chat);
                    if (chat.room_name) {
                        existingChatCount++; // Count only existing chats with room_name
                    }
                    if (chat.unread_count > 0) {
                        chatRow.classList.add('unread');
                        unreadCount++;
                    }
                    this.chatList.appendChild(chatRow);
                });
            } else {
                // No chats available - show a friendly message
                const noChatsMessage = document.createElement('p');
                noChatsMessage.className = 'no-chats-message';
                noChatsMessage.style.textAlign = 'center';
                noChatsMessage.style.padding = '20px';
                noChatsMessage.style.color = '#888';
                noChatsMessage.textContent = 'No messages';
                this.chatList.appendChild(noChatsMessage);
            }
            
            // Update unread count in the messenger icon
            this.updateUnreadCount(unreadCount);
            
            // Update All Messages count - only show count of EXISTING chats
            const allMessagesCountSpan = document.querySelector('.message-filter-tab.active .count');
            if (allMessagesCountSpan) {
                allMessagesCountSpan.textContent = existingChatCount;
            }
            
            // Update Unread Messages count
            const unreadMessagesCountSpan = document.querySelector('.message-filter-tab.unread .count');
            if (unreadMessagesCountSpan) {
                unreadMessagesCountSpan.textContent = unreadCount;
            }
            
            // Apply search filter if there's an active search
            if (searchTerm) {
                this.filterChatList(searchTerm);
                return; // Skip the tab filtering if we're searching
            }
            
            // Check which tab is active and apply the appropriate filter
            const isUnreadTab = document.querySelector('.message-filter-tab.unread.active');
            if (isUnreadTab) {
                this.showUnreadMessages();
            } else {
                this.showAllMessages();
            }
        } catch (error) {
            console.error('Error loading chats:', error);
            if (this.chatList) {
                const errorMessage = document.createElement('p');
                errorMessage.style.textAlign = 'center';
                errorMessage.style.padding = '20px';
                errorMessage.style.color = '#ff4444';
                errorMessage.textContent = 'Error loading chats: ' + error.message;
                this.chatList.innerHTML = '';
                this.chatList.appendChild(errorMessage);
            }
        }
    }
    
    async openChat(roomName, otherUser) {
        this.currentRoom = roomName;
        this.currentUser = otherUser;
        
        this.messageBox.style.display = 'none';
        this.detailedChat.classList.add('visible');
        
        const chatState = localStorage.getItem('chatState');
        const isMinimized = chatState ? JSON.parse(chatState).isMinimized : false;
        
        if (isMinimized) {
            this.detailedChat.classList.add('minimized');
        } else {
            this.detailedChat.classList.remove('minimized');
        }
        
        localStorage.setItem('chatState', JSON.stringify({
            isOpen: true,
            roomName: roomName,
            otherUser: otherUser,
            isMinimized: isMinimized
        }));
        
        this.loadMessages(roomName);
        this.connectWebSocket(roomName);
        this.updateChatHeader(otherUser);
    }
    
    async loadMessages(roomName) {
        try {
            const languagePrefix = this.getLanguagePrefix();
            const url = `${languagePrefix}/chat/chats/${roomName}/`;
            console.log('Loading messages from', url);
            
            const response = await fetch(url);
            if (!response.ok) {
                console.error(`HTTP error loading messages! status: ${response.status}`);
                throw new Error(`Failed to load messages: ${response.status}`);
            }
            
            const data = await response.json();
            
            this.messagesContainer.innerHTML = '';
            
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => this.appendMessage(msg, msg.is_sent));
            } else {
                this.showWelcomeMessage();
            }
            
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        } catch (error) {
            console.error('Error loading messages:', error);
        }
    }
    
    connectWebSocket(roomName) {
        if (this.chatSocket) {
            this.chatSocket.close();
        }
        
        const wsScheme = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsPath = `${wsScheme}${window.location.host}/ws/chat/${roomName}/`;
        
        console.log('Connecting to WebSocket at', wsPath);
        
        try {
            this.chatSocket = new WebSocket(wsPath);
            
            this.chatSocket.onopen = () => {
                console.log('WebSocket connection established');
            };
            
            this.chatSocket.onmessage = (e) => {
                const data = JSON.parse(e.data);
                console.log('WebSocket message received:', data);
                
                // Handle different message types
                if (data.type === 'typing') {
                    // Show typing indicator when someone else is typing
                    if (data.sender !== this.currentUser.id) {
                        this.showTypingIndicator();
                    }
                } else if (data.type === 'status_change') {
                    // Handle status change events
                    this.handleStatusChange(data.user_id, data.is_online);
                } else {
                    // Regular message
                    this.appendMessage({
                        content: data.message,
                        sender: {
                            id: data.sender,
                            username: data.sender === this.currentUser.id ? this.currentUser.username : 'You'
                        },
                        timestamp: new Date().toISOString(),
                        is_sent: data.sender !== this.currentUser.id
                    }, data.sender !== this.currentUser.id);
                }
            };
            
            this.chatSocket.onclose = (e) => {
                console.error('Chat socket closed unexpectedly:', e);
            };
            
            this.chatSocket.onerror = (e) => {
                console.error('WebSocket error:', e);
            };
        } catch (error) {
            console.error('Error establishing WebSocket connection:', error);
        }
    }
    
    sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message) {
            return;
        }
        
        if (!this.chatSocket) {
            return;
        }
        
        if (this.chatSocket.readyState !== WebSocket.OPEN) {
            this.connectWebSocket(this.currentRoom);
            return;
        }
        
        try {
            const messageData = JSON.stringify({
                'message': message,
                'room_name': this.currentRoom
            });
        
            this.chatSocket.send(messageData);
            
            this.messageInput.value = '';
            
            this.loadChatList();
        } catch (error) {
            console.error('Error sending message:', error);
        }
    }
    
    createChatRow(chat) {
        const chatRow = document.createElement('div');
        chatRow.className = 'chat-row';
        if (chat.room_name) {
            chatRow.dataset.roomName = chat.room_name;
        }
        chatRow.dataset.userId = chat.other_user.id;
        
        // User icon/image with status indicator properly positioned
        const userIconContainer = document.createElement('div');
        userIconContainer.className = 'user-icon-container';
        
        const userIcon = document.createElement('div');
        userIcon.className = 'user-icon';
        
        if (chat.other_user.profile_image) {
            const img = document.createElement('img');
            img.src = chat.other_user.profile_image;
            img.alt = chat.other_user.full_name || 'User';
            userIcon.appendChild(img);
        } else {
            const icon = document.createElement('i');
            icon.className = 'fa-regular fa-user';
            userIcon.appendChild(icon);
        }
        
        // Add status indicator only if user is online
        if (chat.other_user.is_online) {
            const statusIndicator = document.createElement('span');
            statusIndicator.className = 'status-indicator';
            userIconContainer.appendChild(statusIndicator);
        }
        
        userIconContainer.appendChild(userIcon);
        
        const chatDetails = document.createElement('div');
        chatDetails.className = 'chat-details';
        
        const chatName = document.createElement('p');
        chatName.className = 'chat-name';
        chatName.textContent = chat.other_user.full_name;
        chatName.title = chat.other_user.full_name;
        
        const chatMeta = document.createElement('div');
        chatMeta.className = 'chat-meta';
        
        const message = document.createElement('span');
        message.className = 'message';
        if (chat.last_message?.content) {
            message.textContent = chat.last_message.content;
            message.title = chat.last_message.content;
        } else {
            message.textContent = 'Start a new conversation';
            message.style.fontStyle = 'italic';
            message.style.color = '#888';
        }
        
        const time = document.createElement('span');
        time.className = 'time';
        time.textContent = chat.last_message ? this.formatTime(chat.last_message.timestamp) : '';
        
        chatMeta.appendChild(message);
        chatMeta.appendChild(time);
        chatDetails.appendChild(chatName);
        chatDetails.appendChild(chatMeta);
        chatRow.appendChild(userIconContainer);
        chatRow.appendChild(chatDetails);
        
        // Handle click for both existing and new chats
        chatRow.addEventListener('click', () => {
            if (chat.room_name) {
                this.openChat(chat.room_name, chat.other_user);
            } else {
                this.startNewChat(chat.other_user);
            }
        });
        
        return chatRow;
    }

    async startNewChat(otherUser) {
        try {
            const languagePrefix = this.getLanguagePrefix();
            const url = `${languagePrefix}/chat/start-chat/${otherUser.id}/`;
            console.log('Starting new chat with', otherUser.full_name, 'at', url);
            
            const csrftoken = this.getCookie('csrftoken');
            if (!csrftoken) {
                console.error('CSRF token not found');
                alert('Security token not found. Please refresh the page and try again.');
                return;
            }
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({}), // Empty body but ensuring it's a valid JSON
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                console.error(`HTTP error starting chat! status: ${response.status}`);
                throw new Error(`Failed to start chat: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Chat started successfully', data);
            this.openChat(data.room_name, data.other_user);
        } catch (error) {
            console.error('Error starting new chat:', error);
            alert('Failed to start a new chat. Please try again later.');
        }
    }
    
    // Helper function to get CSRF token
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    updateUnreadCount(count) {
        if (!this.messengerIcon) return;
        
        const unreadSpan = this.messengerIcon.querySelector('span');
        if (!unreadSpan) return;
        
        if (count > 0) {
            unreadSpan.textContent = count;
            unreadSpan.style.display = 'inline';
        } else {
            unreadSpan.style.display = 'none';
        }
    }
    
    updateChatHeader(otherUser) {
        const userInfo = this.detailedChat.querySelector('.user-info');
        if (userInfo) {
            const userName = userInfo.querySelector('.user-name');
            if (userName) {
                userName.textContent = otherUser.full_name || otherUser.username;
            }
            
            // Update online status text and indicator
            const statusText = userInfo.querySelector('.status .status-text');
            const statusIndicator = userInfo.querySelector('.status .status-indicator');
            
            if (statusText) {
                statusText.textContent = otherUser.is_online ? 'Online' : 'Offline';
            }
            
            if (statusIndicator) {
                statusIndicator.style.display = otherUser.is_online ? 'block' : 'none';
                statusIndicator.style.backgroundColor = otherUser.is_online ? '#4caf50' : '#bbb';
            }
            
            const avatar = this.detailedChat.querySelector('.avatar img');
            if (avatar && otherUser.profile_image) {
                avatar.src = otherUser.profile_image;
                avatar.alt = otherUser.full_name || otherUser.username;
            }
        }
    }
    
    showWelcomeMessage(otherUser = null) {
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'welcome-message';
        
        if (otherUser) {
            welcomeDiv.innerHTML = `
                <div class="empty-chat-message">
                    <i class="fa-regular fa-comments" style="font-size: 48px; color: #ccc; margin-bottom: 15px;"></i>
                    <p style="font-size: 18px; color: #666; margin-bottom: 10px;">Start a Conversation with ${otherUser.full_name}</p>
                    <p style="color: #888; font-size: 14px;">Say hi and begin chatting!</p>
                </div>
            `;
        } else {
            welcomeDiv.innerHTML = `
                <div class="empty-chat-message">
                    <i class="fa-regular fa-comments" style="font-size: 48px; color: #ccc; margin-bottom: 15px;"></i>
                    <p style="font-size: 18px; color: #666; margin-bottom: 10px;">No messages yet</p>
                    <p style="color: #888; font-size: 14px;">Start a new conversation</p>
                </div>
            `;
        }
        
        welcomeDiv.style.cssText = `
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            text-align: center;
        `;
        this.messagesContainer.appendChild(welcomeDiv);
    }
    
    appendMessage(message, isReceived) {
        const welcomeMessage = this.messagesContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isReceived ? 'received' : 'sent'}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = message.content;
        
        const timeSpan = document.createElement('span');
        timeSpan.className = 'message-meta';
        timeSpan.textContent = this.formatTime(message.timestamp);
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeSpan);
        this.messagesContainer.appendChild(messageDiv);
        
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    formatTime(timestamp) {
        if (!timestamp) return '';
        
        const date = new Date(timestamp);
        const now = new Date();
        
        if (date.toDateString() === now.toDateString()) {
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } else if (date.getFullYear() === now.getFullYear()) {
            return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
        } else {
            return date.toLocaleDateString();
        }
    }

    restoreChatState() {
        const chatState = localStorage.getItem('chatState');
        if (chatState) {
            const { isOpen, roomName, otherUser, isMinimized } = JSON.parse(chatState);
            if (isOpen) {
                // First make sure the chat container has the visible class
                if (this.detailedChat) {
                    this.detailedChat.classList.add('visible');
                }
                
                this.openChat(roomName, otherUser).then(() => {
                    // Restore minimized state after chat is opened
                    if (isMinimized) {
                        this.detailedChat.classList.add('minimized');
                    } else {
                        this.detailedChat.classList.remove('minimized');
                    }
                });
            }
        }
    }

    filterChatList(searchTerm) {
        if (!this.chatList) return;
        
        searchTerm = searchTerm.toLowerCase().trim();
        console.log('Filtering chat list with search term:', searchTerm);
        
        // If search is cleared (empty search term), reload the full chat list
        if (searchTerm === '') {
            console.log('Search cleared, reloading chat list');
            this.loadChatList();
            return;
        }
        
        // Check which tab is active
        const isUnreadTab = document.querySelector('.message-filter-tab.unread.active');
        
        if (isUnreadTab) {
            // If unread tab is active, only show unread messages that match search
            this.showUnreadMessages();
        } else {
            // Otherwise show all messages that match search
            this.showAllMessages();
        }
    }

    activateTab(activeTab, inactiveTab) {
        if (!activeTab || !inactiveTab) return;
        
        activeTab.classList.add('active');
        inactiveTab.classList.remove('active');
    }
    
    showAllMessages() {
        if (!this.chatList) return;
        
        console.log('Showing all messages');
        const searchInput = document.querySelector('.message-box .search-bar input[type="text"]');
        const searchTerm = searchInput ? searchInput.value.trim().toLowerCase() : '';
        
        const chatRows = this.chatList.querySelectorAll('.chat-row');
        
        // If no chat rows found, reload the chat list to get the appropriate "No messages" display
        if (chatRows.length === 0 && !searchTerm) {
            console.log('No chat rows found, reload to get proper display');
            this.loadChatList();
            return;
        }
        
        // If there's a search term, first hide all chat rows
        if (searchTerm) {
            chatRows.forEach(row => {
                row.style.display = 'none';
            });
        }
        
        let visibleCount = 0;
        let existingChatCount = 0;
        
        chatRows.forEach(row => {
            // Check if this is an existing chat room (has a room_name attribute)
            const hasExistingChat = row.dataset.roomName ? true : false;
            
            if (searchTerm) {
                // If searching, only show matching rows
                const userName = row.querySelector('.chat-name')?.textContent?.toLowerCase() || '';
                const lastMessage = row.querySelector('.message')?.textContent?.toLowerCase() || '';
                
                if (userName.includes(searchTerm) || lastMessage.includes(searchTerm)) {
                    row.style.display = 'flex'; // Show matching rows
                    visibleCount++;
                    if (hasExistingChat) {
                        existingChatCount++;
                    }
                }
            } else {
                // If not searching, show all rows
                row.style.display = 'flex';
                visibleCount++;
                if (hasExistingChat) {
                    existingChatCount++;
                }
            }
        });
        
        // Update no results message if needed
        this.updateNoResultsMessage(visibleCount, searchTerm);
        
        // Update the count in the tab - only show count of EXISTING chats
        const allMessagesCountSpan = document.querySelector('.message-filter-tab.active .count');
        if (allMessagesCountSpan) {
            allMessagesCountSpan.textContent = existingChatCount;
        }
    }
    
    showUnreadMessages() {
        if (!this.chatList) return;
        
        console.log('Showing unread messages only');
        const searchInput = document.querySelector('.message-box .search-bar input[type="text"]');
        const searchTerm = searchInput ? searchInput.value.trim().toLowerCase() : '';
        
        // First hide all chat rows
        const allChatRows = this.chatList.querySelectorAll('.chat-row');
        allChatRows.forEach(row => {
            row.style.display = 'none';
        });
        
        const chatRows = this.chatList.querySelectorAll('.chat-row');
        let visibleCount = 0;
        let unreadChatCount = 0;
        
        chatRows.forEach(row => {
            const isUnread = row.classList.contains('unread');
            const hasExistingChat = row.dataset.roomName ? true : false;
            
            if (isUnread) {
                if (searchTerm) {
                    // If searching, only show unread rows that match
                    const userName = row.querySelector('.chat-name')?.textContent?.toLowerCase() || '';
                    const lastMessage = row.querySelector('.message')?.textContent?.toLowerCase() || '';
                    
                    if (userName.includes(searchTerm) || lastMessage.includes(searchTerm)) {
                        row.style.display = 'flex';
                        visibleCount++;
                        if (hasExistingChat) {
                            unreadChatCount++;
                        }
                    }
                } else {
                    // If not searching, show all unread rows
                    row.style.display = 'flex';
                    visibleCount++;
                    if (hasExistingChat) {
                        unreadChatCount++;
                    }
                }
            }
        });
        
        // Update no results message if needed
        this.updateNoResultsMessage(visibleCount, searchTerm);
        
        // Update the count in the tab - should reflect unread messages in actual chat rooms
        const unreadMessagesCountSpan = document.querySelector('.message-filter-tab.unread .count');
        if (unreadMessagesCountSpan) {
            unreadMessagesCountSpan.textContent = unreadChatCount;
        }
    }
    
    updateNoResultsMessage(visibleCount, searchTerm) {
        if (visibleCount === 0) {
            // Clear the chat list and show only the no results message
            this.chatList.innerHTML = '';
            
            const noResultsMsg = document.createElement('p');
            noResultsMsg.className = 'no-results-message';
            noResultsMsg.style.textAlign = 'center';
            noResultsMsg.style.padding = '20px';
            noResultsMsg.style.color = '#888';
            
            if (searchTerm) {
                noResultsMsg.textContent = `No results found for "${searchTerm}"`;
            } else {
                // Check which tab is active
                const isUnreadTab = document.querySelector('.message-filter-tab.unread.active');
                noResultsMsg.textContent = isUnreadTab ? 'No unread messages' : 'No messages';
            }
            
            this.chatList.appendChild(noResultsMsg);
        }
    }

    toggleMinimized() {
        if (!this.detailedChat) return;
        
        const isMinimized = this.detailedChat.classList.toggle('minimized');
        
        // Update the button icon
        if (this.minimizeBtn) {
            this.minimizeBtn.innerHTML = isMinimized ? 
                '<i class="fa-solid fa-caret-up"></i>' : 
                '<i class="fa-solid fa-minus"></i>';
        }
        
        // Store the state in localStorage
        const chatState = localStorage.getItem('chatState');
        if (chatState) {
            const state = JSON.parse(chatState);
            state.isMinimized = isMinimized;
            localStorage.setItem('chatState', JSON.stringify(state));
        }
    }
    
    showTypingIndicator() {
        if (!this.messagesContainer) return;
        
        // Remove existing typing indicator if any
        const existingIndicator = this.messagesContainer.querySelector('.typing-indicator');
        if (existingIndicator) return;
        
        // Create typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        
        // Add three dots
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            typingIndicator.appendChild(dot);
        }
        
        this.messagesContainer.appendChild(typingIndicator);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        
        // Set a timeout to remove the indicator
        setTimeout(() => this.removeTypingIndicator(), 3000);
    }
    
    removeTypingIndicator() {
        if (!this.messagesContainer) return;
        
        const typingIndicator = this.messagesContainer.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Add new method to handle status changes
    handleStatusChange(userId, isOnline) {
        console.log('Status change:', userId, isOnline);
        
        // Update chat list status
        const chatRow = this.chatList.querySelector(`.chat-row[data-user-id="${userId}"]`);
        if (chatRow) {
            const statusIndicator = chatRow.querySelector('.status-indicator');
            if (statusIndicator) {
                if (isOnline) {
                    statusIndicator.style.display = 'block';
                    statusIndicator.style.backgroundColor = '#4caf50';
                } else {
                    statusIndicator.style.display = 'none';
                }
            }
        }

        // Update detailed chat view if this user's chat is open
        if (this.currentUser && this.currentUser.id === userId) {
            const detailedChatStatus = this.detailedChat.querySelector('.status');
            if (detailedChatStatus) {
                const statusText = detailedChatStatus.querySelector('.status-text');
                const statusIndicator = detailedChatStatus.querySelector('.status-indicator');
                
                if (statusText) {
                    statusText.textContent = isOnline ? 'Online' : 'Offline';
                }
                
                if (statusIndicator) {
                    statusIndicator.style.display = isOnline ? 'block' : 'none';
                    statusIndicator.style.backgroundColor = isOnline ? '#4caf50' : '#bbb';
                }
            }
        }

        // Update the user's online status in our data
        if (this.currentUser && this.currentUser.id === userId) {
            this.currentUser.is_online = isOnline;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const chatApp = new ChatApp();
});