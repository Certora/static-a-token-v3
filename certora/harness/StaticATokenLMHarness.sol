// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.10;

import {StaticATokenLM} from 'src/StaticATokenLM.sol';

contract StaticATokenLMHarness is StaticATokenLM{
    function previewAndDepositCallHelper(uint256    assets, 
                                         address    recipient) public returns (uint256, uint256){
        uint256 previewShares = previewDeposit(assets);
        uint256 shares = deposit(assets, recipient);
        return (previewShares, shares);
    }

    function previewAndMintCallHelper(uint256 shares, address receiver) public returns (uint256, uint256){
        uint256 previewAssets = previewMint(shares);
        uint256 assets = mint(shares, receiver);
        return (previewAssets, assets);
    }

    function previewAndWithdrawCallHelper(uint256 assets, address receiver, address owner) public returns (uint256, uint256){
        uint256 previewShares = previewWithdraw(assets);
        uint256 shares = withdraw(assets, receiver, owner);
        return (previewShares, shares);

    }
}