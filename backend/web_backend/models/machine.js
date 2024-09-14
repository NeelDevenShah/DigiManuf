const mongoose = require('mongoose');

const machineSchema = new mongoose.Schema({
    name: String,         // e.g., Machine 1
    model: String,        // e.g., Model A
    sensors: [{ 
      type: mongoose.Schema.Types.ObjectId, 
      ref: 'Sensor' 
    }],   // Reference to the sensors
    unit: { 
      type: mongoose.Schema.Types.ObjectId, 
      ref: 'Unit' 
    }  // Reference to the unit

  });
  
  const Machine = mongoose.model('Machine', machineSchema);

module.exports = Machine;
  