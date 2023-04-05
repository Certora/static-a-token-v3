#!/bin/sh
certoraRun  certora/harness/StaticATokenLMHarness.sol \
    certora/harness/RewardsControllerHarness.sol \
    certora/harness/SymbolicLendingPoolL1.sol \
    certora/munged/lib/aave-v3-core/contracts/protocol/tokenization/AToken.sol \
    certora/harness/TransferStrategyHarness.sol \
    certora/harness/ScaledBalanceTokenHarness.sol \
    certora/harness/DummyERC20_aTokenUnderlying.sol \
    certora/harness/DummyERC20_rewardToken.sol \
    --verify StaticATokenLMHarness:certora/specs/atoken_balance.spec \
    --link StaticATokenLMHarness:INCENTIVES_CONTROLLER=RewardsControllerHarness \
           StaticATokenLMHarness:POOL=SymbolicLendingPoolL1 \
           AToken:POOL=SymbolicLendingPoolL1 \
            StaticATokenLMHarness:_aToken=AToken \
           StaticATokenLMHarness:_aTokenUnderlying=DummyERC20_aTokenUnderlying \
           AToken:_incentivesController=RewardsControllerHarness \
    --solc solc8.10 \
    --optimistic_loop \
	--loop_iter 1 \
    --optimistic_hashing \
    --settings -t=7200,-mediumTimeout=20,-depth=20  \
    --cloud \
    --packages aave-v3-core=certora/munged/lib/aave-v3-core \
               @aave/core-v3=certora/munged/lib/aave-v3-core \
               aave-v3-periphery=certora/munged/lib/aave-v3-periphery \
               solidity-utils=certora/munged/lib/solidity-utils/src \
               openzeppelin-contracts=lib/openzeppelin-contracts \
	--msg "aToken balance" \
