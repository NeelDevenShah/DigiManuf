const express = require('express');
const { getOrg, getMachine, getSensor, getUnit, createMachine, createSensor, createUnit, createOrg} = require('../controllers/org.controller.js');
const verifyuser = require('../middleware/verify.js');

const router = express.Router();

router.get('/organization',verifyuser, getOrg);
router.get('/sensor',verifyuser, getSensor);
router.get('/machine',verifyuser, getMachine);
router.get('/unit',verifyuser, getUnit);
router.post('/unit',verifyuser, createUnit);
router.post('/machine',verifyuser, createMachine);
router.post('/sensor',verifyuser, createSensor);
router.post('/organization',verifyuser, createOrg);

module.exports = router;