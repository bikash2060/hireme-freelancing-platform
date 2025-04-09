// Chat Application Class
class ChatApp {
    constructor() {
        console.log('Initializing ChatApp...');
        this.chatSocket = null;
        this.currentRoom = null;
        this.currentUser = null;
        
        this.initElements();
        this.bindEvents();
        this.loadChatList();
        console.log('ChatApp initialized');
    }
    
    // Initialize DOM elements
    initElements() {
        console.log('Initializing elements...');
        this.chatList = document.querySelector('.chat-list');
        this.messageBox = document.getElementById('message-box');
        this.detailedChat = document.querySelector('.detailed-chat .main-box');
        this.messagesContainer = this.detailedChat.querySelector('.messages');
        this.messageInput = this.detailedChat.querySelector('#message-input');
        this.sendButton = this.detailedChat.querySelector('#send-message');
        this.messengerIcon = document.getElementById('messenger-icon');
        this.minimizeBtn = this.detailedChat.querySelector('#minimize-chat');
        this.closeBtn = this.detailedChat.querySelector('#close-chat');
        
        console.log('Elements initialized');
    }
    
    // Bind event listeners
    bindEvents() {
        // Send message
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Minimize/close chat
        this.minimizeBtn.addEventListener('click', () => {
            const isMinimized = this.detailedChat.classList.toggle('minimized');
            // Update button icon
            this.minimizeBtn.innerHTML = isMinimized ? 
                '<i class="fa-solid fa-caret-up"></i>' : 
                '<i class="fa-solid fa-minus"></i>';
            
            // Save minimized state
            const chatState = localStorage.getItem('chatState');
            if (chatState) {
                const state = JSON.parse(chatState);
                state.isMinimized = isMinimized;
                localStorage.setItem('chatState', JSON.stringify(state));
            }
        });
        
        this.closeBtn.addEventListener('click', () => {
            this.detailedChat.style.display = 'none';
            if (this.chatSocket) {
                this.chatSocket.close();
                this.chatSocket = null;
            }
            // Clear chat state when closing
            localStorage.removeItem('chatState');
        });

        // Restore chat state on page load
        this.restoreChatState();

        const messageInput = document.querySelector('.message-input textarea');

        messageInput.addEventListener('input', function() {
            this.style.height = 'auto'; // Reset height
            this.style.height = (this.scrollHeight) + 'px'; // Set new height
        });
    }
    
    // Load chat list from server
    async loadChatList() {
        try {
            console.log('Loading chat list...');
            const response = await fetch('/chat/chats/');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('Chat data received:', data);
            
            this.chatList.innerHTML = '';
            let unreadCount = 0;
            
            if (data.chats && data.chats.length > 0) {
                data.chats.forEach(chat => {
                    const chatRow = this.createChatRow(chat);
                    if (chat.unread_count > 0) {
                        chatRow.classList.add('unread');
                        unreadCount++;
                    }
                    this.chatList.appendChild(chatRow);
                });
            } else {
                const noChatsMessage = document.createElement('p');
                noChatsMessage.style.textAlign = 'center';
                noChatsMessage.style.padding = '20px';
                noChatsMessage.style.color = '#666';
                noChatsMessage.textContent = 'No chats yet';
                this.chatList.appendChild(noChatsMessage);
            }
            
            // Update messenger icon with unread count
            this.updateUnreadCount(unreadCount);
        } catch (error) {
            console.error('Error loading chat list:', error);
            const errorMessage = document.createElement('p');
            errorMessage.style.textAlign = 'center';
            errorMessage.style.padding = '20px';
            errorMessage.style.color = '#ff4444';
            errorMessage.textContent = 'Error loading chats';
            this.chatList.innerHTML = '';
            this.chatList.appendChild(errorMessage);
        }
    }
    
