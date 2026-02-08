
/**
 * @OnlyCurrentDoc
 */

/* -------------------------------------------------------------------------- */
/*                                CONFIGURATION                               */
/* -------------------------------------------------------------------------- */

const SHEET_NAME_RESPONSES = "Form Responses 1";
const SHEET_NAME_KEY = "Key";
const RESPONSE_NAME_COL_INDEX = 2; // Column C (0-indexed = 2)
const RESPONSE_Q_START_INDEX = 3;  // Column D (0-indexed = 3)

/* -------------------------------------------------------------------------- */
/*                                 HTML SERVICE                               */
/* -------------------------------------------------------------------------- */

function doGet(e) {
  return HtmlService.createTemplateFromFile("index")
    .evaluate()
    .setTitle("SUPER BOWL LX BETTING BOARD")
    .addMetaTag("viewport", "width=device-width, initial-scale=1")
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/* -------------------------------------------------------------------------- */
/*                                  API LOGIC                                 */
/* -------------------------------------------------------------------------- */

/**
 * Main API function called by the client.
 * Returns { leaderboard, stats, meta }
 */
function getDataPacket() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const respSheet = ss.getSheetByName(SHEET_NAME_RESPONSES);
  const keySheet = ss.getSheetByName(SHEET_NAME_KEY);

  if (!respSheet || !keySheet) {
    throw new Error(`Missing tabs: '${SHEET_NAME_RESPONSES}' or '${SHEET_NAME_KEY}'. Check tab names.`);
  }

  // 1. Parse The Key (Vertical: Col A=Question, Col B=Answer)
  const keyRaw = keySheet.getDataRange().getValues(); // [[Q, A], [Q, A]...]
  
  let keyMap = []; // Array of objects { q: string, a: string, respColIndex: number }
  let pointsRemaining = 0;

  // Start from row 0, but if row 0 is "Question/Answer" header, skip it.
  let startRow = 0;
  if (keyRaw.length > 0 && String(keyRaw[0][0]).toLowerCase().includes("question")) {
    startRow = 1;
  }

  // We map sequentially: 
  // Key Row X (after header) -> Response Column (RESPONSE_Q_START_INDEX + X)
  let validKeyCount = 0;

  for (let i = startRow; i < keyRaw.length; i++) {
    const q = String(keyRaw[i][0]).trim();
    const a = String(keyRaw[i][1]).trim(); // key answer
    
    // Valid key item if it has a question text in Col A
    if (q) {
      keyMap.push({ 
        q: q, 
        a: a,
        respColIndex: RESPONSE_Q_START_INDEX + validKeyCount 
      });
      
      if (a === "") {
        pointsRemaining++;
      }
      validKeyCount++;
    }
  }

  // 2. Score Users
  const respData = respSheet.getDataRange().getValues();
  if (respData.length <= 1) return { leaderboard: [], stats: {}, meta: {} };
  
  // Slice off headers (Row 1)
  const usersRaw = respData.slice(1);

  let leaderboard = [];

  usersRaw.forEach(row => {
    // Name is at Index 2 (Col C)
    let name = row[RESPONSE_NAME_COL_INDEX]; 
    
    if (!name || String(name).trim() === "") return;

    let score = 0;
    
    // Loop through our Key Map and compare
    keyMap.forEach(kItem => {
      const targetCol = kItem.respColIndex;
      const correctAns = kItem.a.toLowerCase();
      
      // Only score if key has an answer and column exists in user row
      if (correctAns !== "" && targetCol < row.length) {
        const userAns = String(row[targetCol]).toString().trim().toLowerCase();
        if (userAns === correctAns) {
          score++;
        }
      }
    });

    leaderboard.push({
      name: String(name).trim(),
      score: score
    });
  });

  // Sort Descending
  leaderboard.sort((a, b) => b.score - a.score);

  // Assign Ranks
  leaderboard = leaderboard.map((p, i) => ({...p, rank: i + 1}));

  // 3. Stats Logic (Unchanged from before, just re-integrated)
  
  // A. Rivalry
  let rivalry = null;
  if (leaderboard.length >= 5) {
    rivalry = {
      player1: leaderboard[3].name,
      score1: leaderboard[3].score,
      player2: leaderboard[4].name,
      score2: leaderboard[4].score,
      diff: Math.abs(leaderboard[3].score - leaderboard[4].score)
    };
  }

  // B. Wooden Spoon
  let woodenSpoon = null;
  if (leaderboard.length > 0) {
    const lastPlayer = leaderboard[leaderboard.length - 1];
    woodenSpoon = {
      name: lastPlayer.name,
      score: lastPlayer.score
    };
  }

  // C. Pulse
  let pulse = { label: "Completed", value: "FINAL", details: "All Set" };
  
  // Find first key item with empty answer
  const firstUnanswered = keyMap.find(k => k.a === "");
  
  if (firstUnanswered) {
    const qText = firstUnanswered.q;
    const colIdx = firstUnanswered.respColIndex;
    
    // Tally votes for this column
    let voteCounts = {};
    let totalVotes = 0;

    usersRaw.forEach(row => {
      if (colIdx < row.length) {
        const ans = String(row[colIdx]).trim();
        if (ans) {
          voteCounts[ans] = (voteCounts[ans] || 0) + 1;
          totalVotes++;
        }
      }
    });

    // Find top choice
    let topChoice = "Waiting...";
    let topCount = 0;
    for (const [ans, count] of Object.entries(voteCounts)) {
      if (count > topCount) {
        topCount = count;
        topChoice = ans;
      }
    }
    
    let percent = totalVotes > 0 ? Math.round((topCount / totalVotes) * 100) : 0;
    
    pulse = {
      question: qText.length > 25 ? qText.substring(0, 22) + "..." : qText,
      topChoice: topChoice,
      percent: percent,
      totalVotes: totalVotes
    };
  }

  return {
    leaderboard: leaderboard,
    stats: {
      rivalry: rivalry,
      woodenSpoon: woodenSpoon,
      pulse: pulse,
      pointsRemaining: pointsRemaining
    },
    meta: {
      totalPlayers: leaderboard.length,
      timestamp: new Date().toLocaleTimeString('en-US', {hour: '2-digit', minute:'2-digit'})
    }
  };
}

