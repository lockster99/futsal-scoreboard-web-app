// ── Team data ────────────────────────────────────────────────────────────────

const LINEUPS = {
  home: {
    title: 'IPS — Starting Lineup',
    starters: [
      { n: 1,  name: 'Garcia',   pos: 'GK' },
      { n: 5,  name: 'Santos',   pos: 'FX' },
      { n: 7,  name: 'Oliveira', pos: 'FX' },
      { n: 9,  name: 'Mendez',   pos: 'FX' },
      { n: 11, name: 'Reyes',    pos: 'FX' },
    ],
    subs: [
      { n: 2,  name: 'Torres',   pos: 'FX' },
      { n: 4,  name: 'Vargas',   pos: 'GK' },
      { n: 6,  name: 'Ruiz',     pos: 'FX' },
      { n: 8,  name: 'Flores',   pos: 'FX' },
      { n: 12, name: 'Morales',  pos: 'FX' },
      { n: 14, name: 'Jimenez',  pos: 'FX' },
    ],
  },
  away: {
    title: 'RIV — Starting Lineup',
    starters: [
      { n: 1,  name: 'Nakamura', pos: 'GK' },
      { n: 4,  name: 'Costa',    pos: 'FX' },
      { n: 8,  name: 'Ferreira', pos: 'FX' },
      { n: 10, name: 'Silva',    pos: 'FX' },
      { n: 14, name: 'Alves',    pos: 'FX' },
    ],
    subs: [
      { n: 2,  name: 'Pereira',  pos: 'FX' },
      { n: 3,  name: 'Rocha',    pos: 'GK' },
      { n: 6,  name: 'Lima',     pos: 'FX' },
      { n: 7,  name: 'Gomes',    pos: 'FX' },
      { n: 11, name: 'Dias',     pos: 'FX' },
      { n: 13, name: 'Nunes',    pos: 'FX' },
    ],
  },
};

// Scorer names cycle round-robin when goals are clicked
const SCORERS = {
  home: ['Oliveira', 'Mendez', 'Santos', 'Reyes', 'Torres'],
  away: ['Silva', 'Costa', 'Alves', 'Ferreira', 'Gomes'],
};

const SPONSORS = [
  { name: 'FutsalPro', tag: 'Official Equipment Partner' },
  { name: 'SportZone', tag: 'Proud Match Sponsor'        },
  { name: 'ArenaKing', tag: 'Venue Partner'              },
];


// ── State ────────────────────────────────────────────────────────────────────

let scoreHome    = 0;
let scoreAway    = 0;
let timerSeconds = 20 * 60;  // counts down from 20:00
let timerRunning  = false;
let timerInterval = null;

let lineupVisible = false;
let lineupSide    = null;   // 'home' | 'away' | null

let sponsorVisible = false;
let sponsorIndex   = 0;     // cycles through SPONSORS array

const scorerIndex = { home: 0, away: 0 };

let goalDismissTimer = null;


// ── Scorebug ─────────────────────────────────────────────────────────────────

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
}

function updateBug() {
  document.getElementById('bug-score').textContent = scoreHome + ' – ' + scoreAway;
  document.getElementById('bug-timer').textContent = formatTime(timerSeconds);
}


// ── Timer controls ────────────────────────────────────────────────────────────

function startTimer() {
  if (timerRunning) return;
  timerRunning = true;
  timerInterval = setInterval(() => {
    if (timerSeconds > 0) {
      timerSeconds--;
      updateBug();
    } else {
      pauseTimer();
    }
  }, 1000);
}

function pauseTimer() {
  timerRunning = false;
  clearInterval(timerInterval);
}

function resetTimer() {
  pauseTimer();
  timerSeconds = 20 * 60;
  updateBug();
}


// ── Goal notification ─────────────────────────────────────────────────────────

function scoreGoal(side) {
  if (side === 'home') scoreHome++;
  else                 scoreAway++;
  updateBug();

  // Pick the next scorer name for this team
  const scorer = SCORERS[side][scorerIndex[side] % SCORERS[side].length];
  scorerIndex[side]++;

  document.getElementById('goal-team-label').textContent = (side === 'home') ? 'IPS' : 'RIV';
  document.getElementById('goal-scorer').textContent     = scorer;
  document.getElementById('goal-score-val').textContent  = scoreHome + ' – ' + scoreAway;

  // Slide the card up; auto-dismiss after 4 s
  const el = document.getElementById('goal-notif');
  el.classList.add('show');
  if (goalDismissTimer) clearTimeout(goalDismissTimer);
  goalDismissTimer = setTimeout(() => el.classList.remove('show'), 4000);
}


// ── Lineup graphic ────────────────────────────────────────────────────────────

