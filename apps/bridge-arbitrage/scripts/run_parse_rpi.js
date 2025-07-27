const path = require('path');
const { PDFDocument } = require('pdf-lib');
const fs = require('fs').promises;
const parseRPI = require('./parse_rpi');

async function main() {
  try {
    console.log('Starting RPI parsing...');
    await parseRPI();
    console.log('RPI parsing completed successfully!');
  } catch (error) {
    console.error('Error during RPI parsing:', error);
    process.exit(1);
  }
}

main();
