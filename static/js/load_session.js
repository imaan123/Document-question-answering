async function sendMessage() {
      let msg = document.getElementById('message').value.trim();
      let box = document.getElementById('chat-list');
      box.innerHTML += `<li class="out">
                                <div class="chat-img">
                                    <img alt="Avtar" src=${userAvatar}>
                                </div>
                                <div class="chat-body">
                                    <div class="chat-message">
                                        <h5>You</h5>
                                        <p>${msg}</p>
                                    </div>
                                </div>
                            </li>`;
      document.getElementById('message').value = '';

      // 2. Add "Bot is typing..." placeholder with a unique ID for later replacement
      const loadingId = `loading-${Date.now()}`;
      box.innerHTML += `<li class="in">
                                <div class="chat-img">
                                    <img alt="Avtar" src=${botAvatar}>
                                </div>
                                <div class="chat-body">
                                    <div class="chat-message">
                                        <h5>Bot</h5>
                                        <p id="${loadingId}"><i>Typing...</i></p>
                                    </div>
                                </div>
                            </li>`
      // Scroll to bottom
      box.scrollTop = box.scrollHeight;

      let res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: msg})
      });
      let data = await res.json();
      let loadingElem = document.getElementById(loadingId);
      if (loadingElem) {
      loadingElem.innerHTML = `${data.response}`;}
      else{
        box.innerHTML += `<p>${data.response}</p>`;
      }
      box.scrollTop = box.scrollHeight;
    }

    async function resetSession() {
      await fetch('/reset', { method: 'POST' });
      document.getElementById('chat-list').innerHTML = '<p><i>Session reset.</i></p>';
    }