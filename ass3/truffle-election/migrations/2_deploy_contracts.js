const ExampleElection = artifacts.require("ExampleElection.sol");

module.exports = function (deployer) {
  deployer.deploy(ExampleElection);
};
