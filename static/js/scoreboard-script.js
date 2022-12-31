const second = 1000;
const minute = 60*second;
var socket = io;
$(document).ready(function(){
    // Initialise variables
    var fixtureQueue;
    var periodConfiguration;
    var current = 0;
    var currentFixture;
    var period = 0;
    var paused = false;
    var currentPeriod;
    var targetTime;
    var stop = false;
    var loaded = false;
    var siren = new Audio("/static/audio/siren.mp3");
    //var sirenLoop = new Audio("/static/audio/siren-loop.mp3");
    var mins, secs, minsTxt, secsTxt;
    var previousTimeStamp;
    var currentHomeLogo = document.getElementById('defaultHomeLogo');
    var currentAwayLogo = document.getElementById('defaultAwayLogo');
    var suddenDeathApplied = false;
    var timerString;
    var periodManualStarted = false;
    var prevEndTime = 0;
    var prevTime = -1;
    var tickerConnected = false;
    var copyConnected = false;
    var time;
    var finished = false;

    //connect to the socket server.
    socket = io.connect(`http://${location.host}/court${document.getElementById("court").textContent}`);

    socket.on('connect', () => {
        console.log('connected to socket');
        socket.emit('mymessage', 'Hi server, I am scoreboard client.');
    });

    // Function to load page based on fixture queue and current fixture.
    socket.on('fixturequeue', function(fixturequeue) {
        fixtureQueue = fixturequeue.fixtures;
        current = fixturequeue.current;
        currentFixture = fixturequeue.fixtures[current];
        periodConfiguration = currentFixture.periodConfiguration;
        period = currentFixture.currentPeriod;
        currentPeriod = periodConfiguration.periods[period];
        $("#period").text(currentPeriod.displayName);
        $("#homeName").text(currentFixture.homeName);
        $("#awayName").text(currentFixture.awayName);
        $("#homeNamePenalties").text(currentFixture.homeName);
        $("#awayNamePenalties").text(currentFixture.awayName);
        $("#homeGoals").text(currentFixture.homeGoals);
        $("#awayGoals").text(currentFixture.awayGoals);
        $("#homeFouls").text(currentFixture.homeFouls);
        $("#awayFouls").text(currentFixture.awayFouls);
        updateShownContent();
        targetTime = new Date(currentFixture.gameTime).getTime();
        loaded = true;
    });

    setTimeout(checkLoaded);

    function checkLoaded() {
        if (loaded) {
            requestAnimationFrame(timer);
        } else {
            setTimeout(checkLoaded, 100);
        }
    }

    function hasPenaltiesFinished() {
        if (currentFixture.homePenalties.reduce((a, b) => a + b, 0) > 
                currentFixture.awayPenalties.reduce((a, b) => a + b, 0) + currentFixture.awayPenaltiesLeft) {
            return true;
        } else if (currentFixture.awayPenalties.reduce((a, b) => a + b, 0) > 
                currentFixture.homePenalties.reduce((a, b) => a + b, 0) + currentFixture.homePenaltiesLeft) {
            return true;
        }
        if (currentFixture.homePenalties.reduce((a, b) => a + b, 0) == currentFixture.awayPenalties.reduce((a, b) => a + b, 0) && 
                currentFixture.homePenaltiesLeft === 0 && currentFixture.awayPenaltiesLeft === 0 && !suddenDeathApplied) {
            var suddenDeaths = document.getElementsByClassName("sudden-death");
            for (var i=0; i<suddenDeaths.length; i++) {
                suddenDeaths.item(i).classList.remove("display-none");
                suddenDeaths.item(i).classList.replace("missed", "untaken");
                suddenDeaths.item(i).classList.replace("scored", "untaken");
            }
            currentFixture.homePenaltiesLeft = 1;
            currentFixture.awayPenaltiesLeft = 1;
            socket.emit('suddendeath');
            suddenDeathApplied = true;
        }
        return false;
    }


    function updateShownContent() {
        if (!currentFixture.showTeams) {
            document.getElementById("goalsContainer").classList.add("display-none");
            document.getElementById("foulsContainer").classList.add("display-none");
        } else if (currentFixture.showTeams && !currentFixture.showScore) {
            document.getElementById("goalsContainer").classList.remove("display-none");
            document.getElementById("foulsContainer").classList.remove("display-none");
            document.getElementById("homeGoals").classList.add("invisible");
            document.getElementById("awayGoals").classList.add("invisible");
        } else {
            document.getElementById("goalsContainer").classList.remove("display-none");
            document.getElementById("foulsContainer").classList.remove("display-none");
            document.getElementById("homeGoals").classList.remove("invisible");
            document.getElementById("awayGoals").classList.remove("invisible");
        }
        showCurrentLogos();
    }


    function showCurrentLogos() {
        if (currentFixture.homeLogo != null && currentFixture.showTeams) {
            currentHomeLogo.classList.add('display-none');
            currentHomeLogo = document.getElementById(`homeLogo${currentFixture.homeId}`)
            currentHomeLogo.classList.remove('display-none');
        } else if (currentFixture.homeLogo == null && currentHomeLogo.id != "defaultHomeLogo") {
            currentHomeLogo.classList.add('display-none')
            currentHomeLogo = document.getElementById('defaultHomeLogo');
            currentHomeLogo.classList.remove('display-none');
        }
        if (currentFixture.awayLogo != null && currentFixture.showTeams) {
            currentAwayLogo.classList.add('display-none');
            currentAwayLogo = document.getElementById(`awayLogo${currentFixture.awayId}`)
            currentAwayLogo.classList.remove('display-none');
        } else if (currentFixture.awayLogo === null && currentAwayLogo.id != "defaultAwayLogo") {
            currentAwayLogo.classList.add('display-none')
            currentAwayLogo = document.getElementById('defaultAwayLogo');
            currentAwayLogo.classList.remove('display-none');
        }
    }


    function timer(timeStamp) {
        if(Date.now() >= targetTime) {

            if (currentPeriod.endSiren) {
                socket.emit('playsiren');
                siren.play();
            }
            if (currentPeriod.displayName === "Full time") {
                if (current+1 < fixtureQueue.length) {
                    newFixture();
                } else {
                    stop = true;
                    if (!finished) {
                        socket.emit('allfinished');
                    }
                    finished = true;
                }
            } else {
                if (currentPeriod.showTimeTicker) {
                    if (currentPeriod.countUp) {
                        updateTimer((prevEndTime+currentPeriod.periodLength)/1000);
                    } else {
                        updateTimer(0);
                    }
                    prevEndTime = prevEndTime + currentPeriod.periodLength;
                }
                if ((currentPeriod.decidesExtraTime || currentPeriod.decidesPenalties) && 
                        currentFixture.homeGoals != currentFixture.awayGoals) {
                    period = periodConfiguration.periods.length - 2;
                    updatePeriod();
                } else if (currentPeriod.decidesPenalties && currentFixture.homeGoals === currentFixture.awayGoals) {
                    // Move to penalties
                    currentFixture.wentPenalties = true;
                    socket.emit('wentpenalties');
                    paused = true;
                    updatePeriod();
                    showPenaltyShootout();
                } else {
                    updatePeriod();
                }
            } 
        }  
        if (!stop) {
            if (!paused) {
                time = (prevEndTime + currentPeriod.periodLength - (targetTime - Date.now()))/1000;   // for display of time
                if (!currentPeriod.countUp) {
                    time = (targetTime - Date.now())/1000;   // for display of time till stop
                }
            } else {
                if (hasPenaltiesFinished()) {
                    // End penalties
                    paused = false;
                    updatePeriod();
                }
                targetTime = targetTime + (timeStamp-previousTimeStamp);
            }
            previousTimeStamp = timeStamp;
            if (!paused && currentPeriod.showTime) {
                updateTimer(time);
            }
            requestAnimationFrame(timer); // continue animation until stop 
        }
    }


    function startPeriod() {
        if (!currentPeriod.autoStart & !periodManualStarted) {
            frameNumber = 0;
            stop = false;
            paused = false;
            socket.emit('pausestatus', paused);
            targetTime = Date.now() + currentPeriod.periodLength;
            periodManualStarted = true;
            requestAnimationFrame(timer);
        }
    }

    socket.on('startperiod', ()=> {
        startPeriod();
    });

    socket.on('startnextgame', ()=> {
        newFixture();
        stop = false;
        requestAnimationFrame(timer);
    });

    socket.on('homegoaladd', () => {
        handleHomeGoalAdd();
    });

    socket.on('homegoaltake', () => {
        handleHomeGoalTake();
    });

    socket.on('homescoreupdate', function(score) {
        updateHomeGoals(score - currentFixture.homeGoals);
    });

    socket.on('awaygoaladd', () => {
        handleAwayGoalAdd();
    })

    socket.on('awaygoaltake', () => {
        handleAwayGoalTake();
    })

    socket.on('awayscoreupdate', function(score) {
        updateAwayGoals(score - currentFixture.awayGoals);
    });

    socket.on('homefouladd', () => {
        handleHomeFoulAdd();
    });

    socket.on('homefoultake', () => {
        handleHomeFoulTake();
    });

    socket.on('homefoulupdate', function(fouls) {
        updateHomeFouls(fouls - currentFixture.homeFouls);
    });

    socket.on('awayfouladd', () => {
        handleAwayFoulAdd();
    })

    socket.on('awayfoultake', () => {
        handleAwayFoulTake();
    })

    socket.on('awayfoulupdate', function(fouls) {
        updateAwayFouls(fouls - currentFixture.awayFouls);
    });

    socket.on('pause', ()=> {
        paused = true;
    });

    socket.on('resume', ()=> {
        paused = false;
    });

    socket.on('delay', (time)=> {
        targetTime = targetTime + time;
    });

    socket.on('bringforward', (time)=> {
        targetTime = targetTime - time;
    });

    socket.on('firstcopyfixture', ()=> {
        socket.emit('firstfixture', currentFixture);
    });

    socket.on('getpausestatus', ()=> {
        socket.emit('pausestatus', paused);
    });

    socket.on('tickerconnected', ()=> {
        tickerConnected = true;
    });

    socket.on('copyconnected', ()=> {
        copyConnected = true;
    });

    socket.on('siren', ()=> {
        siren.play();
    });

    socket.on('sirenloop', ()=> {
        if (!sirenLoop.loop) {
            sirenLoop.loop = true;
            sirenLoop.play();
        }
    });

    socket.on('endsirenloop', ()=> {
        sirenLoop.loop = false;
    });

    function roundDecimal(number, decimalPlaces) {
        return Number(Math.round(number + "e" + decimalPlaces) + "e-" + decimalPlaces);
    }

    function updateTimer(time) {
        mins = (Math.max(0, Math.floor(time/60)));
        secs = Math.ceil((time % 60));
        if (currentPeriod.countUp) {
            secs = Math.floor((time % 60));
        }
        if (secs === 60) {
            mins++;
            secs = 0;
        }
        secs = Math.max(0, secs);
        minsTxt = mins.toString().padStart(2, '0');
        secsTxt = secs.toString().padStart(2, '0');
        timerString = `${minsTxt}:${secsTxt}`;
        $("#timer").text(timerString);
        if ((60*mins+secs) != prevTime) {
            prevTime = 60*mins + secs;
            if (currentPeriod.showTimeTicker && tickerConnected) {
                socket.emit('tickertimer', timerString);
            }
            if (copyConnected) {
                socket.emit('copytimer', timerString);
            }
        }
    }

    function updatePeriod() {
        period++;
        currentPeriod = periodConfiguration.periods[period];
        targetTime = targetTime + currentPeriod.periodLength;
        if (!currentPeriod.autoStart) {
            firstUpdate = true;
            if (currentPeriod.countUp) {
                updateTimer(prevEndTime/1000);
            } else {
                updateTimer(currentPeriod.periodLength/1000);
            }
            stop = true;
        }
        $("#period").text(currentPeriod.displayName);
        if (currentPeriod.resetFouls) {
            resetFouls();
        }
        firstUpdate = true;
        socket.emit('updateperiod', currentPeriod);
        if (currentPeriod.showTimeTicker) {
            socket.emit('showtimeticker');
        }
        periodManualStarted = false;
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
        $("#homeNumberPenalties").text('0');
        $("#awayNumberPenalties").text('0');
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

    function newFixture() {
        if (currentFixture.wentPenalties) {
            cleanUpPenalties();
        }
        fixtureQueue[current] = currentFixture;
        if (current+1 < fixtureQueue.length) {
            current++;
            currentFixture = fixtureQueue[current];
            periodConfiguration = currentFixture.periodConfiguration;
            period = 0;
            currentPeriod = periodConfiguration.periods[period];
            targetTime = getTargetTime();
            prevEndTime = 0;
            resetFouls();
            $("#homeName").text(currentFixture.homeName);
            $("#awayName").text(currentFixture.awayName);
            $("#homeNamePenalties").text(currentFixture.homeName);
            $("#awayNamePenalties").text(currentFixture.awayName);
            $("#homeGoals").text(currentFixture.homeGoals);
            $("#awayGoals").text(currentFixture.awayGoals);
            $("#period").text(currentPeriod.displayName);
            socket.emit('newfixture', currentFixture);
            updateShownContent();
            periodManualStarted = false;
        }
    }

    function getTargetTime() {
        return Math.max(new Date(currentFixture.gameTime).getTime(), Date.now() + periodConfiguration.minimumPregame);
    }

    function resetFouls() {
        currentFixture.homeFouls = 0;
        $("#homeFouls").text(0);
        socket.emit('foul', {'homeFouls': 0});
        currentFixture.awayFouls = 0;
        $("#awayFouls").text(0);
        socket.emit('foul', {'awayFouls': 0});
    }

    document.getElementById('homeLogo').addEventListener('click', ()=> {
        interacted = true;
    });

    function updateHomeGoals(change) {
        currentFixture.homeGoals = currentFixture.homeGoals + change;
        $("#homeGoals").text(currentFixture.homeGoals);
        socket.emit('score', {'homeGoals': currentFixture.homeGoals});
    }

    function updateHomeFouls(change) {
        currentFixture.homeFouls = currentFixture.homeFouls + change;
        $("#homeFouls").text(currentFixture.homeFouls);
        socket.emit('foul', {'homeFouls': currentFixture.homeFouls});
    }

    function updateHomePenalties(outcome) {
        if (outcome === -1) {
            document.getElementById(`homePenalty${Math.min(6, currentFixture.homePenalties.length)}`).classList.remove("scored", "missed");
            document.getElementById(`homePenalty${Math.min(6, currentFixture.homePenalties.length)}`).classList.add("untaken");
            currentFixture.homePenalties.pop();
            currentFixture.homePenaltiesLeft++;
            socket.emit('penalty', {"homePenalties": currentFixture.homePenalties, "homePenaltiesLeft": currentFixture.homePenaltiesLeft});
        } else if (currentFixture.homePenaltiesLeft > 0) {
            currentFixture.homePenalties.push(outcome);
            document.getElementById(`homePenalty${Math.min(6, currentFixture.homePenalties.length)}`).classList.remove("untaken");
            if (outcome === 0) {
                document.getElementById(`homePenalty${Math.min(6, currentFixture.homePenalties.length)}`).classList.add("missed");
            } else {
                document.getElementById(`homePenalty${Math.min(6, currentFixture.homePenalties.length)}`).classList.add("scored");
            }
            currentFixture.homePenaltiesLeft--;
            socket.emit('penalty', {"homePenalties": currentFixture.homePenalties, "homePenaltiesLeft": currentFixture.homePenaltiesLeft});
        }
        $("#homeNumberPenalties").text(currentFixture.homePenalties.reduce((a, b) => a + b, 0))
        suddenDeathApplied = false;
    }

    function updateAwayGoals(change) {
        currentFixture.awayGoals = currentFixture.awayGoals + change;
        document.getElementById("awayGoals").innerHTML = currentFixture.awayGoals.toString();
        socket.emit('score', {'awayGoals': currentFixture.awayGoals});
    }

    function updateAwayFouls(change) {
        currentFixture.awayFouls = currentFixture.awayFouls + change;
        document.getElementById("awayFouls").innerHTML = currentFixture.awayFouls.toString();
        socket.emit('foul', {'awayFouls': currentFixture.awayFouls});
    }

    function updateAwayPenalties(outcome) {
        if (outcome === -1) {
            document.getElementById(`awayPenalty${Math.min(6, currentFixture.awayPenalties.length)}`).classList.remove("scored", "missed");
            document.getElementById(`awayPenalty${Math.min(6, currentFixture.awayPenalties.length)}`).classList.add("untaken");
            currentFixture.awayPenalties.pop();
            currentFixture.awayPenaltiesLeft++;
            socket.emit('penalty', {"awayPenalties": currentFixture.awayPenalties, "awayPenaltiesLeft": currentFixture.awayPenaltiesLeft});
        } else if (currentFixture.awayPenaltiesLeft > 0) {
            currentFixture.awayPenalties.push(outcome);
            document.getElementById(`awayPenalty${Math.min(6, currentFixture.awayPenalties.length)}`).classList.remove("untaken");
            if (outcome === 0) {
                document.getElementById(`awayPenalty${Math.min(6, currentFixture.awayPenalties.length)}`).classList.add("missed");
            } else {
                document.getElementById(`awayPenalty${Math.min(6, currentFixture.awayPenalties.length)}`).classList.add("scored");
            }
            currentFixture.awayPenaltiesLeft--;
            socket.emit('penalty', {"awayPenalties": currentFixture.awayPenalties, "awayPenaltiesLeft": currentFixture.awayPenaltiesLeft});
        }
        $("#awayNumberPenalties").text(currentFixture.awayPenalties.reduce((a, b) => a + b, 0))
        suddenDeathApplied = false;
    }

    function handleHomeGoalAdd() {
        if (currentPeriod.displayName === "Penalties" || 
                (currentPeriod.displayName === "Full time" && currentFixture.wentPenalties)) {
            updateHomePenalties(1);
        } else {
            updateHomeGoals(1);
        }
    }

    function handleAwayGoalAdd() {
        if (currentPeriod.displayName === "Penalties" || 
                (currentPeriod.displayName === "Full time" && currentFixture.wentPenalties)) {
            updateAwayPenalties(1);
        } else {
            updateAwayGoals(1);
        }
    }

    function handleHomeFoulAdd() {
        if (currentPeriod.displayName === "Penalties" || 
                (currentPeriod.displayName === "Full time" && currentFixture.wentPenalties)) {
            // Add penalty miss
            updateHomePenalties(0)
            currentFixture.homePenaltyMisses++;
        } else {
            updateHomeFouls(1);
        }
    }

    function handleAwayFoulAdd() {
        if (currentPeriod.displayName === "Penalties" || 
                (currentPeriod.displayName === "Full time" && currentFixture.wentPenalties)) {
            // Add penalty miss
            updateAwayPenalties(0)
        } else {
            updateAwayFouls(1);
        }
    }

    function handleHomeGoalTake() {
        if ((currentPeriod.displayName === "Penalties" || 
                (currentPeriod.displayName === "Full time" && currentFixture.wentPenalties)) && 
                currentFixture.homePenalties.length > 0) {
            // Take latest home penalty away
            updateHomePenalties(-1);
        } else if (currentPeriod.displayName != "Penalties" && currentFixture.homeGoals > 0) {
            updateHomeGoals(-1);
        }
    }

    function handleAwayGoalTake() {
        if ((currentPeriod.displayName === "Penalties" || 
                (currentPeriod.displayName === "Full time" && currentFixture.wentPenalties)) && 
                currentFixture.awayPenalties.length > 0) {
            // Take latest away penalty away
            updateAwayPenalties(-1);
        } else if (currentPeriod.displayName != "Penalties" && currentFixture.awayGoals > 0) {
            updateAwayGoals(-1);
        }
    }

    function handleHomeFoulTake() {
        if (currentPeriod.displayName != "Penalties" && currentFixture.homeFouls > 0) {
            updateHomeFouls(-1);
        }
    }
    
    function handleAwayFoulTake() {
        if (currentPeriod.displayName != "Penalties" && currentFixture.awayFouls > 0) {
            updateAwayFouls(-1);
        }
    }

    document.addEventListener('keyup', event => {
        var actionDict = {
            1: "HG+",
            2: "AG+",
            3: "HG-",
            4: "AG-",
            5: "HF+",
            6: "AF+",
            7: "HF-",
            8: "AF-",
        };
        var foulIdPart = {
            1: "Foul1",
            2: "Foul2",
            3: "Foul3",
            4: "Foul4",
            5: "Foul5",
            6: "Foul6",
        };
        const key = event.key.toLowerCase();
    
        // we are only interested in valid keys
        //if (!actionDict[key]) return;
        if (document.getElementById("period") != "Pre game") {
            switch(key) {
                case '1':
                    handleHomeGoalAdd();
                    return;
                case '2':
                    handleAwayGoalAdd();
                    return;
                case '3':
                    handleHomeFoulAdd();
                    return;
                case '4':
                    handleAwayFoulAdd();
                    return;
                case '5':
                    handleHomeGoalTake();
                    return;
                case '6':
                    handleAwayGoalTake();
                    return;
                case '7':
                    handleHomeFoulTake();
                    return;
                case '8':
                    handleAwayFoulTake();
                    return;
            }
        }   
    });
});