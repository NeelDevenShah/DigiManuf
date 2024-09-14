const mongoose = require('mongoose');

const sensorSchema = new mongoose.Schema({
    name: String,          // e.g., temperature, pressure, etc.
    status: String,        // e.g., active, inactive
    value: Number,         // last known value
    timestamp: Date,       // when the value was last updated
    machine: { 
      type: mongoose.Schema.Types.ObjectId, 
      ref: 'Machine' 
    }  // Reference to the machine
  });
  
  const Sensor = mongoose.model('Sensor', sensorSchema);

module.exports = Sensor;
  