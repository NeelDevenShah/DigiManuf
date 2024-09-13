const sensorSchema = new mongoose.Schema({
    type: String,          // e.g., temperature, pressure, etc.
    status: String,        // e.g., active, inactive
    value: Number,         // last known value
    timestamp: Date,       // when the value was last updated
  });
  
  const Sensor = mongoose.model('Sensor', sensorSchema);
  