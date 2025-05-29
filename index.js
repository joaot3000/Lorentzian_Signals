const express = require("express");
const bodyParser = require("body-parser");
const { google } = require("googleapis");
const app = express();

app.use(bodyParser.json());

app.post("/", async (req, res) => {
  try {
    const data = req.body;
    console.log("Received data:", data);

    const positionSize = Number(data.position_size);
    const action = positionSize > 0 ? "BUY" : positionSize < 0 ? "SELL" : "NONE";

    const row = [
      new Date().toISOString(),
      data.symbol || "",
      action,
      data.price || "",
      data.size || "0.1"
    ];

    const auth = new google.auth.GoogleAuth({
      credentials: require("./credentials.json"),
      scopes: ["https://www.googleapis.com/auth/spreadsheets"]
    });

    const sheets = google.sheets({ version: "v4", auth });

    await sheets.spreadsheets.values.append({
      spreadsheetId: "https://script.google.com/macros/s/AKfycbysXzW8TFr3DXG2h7G3_ufQJGx5I7gweq_p-Croxck7-Iio_h_J4yAHIyOF5hE9jcZ4/exec", // ← Replace this
      range: "Signals!A:E",                  // ← Update if your sheet is named differently
      valueInputOption: "RAW",
      requestBody: {
        values: [row]
      }
    });

    res.status(200).send({ status: "success", written: row });
  } catch (err) {
    console.error("Error:", err);
    res.status(500).send({ status: "error", message: err.toString() });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Webhook server running on port ${PORT}`);
});
