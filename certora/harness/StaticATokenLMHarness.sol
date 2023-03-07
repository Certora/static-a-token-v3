// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.10;

import {StaticATokenLM} from 'certora/munged/StaticATokenLM.sol';
import {IERC20} from 'solidity-utils/contracts/oz-common/interfaces/IERC20.sol';

contract StaticATokenLMHarness is StaticATokenLM{
    


    function getULBalanceOf(address recipient) public returns (uint256 balance){
        balance = IERC20(_aTokenUnderlying).balanceOf(recipient);
    }

    function getATokenBalanceOf(address recipient) public returns (uint256 balance){
        balance = _aToken.balanceOf(recipient);
    }

    // function metaWithdrawCallHelper(address owner,
    //                                 address recipient, 
    //                                 uint256 shares, 
    //                                 uint256 assets, 
    //                                 bool toUnderlying, 
    //                                 uint256 deadline, 
    //                                 uint8 v, 
    //                                 bytes32 r, 
    //                                 bytes32 s) 
                                    
    //                                 public returns (uint256 sharesBurnt, uint256 assetsReceived){
        
    //     SignatureParams memory SP = SignatureParams(v, r, s);
    //     (sharesBurnt, assetsReceived) = metaWithdraw(owner, recipient, shares, assets, toUnderlying, deadline, SP);

    // }

    // function metaDepositHelper(    address depositor,
    //                                 address recipient,
    //                                 uint256 value,
    //                                 uint16 referralCode,
    //                                 bool fromUnderlying,
    //                                 uint256 deadline,
    //                                 PermitParams calldata permit,
    //                                 SignatureParams calldata sigParams) public returns (bool fromUnderlying_, uint256 value_){
    //     uint256 shares = metaDeposit(depositor, recipient, value, referralCode, fromUnderlying, deadline, permit, sigParams);
    //     fromUnderlying_ = fromUnderlying;
    //     value_ = value;
    // }
    

    function assetsTotal(address account) public returns (uint256 assets){
        assets = _aToken.balanceOf(account) + IERC20(_aTokenUnderlying).balanceOf(account);

    }

    function getStaticATokenUnderlying() public view returns (address){
        return _aTokenUnderlying;
    }
    

    function upperBound(uint256 index) public returns (uint256){
        return (index/ (2*1e27));
    }

}