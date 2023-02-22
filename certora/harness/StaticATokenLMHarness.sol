// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.10;

import {StaticATokenLM} from 'certora/munged/StaticATokenLM.sol';
import {IERC20} from 'solidity-utils/contracts/oz-common/interfaces/IERC20.sol';

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

    function getULBalanceOf(address recipient) public returns (uint256 balance){
        balance = IERC20(_aTokenUnderlying).balanceOf(recipient);
    }

    function getATokenBalanceOf(address recipient) public returns (uint256 balance){
        balance = _aToken.balanceOf(recipient);
    }

    function metaWithdrawCallHelper(address owner,
                                    address recipient, 
                                    uint256 shares, 
                                    uint256 assets, 
                                    bool toUnderlying, 
                                    uint256 deadline, 
                                    uint8 v, 
                                    bytes32 r, 
                                    bytes32 s) 
                                    
                                    public returns (uint256 sharesBurnt, uint256 assetsReceived){
        
        SignatureParams memory SP = SignatureParams(v, r, s);
        (sharesBurnt, assetsReceived) = metaWithdraw(owner, recipient, shares, assets, toUnderlying, deadline, SP);

    }

    function metaDepositHelper(    address depositor,
                                    address recipient,
                                    uint256 value,
                                    uint16 referralCode,
                                    bool fromUnderlying,
                                    uint256 deadline,
                                    PermitParams calldata permit,
                                    SignatureParams calldata sigParams) public returns (bool fromUnderlying_, uint256 value_){
        uint256 shares = metaDeposit(depositor, recipient, value, referralCode, fromUnderlying, deadline, permit, sigParams);
        fromUnderlying_ = fromUnderlying;
        value_ = value;
    }
    
    function previewAndRedeemHelper(uint256 shares, address receiver, address owner) public returns (uint256 previewAssets, uint256 assets){
        previewAssets = previewRedeem(shares);
        assets = redeem(shares, receiver, owner);
    }

    function assetsTotal(address account) public returns (uint256 assets){
        assets = _aToken.balanceOf(account) + IERC20(_aTokenUnderlying).balanceOf(account);

    }
}