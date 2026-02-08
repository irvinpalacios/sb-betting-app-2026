
/**
 * @OnlyCurrentDoc
 */

/* -------------------------------------------------------------------------- */
/*                                CONFIGURATION                               */
/* -------------------------------------------------------------------------- */

const SHEET_NAME_RESPONSES = "Responses";
const SHEET_NAME_KEY = "AnswerKey";

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
    throw new Error("Missing specific sheets. Please run setupDemoData() first.");
  }

  // 1. Fetch Data
  // Assuming Row 1 is Headers. 
  // Responses: Col A=Timestamp, Col B=Name, Col C...=Answers
  // Key: Row 2 = Answers (aligns with Col C...)
  
  const respData = respSheet.getDataRange().getValues();
  // Remove header
  const respHeaders = respData.shift(); 
  
  const keyData = keySheet.getDataRange().getValues();
  // Key Row might be row 2 (index 1) if row 1 is headers. Let's assume Row 2 is the actual key.
  // If only 1 row exists, assume it's row 2. Safer to explicitly grab row 2.
  // Let's assume Row 1: Headers (Questions), Row 2: Answers.
  const keyHeaders = keyData[0];
  const keyRow = keyData.length > 1 ? keyData[1] : [];

  // Column mapping
  // Responsive data usually starts at index 2 (Col C) for answers
  // So key answer for question at respHeaders[i] should be at keyHeaders corresponding index.
  // Let's assume strict column alignment for simplicity: Col C in Responses = Col C in Key.
  
  const START_COL_INDEX = 2; // 0=Timestamp, 1=Name, 2=Q1...

  // 2. Score Calculation
  let leaderboard = [];
  let pointsRemaining = 0;

  // Calculate Points Remaining (Count empty cells in Key starting from START_COL_INDEX)
  // We only count up to the length of the headers to avoid infinite trailing emptiness
  const totalQuestions = Math.min(respHeaders.length, keyHeaders.length);
  
  for (let c = START_COL_INDEX; c < totalQuestions; c++) {
    let keyAns = (keyRow[c] || "").toString().trim();
    if (keyAns === "") {
      pointsRemaining++;
    }
  }

  // Calculate User Scores
  respData.forEach(row => {
    let name = row[1]; // Col B
    if (!name) return; // Skip empty rows

    let score = 0;
    
    for (let c = START_COL_INDEX; c < totalQuestions; c++) {
      let userAns = (row[c] || "").toString().trim().toLowerCase();
      let keyAns = (keyRow[c] || "").toString().trim().toLowerCase();
      
      if (keyAns !== "" && userAns === keyAns) {
        score++;
      }
    }

    leaderboard.push({
      name: name,
      score: score
    });
  });

  // Sort Descending by Score
  leaderboard.sort((a, b) => b.score - a.score);

  // Assign Ranks (handle ties visually on frontend, but here just simple index)
  leaderboard = leaderboard.map((p, i) => ({...p, rank: i + 1}));

  // 3. Calculate Stats

  // A. Rivalry (Rank 4 vs Rank 5)
  // Indices 3 and 4
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

  // B. Wooden Spoon (Last Place)
  let woodenSpoon = null;
  if (leaderboard.length > 0) {
    const lastPlayer = leaderboard[leaderboard.length - 1];
    woodenSpoon = {
      name: lastPlayer.name,
      score: lastPlayer.score
    };
  }

  // C. Pulse (Next Unanswered Question Analysis)
  let pulse = { label: "Completed", value: "FINAL", details: "All Set" };
  
  // Find first index where key is empty
  let nextQIndex = -1;
  for (let c = START_COL_INDEX; c < totalQuestions; c++) {
    let keyAns = (keyRow[c] || "").toString().trim();
    if (keyAns === "") {
      nextQIndex = c;
      break;
    }
  }

  if (nextQIndex !== -1) {
    let questionName = keyHeaders[nextQIndex];
    if (questionName.length > 25) questionName = questionName.substring(0, 22) + "...";

    // Analyze votes
    let voteCounts = {};
    let totalVotes = 0;
    
    respData.forEach(row => {
      let ans = (row[nextQIndex] || "").toString().trim();
      if (ans) {
        voteCounts[ans] = (voteCounts[ans] || 0) + 1;
        totalVotes++;
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
      question: questionName,
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
 * Run this once to populate the sheet with testing data.
 */
function setupDemoData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. Setup AnswerKey
  let keySheet = ss.getSheetByName(SHEET_NAME_KEY);
  if (!keySheet) {
    keySheet = ss.insertSheet(SHEET_NAME_KEY);
  }
  keySheet.clear();
  // Headers
  const questions = ["Timestamp", "DummyName", "Coin Toss", "First TD Scorer", "Gatorade Color", "MVP", "Over/Under 48.5", "Halftime Short 1", "Halftime Short 2", "Winner"];
  const answers = ["", "", "Heads", "McCaffrey", "", "", "Over", "", "", ""]; // Some empty for 'Points Remaining' logic
  
  keySheet.getRange(1, 1, 1, questions.length).setValues([questions]).setFontWeight("bold").setBackground("#f3f3f3");
  keySheet.getRange(2, 1, 1, answers.length).setValues([answers]);

  // 2. Setup Responses
  let respSheet = ss.getSheetByName(SHEET_NAME_RESPONSES);
  if (!respSheet) {
    respSheet = ss.insertSheet(SHEET_NAME_RESPONSES);
  }
  respSheet.clear();
  respSheet.getRange(1, 1, 1, questions.length).setValues([questions]).setFontWeight("bold").setBackground("#e6efff");

  // Dummy Respondants
  const players = [
    {n: "Tony Stark", a: ["Heads", "McCaffrey", "Orange", "Purdy", "Over", "Yes", "No", "49ers"]},
    {n: "Steve Rogers", a: ["Tails", "Kelce", "Red", "Mahomes", "Under", "Yes", "Yes", "Chiefs"]},
    {n: "Bruce Banner", a: ["Heads", "Deebo", "Clear", "Purdy", "Over", "No", "No", "49ers"]},
    {n: "Natasha Romanoff", a: ["Heads", "Pacheco", "Orange", "Kelce", "Over", "Yes", "No", "Chiefs"]},
    {n: "Clint Barton", a: ["Tails", "McCaffrey", "Blue", "Mahomes", "Over", "No", "Yes", "Chiefs"]}, // Rivalry
    {n: "Wanda Maximoff", a: ["Heads", "Kelce", "Purple", "Kelce", "Under", "Yes", "Yes", "Chiefs"]}, // Rivalry
    {n: "Peter Parker", a: ["Heads", "McCaffrey", "Orange", "Kittle", "Over", "Yes", "No", "49ers"]}, 
    {n: "Scott Lang", a: ["Tails", "Rice", "Green", "Mahomes", "Under", "No", "No", "Chiefs"]}, // Wooden Spoon candidate
  ];

  const rows = players.map(p => {
    return [new Date(), p.n, ...p.a];
  });

  if (rows.length > 0) {
    respSheet.getRange(2, 1, rows.length, rows[0].length).setValues(rows);
  }
  
  Logger.log("Demo Data Created Successfully");
  return "Done";
}
