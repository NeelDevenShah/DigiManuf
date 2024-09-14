const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');
dotenv.config();
SECRET_KEY = process.env.SECRET_KEY;
const generateToken = (res, userId) => {
  const token = jwt.sign({ userId }, SECRET_KEY, {
    expiresIn: '30d'
  });
  console.log(token)

  res.cookie('token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV !== 'development',
    sameSite: 'strict',
    maxAge: 30 * 24 * 60 * 60 * 1000 // 30 days
  });
};

module.exports = generateToken;