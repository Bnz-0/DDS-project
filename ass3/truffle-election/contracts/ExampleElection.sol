// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

import "./IElection.sol";
import "./Election.sol";

contract ExampleElection is IElection, Election {
	string public constant name = "ExampleElection";
	uint public constant deadline = 1618570000;

	constructor() Election( deadline ) public {
	}
}
