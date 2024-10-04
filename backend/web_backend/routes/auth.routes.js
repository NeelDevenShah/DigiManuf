var express = require('express');
const { register, login, resetPassword,addUser } = require('../controllers/auth.controller.js');
const verifyuser = require('../middleware/verify.js');

router = express.Router();

router.post('/signup', register);
router.post('/signin', login);
router.post('/add-user',verifyuser, addUser);
router.post('/reset-password',verifyuser, resetPassword);

module.exports = router;
