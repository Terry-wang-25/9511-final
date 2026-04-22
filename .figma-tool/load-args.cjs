const fs = require('fs');
const p = 'c:/Users/tiany/Desktop/9511-final/.figma-tool/_invoke_full_wires.json';
module.exports = JSON.parse(fs.readFileSync(p, 'utf8'));
