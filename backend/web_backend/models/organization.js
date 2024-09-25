const mongoose = require('mongoose');

const organizationSchema = new mongoose.Schema({
    name: String,         // Organization name
    address: String,      // Organization address
    units: [{ 
      type: mongoose.Schema.Types.ObjectId, 
      ref: 'Unit' 
    }]  // Reference to units
  });
  
const Organization = mongoose.model('Organization', organizationSchema);

module.exports = Organization;
  