    // Open chat with specific user
    async openChat(roomName, otherUser) {
        this.currentRoom = roomName;
        this.currentUser = otherUser;
        
        // Hide message box and show detailed chat
        this.messageBox.style.display = 'none';
        this.detailedChat.style.display = 'block';
        
        // Get existing minimized state or default to false
        const chatState = localStorage.getItem('chatState');
        const isMinimized = chatState ? JSON.parse(chatState).isMinimized : false;
        
        // Apply minimized state
        if (isMinimized) {
            this.detailedChat.classList.add('minimized');
            this.minimizeBtn.innerHTML = '<i class="fa-solid fa-caret-up"></i>';
        } else {
            this.detailedChat.classList.remove('minimized');
            this.minimizeBtn.innerHTML = '<i class="fa-solid fa-minus"></i>';
        }
        
        // Store chat state in localStorage
        localStorage.setItem('chatState', JSON.stringify({
            isOpen: true,
            roomName: roomName,
            otherUser: otherUser,
            isMinimized: isMinimized
        }));
        
        // Load messages
        await this.loadMessages(roomName);
        
        // Set up WebSocket connection
        this.connectWebSocket(roomName);
        
        // Update chat header
        this.updateChatHeader(otherUser);
    }
    
    // Load messages for a specific chat
    async loadMessages(roomName) {
        try {
            const response = await fetch(`/chat/chats/${roomName}/`);
            const data = await response.json();
            
            this.messagesContainer.innerHTML = '';
            
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => this.appendMessage(msg, msg.is_sent));
            } else {
                // Show welcome message when there are no messages
                this.showWelcomeMessage();
            }
            
