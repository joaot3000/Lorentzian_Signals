const express = require("express");
const bodyParser = require("body-parser");
const { google } = require("googleapis");

const app = express();
app.use(bodyParser.json());

app.post("/", async (req, res) => {
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

  try {
    const auth = new google.auth.GoogleAuth({
      credentials: require("./credentials.json"),
      scopes: ["https://www.googleapis.com/auth/spreadsheets"],
    });

    const sheets = google.sheets({ version: "v4", auth });
    await sheets.spreadsheets.values.append({
      spreadsheetId: "https://script.google.com/macros/s/AKfycbysXzW8TFr3DXG2h7G3_ufQJGx5I7gweq_p-Croxck7-Iio_h_J4yAHIyOF5hE9jcZ4/exec",
      range: "Signals!A:E",
      valueInputOption: "RAW",
      requestBody: { values: [row] },
    });

    res.send({ status: "success" });
  } catch (err) {
    console.error(err);
    res.status(500).send({ status: "error", message: err.toString() });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
