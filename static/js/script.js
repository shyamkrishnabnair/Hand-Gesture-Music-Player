document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const gestureList = document.getElementById('gestureList');

    startBtn.addEventListener('click', () => {
        fetch('/start_recognition', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.status);
                startBtn.disabled = true;
                stopBtn.disabled = false;
            });
    });

    stopBtn.addEventListener('click', () => {
        fetch('/stop_recognition', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.status);
                startBtn.disabled = false;
                stopBayes.disabled = true;
                updateGestureLog(data.gestures);
            });
    });

    function updateGestureLog(gestures) {
        gestureList.innerHTML = '';
        gestures.forEach(gesture => {
            const li = document.createElement('li');
            li.textContent = `Fingers: ${gesture}`;
            gestureList.appendChild(li);
        });
    }

    // Periodically fetch gesture log while running
    setInterval(() => {
        if (!startBtn.disabled) return; // Only fetch if recognition is running
        fetch('/gesture_log')
            .then(response => response.json())
            .then(data => updateGestureLog(data.gestures));
    }, 1000);
});