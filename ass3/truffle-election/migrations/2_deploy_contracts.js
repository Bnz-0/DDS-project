const ExampleElection = artifacts.require("ExampleElection.sol");
const CapiesoElection = artifacts.require("CapiesoElection.sol");

module.exports = function (deployer) {
  deployer.deploy(ExampleElection);
  deployer.deploy(CapiesoElection);
};
