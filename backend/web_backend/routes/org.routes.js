const express = require('express');
const { getOrg, getMachine, getSensor, getUnit, createMachine, createSensor, createUnit, createOrg} = require('../controllers/org.controller.js');

const router = express.Router();

router.get('/organization', getOrg);
router.get('/sensor/:id', getSensor);
router.get('/machine/:id', getMachine);
router.get('/unit/:id', getUnit);
router.post('/unit', createUnit);
router.post('/machine', createMachine);
router.post('/sensor', createSensor);
router.post('/organization', createOrg);

module.exports = router;