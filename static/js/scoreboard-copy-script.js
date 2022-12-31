var socket = io;
$(document).ready(function(){
    var currentFixture;
    var periodConfiguration;
    var currentHomeLogo = document.getElementById('defaultHomeLogo');
    var currentAwayLogo = document.getElementById('defaultAwayLogo');
    var siren = new Audio("/static/audio/siren.mp3");
    socket = io.connect(`http://${location.host}/court${document.getElementById("court").textContent}copy`);
    socket.on('connect', () => {
        console.log('connected to socket');
        socket.emit('mymessage', 'Hi server, I am scoreboard display copy client.');
    });

    function showCurrentLogos() {
        if (currentFixture.homeLogo != null) {
            currentHomeLogo.classList.add('display-none');
            currentHomeLogo = document.getElementById(`homeLogo${currentFixture.homeId}`)
            currentHomeLogo.classList.remove('display-none');
        } else if (currentFixture.homeLogo == null && currentHomeLogo.id != "defaultHomeLogo") {
            currentHomeLogo.classList.add('display-none')
            currentHomeLogo = document.getElementById('defaultHomeLogo');
            currentHomeLogo.classList.remove('display-none');
        }
        if (currentFixture.awayLogo != null) {
            currentAwayLogo.classList.add('display-none');
            currentAwayLogo = document.getElementById(`awayLogo${currentFixture.awayId}`)
            currentAwayLogo.classList.remove('display-none');
        } else if (currentFixture.awayLogo == null && currentAwayLogo.id != "defaultAwayLogo") {
            currentAwayLogo.classList.add('display-none')
            currentAwayLogo = document.getElementById('defaultAwayLogo');
            currentAwayLogo.classList.remove('display-none');
        }
    }

    function resetFouls() {
        currentFixture.homeFouls = 0;
        $("#homeFouls").text(0);
        currentFixture.awayFouls = 0;
        $("#awayFouls").text(0);
    }

    function showPenaltyShootout() {
        document.getElementById("goalsContainer").classList.add("display-none");
        document.getElementById("penaltiesContainer").classList.remove("display-none");
        document.getElementById("foulsContainer").classList.add("display-none");
        document.getElementById("FTScoreContainer").classList.remove("display-none");
        $("#homeFTScore").text(currentFixture.homeGoals);
        $("#awayFTScore").text(currentFixture.awayGoals);
    }

    function cleanUpPenalties() {
        $("#homeNumberPenalties").text(0);
        $("#awayNumberPenalties").text(0);
        document.getElementById("penaltiesContainer").classList.add("display-none");
        document.getElementById("goalsContainer").classList.remove("display-none");
        var penaltyDots = document.getElementsByClassName("penalty");
        for (var i=0; i<penaltyDots.length; i++) {
            penaltyDots.item(i).classList.replace("missed", "untaken");
            penaltyDots.item(i).classList.replace("scored", "untaken");
        }
        document.getElementById("homePenalty6").classList.add('display-none');
        document.getElementById("awayPenalty6").classList.add('display-none');
        document.getElementById("FTScoreContainer").classList.add("display-none");
        document.getElementById("foulsContainer").classList.remove("display-none");
    }

    socket.on('firstfixture', function(firstFixture) {
        currentFixture = firstFixture;
        periodConfiguration = currentFixture.periodConfiguration;
        $("#period").text(periodConfiguration.periods[0].displayName);
        $("#homeName").text(currentFixture.homeName);
        $("#awayName").text(currentFixture.awayName);
        $("#homeNamePenalties").text(currentFixture.homeName);
        $("#awayNamePenalties").text(currentFixture.awayName);
        $("#homeGoals").text(currentFixture.homeGoals);
        $("#awayGoals").text(currentFixture.awayGoals);
        $("#homeFouls").text(currentFixture.homeFouls);
        $("#awayFouls").text(currentFixture.awayFouls);
        showCurrentLogos();
    });

    socket.on('nextfixture', function(newFixture) {
        currentFixture = newFixture;
        periodConfiguration = currentFixture.periodConfiguration;
        $("#period").text(periodConfiguration.periods[0].displayName);
        $("#homeName").text(currentFixture.homeName);
        $("#awayName").text(currentFixture.awayName);
        $("#homeNamePenalties").text(currentFixture.homeName);
        $("#awayNamePenalties").text(currentFixture.awayName);
        $("#homeGoals").text(currentFixture.homeGoals);
        $("#awayGoals").text(currentFixture.awayGoals);
        resetFouls();
        cleanUpPenalties();
        showCurrentLogos();
    });

    socket.on('playsiren', ()=> {
        siren.play();
    })

    socket.on('copytimer', function(timer) {
        $("#timer").text(timer);
    });

    socket.on('homescoreupdate', function(goals) {
        $('#homeGoals').text(goals);
    });

    socket.on('awayscoreupdate', function(goals) {
        $('#awayGoals').text(goals);
    });

    socket.on('homefoulupdate', function(fouls) {
        $('#homeFouls').text(fouls);
    });

    socket.on('awayfoulupdate', function(fouls) {
        $('#awayFouls').text(fouls);
    });

    socket.on('updateperiod', function(period) {
        $('#period').text(period);
        if (period == "Half time" || period == "Pre game") {
            resetFouls();
        }
    });

    // socket.on('wentpenalties', function() {
    //     currentFixture.wentPenalties = true;
    //     var penaltyLayouts = document.getElementsByClassName('penalties')
    //     for (var i=0; i<penaltyLayouts.length; i++) {
    //         penaltyLayouts.item(i).classList.replace("missed", "untaken");
    //         penaltyLayouts.item(i).classList.replace("scored", "untaken");
    //     }
    //     document.getElementById("normalTicker").classList.add("display-none");
    //     document.getElementById("penaltyTicker").classList.remove("display-none");
    // });

    // socket.on('homepenaltyupdate', function(penalties) {
    //     setPenalties(penalties, "home");
    //     currentFixture.homePenalties = penalties;
    //     $("#homeNumberPenalties").text(penalties.reduce((a, b) => a + b, 0));
    // });

    // socket.on('awaypenaltyupdate', function(penalties) {
    //     setPenalties(penalties, "away");
    //     currentFixture.awayPenalties = penalties;
    //     $("#awayNumberPenalties").text(penalties.reduce((a, b) => a + b, 0));
    // });

    // socket.on('suddendeath', function() {
    //     var suddenDeaths = document.getElementsByClassName("sudden-death");
    //     for (var i=0; i<suddenDeaths.length; i++) {
    //         suddenDeaths.item(i).classList.remove("display-none");
    //         suddenDeaths.item(i).classList.replace("missed", "untaken");
    //         suddenDeaths.item(i).classList.replace("scored", "untaken");
    //     }
    //     wentSuddenDeath = true;
    // });
});