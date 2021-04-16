pragma solidity >=0.4.22 <0.9.0;


interface IElection {
	function vote(string calldata _party) external returns (bool success);
	function approve(address _voter) external returns (bool success);
	function voteFor(address _from, string calldata _party) external returns (bool success);

	event VoteParty(
		address indexed _from,
		string _party
	);
  
  event Approval(
    address indexed _owner,
    address indexed _voter
  );
}
