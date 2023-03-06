#!/bin/sh
certoraRun src/StaticATokenLM.sol \
    certora/harness/RewardsControllerHarness.sol \
    certora/harness/SymbolicLendingPoolL1.sol \
    lib/aave-v3-core/contracts/protocol/tokenization/AToken.sol \
    certora/harness/TransferStrategyHarness.sol \
    certora/harness/DummyERC20_aTokenUnderlying.sol \
    certora/harness/DummyERC20_rewardToken.sol \
    --verify StaticATokenLM:certora/specs/rewardsPreserve.spec \
    --link StaticATokenLM:_incentivesController=RewardsControllerHarness \
           StaticATokenLM:_pool=SymbolicLendingPoolL1 \
           AToken:POOL=SymbolicLendingPoolL1 \
            StaticATokenLM:_aToken=AToken \
           StaticATokenLM:_aTokenUnderlying=DummyERC20_aTokenUnderlying \
           StaticATokenLM:_rewardToken=DummyERC20_rewardToken \
           AToken:_incentivesController=RewardsControllerHarness \
    --solc solc8.10 \
    --optimistic_loop \
    --optimistic_hashing \
    --settings -t=2250,-mediumTimeout=90,-depth=45 \
	--staging \
    --packages aave-v3-core=lib/aave-v3-core \
               @aave/core-v3=lib/aave-v3-core \
               aave-v3-periphery=lib/aave-v3-periphery \
               solidity-utils=lib/solidity-utils/src \
    --send_only \
	--rule_sanity \
    --msg "Rewards consistency"
