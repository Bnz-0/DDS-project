// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

import "./IElection.sol";

contract Election is IElection {

  string public name;
  uint public deadline;
  
  mapping(address => bool) public hasVoted;
  mapping(string => uint256) public parties;
  mapping(address => mapping(address => bool)) public allowance;

  constructor(string memory _name, uint _deadline) public {
    deadline = _deadline;
    name = _name;
  }
  
  function vote(string memory _party) public returns (bool success) {
    require(hasVoted[msg.sender] == false);
    require(now < deadline);
    
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
  	require(allowance[_from][msg.sender] == true);
  	require(hasVoted[_from] == false);
	require(now < deadline);
  	
  	allowance[_from][msg.sender] = false;
  	parties[_party] += 1;
  	hasVoted[_from] = true;
  	
  	emit VoteParty(_from, _party);
  	
  	return true;
  }
}
