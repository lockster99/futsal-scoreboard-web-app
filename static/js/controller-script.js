var socket;
var time;
var units = {'s': 1000, 'm': 60*1000, 'h': 60*60*1000};
var pause = false;
// var sirenLoop = false;
$(document).ready(function(){
    var delayTime = document.getElementById('delay-time');
    var delayUnit = document.getElementById('delay-unit');
    var forwardTime = document.getElementById('forwardTime');
    var forwardUnit = document.getElementById('forwardUnit');
    socket = io.connect(`http://${location.host}/remote${document.getElementById("court").textContent}`);

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

    document.getElementById('simpleBtn').addEventListener('click', () => {
        document.getElementById('gameControl').classList.add('hide');
        document.getElementById('simpleBtn').classList.add('selected');
        document.getElementById('fullBtn').classList.remove('selected');
    });

    document.getElementById('fullBtn').addEventListener('click', () => {
        document.getElementById('gameControl').classList.remove('hide');
        document.getElementById('simpleBtn').classList.remove('selected');
        document.getElementById('fullBtn').classList.add('selected');
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

    // document.getElementById('sirenLoop').addEventListener('mousedown', ()=> {
    //     if (!sirenLoop) {
    //         socket.emit('sirenloop');
    //     }
    //     sirenLoop = true;
    // });

    // document.getElementById('sirenLoop').addEventListener('mouseup', ()=> {
    //     sirenLoop = false;
    //     socket.emit('endsirenloop');
    // })

    document.getElementById('siren').addEventListener('click', ()=> {
        socket.emit('siren');
    });

    document.getElementById('pausePlay').addEventListener('click', ()=> {
        var btn = document.getElementById('pausePlay');
        if (!pause) {
            pause = true;
            socket.emit('pause');
            btn.classList.replace('pause-colour', 'play-colour');
            btn.textContent = "Play";
        } else {
            pause = false;
            socket.emit('resume');
            btn.classList.replace('play-colour', 'pause-colour');
            btn.textContent = "Pause";
        }
    });

    document.getElementById('delay').addEventListener('click', ()=> {
        var delayConfirm = confirm("Are you sure you want to delay the current period?");
        if (delayConfirm && delayTime.value != null && delayUnit.value != null) {
            time = parseInt(delayTime.value) * units[delayUnit.value];
            socket.emit('delay', time);
        }
    });

    document.getElementById('bringForward').addEventListener('click', ()=> {
        var bringForwardConfirm = confirm("Are you sure you want to advance/shorten the current period?")
        if (bringForwardConfirm && forwardTime.value != null && forwardUnit.value != null) {
            time = parseInt(forwardTime.value) * units[forwardUnit.value];
            socket.emit('bringforward', time);
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
});