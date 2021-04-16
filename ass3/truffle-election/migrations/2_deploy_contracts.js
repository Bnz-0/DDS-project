const Election = artifacts.require("Election.sol");

module.exports = function (deployer) {
  deployer.deploy(Election, "Cogoleto", 1618606213);
};
