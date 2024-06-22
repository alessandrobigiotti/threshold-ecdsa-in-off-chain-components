// SPDX-License-Identifier: Apache 2.0
pragma solidity >=0.8.19 <0.9.0;

import {Strings} from "@openzeppelin/contracts/utils/Strings.sol";

interface IUpdateNumber {
    function updateNumber(address from, uint _number) external;
    function getNum() external returns(uint);
}

contract TargetSmartContract {

    address public owner;
    // Verifier SC address
    address public verifierSmartContract;

    string constant SYNC_DATA = "SYNC_DATA";

    address public syncSmartContract;

    event eventInterChainTransactionSyncDataExecuted(address indexed from, uint indexed nonce, string message);
    event eventBadSignature(address indexed from, uint indexed nonce, string message);

    constructor(address _syncSmartContract) {
        owner = msg.sender;
        syncSmartContract = _syncSmartContract;
    }

    function interChainTransactionSyncDataExecute(
        uint _nonce, address _from, string calldata service, uint256 number) public {
        require(msg.sender == verifierSmartContract);

        this.updateNumber(service, number);

        string memory numString = Strings.toString(number);
        string memory header = createHeader(_from, SYNC_DATA, "");
        string memory body = string(string.concat(
            '"body":{',
            '   "content":{'
            '       "value":"', numString, '"',
            '   }',
            '}'
        ));

        string memory message = string.concat('{', header, body, '}');
        emit eventInterChainTransactionSyncDataExecuted(_from, _nonce, message);

    }

    function badSignatureNotify(uint _nonce, address _sender) public {
        require(msg.sender == verifierSmartContract);

        string memory header = createHeader(msg.sender, "Bad-Signature", "");
        string memory body = string.concat(
            '"body":{',
            '   "instructions":{',
            '       "service":"', SYNC_DATA,'",',
            '   }',
            '}'
        );

        string memory message = string.concat('{', header, body,'}');
        emit eventBadSignature(_sender, _nonce, message);

    }

    function setVerifierSC(address _verificationSC) public {
        require(msg.sender == owner);
        verifierSmartContract = _verificationSC;

    }

    function updateNumber(string calldata service, uint number) external {
        require(msg.sender == address(this));
        IUpdateNumber(syncSmartContract).updateNumber(address(this), number);
    }


    function createHeader(address sender, string memory _type, string memory to) private view returns(string memory) {
        string memory header;
        if (bytes(to).length != 0) {
            header = string.concat(
            '"header":{',
            '   "source_chain":"',Strings.toString(block.chainid),'",',
            '   "type":"',_type,'",',
            '   "block_number":"' ,Strings.toString(block.number),'",',
            '   "timestamp":"', Strings.toString(block.timestamp),'",',
            '   "sender":"', Strings.toHexString(uint256(uint160(sender)), 20),'",',
            '   "receiver":"',to,'"},');

        } else {
            header = string.concat(
            '"header":{',
            '   "source_chain":"',Strings.toString(block.chainid),'",',
            '   "type":"',_type,'",',
            '   "block_number":"' ,Strings.toString(block.number),'",',
            '   "timestamp":"', Strings.toString(block.timestamp),'",',
            '   "sender":"', Strings.toHexString(sender),'"},');
        }

        return header;
    }
}
