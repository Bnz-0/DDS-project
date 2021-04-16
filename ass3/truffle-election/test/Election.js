const Election = artifacts.require("Election.sol");

contract('Election', function(accounts) {

  it('basic checks', function() {
    var inst;
    return Election.deployed().then(function(instance) {
      inst = instance;
      return inst.name();
    }).then(function(name) {
      assert.equal(name, 'Cogoleto', 'should be named Cogoleto');
      return inst.vote.call('Pinuccio', {from: accounts[0]});
    }).then(function(success) {
      assert.equal(success, true, 'accounts[0] should vote');
      return inst.vote('Pinuccio', {from: accounts[0]});
    }).then(function(receipt) {
      assert.equal(receipt.logs[0].event, 'VoteParty', 'event should be "Transfer"');
			assert.equal(receipt.logs[0].args._from, accounts[0], 'event should be accounts[0]');
			assert.equal(receipt.logs[0].args._party, 'Pinuccio', 'party voted should be Pinuccio');
  		return inst.parties('Pinuccio');
    }).then(function(pinucciosVotes) {
      assert.equal(pinucciosVotes.toNumber(), 1, 'Pinuccio should have 1 vote');
    })
  })
  
  it('approve checks', function() {
    var inst;
    return Election.deployed().then(function(instance) {
      inst = instance;
      return inst.approve.call(accounts[1], {from: accounts[0]});
    }).then(function(success) {
    	assert.equal(success, true, 'approve should return true');
    	return inst.approve(accounts[1], {from: accounts[0]});
    }).then(function(approved) {
   		assert.equal(approved.logs[0].event, 'Approval', 'event should be "Approval"');
    	assert.equal(approved.logs[0].args._owner, accounts[0], 'event should be accounts[0]');
    	assert.equal(approved.logs[0].args._voter, accounts[1], 'event should be accounts[1]');
    	return inst.allowance(accounts[0],accounts[1]);
    }).then(function(isapproved) {
    	assert.equal(isapproved, true, 'accounts[1] is approved from accounts[0]');
    })
  })
  
  it('delegated voting', function() {
  	var inst;
    return Election.deployed().then(function(instance) {
      inst = instance;
      fromAccount = accounts[2];
      toAccount = accounts[3];
      votingAccount = accounts[4];
			return inst.approve(votingAccount, {from: fromAccount});
		}).then(function(receipt) {
			return inst.voteFor(accounts[5], 'Pinuccio', {from: votingAccount});
		}).then(assert.fail).catch(function(error) {
			assert(error.message.indexOf('revert') >= 0, 'cannot vote for an account not allowed');
			return inst.voteFor.call(fromAccount, 'Pinuccio', {from: votingAccount});
		}).then(function(success) {
    	assert.equal(success, true, 'voteFor should succeed')
    	return inst.voteFor(fromAccount, 'Pinuccio', {from: votingAccount});
		}).then(function(receipt) {
    	return inst.parties('Pinuccio');
    }).then(function(votes) {
    	assert.equal(votes.toNumber(), 1, 'vote gone well');
    }).then(function(receipt) {
    	return inst.hasVoted(fromAccount);
    }).then(function(hasvoted) {
    	assert.equal(hasvoted, true, 'transfer gone well');
    	return inst.allowance(fromAccount,toAccount);
    }).then(function(isapproved) {
    	assert.equal(isapproved, false, 'accounts[1] is not approved from accounts[0] anymore');
    })
  })

})


