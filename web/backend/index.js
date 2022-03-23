const express = require('express');
const app = express();
const cors = require('cors');
const auth = require('./src/routes/auth/auth');
const video = require('./src/routes/video/video');

app.use(cors());
app.use(express.json());
app.use("/",auth);
app.use("/",video);
module.exports = app;