function playerRow(player, isSub) {
  const cls = isSub ? 'lineup-player sub-player' : 'lineup-player';
  return `
    <div class="${cls}">
      <span class="lineup-num">${player.n}</span>
      <span class="lineup-name">${player.name}</span>
      <span class="lineup-pos">${player.pos}</span>
    </div>`;
}

function toggleLineup(side) {
  const el   = document.getElementById('lineup');
  const btnH = document.getElementById('btn-lineup-h');
  const btnA = document.getElementById('btn-lineup-a');

  // Clicking the same side again dismisses the graphic
  if (lineupVisible && lineupSide === side) {
    el.classList.remove('on');
    el.classList.add('off-bottom');
    lineupVisible = false;
    lineupSide    = null;
    btnH.classList.remove('active');
    btnA.classList.remove('active');
    return;
  }

  // Build HTML for starters + subs
  const data = LINEUPS[side];
  document.getElementById('lineup-title').textContent = data.title;

  const html =
    '<div class="lineup-section-label">Starting Five</div>' +
    data.starters.map(p => playerRow(p, false)).join('') +
    '<div class="lineup-section-label">Substitutes</div>' +
    data.subs.map(p => playerRow(p, true)).join('');

  document.getElementById('lineup-body').innerHTML = html;

  // Force a reflow so the transition fires even when swapping sides
  el.classList.remove('on', 'off-bottom');
  void el.offsetWidth;
  el.classList.add('off-bottom');
  void el.offsetWidth;
  el.classList.add('on');

  lineupVisible = true;
  lineupSide    = side;
  btnH.classList.toggle('active', side === 'home');
  btnA.classList.toggle('active', side === 'away');
}


// ── Sponsor popup ─────────────────────────────────────────────────────────────

function toggleSponsor() {
  const el  = document.getElementById('sponsor');
  const btn = document.getElementById('btn-sponsor');

  if (sponsorVisible) {
    el.classList.remove('on');
    el.classList.add('off-right');
    sponsorVisible = false;
    btn.classList.remove('active');
  } else {
    // Advance to the next sponsor in the rotation
    const s = SPONSORS[sponsorIndex % SPONSORS.length];
    sponsorIndex++;
    document.getElementById('sponsor-name').textContent = s.name;
    document.getElementById('sponsor-tag').textContent  = s.tag;

    el.classList.remove('off-right');
    void el.offsetWidth;
    el.classList.add('on');
    sponsorVisible = true;
    btn.classList.add('active');
  }
}


// ── Scene switching ───────────────────────────────────────────────────────────

/*
 * Each scene config describes:
 *   showBanner  – whether the centred title card is visible
 *   showHT      – whether the half-time stats panel is visible
 *   title / sub – text for the title card (when showBanner is true)
 */
function buildSceneConfigs() {
  return {
    pregame:  { showBanner: true,  showHT: false, title: 'Pre-Match', sub: 'IPS vs RIV — Kickoff Soon' },
    ingame:   { showBanner: false, showHT: false },
    halftime: { showBanner: false, showHT: true  },
    fulltime: { showBanner: true,  showHT: false, title: 'Full Time', sub: `IPS ${scoreHome} – ${scoreAway} RIV` },
  };
}

function setScene(scene) {
  // Update scene button highlights
  ['pregame', 'ingame', 'halftime', 'fulltime'].forEach(s => {
    document.getElementById('btn-' + s).classList.toggle('active', s === scene);
  });

  const cfg    = buildSceneConfigs()[scene];
  const banner = document.getElementById('scene-banner');
  const ht     = document.getElementById('ht-stats');

  // Scene banner (Pre-Match / Full Time)
  if (cfg.showBanner) {
    document.getElementById('scene-title-text').textContent = cfg.title;
    document.getElementById('scene-sub-text').textContent   = cfg.sub;
    banner.classList.remove('off-top');
    void banner.offsetWidth;
    banner.classList.add('on');
  } else {
    banner.classList.remove('on');
    banner.classList.add('off-top');
  }

  // Half-time stats panel
  if (cfg.showHT) {
    ht.classList.remove('off-bottom');
    void ht.offsetWidth;
    ht.classList.add('on');
  } else {
    ht.classList.remove('on');
    ht.classList.add('off-bottom');
  }

  // Dismiss the lineup graphic when going live
  if (scene === 'ingame') {
    const lineup = document.getElementById('lineup');
    lineup.classList.remove('on');
    lineup.classList.add('off-bottom');
    lineupVisible = false;
    lineupSide    = null;
    document.getElementById('btn-lineup-h').classList.remove('active');
    document.getElementById('btn-lineup-a').classList.remove('active');
  }
}


// ── Init ──────────────────────────────────────────────────────────────────────

setScene('pregame');
updateBug();
