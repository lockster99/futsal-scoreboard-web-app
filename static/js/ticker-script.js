var socket;
$(document).ready(function(){
    let court = document.getElementById("court-hidden").textContent;

    // function set_heights(){
    //     var divHeight = $('.banner').height(); 
    //     $('#timer').css('min-height', divHeight+'px');
    // }

    // set_heights();

    // $('.banner').bind('resize', function(){
    //     set_heights();
    // });

    console.log(court);
    var current = 0;
    var fixtureQueue;
    var currentFixture;
    var wentSuddenDeath = false;
    socket = io.connect(`http://${location.host}/court${court}ticker`);


    socket.on('connect', () => {
        console.log('connected to socket');
        socket.emit('mymessage', 'Hi server, I am score ticker client.');
    });

    socket.on('fixturequeue', function(fixturequeue) {
        fixtureQueue = fixturequeue.fixtures;
        currentFixture = fixturequeue.fixtures[0];
        $(".homeTeam").text(currentFixture.homeAbbrev);
        $(".awayTeam").text(currentFixture.awayAbbrev);
        setTeamColour('home', currentFixture.homeColour);
        setTeamColour('away', currentFixture.awayColour);
        $("#homeGoals").text(currentFixture.homeGoals);
        $("#awayGoals").text(currentFixture.awayGoals);
    });

    function setTeamColour(team, colour) {
        if (colour == "black") {
            $(`.${team}Colour`).css('background-color', '#222222');
        } else {
            $(`.${team}Colour`).css('background-color', colour);
        }
    }

    function setPenalties(penalties, team) {
        if (wentSuddenDeath) {
            var penaltyDot = document.getElementById(`${team}Penalty6`);
            if (penalties[penalties.length-1] == 0) {
                penaltyDot.classList.replace("untaken", "missed");
                penaltyDot.classList.replace("scored", "missed");
            } else if (penalties[penalties.length-1] == 1) {
                penaltyDot.classList.replace("untaken", "scored");
                penaltyDot.classList.replace("missed", "scored");
            }
        } else {
            for (var i=0; i<6; i++) {
                var penaltyDot = document.getElementById(`${team}Penalty${i+1}`);
                if (i >= penalties.length) {
                    penaltyDot.classList.replace("missed", "untaken");
                    penaltyDot.classList.replace("scored", "untaken");
                } else if (penalties[i] == 0) {
                    penaltyDot.classList.replace("untaken", "missed");
                    penaltyDot.classList.replace("scored", "missed");
                } else if (penalties[i] == 1) {
                    penaltyDot.classList.replace("untaken", "scored");
                    penaltyDot.classList.replace("missed", "scored");
                }
            }
        }
    }

    socket.on('homescoreupdate', function(score) {
        $("#homeGoals").text(score);
        currentFixture.homeGoals = score;
    });

    socket.on('awayscoreupdate', function(score) {
        $("#awayGoals").text(score);
        currentFixture.awayGoals = score;
    });

    socket.on('wentpenalties', function() {
        currentFixture.wentPenalties = true;
        var penaltyLayouts = document.getElementsByClassName('penalties')
        for (var i=0; i<penaltyLayouts.length; i++) {
            penaltyLayouts.item(i).classList.replace("missed", "untaken");
            penaltyLayouts.item(i).classList.replace("scored", "untaken");
        }
        document.getElementById("normalTicker").classList.add("display-none");
        document.getElementById("penaltyTicker").classList.remove("display-none");
    });

    socket.on('homepenaltyupdate', function(penalties) {
        setPenalties(penalties, "home");
        currentFixture.homePenalties = penalties;
        $("#homeNumberPenalties").text(penalties.reduce((a, b) => a + b, 0));
    });

    socket.on('awaypenaltyupdate', function(penalties) {
        setPenalties(penalties, "away");
        currentFixture.awayPenalties = penalties;
        $("#awayNumberPenalties").text(penalties.reduce((a, b) => a + b, 0));
    });

    socket.on('suddendeath', function() {
        var suddenDeaths = document.getElementsByClassName("sudden-death");
        for (var i=0; i<suddenDeaths.length; i++) {
            suddenDeaths.item(i).classList.remove("display-none");
            suddenDeaths.item(i).classList.replace("missed", "untaken");
            suddenDeaths.item(i).classList.replace("scored", "untaken");
        }
        wentSuddenDeath = true;
    });

    socket.on('tickertimer', function(timer) {
        $("#time").text(timer);
    });

    socket.on('showtimer', () => {
        var timer = document.getElementById("timer")
        timer.classList.remove("display-none");
    })

    socket.on('nextfixture', function() {
        newFixture();
    });

    function resetPenalties() {
        var penaltyDots = document.getElementsByClassName('penalty');
        for (var i=0; i<penaltyDots.length; i++) {
            penaltyDots.item(i).classList.replace('missed', 'untaken');
            penaltyDots.item(i).classList.replace('scored', 'untaken');
        }
        document.getElementById("homePenalty6").classList.add("display-none");
        document.getElementById("awayPenalty6").classList.add("display-none");
        $('#homeNumberPenalties').text('0');
        $('#awayNumberPenalties').text('0');
        document.getElementById("penaltyTicker").classList.add("display-none");
        document.getElementById("normalTicker").classList.remove("display-none");
        wentSuddenDeath = false;
    }

    function newFixture() {
        if (currentFixture.wentPenalties) {
            resetPenalties();
        }
        fixtureQueue[current] = currentFixture;
        current++;
        currentFixture = fixtureQueue[current];
        $(".homeTeam").text(currentFixture.homeAbbrev);
        $(".awayTeam").text(currentFixture.awayAbbrev);
        setTeamColour('home', currentFixture.homeColour);
        setTeamColour('away', currentFixture.awayColour);
        $("#homeGoals").text(currentFixture.homeGoals);
        $("#awayGoals").text(currentFixture.awayGoals);
        $("#time").text("18:00");
    }
});
