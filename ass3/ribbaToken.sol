// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.7.0 <0.8.0;

contract ribbaToken{

    // state variables
   string public name = "ribbaToken";
   string public symbol = "RIB";
   uint256 public totalSupply = 1000000;

   mapping (address => uint256) public balances;
   mapping (address => mapping (address => uint256)) public allowed;

   event Transfer(address indexed _from, address indexed _to, uint256 _value);
   event Approval(address indexed _owner, address indexed _spender, uint256 _value);

   constructor() {
      // the totalSupply belongs to the contract creator
      balances[msg.sender] = totalSupply;
   }


   function transfer(address _to, uint256 _value) public returns (bool) {
      // if the sender has enough tokens
      if (balances[msg.sender] >= _value) {

      balances[msg.sender] -= _value;
      balances[_to] += _value;
      emit Transfer(msg.sender, _to, _value);
      return true;
      }
      else 
      return false;
    }

     function approve(address _spender, uint256 _value) public returns (bool) {
        allowed[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }

    function transferFrom(address _from, address _to, uint256 _value) public returns (bool) {

        // the _from account has enough tokens
        require(balances[_from] >= _value);

         // the allowance is big enoung
        require(allowed[_from][msg.sender] >= _value);

        // change the balance
        balances[_to] += _value;
        balances[_from] -= _value;

        // update the allowance
        allowed[_from][msg.sender] -= _value;

        emit Transfer(_from, _to, _value);
        return true;
    }

    function balanceOf(address _owner) public view returns (uint256) {
        return balances[_owner];
    }


    function allowance(address _owner, address _spender) public view returns (uint256) {
        return allowed[_owner][_spender];
    }

}