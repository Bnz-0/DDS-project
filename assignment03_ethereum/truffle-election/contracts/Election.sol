// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

import "./IElection.sol";

contract Election is IElection {

	string public name;
	uint public deadline;

	mapping(address => bool) public hasVoted;
	mapping(string => uint256) public parties;
	mapping(address => mapping(address => bool)) public allowance;

	constructor(uint _deadline) {
		deadline = _deadline;
	}

	function vote(string memory _party) override public returns (bool success) {
		require(!hasVoted[msg.sender], "The voter has already voted");
		require(block.timestamp < deadline, "The deadline is over");

		hasVoted[msg.sender] = true;
		parties[_party] += 1;

		emit VoteParty(msg.sender, _party);

		return true;
	}

	function approve(address _voter) override public returns (bool success) {
		allowance[msg.sender][_voter] = true;

		emit Approval(msg.sender, _voter);

		return true;
	}

	function voteFor(address _from, string memory _party) override public returns (bool success) {
		require(allowance[_from][msg.sender], "Not approved by the voter");
		require(!hasVoted[_from], "The voter has already voted");
		require(block.timestamp < deadline, "The deadline is over");

		allowance[_from][msg.sender] = false;
		parties[_party] += 1;
		hasVoted[_from] = true;

		emit VoteParty(_from, _party);

		return true;
	}
}
