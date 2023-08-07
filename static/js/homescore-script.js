var socket;
$(document).ready(function(){
    var homeGoals = 0;
    socket = io.connect(`http://${location.host}/homescoreB`);

    socket.on('connect', () => {
        console.log('connected to socket');
        socket.emit('mymessage', 'Hi server, I am home score client.');
    });

    socket.on('homescoreupdate', function(score) {
        console.log('received update');
        console.log(score);
        $("#homeGoals").text(score);
        homeGoals = score;
    });

    socket.on('nextfixture', function() {
        $("#homeGoals").text(0);
        homeGoals = 0;
    })
});