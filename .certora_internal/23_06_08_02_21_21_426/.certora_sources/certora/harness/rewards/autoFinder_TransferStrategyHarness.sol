
pragma solidity ^0.8.10;

import {IERC20} from '../../../lib/aave-v3-core/contracts/dependencies/openzeppelin/contracts/IERC20.sol';
import { TransferStrategyBase } from '/Users/dev1644/workspace/workspace-west/aave-certora/.certora_internal/23_06_08_02_21_21_426/.certora_sources/lib/aave-v3-periphery/contracts/rewards/transfer-strategies/autoFinder_TransferStrategyBase.sol';

contract TransferStrategyHarness is TransferStrategyBase{

constructor(address incentivesController, address rewardsAdmin) TransferStrategyBase(incentivesController, rewardsAdmin) {}

    IERC20 public REWARD;

    // executes the actual transfer of the reward to the receiver
    function performTransfer(
        address to,
        address reward,
        uint256 amount
    ) external override(TransferStrategyBase) returns (bool){
        require(reward == address(REWARD));
        return REWARD.transfer(to, amount);
    }
}