/* -------------------------------------------------------------------------- */
/*                                HELPER TOOLS                                */
/* -------------------------------------------------------------------------- */

/**
 * Creates the Sheet Structure requested by User for testing purposes.
 * WARNING: This clears existing data in these tabs.
 */
function setupDemoData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. Setup 'Key' (Vertical)
  let keySheet = ss.getSheetByName(SHEET_NAME_KEY);
  if (!keySheet) {
    keySheet = ss.insertSheet(SHEET_NAME_KEY);
  } else {
    keySheet.clear();
  }
  
  const keyData = [
    ["Question", "Answer"],
    ["Coin Toss", "Heads"],
    ["First TD Scorer", "McCaffrey"],
    ["Gatorade Color", ""], // Pending
    ["MVP", ""],
    ["Over/Under 48.5", "Over"],
    ["Winner", ""]
  ];
  keySheet.getRange(1, 1, keyData.length, 2).setValues(keyData);
  keySheet.getRange("A1:B1").setFontWeight("bold").setBackground("#f3f3f3");

  // 2. Setup 'Form Responses 1'
  let respSheet = ss.getSheetByName(SHEET_NAME_RESPONSES);
  if (!respSheet) {
    respSheet = ss.insertSheet(SHEET_NAME_RESPONSES);
  } else {
    respSheet.clear();
  }

  // Headers: Timestamp(A), Email(B), Name(C), Q1(D)...
  const headers = ["Timestamp", "Email Address", "Name", "Coin Toss", "First TD Scorer", "Gatorade Color", "MVP", "Over/Under 48.5", "Winner"];
  respSheet.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight("bold");

  // Dummy Data
  const participants = [
    ["Tony", "Heads", "McCaffrey", "Orange", "Purdy", "Over", "49ers"],
    ["Steve", "Tails", "Kelce", "Red", "Mahomes", "Under", "Chiefs"],
    ["Natasha", "Heads", "Pacheco", "Orange", "Kelce", "Over", "Chiefs"],
    ["Bruce", "Heads", "Deebo", "Clear", "Purdy", "Over", "49ers"],
    ["Clint", "Tails", "McCaffrey", "Blue", "Mahomes", "Over", "Chiefs"],
    ["Wanda", "Heads", "Kelce", "Purple", "Kelce", "Under", "Chiefs"],
    ["Thor", "Tails", "McCaffrey", "Orange", "Purdy", "Over", "49ers"],
    ["Loki", "Tails", "Rice", "Green", "Mahomes", "Under", "Chiefs"] 
  ];

  const rows = participants.map(p => [new Date(), "test@example.com", ...p]);
  respSheet.getRange(2, 1, rows.length, rows[0].length).setValues(rows);

  return "Setup Complete. Tabs 'Form Responses 1' and 'Key' created.";
}
