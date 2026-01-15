// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HealthScheme {

    struct Application {
        uint schemeId;
        uint timestamp;
        bool applied;
    }

    mapping(address => Application) private applications;

    event SchemeApplied(address indexed user, uint schemeId, uint timestamp);

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
}
