// # Micro-service-7

var express = require("express");
var authRoutes = require("./routes/auth.routes");
var orgRoutes = require("./routes/org.routes");
const connectDB = require("./config/db.js");
const cookieParser = require("cookie-parser");
const app = express();
const cors = require("cors");

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cookieParser());

app.use(
  cors({
    origin: ["http://localhost:3000", "http://localhost:3001"],
    credentials: true,
  })
);

app.use("/api/auth", authRoutes);
app.use("/api/org", orgRoutes);

app.get("/", (req, res) => {
  res.send("Hello World!");
});

app.listen(3001, () => {
  console.log("Server is running on http://localhost:3001");
  connectDB();
});
