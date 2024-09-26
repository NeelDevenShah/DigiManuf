const mongoose = require('mongoose');

const unitSchema = new mongoose.Schema({
    name: String,         // e.g., Unit 1
    location: String,     // e.g., City, Region
 // Reference to machines
    organization: { 
      type: mongoose.Schema.Types.ObjectId, 
      ref: 'Organization' 
    }  // Reference to the organization
  });
  
  const Unit = mongoose.model('Unit', unitSchema);

module.exports = Unit;
  