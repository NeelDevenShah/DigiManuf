const mongoose = require('mongoose');
const Organization = require('./organization');

const sensorSchema = new mongoose.Schema({
    name: String,          // e.g., temperature, pressure, etc.
    status: String,        // e.g., active, inactive
    value: Number,         // last known value
    type: String,
    timestamp: Date,       // when the value was last updated
    machine: { 
      type: mongoose.Schema.Types.ObjectId, 
      ref: 'Machine' 
    },  // Reference to the machine
    organization: { 
      type: mongoose.Schema.Types.ObjectId, 
      ref: 'Organization' 
    },  // Reference to the organization
    unit: { 
      type: mongoose.Schema.Types.ObjectId, 
      ref: 'Unit' 
    }  // Reference to the unit

  });
  
  const Sensor = mongoose.model('Sensor', sensorSchema);

module.exports = Sensor;
  