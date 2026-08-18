// username, csrftoken, and chatId are set in chat.html
const chat = chatId || '' // Set current chat ID or empty string for global chat

const eventSource = new EventSource('/api/stream-chat-events/' + chat);

eventSource.onopen = () => {
    console.log("Connection established")
}
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data)
    console.log(data)
    switch (data.action) {
        case 'create':
            handleNewMessage(data.message);
            break;
        case 'delete':
            $(`.message#${data.message_id}`).remove();
            break;
        case 'typing':
            renderTypingUsers(data.users);
            break;
        default:
            console.log('Unknown action:', data.action);
    }
}

function handleNewMessage(message) {
    if (message.chat_id !== chatId) {
        const $messageChat = $(`.chat#${message.chat_id}`);
        const $unreadCount = $messageChat.find('.unread-count');
        const unreadCount = $unreadCount.length ? parseInt($unreadCount.text()) : 0;
        $unreadCount.text(unreadCount + 1);

        if (!$unreadCount.length) {
            $messageChat.append('<span class="unread-count">1</span>');
        }
        return;
    }

    message.timestamp = formatDate(message.timestamp + 'Z'); // add 'Z' to convert to UTC
    renderMessage(message);
}

function renderMessage({ id, author, timestamp, text }) {
    if ($(`.message#${id}`).length) {
        return // Avoid rendering the same message multiple times
    }

    const $message = $(`
        <div class="message" id="${id}">
            <div class="message-info">
                <img src="${author.pfp}" alt="Avatar">
                <span class="message-author"></span>
                <span class="timestamp">${timestamp}</span>
            </div>
            <p class="message-text"></p>
        </div>
    `);

    // Set message content using .text() to prevent XSS
    $message.find('.message-author').text(author.display_name);
    $message.find('.message-text').text(text);

    if (author.username === username) {
        $message.addClass('own-message')
            .find('.message-info').append(
                $('<div class="delete-message">')
                    .on('click', () => { deleteMessage(id) })
                    .append('<img src="/static/icons/remove.svg">')
            );
    }

    $('#chat-messages').append($message);
    $message[0].scrollIntoView();
}

function deleteMessage(messageId) {
    $.ajax({
        url: `/api/messages/${messageId}/`,
        type: 'DELETE'
    })
}

// Send message
$('#message-form').on('submit', (event) => {
    event.preventDefault() // Prevent the form from submitting the traditional way
    const text = $('#message-input').val()
    if (text.trim()) { // check if message text is not empty
        $.post('/api/messages/', {
            'chat': chat,
            'text': text,
        })
    }
    $('#message-input').val('')
});

// Typing indicator logic
let typingTimeout;
let isTyping = false;

$('#message-input').on('input', function() {
    if (!chatId) {
        return; // Skip typing status if in global chat
    }
    const text = $(this).val();
    updateTypingStatus(!!text); // set isTyping to true if text is not empty

    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(updateTypingStatus, 10000, false);
});

function updateTypingStatus(isTypingNow = true) {
    if (isTypingNow !== isTyping) {
        $.get(`/api/set-typing-status/${isTypingNow ? chatId : ''}`, () => {
            isTyping = isTypingNow;
        });
    }
}

const $chatMembers = $('#chat-members');
const initialChatMembersText = $chatMembers.text();
function renderTypingUsers(users) {
    let text = initialChatMembersText;

    if (users.length === 1) {
        text = `${users[0]} is typing...`;
    } else if (users.length === 2) {
        text = `${users[0]} and ${users[1]} are typing...`;
    } else if (users.length > 2) {
        const firstTwoUsers = users.slice(0, 2).join(', ');
        const othersCount = users.length - 2;
        text = `${firstTwoUsers}, and ${othersCount} others are typing...`;
    }

    $chatMembers.text(text);
}