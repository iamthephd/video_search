document.getElementById('submit').addEventListener('click', function() {
    const prompt = document.getElementById('prompt').value;
  
    // Replace with your server's URL
    const url = 'http://127.0.0.1:5000/get-timestamps';
  
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ prompt: prompt, video_url: window.location.href })
    })
    .then(response => response.json())
    .then(data => {
      const timestampsList = document.getElementById('timestamps');
      timestampsList.innerHTML = '';
  
      data.timestamps.forEach(ts => {
        const listItem = document.createElement('li');
        listItem.textContent = ts;
        listItem.addEventListener('click', () => {
          chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, { action: 'seek', time: ts });
          });
        });
        timestampsList.appendChild(listItem);
      });
    })
    .catch(error => {
      console.error('Error:', error);
    });
  });
  