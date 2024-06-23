// SPDX-License-Identifier: Apache 2.0
pragma solidity >=0.8.19 <0.9.0;

contract DataStorage {

    address public owner;
    uint256 private number;
    uint public lastUpdateTime;
    uint public lastUpdateBlock;

    constructor() {
        owner = msg.sender;
    }

    function updateNumber(address from, uint _number) public {
        number = _number;
        lastUpdateTime = block.timestamp;
        lastUpdateBlock = block.number;
    }

    function getNum() public view returns(uint) {
        return number;
    }
}
