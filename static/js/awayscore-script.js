var socket;
$(document).ready(function(){
    var awayGoals = 0;
    socket = io.connect(`http://${location.host}/awayscoreB`);

    socket.on('connect', () => {
        console.log('connected to socket');
        socket.emit('mymessage', 'Hi server, I am away score client.');
    });

    socket.on('awayscoreupdate', function(score) {
        console.log('received update');
        console.log(score);
        $("#awayGoals").text(score);
        awayGoals = score;
    });

    socket.on('nextfixture', function() {
        $("#awayGoals").text(0);
        awayGoals = 0;
    })
});