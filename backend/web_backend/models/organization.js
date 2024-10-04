const mongoose = require('mongoose');
const machine = require('./machine');
const sensor = require('./sensor');
const unit = require('./unit');

const organizationSchema = new mongoose.Schema({
    name: String,         // Organization name
    address: String,      // Organization address
  });
  
const Organization = mongoose.model('Organization', organizationSchema);

module.exports = Organization;
    