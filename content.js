chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'seek') {
      const videoPlayer = document.querySelector('video');
      if (videoPlayer) {
        videoPlayer.currentTime = request.time;
        videoPlayer.play();
      }
    }
  });
  