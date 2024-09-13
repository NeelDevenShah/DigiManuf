const machineSchema = new mongoose.Schema({
    name: String,         // e.g., Machine 1
    model: String,        // e.g., Model A
    sensors: [{ 
      type: mongoose.Schema.Types.ObjectId, 
      ref: 'Sensor' 
    }]   // Reference to the sensors
  });
  
  const Machine = mongoose.model('Machine', machineSchema);
  