// Chat Application Class
class ChatApp {
    constructor() {
        this.chatSocket = null;
        this.currentRoom = null;
        this.currentUser = null;
        
        this.initElements();
        this.bindEvents();
        this.loadChatList();
    }
    
    initElements() {
        this.chatList = document.querySelector('.chat-list');
        this.messageBox = document.getElementById('message-box');
        this.detailedChat = document.querySelector('.detailed-chat .main-box');
        this.messagesContainer = this.detailedChat.querySelector('.messages');
        this.messageInput = this.detailedChat.querySelector('#message-input');
        this.sendButton = this.detailedChat.querySelector('#send-message');
        this.messengerIcon = document.getElementById('messenger-icon');
        this.minimizeBtn = this.detailedChat.querySelector('#minimize-chat');
        this.closeBtn = this.detailedChat.querySelector('#close-chat');
    }
    
    bindEvents() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        this.minimizeBtn.addEventListener('click', () => {
            const isMinimized = this.detailedChat.classList.toggle('minimized');
            this.minimizeBtn.innerHTML = isMinimized ? 
                '<i class="fa-solid fa-caret-up"></i>' : 
                '<i class="fa-solid fa-minus"></i>';
            
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
            localStorage.removeItem('chatState');
        });

        this.restoreChatState();

        const messageInput = document.querySelector('.message-input textarea');

        messageInput.addEventListener('input', function() {
            this.style.height = 'auto'; 
            this.style.height = (this.scrollHeight) + 'px'; 
        });
    }
    
    async loadChatList() {
        try {
            const response = await fetch('/chat/chats/');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
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
                noChatsMessage.className = 'no-chats-message';
                noChatsMessage.textContent = 'No chats yet';
                this.chatList.appendChild(noChatsMessage);
            }
            
            this.updateUnreadCount(unreadCount);
        } catch (error) {
            const errorMessage = document.createElement('p');
            errorMessage.style.textAlign = 'center';
            errorMessage.style.padding = '20px';
            errorMessage.style.color = '#ff4444';
            errorMessage.textContent = 'Error loading chats';
            this.chatList.innerHTML = '';
            this.chatList.appendChild(errorMessage);
        }
    }
    
    async openChat(roomName, otherUser) {
        this.currentRoom = roomName;
        this.currentUser = otherUser;
        
        this.messageBox.style.display = 'none';
        this.detailedChat.style.display = 'block';
        
        const chatState = localStorage.getItem('chatState');
        const isMinimized = chatState ? JSON.parse(chatState).isMinimized : false;
        
        if (isMinimized) {
            this.detailedChat.classList.add('minimized');
            this.minimizeBtn.innerHTML = '<i class="fa-solid fa-caret-up"></i>';
        } else {
            this.detailedChat.classList.remove('minimized');
            this.minimizeBtn.innerHTML = '<i class="fa-solid fa-minus"></i>';
        }
        
        localStorage.setItem('chatState', JSON.stringify({
            isOpen: true,
            roomName: roomName,
            otherUser: otherUser,
            isMinimized: isMinimized
        }));
        
        await this.loadMessages(roomName);
        
        this.connectWebSocket(roomName);
        
        this.updateChatHeader(otherUser);
    }
    
    async loadMessages(roomName) {
        try {
            const response = await fetch(`/chat/chats/${roomName}/`);
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
        
        this.chatSocket = new WebSocket(wsPath);
        
        this.chatSocket.onopen = () => {
        };
        
        this.chatSocket.onmessage = (e) => {
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
        chatName.title = chat.other_user.full_name; 
        
        const chatMeta = document.createElement('div');
        chatMeta.className = 'chat-meta';
        
        const message = document.createElement('span');
        message.className = 'message';
        if (chat.last_message?.content) {
            message.textContent = chat.last_message.content;
            message.title = chat.last_message.content;
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

document.addEventListener('DOMContentLoaded', () => {
    const chatApp = new ChatApp();
});