var socket;
var time;
var units = {'s': 1000, 'm': 60*1000, 'h': 60*60*1000};
var pause = false;
var timeout = false;
// var sirenLoop = false;
$(document).ready(function(){
    var delayTime = document.getElementById('delay-time');
    var delayUnit = document.getElementById('delay-unit');
    var forwardTime = document.getElementById('forwardTime');
    var forwardUnit = document.getElementById('forwardUnit');
    var homeNameInput = document.getElementById('homeNameInput');
    var awayNameInput = document.getElementById('awayNameInput');
    var homeAbbreviationInput = document.getElementById('homeAbbreviationInput');
    var awayAbbreviationInput = document.getElementById('awayAbbreviationInput');
    var homeColourInput = document.getElementById('homeColourInput');
    var awayColourInput = document.getElementById('awayColourInput');

    socket = io.connect(`http://${location.host}/extendedRemoteB`);

    socket.on('connect', () => {
        console.log('connected to socket');
        socket.emit('mymessage', 'Hi server, I am remote client.');
    });

    socket.on('pausestatus', function(paused) {
        var btn = document.getElementById('pausePlay');
        pause = paused;
        if (pause) {
            btn.classList.replace('pause-colour', 'play-colour');
            btn.textContent = "Play";
        } else {
            btn.classList.replace('play-colour', 'pause-colour');
            btn.textContent = "Pause";
        }
    });

    document.getElementById('gameControlsTab').addEventListener('click', () => {
        document.getElementById('configContainer').classList.add('hide');
        document.getElementById('gameControlContainer').classList.remove('hide');
        document.getElementById('gameControlsTab').classList.add('selected');
        document.getElementById('gameConfigTab').classList.remove('selected');
    });

    document.getElementById('gameConfigTab').addEventListener('click', () => {
        document.getElementById('gameControlContainer').classList.add('hide');
        document.getElementById('configContainer').classList.remove('hide');
        document.getElementById('gameControlsTab').classList.remove('selected');
        document.getElementById('gameConfigTab').classList.add('selected');
    });

    document.getElementById('startPeriod').addEventListener('click', ()=> {
        socket.emit('startperiod');
    });

    document.getElementById('nextGame').addEventListener('click', ()=> {
        var next = confirm("Are you sure you want to move to the next game?");
        if (next) {
            socket.emit('startnextgame');
        }
    });

    document.getElementById('playSiren').addEventListener('click', ()=> {
        socket.emit('siren');
    });

    function pausePlay() {
        var btn = document.getElementById('pausePlay');
        if (!pause) {
            pause = true;
            socket.emit('pause');
            btn.classList.replace('pause-colour', 'play-colour');
            btn.textContent = "Play";
        } else if (pause && timeout) {
            // Handle timeout case and do nothing.
        } else {
            pause = false;
            socket.emit('resume');
            btn.classList.replace('play-colour', 'pause-colour');
            btn.textContent = "Pause";
        }
    }

    document.getElementById('pausePlay').addEventListener('click', ()=> {
        pausePlay();
    });

    document.addEventListener('keyup', event => {
        if (event.code === 'Space') {
            pausePlay();
        }
    });

    // Add
    document.getElementById('homeGoalPlus').addEventListener('click', ()=> {
        socket.emit('score', 'homeGoalIncrement');
    });

    document.getElementById('awayGoalPlus').addEventListener('click', ()=> {
        socket.emit('score', 'awayGoalIncrement');
    });

    document.getElementById('homeFoulPlus').addEventListener('click', ()=> {
        socket.emit('foul', 'homeFoulIncrement');
    });

    document.getElementById('awayFoulPlus').addEventListener('click', ()=> {
        socket.emit('foul', 'awayFoulIncrement');
    });

    // Take
    document.getElementById('homeGoalTake').addEventListener('click', ()=> {
        socket.emit('score', 'homeGoalDecrement');
    });

    document.getElementById('awayGoalTake').addEventListener('click', ()=> {
        socket.emit('score', 'awayGoalDecrement');
    });

    document.getElementById('homeFoulTake').addEventListener('click', ()=> {
        socket.emit('foul', 'homeFoulDecrement');
    });

    document.getElementById('awayFoulTake').addEventListener('click', ()=> {
        socket.emit('foul', 'awayFoulDecrement');
    });

    socket.on('homescoreupdate', function(score) {
        $("#homeGoals").text(score);
    });

    socket.on('awayscoreupdate', function(score) {
        $("#awayGoals").text(score);
    });

    socket.on('homefoulupdate', function(fouls) {
        $('#homeFouls').text(fouls);
    });

    socket.on('awayfoulupdate', function(fouls) {
        $('#awayFouls').text(fouls);
    });

    socket.on('ertimer', function(timer) {
        $("#timer").text(timer);
    });

    socket.on('updateperiod', function(period) {
        $('#period').text(period);
        if (period == "Half time" || period == "Pre game") {
            resetFouls();
        }
    });

    document.getElementById('editHomeNameButton').addEventListener('click', ()=> {
        //var bringForwardConfirm = confirm("Are you sure you want to advance/shorten the current period?")
        if (homeNameInput.value != null) {
            socket.emit('changehomename', homeNameInput.value);
        }
    });

    socket.on('changehomename', function(name) {
        $('.homeName').text(name);
    });

    socket.on('changeawayname', function(name) {
        $('.awayName').text(name);
    });

    socket.on('changehomeabbrev', function(abbrev) {
        $('.homeAbbreviation').text(`(${abbrev})`);
    });

    socket.on('changeawayabbrev', function(abbrev) {
        $('.awayAbbreviation').text(`(${abbrev})`);
    });

    document.getElementById('editAwayNameButton').addEventListener('click', ()=> {
        if (awayNameInput.value != null) {
            socket.emit('changeawayname', awayNameInput.value);
        }
    });

    document.getElementById('editHomeAbbreviationButton').addEventListener('click', ()=> {
        if (homeAbbreviationInput.value != null) {
            socket.emit('changehomeabbrev', homeAbbreviationInput.value);
        }
    });

    document.getElementById('editAwayAbbreviationButton').addEventListener('click', ()=> {
        if (awayAbbreviationInput.value != null) {
            socket.emit('changeawayabbrev', awayAbbreviationInput.value);
        }
    });

    document.getElementById('editHomeColourButton').addEventListener('click', ()=> {
        if (homeColourInput.value != null) {
            socket.emit('changehomecolour', homeColourInput.value);
        }
    });

    document.getElementById('editAwayColourButton').addEventListener('click', ()=> {
        if (awayColourInput.value != null) {
            socket.emit('changeawaycolour', awayColourInput.value);
        }
    });

    document.getElementById('addTime').addEventListener('click', ()=> {
        var delayConfirm = confirm("Are you sure you want to add time to the current period?");
        if (delayConfirm && delayTime.value != null && delayUnit.value != null) {
            time = parseInt(delayTime.value) * units[delayUnit.value];
            socket.emit('delay', time);
        }
    });

    document.getElementById('takeTime').addEventListener('click', ()=> {
        var bringForwardConfirm = confirm("Are you sure you want to advance/shorten the current period?")
        if (bringForwardConfirm && forwardTime.value != null && forwardUnit.value != null) {
            time = parseInt(forwardTime.value) * units[forwardUnit.value];
            socket.emit('bringforward', time);
        }
    });
    
    document.getElementById('restartGame').addEventListener('click', ()=> {
        var restartConfirm = confirm("Are you sure you want to restart the game? The timer, scores and fouls will be reset.")
        if (restartConfirm) {
            socket.emit('restartgame');
        }
    });

    document.getElementById('restartPeriod').addEventListener('click', ()=> {
        var restartConfirm = confirm("Are you sure you want to restart the current period? The timer will be reset.")
        if (restartConfirm) {
            socket.emit('restartperiod');
        }
    });

    document.getElementById('previousPeriod').addEventListener('click', ()=> {
        var restartConfirm = confirm("Are you sure you want to move to the previous period? The period will be changed and the timer will be reset.")
        if (restartConfirm) {
            socket.emit('previousperiod');
        }
    });

    document.getElementById('nextPeriod').addEventListener('click', ()=> {
        var restartConfirm = confirm("Are you sure you want to move to the next period? The period will be changed and the timer will be reset.")
        if (restartConfirm) {
            socket.emit('nextperiod');
        }
    });

    document.getElementById('previousGame').addEventListener('click', ()=> {
        var next = confirm("Are you sure you want to move to the previous game?");
        if (next) {
            socket.emit('startpreviousgame');
        }
    });

    document.getElementById('nextGame').addEventListener('click', ()=> {
        var next = confirm("Are you sure you want to move to the next game?");
        if (next) {
            socket.emit('startnextgame');
        }
    });

    document.getElementById('timeout').addEventListener('click', ()=> {
        if (timeout) {
            socket.emit('canceltimeout');
            timeout = false;
            document.getElementById('timeout').textContent = "Timeout (1:00)";
            document.getElementById('timeout-header').classList.add('hide');
            document.getElementById('period').classList.remove('hide');
        } else {
            socket.emit('timeout');
            timeout = true;
            document.getElementById('timeout').textContent = "Cancel Timeout";
            document.getElementById('period').classList.add('hide');
            document.getElementById('timeout-header').classList.remove('hide');
        }
    });

    socket.on('timeoutover', function() {
        timeout = false;
        document.getElementById('timeout').textContent = "Timeout (1:00)";
        document.getElementById('timeout-header').classList.add('hide');
        document.getElementById('period').classList.remove('hide');
    });


    const homeLogoForm = document.getElementById('homeLogoForm');
    const homeFileInput = document.getElementById('homeLogoInput');

    homeLogoForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData();
        formData.append('homeLogo', homeFileInput.files[0]); // 'uploadedFile' is the name expected by the server

        try {
            const response = await fetch('/upload-home-logo', { // Replace with your server's upload endpoint
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                console.log('File uploaded successfully:', result);
            } else {
                console.error('File upload failed:', response.statusText);
            }
        } catch (error) {
            console.error('Error during file upload:', error);
        }
    });

    const awayLogoForm = document.getElementById('awayLogoForm');
    const awayFileInput = document.getElementById('awayLogoInput');

    awayLogoForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData();
        formData.append('awayLogo', awayFileInput.files[0]); // 'uploadedFile' is the name expected by the server

        try {
            const response = await fetch('/upload-away-logo', { // Replace with your server's upload endpoint
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                console.log('File uploaded successfully:', result);
            } else {
                console.error('File upload failed:', response.statusText);
            }
        } catch (error) {
            console.error('Error during file upload:', error);
        }
    });
});