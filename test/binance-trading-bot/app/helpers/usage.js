const os = require('os');

/**
 * Print CPU RAM ... usage
 *
 * @param {*} text
 */
const printUsage = () => {
  console.log(os.cpus());
  console.log(os.totalmem());
  console.log(os.freemem());
};

module.exports = { printUsage };
