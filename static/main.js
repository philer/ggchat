addEventListener("DOMContentLoaded", function() {
  "use strict";

  const byId = document.getElementById.bind(document);

  const chat = byId("chat");
  const chatlog = chat.getElementsByClassName("chat-log")[0];
  const form = byId("message-form");
  const messageInput = byId("message-input");
  const usernameInput = byId("username-input");
  const status = byId("chat-status");

  const defaultPreventer = fn => function(evt) {
    evt.preventDefault();
    return fn();
  };

  function appendChat(html) {
    chatlog.insertAdjacentHTML("beforeend", html);
    scrollDown();
  }

  function scrollDown() {
    chatlog.scrollTo({top: chatlog.scrollHeight + 100, behavior: 'smooth'});
  }

  function adjustInputHeight() {
    messageInput.style.minHeight = 'inherit';
    messageInput.style.minHeight = messageInput.scrollHeight + 'px';
  }

  const socket = io.connect('http://' + document.domain + ':' + location.port);

  socket.once('connect', function() {
    const username = usernameInput.value.trim();
    socket.emit("startup", username, appendChat);
  });
  socket.on('message', appendChat);
  socket.on('connect', function() {
    status.innerHTML = "connected";
  });
  socket.on('disconnect', function() {
    status.innerHTML = "disconnected";
  });
  socket.on('reconnecting', function() {
    status.innerHTML = "reconnecting…";
  });

  function send() {
    const content = messageInput.value.trim();
    const author = usernameInput.value.trim();
    if (content) {
      if (author) {
        socket.emit("msg", {author, content}, appendChat);
        messageInput.value = "";
        adjustInputHeight();
      } else {
        alert("Please enter a user name.");
      }
    }
  }

  form.addEventListener("submit", defaultPreventer(send));

  messageInput.addEventListener("keypress", function submitOnEnter(evt) {
    if (evt.key == "Enter"
        && !(evt.getModifierState("Shift") || evt.getModifierState("Control"))
        ) {
      defaultPreventer(send)(evt);
    }
  });

  messageInput.addEventListener("input", adjustInputHeight);
  adjustInputHeight();
  scrollDown();
});
