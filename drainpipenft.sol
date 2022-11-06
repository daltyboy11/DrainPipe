// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";

contract DrainPipeNtf is ERC1155("URI") {
    function mint(uint256 id, uint256 amount) external {
        _mint(msg.sender, id, amount, bytes(""));
    }
}