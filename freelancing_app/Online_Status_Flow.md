# Online Status Feature - Implementation Flow

## Overview
This document explains how the real-time online status feature works in our chat system, showing a green indicator dot for users who are currently active.

## Components

### 1. User Activity Tracking
- **User Model**: Added `last_activity` field to store when a user was last active
- **Activity Property**: Added `is_online` property that returns `True` if user was active in the last 5 minutes
- **Middleware**: Created `UserActivityMiddleware` to update `last_activity` on every request

### 2. Backend Implementation

#### User Model (accounts/models.py)
```python
class User(AbstractBaseUser, PermissionsMixin):
    # Other fields...
    last_activity = models.DateTimeField(null=True, blank=True)
    
    @property
    def is_online(self):
        if not self.last_activity:
            return False
        from django.utils import timezone
        return (timezone.now() - self.last_activity).seconds < 300  # 5 minutes
```

#### Activity Middleware (accounts/middleware.py)
```python
class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Update last activity time for the user
            request.user.last_activity = timezone.now()
            request.user.save(update_fields=['last_activity'])
        
        response = self.get_response(request)
        return response
```

#### Chat API (chat/views.py)
In the API responses, we include the `is_online` flag for each user:
```python
# In ChatListView
is_online = other_user.is_online if hasattr(other_user, 'is_online') else False

existing_chats.append({
    # Other data...
    'other_user': {
        # Other user info...
        'is_online': is_online
    },
})
```

### 3. Frontend Implementation

#### JavaScript (static/js/common/chat.js)
When creating each chat row, conditionally add the status indicator:
```javascript
// In createChatRow method
if (chat.other_user.is_online) {
    const statusIndicator = document.createElement('span');
    statusIndicator.className = 'status-indicator';
    userIconContainer.appendChild(statusIndicator);
}
```

#### CSS (static/css/base.css)
Style the status indicator as a green dot:
```css
.user-icon-container {
    position: relative;
}

.status-indicator {
    position: absolute;
    bottom: 0;
    right: 0;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: #2ecc71;
    border: 2px solid #ffffff;
    z-index: 2;
}
```

## Data Flow

1. **User Activity Update**:
   - User performs any action on the site
   - Middleware updates their `last_activity` timestamp

2. **Status Determination**:
   - When chat lists are requested, the server checks each user's `is_online` property
   - This is calculated by comparing `last_activity` with the current time
   - If difference is less than 5 minutes, user is considered online

3. **Visual Representation**:
   - Frontend receives user data with `is_online` flag
   - If `is_online` is true, a green status indicator is added to the profile picture
   - CSS positions this indicator at the bottom-right of the profile image

## Benefits

- Real-time status without websocket connections for status updates
- Efficient database usage (updates only one field)
- Clean separation between backend logic and frontend display
- Minimal overhead on the system 