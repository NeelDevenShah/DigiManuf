var Org = require('../models/organization.js');
var Sensor = require('../models/sensor.js');
var Machine = require('../models/machine.js');
var Unit = require('../models/unit.js');
var User = require('../models/user.js');
var dotenv = require('dotenv');
const jwt = require("jsonwebtoken")
dotenv.config();
const SECRET_KEY = process.env.SECRET_KEY;


exports.getOrg = async (req, res) => {
    try {

        const user = req.user;
        let uid = user.organization;
        console.log("org id", uid)

        if(uid){
            let org = await Org.findById({_id: uid});
            // console.log("req.userOrg",req.userOrg)
            // console.log("org._id.toString()",org._id.toString())
            if (!org || org._id.toString() !== req.userOrg.toString()) {
                return res.status(403).json({ error: 'Access Denied: You are not authorized to view this organization' });
            }
            return res.status(200).json({ success: true, data: org });
        }
        else{
            res.status(400).json({ error: 'Organizationnto found' });
        }
        
    } catch (error) {
        console.log(error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}


exports.getMachine = async (req, res) => {
    try {
        if(req.query.uid){
            let machine = await Machine.find({unit: req.query.uid});
            return res.status(200).json({ success: true, data: machine });
        }
        else if(req.query.mid){
            let machine = await Machine.find({_id: req.query.mid});
            return res.status(200).json({ success: true, data: machine });
        }
        else{
            let machines = await Machine.find();
            return res.status(200).json({success:true, data: machines})
        }

    } catch (error) {
        console.log(error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}


exports.getSensor = async (req, res) => {
    try {
        if(req.query.mid){
            let sensor = await Sensor.find({machine: req.query.mid});
            return res.status(200).json({ success: true, data: sensor });
        }
        else if(req.query.id){
            let sensor = await Sensor.find({_id: req.query.mid});
            return res.status(200).json({ success: true, data: sensor });
        }
        else{
            let sensors = await Sensor.find();
            return res.status(200).json({ success: true, data: sensors })
        }

    } catch (error) {
        console.log(error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}

exports.getUnit = async (req, res) => {
    try {
        if(req.query.id){
            let unit = await Unit.findById(req.query.id);
            return res.status(200).json({ success: true, data: unit });
        }
        else{
            let units = await Unit.find();
            return res.status(200).json({ success: true, data: units });
        }

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
