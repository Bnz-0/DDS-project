const TimeCoin = artifacts.require("TimeCoin.sol");

contract('TimeCoin', function(accounts) {

  it('check total supply', function() {
    var tokenInstance;
    return TimeCoin.deployed().then(function(instance) {
      tokenInstance = instance;
      return tokenInstance.totalSupply();
    }).then(function(totalSupply) {
      assert.equal(totalSupply, 1000000000, 'boh');
      return tokenInstance.balanceOf(accounts[0]);
    }).then(function(adminBalance) {
      assert.equal(adminBalance.toNumber(), 1000000000, 'boh2');
    })
  })
  
  it('transfer token', function() {
    return TimeCoin.deployed().then(function(instance) {
      tokenInstance = instance;
      return tokenInstance.transfer.call(accounts[1], 10, {from: accounts[0]});
    }).then(function(success) {
    	assert.equal(success, true, 'the call should return true');
    	return tokenInstance.transfer(accounts[1], 10, {from: accounts[0]});
    }).then(function(receipt) {
   		assert.equal(receipt.logs[0].event, 'Transfer', 'event should be "Transfer"');
    	assert.equal(receipt.logs[0].args._from, accounts[0], 'event should be accounts[0]');
    	assert.equal(receipt.logs[0].args._to,   accounts[1], 'event should be accounts[1]');
    	return tokenInstance.balanceOf(accounts[1]);
    }).then(function(balanceOne) {
    	assert.equal(balanceOne.toNumber(), 10, 'assert transaction was done');
    })
  })
  
  it('check approve', function() {
    var tokenInstance;
    return TimeCoin.deployed().then(function(instance) {
      tokenInstance = instance;
      return tokenInstance.approve.call(accounts[1], 100, {from: accounts[0]});
    }).then(function(success) {
    	assert.equal(success, true, 'approve should return true');
    	return tokenInstance.approve(accounts[1], 100, {from: accounts[0]});
    }).then(function(approved) {
   		assert.equal(approved.logs[0].event, 'Approval', 'event should be "Approval"');
    	assert.equal(approved.logs[0].args._owner,   accounts[0], 'event should be accounts[0]');
    	assert.equal(approved.logs[0].args._spender, accounts[1], 'event should be accounts[1]');
    	return tokenInstance.allowance(accounts[0],accounts[1]);
    }).then(function(approved_amount) {
    	assert.equal(approved_amount, 100, 'approved amount to accounts[1] from accounts[0] not match');
    })
  })
  
  it('delegated transfers', function() {
  	var tokenInstance;
    return TimeCoin.deployed().then(function(instance) {
      tokenInstance = instance;
      fromAccount = accounts[2];
      toAccount = accounts[3];
      spendingAccount = accounts[4];
      return tokenInstance.transfer(fromAccount, 100, {from: accounts[0]});
		}).then(function(receipt) {
			return tokenInstance.approve(spendingAccount, 10, {from: fromAccount});
		}).then(function(receipt) {
			return tokenInstance.transferFrom(fromAccount, toAccount, 11, {from: spendingAccount});
		}).then(assert.fail).catch(function(error) {
			assert(error.message.indexOf('revert') >= 0, 'cannot transfer value bigger then allowance');
			return tokenInstance.transferFrom.call(fromAccount, toAccount, 10, {from: spendingAccount});
		}).then(function(success) {
    	assert.equal(success, true, 'transferFrom should succeed')
    	return tokenInstance.transferFrom(fromAccount, toAccount, 10, {from: spendingAccount});
		}).then(function(receipt) {
    	return tokenInstance.balanceOf(toAccount);
    }).then(function(toBalance) {
    	assert.equal(toBalance.toNumber(), 10, 'transfer gone well');
    }).then(function(receipt) {
    	return tokenInstance.balanceOf(fromAccount);
    }).then(function(fromBalance) {
    	assert.equal(fromBalance.toNumber(), 90, 'transfer gone well');
    	return tokenInstance.allowance(fromAccount,toAccount);
    }).then(function(approved_amount) {
    	assert.equal(approved_amount, 0, 'approved amount to accounts[1] from accounts[0] not match');
    })
  })

})


