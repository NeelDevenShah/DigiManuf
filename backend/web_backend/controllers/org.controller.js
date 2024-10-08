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
        let uid = req.userOrg;
        console.log("org id", uid)

        if(uid){
            let org = await Org.findById({_id: uid});
            
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
    try 
    {
        let oid = req.userOrg
        let mid = req.query.mid 
        let uid = req.query.uid

        // for all machines in organization
        if(oid && mid == null && uid == null){
            let machines = await Machine.find({organization: oid});
            if(machines){
                return res.status(200).json({ success: true, data: machines });
            }
            else{
                return res.status(404).json({error: 'Machine not found'})
            }
        }

        // list machine of organization by organization and unit
        else if(oid && uid && mid==null){
            let machines = await Machine.find({organization:oid, unit:uid})
            if(machines){
                return res.status(200).json({ success: true, data: machines });
            }
            else{
                return res.status(404).json({error: 'Machine not found'})
            }
        }

        else if(mid){
            let machine = await Machine.find({organization:oid, unit:uid, _id:mid})
            if(machine){
                return res.status(200).json({ success: true, data: machine });
            }
            else{
                return res.status(404).json({error: 'Machine not found'})
            }
        }
        else{
            return res.status(403).json({error: 'User is not part of any organization'})
        }
  
    } catch (error) {
        console.log(error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}


exports.getSensor = async (req, res) => {
    try {
        let oid = req.userOrg
        let sid = req.query.sid
        let mid = req.query.mid
        let uid = req.query.uid

        // for all sensors in organization

        if(oid && sid == null && mid == null && uid == null){
            let sensors = await Sensor.find({organization:oid})
            if(sensors){
                return res.status(200).json({ success: true, data: sensors })
            }
            else{
                return res.status(404).json({error: 'Sensors not found'})
            }
        }

        // list sensor of organization by organization and unit

        else if(oid && uid && sid == null && mid == null){
            let sensors = await Sensor.find({organization:oid, unit:uid})
            if(sensors){
                return res.status(200).json({ success: true, data: sensors })
            }
            else{
                return res.status(404).json({error: 'Sensors not found'})
            }
        }

        // list sensor of organization by organization and machine
            
            else if(oid && mid && sid == null){
                let sensors = await Sensor.find({organization:oid, machine:mid})
                if(sensors){
                    return res.status(200).json({ success: true, data: sensors })
                }
                else{
                    return res.status(404).json({error: 'Sensors not found'})
                }
            }
    
            else if(sid){
                let sensor = await Sensor.find({organization:oid, unit:uid, machine:mid, _id:sid})
                if(sensor){
                    return res.status(200).json({ success: true, data: sensor })
                }
                else{
                    return res.status(404).json({error: 'Sensor not found'})
                }
            }
            else{
                return res.status(403).json({error: 'User is not part of any organization'})
            }

    } catch (error) {
        console.log(error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}

exports.getUnit = async (req, res) => {
    try {
        let oid = req.userOrg
        let uid = req.query.uid 
        if(oid && uid == null){
            let units = await Unit.find({organization:oid})
            if(units){
                return res.status(200).json({ success: true, data: units })
            }
            else{
                return res.status(404).json({error: 'Units not found'})
            }
        }
        else if (oid && uid){
            let unit = await Unit.find({organization:oid, _id:uid})
            if(unit){
                return res.status(200).json({ success: true, data: unit })
            }
            else{
                return res.status(404).json({error: 'Unit not found'})
            }
        }
        else{
            return res.status(403).json({error: 'User is not part of any organization'}) 
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
