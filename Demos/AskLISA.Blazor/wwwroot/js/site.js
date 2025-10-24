// Site-wide JavaScript functions

window.applyTheme = function (theme) {
  if (theme === 'light') {
    document.body.classList.add('light-mode');
  } else {
    document.body.classList.remove('light-mode');
  }
};

window.scrollToBottom = function () {
  const chatContainer = document.querySelector('.chat-container');
  if (chatContainer) {
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }
};
