// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.10;

// with mint
contract DummyERC20Impl {
    uint256 t;
    mapping (address => uint256) b;
    mapping (address => mapping (address => uint256)) a;

    string public name;
    string public symbol;
    uint public decimals;

    function myAddress() public returns (address) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00db0000, 1037618708699) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00db0001, 0) }
        return address(this);
    }

    function add(uint a, uint b) internal pure returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d90000, 1037618708697) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d90001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d91000, a) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00d91001, b) }
        uint c = a +b;
        require (c >= a);
        return c;
    }
    function sub(uint a, uint b) internal pure returns (uint256) {assembly { mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00da0000, 1037618708698) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00da0001, 2) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00da1000, a) mstore(0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff00da1001, b) }
        require (a>=b);
        return a-b;
    }

    function totalSupply() external view returns (uint256) {
        return t;
    }
    function balanceOf(address account) external view returns (uint256) {
        return b[account];
    }
    function transfer(address recipient, uint256 amount) external returns (bool) {
        b[msg.sender] = sub(b[msg.sender], amount);
        b[recipient] = add(b[recipient], amount);
        return true;
    }
    function allowance(address owner, address spender) external view returns (uint256) {
        return a[owner][spender];
    }
    function approve(address spender, uint256 amount) external returns (bool) {
        a[msg.sender][spender] = amount;
        return true;
    }

    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) external returns (bool) {
        b[sender] = sub(b[sender], amount);
        b[recipient] = add(b[recipient], amount);
        a[sender][msg.sender] = sub(a[sender][msg.sender], amount);
        return true;
    }
}