var socket;
$(document).ready(function(){
    //let court = document.getElementById("court-hidden").textContent;

    //console.log(court);
    socket = io.connect(`http://${location.host}/alonetimerB`);


    socket.on('connect', () => {
        console.log('connected to socket');
        socket.emit('mymessage', 'Hi server, I am alone timer client.');
    });

    socket.on('alonetimer', function(timer) {
        $("#time").text(timer);
    });

    socket.on('showtimer', () => {
        var timer = document.getElementById("timer");
        timer.classList.remove("display-none");
    })

    socket.on('hidetimer', () => {
        var timer = document.getElementById("timer");
        timer.classList.add("display-none");
    })

    socket.on('nextfixture', function() {
        $("#time").text("20:00");
    });
});
