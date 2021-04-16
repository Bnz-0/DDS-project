// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

import "./IElection.sol";

contract Election is IElection {

  string public name;
  uint public deadline;
  
  mapping(address => bool) public hasVoted;
  mapping(string => uint256) public parties;
  mapping(address => mapping(address => bool)) public allowance;

  constructor(uint _deadline) public {
    deadline = _deadline;
  }
  
  function vote(string memory _party) public returns (bool success) {
    require(hasVoted[msg.sender] == false, "The voter has already voted");
    require(block.timestamp < deadline);
    
    hasVoted[msg.sender] = true;
    parties[_party] += 1; 
    
    emit VoteParty(msg.sender, _party);
    
    return true;
  }
  
  function approve(address _voter) public returns (bool success) {
  	allowance[msg.sender][_voter] = true;
  	
  	emit Approval(msg.sender, _voter);
  	
  	return true;
  }
  
  function voteFor(address _from, string memory _party) public returns (bool success) {
  	require(allowance[_from][msg.sender] == true, "Not approved by the voter");
  	require(hasVoted[_from] == false, "The voter has already voted");
	require(block.timestamp < deadline);
  	
  	allowance[_from][msg.sender] = false;
  	parties[_party] += 1;
  	hasVoted[_from] = true;
  	
  	emit VoteParty(_from, _party);
  	
  	return true;
  }
}
