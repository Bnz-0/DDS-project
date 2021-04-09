// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.7.0 <0.9.0;

contract Test {
	uint x;
	mapping(string => uint) map;

	constructor() {
		x = 42;
	}

	function sum(int a, int b) public pure returns (int) {
		return a + b;
	}

	function getX() public view returns (uint) {
		return x;
	}

	function setX(uint newX) public {
		x = newX;
	}

	function add(string memory s) public returns (uint) {
		map[s] += 1;
		return map[s];
	}
}

/*
get contract by address: web3.eth.contract(ABI).at(ADDRESS)
do a transaction: contract.set.sendTransaction(15, {from: eth.accounts[0]})

*/
