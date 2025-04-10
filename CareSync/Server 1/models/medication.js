const mongoose = require('mongoose');

const medicationSchema = new mongoose.Schema({
    username: { type: String, required: true },
    name: { type: String, required: true },
    time: { type: String, required: true }
});

const Medication = mongoose.model('Medication', medicationSchema);

module.exports = Medication;
