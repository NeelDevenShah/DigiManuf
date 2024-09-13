const unitSchema = new mongoose.Schema({
    name: String,         // e.g., Unit 1
    location: String,     // e.g., City, Region
    machines: [{ 
      type: mongoose.Schema.Types.ObjectId, 
      ref: 'Machine' 
    }]  // Reference to machines
  });
  
  const Unit = mongoose.model('Unit', unitSchema);
  