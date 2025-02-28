// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.9;

import {ECDSAServiceManagerBase} from
    "../lib/eigenlayer-middleware/src/unaudited/ECDSAServiceManagerBase.sol";
import {ECDSAStakeRegistry} from "../lib/eigenlayer-middleware/src/unaudited/ECDSAStakeRegistry.sol";
import {IServiceManager} from "../lib/eigenlayer-middleware/src/interfaces/IServiceManager.sol";
import "../lib/fhenix-contracts/contracts/FHE.sol";

// import {ECDSAUpgradeable} from
//     "../lib/openzeppelin-upgrades/contracts/utils/cryptography/ECDSAUpgradeable.sol";
// import {IERC1271Upgradeable} from
//     "../lib/openzeppelin-upgrades/contracts/interfaces/IERC1271Upgradeable.sol";
// import "../lib/openzeppelin/contracts/utils/Strings.sol";
// import "../lib/eigenlayer/contracts/interfaces/IRewardsCoordinator.sol";
// import {TransparentUpgradeableProxy} from
//     "../lib/openzeppelin/contracts/proxy/transparent/TransparentUpgradeableProxy.sol";

import {IEncryptVectorServiceManager} "./IEncryptVectorServiceManager.sol";


contract EncryptVectorServiceManager is ECDSAServiceManagerBase, IEncryptVectorServiceManager {
    // using ECDSAUpgradeable for bytes32;

    uint32 public latestTaskNum;
    mapping(uint32 => bytes32) public allTaskHashes;

    mapping(address => mapping(uint32 => bytes)) public allTaskResponses;

    modifier onlyOperator() {
        require(
            ECDSAStakeRegistry(stakeRegistry).operatorRegistered(msg.sender),
            "Operator must be the caller"
        );
        _;
    }

    constructor(
        address _avsDirectory,
        address _stakeRegistry,
        address _rewardsCoordinator,
        address _delegationManager
    )
        ECDSAServiceManagerBase(_avsDirectory, _stakeRegistry, _rewardsCoordinator, _delegationManager)
    {}

    function initialize(address initialOwner, address _rewardsInitiator) external initializer {
        __ServiceManagerBase_init(initialOwner, _rewardsInitiator);
    }

    function encryptNumber(uint256 plaintextValue) public returns (euint256){
        return FHE.asEuint256(plaintextValue);
    }

    function getEncryptedValue(Task task, Permission memory permission) public view returns (bytes memory) {
        return FHE.sealoutput(encryptNumber(task.vector_hash), permission.publicKey);
    }
        
    function createNewTask(
        string memory name,
        uint256 vector_hash
    ) external returns (Task memory) {
        // create a new task struct
        Task memory newTask;
        newTask.name = name;
        newTask.vector_hash = vector_hash;
        newTask.taskCreatedBlock = uint32(block.number);

        allTaskHashes[latestTaskNum] = keccak256(abi.encode(newTask));
        encrypted_vector_hash = encryptNumber(vector_hash);
        emit NewTaskCreated(latestTaskNum, newTask);
        latestTaskNum = latestTaskNum + 1;

        return newTask;
    }

    function respondToTask(
        Task calldata task,
        uint32 referenceTaskIndex,
        bytes memory signature
    ) external {
        require(
            keccak256(abi.encode(task)) == allTaskHashes[referenceTaskIndex],
            "supplied task does not match the one recorded in the contract"
        );
        require(
            allTaskResponses[msg.sender][referenceTaskIndex].length == 0,
            "Operator has already responded to the task"
        );

        bytes32 messageHash = keccak256(abi.encodePacked("Encrypt", task.name));
        bytes32 ethSignedMessageHash = messageHash.toEthSignedMessageHash();
        bytes4 magicValue = IERC1271Upgradeable.isValidSignature.selector;
        bytes4 isValidSignatureResult =
            ECDSAStakeRegistry(stakeRegistry).isValidSignature(ethSignedMessageHash, signature);

        require(magicValue == isValidSignatureResult);

        allTaskResponses[msg.sender][referenceTaskIndex] = signature;

        emit TaskResponded(referenceTaskIndex, task, msg.sender);
    }
}
