// SPDX-License-Identifier: Apache 2.0
pragma solidity >=0.8.19 <0.9.0;
/**
 * @title Source Smart Contract for inter-chain transactions
 * @dev SourceSmartContract is a smart contract that contains functions to start
 * an inter-chain transaction from the source blockchain. At present, only the use case
 * in which two smart contracts containing data are synchronised is contemplated.
 *
 * A user can initiate an inter-chain transaction using the 'interChainTransactionSyncDataStart'.
 * This checks whether the transaction is valid and whether the user has
 * inter-chain transactions pending against him, in which case the transaction is rejected
 *
 * @author Alessandro Bigiotti
 */

import {Strings} from "@openzeppelin/contracts/utils/Strings.sol";

// Specify the functions of the smart contract object of the synchronisation
interface IUpdateNumber {
    function updateNumber(address from, uint _number) external;
    function getNum() external returns(uint);
}

contract SourceSmartContract {

    // Smart Contract Owner
    address public owner;
    // Verifier SC address
    address public verifierSmartContract;

    string constant SYNC_DATA = "SYNC_DATA";
    // The address of the smart contract to synchronise
    address public syncSmartContract;

    // The events used to guide inter-chain transactions
    event eventInterChainTransactionSyncDataStart(address indexed from, uint indexed nonce, string message);
    event eventInterChainTransactionSyncDataEnd(address indexed from, uint indexed nonce, string message);
    event eventBadSignature(address indexed from, uint indexed nonce, string message);

    // These variables manage the user actions. The virtual nonce is used to prevent reply attack.
    // The lock is used to regulate the seding of inter-chain transactions.
    mapping(address => uint) public userNonce;
    mapping(address => bool) public userLock;


    constructor(address _syncSmartContract) {
        owner = msg.sender;
        syncSmartContract = _syncSmartContract;
    }

    /**
     * @dev Function to start an inter-chain transaction sync data.
     * This function starts an interchain transaction by updating the number and emits a corresponding event.
     * Only one transaction can be started per sender at any given time.
     * The nonce is expected to be incremented by 1 from the last transaction of the sender.
     * @param _nonce The nonce of the transaction.
     * @param service The service associated with this number update.
     * @param number The new number value.
     */
    function interChainTransactionSyncDataStart(
        uint _nonce, string calldata service, uint256 number
    ) public {
        require(userNonce[msg.sender]+1 == _nonce);
        require(userLock[msg.sender] == false);

        this.updateNumber(service, number);

        string memory numString = Strings.toString(number);
        string memory header = createHeader(msg.sender,  SYNC_DATA, "");

        string memory body = string.concat(
            '"body":{',
            '   "instructions":{',
            '       "service":"', SYNC_DATA,'",',
            '       "function":"interChainTransactionSyncDataExecute"',
            '   },'
            '   "content":{'
            '       "value":"', numString, '"',
            '   }',
            '}'
        );
        userLock[msg.sender] = true;
        userNonce[msg.sender] = _nonce;
        string memory message = string.concat('{', header, body,'}');
        emit eventInterChainTransactionSyncDataStart(msg.sender, _nonce, message);

    }

    /**
     * @dev This function notifies that an Inter-chain transaction has ended.
     * It emits an event with the details of the transaction and updates user's lock status.
     *
     * Requirements:
     * - The caller (msg.sender) must be equal to the verifierSmartContract address.
     *
     * @param _nonce The nonce associated with this transaction. It should be one
     * greater than the previous nonce for the sender.
     * @param _sender The address of the user who initiated the transaction.
     * @param number The number associated with this transaction.
     */
    function interChainTransactionSyncDataEnd(
        uint _nonce, address _sender, uint256 number
    ) public {
        require(msg.sender == verifierSmartContract);

        userLock[_sender] = false;
        string memory header = createHeader(msg.sender, "Inter-Chain-TX-END", "");
        string memory body = string.concat(
            '"body":{',
            '   "instructions":{',
            '       "service":"', SYNC_DATA,'",',
            '   }',
            '}'
        );

        string memory message = string.concat('{', header, body,'}');
        emit eventInterChainTransactionSyncDataEnd(_sender, _nonce, message);
    }

    /**
     * Brief: This function notifies about a bad signature during an Inter-chain transaction.
     * It emits an event with the details of the transaction.
     *
     * Requirements:
     * - The caller (msg.sender) must be equal to the verifierSmartContract address.
     *
     * @dev This function is used to handle bad signature scenarios in Inter-chain
     * transactions. When a bad signature occurs, it's crucial to notify the other
     * party involved so they can take appropriate action if needed.
     *
     * @param _nonce The nonce associated with this transaction. It should be one
     * greater than the previous nonce for the sender.
     * @param _sender The address of the user who initiated the transaction.
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

    function getNumber() public returns(uint) {
        return this.getNumberInternal();
    }


    function updateNumber(string calldata service, uint number) external {
        require(msg.sender == address(this));
        IUpdateNumber(syncSmartContract).updateNumber(address(this), number);
    }

    function getNumberInternal() external returns(uint) {
        return IUpdateNumber(syncSmartContract).getNum();
    }

    function setVerifierSC(address _verificationSC) public {
        require(msg.sender == owner);
        verifierSmartContract = _verificationSC;

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
            '   "sender":"', Strings.toHexString(uint256(uint160(sender)), 20),'"},');
        }
        return header;
    }

}