            // Scroll to bottom
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        } catch (error) {
            console.error('Error loading messages:', error);
        }
    }
    
    // Connect to WebSocket for real-time messaging
    connectWebSocket(roomName) {
        // Close previous connection if exists
        if (this.chatSocket) {
            this.chatSocket.close();
        }
        
        // Create new WebSocket connection
        const wsScheme = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsPath = `${wsScheme}${window.location.host}/ws/chat/${roomName}/`;
        console.log('Connecting to WebSocket:', wsPath);
        
        this.chatSocket = new WebSocket(wsPath);
        
        this.chatSocket.onopen = () => {
            console.log('WebSocket connection established');
        };
        
        this.chatSocket.onmessage = (e) => {
            console.log('WebSocket message received:', e.data);
            const data = JSON.parse(e.data);
            this.appendMessage({
                content: data.message,
                sender: {
                    id: data.sender,
                    username: data.sender === this.currentUser.id ? this.currentUser.username : 'You'
                },
                timestamp: new Date().toISOString(),
                is_sent: data.sender !== this.currentUser.id
            }, data.sender !== this.currentUser.id);
        };
        
        this.chatSocket.onclose = (e) => {
            console.error('Chat socket closed unexpectedly:', e);
        };
        
        this.chatSocket.onerror = (e) => {
            console.error('WebSocket error:', e);
        };
    }
    
    // Send message through WebSocket
    sendMessage() {
        const message = this.messageInput.value.trim();
        console.log('Attempting to send message:', message);
        console.log('WebSocket state:', this.chatSocket?.readyState);
        
        if (!message) {
            console.log('Message is empty, not sending');
            return;
        }
        
        if (!this.chatSocket) {
            console.error('No WebSocket connection');
            return;
        }
        
        if (this.chatSocket.readyState !== WebSocket.OPEN) {
            console.error('WebSocket is not open. Current state:', this.chatSocket.readyState);
            // Try to reconnect
            this.connectWebSocket(this.currentRoom);
            return;
        }
        
        try {
            const messageData = JSON.stringify({
                'message': message,
                'room_name': this.currentRoom
            });
            console.log('Sending message data:', messageData);
            
            this.chatSocket.send(messageData);
            console.log('Message sent successfully');
            
            // Clear input
            this.messageInput.value = '';
            
            // Reload chat list to update last message
            this.loadChatList();
        } catch (error) {
            console.error('Error sending message:', error);
        }
    }
    
    // Helper methods
    createChatRow(chat) {
        const chatRow = document.createElement('div');
        chatRow.className = 'chat-row';
        chatRow.dataset.roomName = chat.room_name;
        
        const userIcon = document.createElement('i');
        userIcon.className = 'fa-regular fa-user user-icon';
        if (chat.other_user.profile_image) {
            userIcon.style.backgroundImage = `url(${chat.other_user.profile_image})`;
            userIcon.style.backgroundSize = 'cover';
            userIcon.classList.remove('fa-user');
        }
        
        const chatDetails = document.createElement('div');
        chatDetails.className = 'chat-details';
        
        const chatName = document.createElement('p');
        chatName.className = 'chat-name';
        chatName.textContent = chat.other_user.full_name;
        chatName.title = chat.other_user.full_name; // Add tooltip for full name
        
        const chatMeta = document.createElement('div');
        chatMeta.className = 'chat-meta';
        
        const message = document.createElement('span');
        message.className = 'message';
        // Only show last message if it exists, otherwise leave empty
        if (chat.last_message?.content) {
            message.textContent = chat.last_message.content;
            message.title = chat.last_message.content; // Add tooltip for full message
        }
        
        const time = document.createElement('span');
        time.className = 'time';
        time.textContent = chat.last_message ? this.formatTime(chat.last_message.timestamp) : '';
        
        chatMeta.appendChild(message);
        chatMeta.appendChild(time);
        chatDetails.appendChild(chatName);
        chatDetails.appendChild(chatMeta);
        chatRow.appendChild(userIcon);
        chatRow.appendChild(chatDetails);
        
        chatRow.addEventListener('click', () => this.openChat(chat.room_name, chat.other_user));
        return chatRow;
    }
    
    updateUnreadCount(count) {
        const unreadSpan = this.messengerIcon.querySelector('span');
        if (count > 0) {
            unreadSpan.textContent = count;
            unreadSpan.style.display = 'inline';
        } else {
            unreadSpan.style.display = 'none';
        }
    }
    
    updateChatHeader(otherUser) {
        const userInfo = this.detailedChat.querySelector('.user-info');
        userInfo.querySelector('.user-name').textContent = otherUser.full_name;
        
        const profileImg = userInfo.querySelector('.profile-img');
        const userIcon = userInfo.querySelector('.user-icon');
        
        if (otherUser.profile_image) {
            profileImg.src = otherUser.profile_image;
            profileImg.style.display = 'block';
            userIcon.style.display = 'none';
        } else {
            profileImg.style.display = 'none';
            userIcon.style.display = 'block';
            userIcon.className = 'fa-regular fa-user user-icon';
        }
    }
    
    showWelcomeMessage() {
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'welcome-message';
        welcomeDiv.innerHTML = `
            <div class="empty-chat-message">
                <i class="fa-regular fa-comments" style="font-size: 48px; color: #ccc; margin-bottom: 15px;"></i>
                <p style="font-size: 18px; color: #666; margin-bottom: 10px;">Start a Conversation</p>
                <p style="color: #888; font-size: 14px;">Say hi and begin chatting!</p>
            </div>
        `;
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
        // Remove welcome message if it exists
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
        timeSpan.className = 'message-time';
        timeSpan.textContent = this.formatTime(message.timestamp);
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeSpan);
        this.messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    formatTime(timestamp) {
        if (!timestamp) return '';
        
        const date = new Date(timestamp);
        const now = new Date();
        
        if (date.toDateString() === now.toDateString()) {
            // Today - show time
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } else if (date.getFullYear() === now.getFullYear()) {
            // This year - show month and day
            return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
        } else {
            // Older - show full date
            return date.toLocaleDateString();
        }
    }

    // Add method to restore chat state
    restoreChatState() {
        const chatState = localStorage.getItem('chatState');
        if (chatState) {
            const { isOpen, roomName, otherUser, isMinimized } = JSON.parse(chatState);
            if (isOpen) {
                this.openChat(roomName, otherUser).then(() => {
                    // Restore minimized state after chat is opened
                    if (isMinimized) {
                        this.detailedChat.classList.add('minimized');
                        this.minimizeBtn.innerHTML = '<i class="fa-solid fa-caret-up"></i>';
                    } else {
                        this.detailedChat.classList.remove('minimized');
                        this.minimizeBtn.innerHTML = '<i class="fa-solid fa-minus"></i>';
                    }
                });
            }
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const chatApp = new ChatApp();
});