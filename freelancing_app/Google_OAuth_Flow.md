# Google OAuth Authentication Flow

This document explains how authentication works when users sign in with Google in our application. It includes all the steps and decision points in the process.

## Overview

The authentication flow is designed to:
1. Allow users to sign in with Google
2. Keep traditional and Google accounts separate
3. Require new Google users to select a role (client or freelancer)
4. Prevent cross-authentication methods

## Flow Diagram

```
+----------------------+     +---------------------+     +---------------------+
| User clicks "Login   |     | Google handles      |     | Our app receives    |
| with Google" button  |---->| authentication and  |---->| user info and       |
| on our website       |     | user authorization  |     | checks database     |
+----------------------+     +---------------------+     +---------+-----------+
                                                                  |
                                                                  v
                       +---------------------------------------------------+
                       |            Check if email exists in DB            |
                       +---------------------------------------------------+
                                    |                    |
             +----------------------+                    +----------------------+
             |                                                                 |
             v                                                                 v
    +--------+------------+                                      +-------------+-----------+
    | Email exists?       |                                      | Email doesn't exist     |
    +--------+------------+                                      | (New user)              |
             |                                                   +-------------+-----------+
             v                                                                 |
    +--------+------------+                                                    |
    | Check auth_method   |                                                    |
    +--------+------------+                                                    |
             |                                                                 |
      +------+-------+                                                         |
      |              |                                                         |
      v              v                                                         v
+-----+------+ +-----+--------+                                  +-------------+-----------+
| Traditional | | Google OAuth |                                 | Store OAuth data in     |
| account    | | account      |                                 | session                  |
+-----+------+ +-----+--------+                                 +-------------+-----------+
      |              |                                                         |
      v              v                                                         v
+-----+------+ +-----+--------+                                  +-------------+-----------+
| Show error | | Complete     |                                  | Redirect to role        |
| message    | | normal OAuth |                                  | selection page          |
|            | | login flow   |                                  +-------------+-----------+
+-----+------+ +-----+--------+                                               |
      |              |                                                         v
      v              v                                           +-------------+-----------+
+-----+------+ +-----+--------+                                  | User selects role      |
| Redirect to| | Redirect to  |                                  | (client or freelancer) |
| login page | | home page    |                                  +-------------+-----------+
+------------+ +-------------+                                                |
                                                                              v
                                                                +-------------+-----------+
                                                                | Create new user with    |
                                                                | auth_method='google'    |
                                                                +-------------+-----------+
                                                                              |
                                                                              v
                                                                +-------------+-----------+
                                                                | Create role profile     |
                                                                | based on selection      |
                                                                +-------------+-----------+
                                                                              |
                                                                              v
                                                                +-------------+-----------+
                                                                | Log in user and         |
                                                                | redirect to home page   |
                                                                +-------------------------+
```