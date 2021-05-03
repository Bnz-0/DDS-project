const TimeCoin = artifacts.require("TimeCoin.sol");

module.exports = function (deployer) {
  deployer.deploy(TimeCoin);
};
