// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract TimeCoin {

  uint256 public totalSupply;
  string public name = "TimeCoin";
  string public symbol = "TMC";
  
  mapping(address => uint256) public balanceOf;
  mapping(address => mapping(address => uint256)) public allowance;

  event Transfer(
    address indexed _from,
    address indexed _to,
    uint256 _value
  );
  
  event Approval(
  	address indexed _owner,
    address indexed _spender,
    uint256 _value
  );

  constructor() public {
    totalSupply = 1000000000;
    balanceOf[msg.sender] = totalSupply;
  }
  
  function transfer(address _to, uint256 _value) public returns (bool success) {
    require(balanceOf[msg.sender] >= _value);
    balanceOf[_to] += _value;
    balanceOf[msg.sender] -= _value;
    
    emit Transfer(msg.sender, _to, _value);
    
    return true;
  }
  
  function approve(address _spender, uint256 _value) public returns (bool success) {
  	allowance[msg.sender][_spender] = _value;
  	
  	emit Approval(msg.sender, _spender, _value);
  	
  	return true;
  }
  
  function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
  	require(allowance[_from][msg.sender] >= _value);
  	require(balanceOf[_from] >= _value);
  	
  	balanceOf[_from] -= _value;
  	balanceOf[_to] += _value;
  	
  	allowance[_from][msg.sender] -= _value;
  	
  	emit Transfer(_from, _to, _value);
  	
  	return true;
  }
}
