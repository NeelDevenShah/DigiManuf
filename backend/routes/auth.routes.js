var express = require('express');
const { register, login, forgotPassword, resetPassword, changePassword } = require('../controllers/auth.controller.js');
const verifyuser = require('../middleware/verify.js');

router = express.Router();

router.post('/signup', register);
router.post('/signin', login);
// router.post('/forgot-password', forgotPassword);
router.post('/reset-password',verifyuser, resetPassword);
// router.post('/change-password', changePassword);


module.exports = router;

