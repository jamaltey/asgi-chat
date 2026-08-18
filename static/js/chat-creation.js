const $chatCreationForm = $('#create-chat-form');
const $newChatBtn = $('#new-chat-btn');

$newChatBtn.on('click', () => {
    $chatCreationForm.toggle();
})

// Create chat
$chatCreationForm.on('submit', function(event) {
    event.preventDefault() // Prevent the form from submitting the traditional way
    const name = $(this).find('[name=name]').val()
    const members = $(this).find('[name=members]').val()
    $.post('/api/chats/', {
        'name': name,
        'members': members,
    }, (data) => {
        if (!data.icon) {
            data.icon = '/static/icons/chat.svg'
        }
        renderChat(data);
        $chatCreationForm.hide();
    })
})

function renderChat({ id, name, icon }) {
    $('.chat-list').prepend(`
        <a class="chat" href="/chat/${id}">
            <img src="${icon}">
            <span>${name}</span>
        </a>
    `)
}