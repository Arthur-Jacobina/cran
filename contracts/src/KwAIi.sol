//SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract KwAIi is ERC20 {
    constructor()
        ERC20("KwAIi", "kwAI")
        // Ownable(initialOwner)
    {
        _mint(msg.sender, 100 * 10 ** decimals());
    }

    function mint(address to, uint256 amount) public {
        _mint(to, amount);
    }

    function transfer(address from, address to, uint256 amount) public {
        _transfer(from, to, amount);
    }

    function getBalance(address account) public view returns (uint256) {
        return balanceOf(account);
    }
}   
