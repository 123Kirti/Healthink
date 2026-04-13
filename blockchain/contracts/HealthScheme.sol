// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HealthScheme {
    address public owner;

    struct Application {
        uint schemeId;
        uint timestamp;
        bool applied;
    }

    struct Record {
        bytes32 recordHash;
        bytes32 userHash;
        string recordType;
        uint timestamp;
    }

    mapping(address => Application) private applications;
    Record[] private records;

    event SchemeApplied(address indexed user, uint schemeId, uint timestamp);
    event RecordStored(uint indexed recordId, bytes32 recordHash, bytes32 indexed userHash, string recordType, uint timestamp);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function applyForScheme(uint _schemeId) public {
        require(!applications[msg.sender].applied, "Already applied for a scheme");
        require(_schemeId > 0, "Invalid scheme ID");

        applications[msg.sender] = Application({
            schemeId: _schemeId,
            timestamp: block.timestamp,
            applied: true
        });

        emit SchemeApplied(msg.sender, _schemeId, block.timestamp);
    }

    function getApplication(address _user) public view returns (uint, uint, bool) {
        Application memory app = applications[_user];
        return (app.schemeId, app.timestamp, app.applied);
    }

    function storeRecord(bytes32 _recordHash, bytes32 _userHash, string memory _recordType) public onlyOwner returns (uint) {
        records.push(Record({
            recordHash: _recordHash,
            userHash: _userHash,
            recordType: _recordType,
            timestamp: block.timestamp
        }));

        uint recordId = records.length - 1;
        emit RecordStored(recordId, _recordHash, _userHash, _recordType, block.timestamp);
        return recordId;
    }

    function getRecord(uint _recordId) public view onlyOwner returns (bytes32, bytes32, string memory, uint) {
        require(_recordId < records.length, "Invalid record ID");
        Record memory record = records[_recordId];
        return (record.recordHash, record.userHash, record.recordType, record.timestamp);
    }

    function getRecordCount() public view onlyOwner returns (uint) {
        return records.length;
    }
}
