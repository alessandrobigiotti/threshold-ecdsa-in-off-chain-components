// SPDX-License-Identifier: Apache 2.0
pragma solidity >=0.8.19 <0.9.0;
/**
 * @title Target Smart Contract for inter-chain transactions
 * @dev TargetSmartContract is a smart contract that contains functions to execute
 * an inter-chain transaction in the target blockchain. At present, only the use case
 * in which two smart contracts containing data are synchronised is contemplated.
 *
 * @author Alessandro Bigiotti
 */

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

    /**
     * This function is used to execute a synchronisation data transaction across chains.
     *
     * @dev It requires that the sender of this message is equal to the verifier smart contract address.
     * The function first updates the number on the `IUpdateNumber` interface by calling its `updateNumber()`
     * method with service and number as parameters.
     * Then, it creates a header for the transaction which includes details about the chain (chain id),
     * type of transaction, block number, timestamp, sender's address, and receiver's address if provided.
     * It then emits an event named 'eventInterChainTransactionSyncDataExecuted' with from, nonce, and message as parameters.
     *
     * @param _nonce The nonce of the transaction.
     * @param _from The sender of this message.
     * @param service The type of service to be executed.
     * @param number The number to be updated.
     */
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

    /**
     * This function notifies about a bad signature.
     * It requires that the caller be the verifier smart contract.
     * @dev The function emits an event 'eventBadSignature' with details of the bad signature notification.
     * @param _nonce A unique identifier for this transaction.
     * @param _sender The address of the sender.
     */
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

    /** Sets the address of Verifier Smart Contract (`verifierSmartContract`).
     * The `_verificationSC` is the new address to be set. This function can only be called by the owner of this contract.
     * @param _verificationSC The new address for verifier smart contract.
     * @dev Requires that msg.sender (the caller) must be equal to owner of this contract.
     */
    function setVerifierSC(address _verificationSC) public {
        require(msg.sender == owner);
        verifierSmartContract = _verificationSC;

    }

    /**
     * Updates a number on another smart contract (`syncSmartContract`).
     * @dev This function can only be called by this contract itself.
     * It uses the `updateNumber()` function from the IUpdateNumber interface of
     * the other smart contract to update the number.
     * @param service The service identifier as string data.
     * @param number The new number to be updated.
     */
    function updateNumber(string calldata service, uint number) external {
        require(msg.sender == address(this));
        IUpdateNumber(syncSmartContract).updateNumber(address(this), number);
    }

    /**
     * This function creates a header for a message based on given parameters.
     * @dev The header includes information such as source chain ID, type of transaction,
     * block number, timestamp, sender's address and receiver's address (if any).
     * @param sender Address of the sender.
     * @param _type Type of the transaction.
     * @param to Address of the receiver (optional).
     * @return Returns a string containing the header information in JSON format.
     */
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
