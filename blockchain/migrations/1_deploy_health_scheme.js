const HealthScheme = artifacts.require("HealthScheme");

module.exports = function (deployer) {
  deployer.deploy(HealthScheme);
};
