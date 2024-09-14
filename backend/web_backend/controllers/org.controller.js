var Org = require('../models/organization.js');
var Sensor = require('../models/sensor.js');
var Machine = require('../models/machine.js');


exports.getOrg = async (req, res) => {
    try {
        let org = await Org.find();
        return res.status(200).json({ success: true, data: org });
    } catch (error) {
        console.log(error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}


exports.getMachine = async (req, res) => {
    try {
        let machine = await Machine.findById(req.params.id);
        return res.status(200).json({ success: true, data: machine });

    } catch (error) {
        console.log(error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}


exports.getSensor = async (req, res) => {
    try {
        let sensor = await Sensor.findById(req.params.id);
        return res.status(200).json({ success: true, data: sensor });

    } catch (error) {
        console.log(error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}

exports.getUnit = async (req, res) => {
    try {
        let unit = await Unit.findById(req.params.id);
        return res.status(200).json({ success: true, data: unit });

    } catch (error) {
        console.log(error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}

exports.createMachine = async (req, res) => {
    try {
        let machine = await Machine.create(req.body);
        return res.status(201).json({ success: true, data: machine });
    } catch (error) {
        console.log(error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}

exports.createSensor = async (req, res) => {
    try {
        let sensor = await Sensor.create(req.body);
        return res.status(201).json({ success: true, data: sensor });
    } catch (error) {
        console.log(error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}

exports.createUnit = async (req, res) => {
    try {
        let unit = await Unit.create(req.body);
        return res.status(201).json({ success: true, data: unit });
    } catch (error) {
        console.log(error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}

exports.createOrg = async (req, res) => {
    try {
        let org = await Org.create(req.body);
        return res.status(201).json({ success: true, data: org });
    } catch (error) {
        console.log(error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}
