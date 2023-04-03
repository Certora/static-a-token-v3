#!/bin/sh
certoraRun  certora/harness/StaticATokenLMHarness.sol \
    certora/harness/RewardsControllerHarness.sol \
    certora/harness/SymbolicLendingPoolL1.sol \
    certora/munged/lib/aave-v3-core/contracts/protocol/tokenization/AToken.sol \
    certora/harness/TransferStrategyHarness.sol \
    certora/harness/ScaledBalanceTokenHarness.sol \
    certora/harness/DummyERC20_aTokenUnderlying.sol \
    certora/harness/DummyERC20_rewardToken.sol \
    --verify StaticATokenLMHarness:certora/specs/ATokenProperties.spec \
    --link StaticATokenLMHarness:INCENTIVES_CONTROLLER=RewardsControllerHarness \
           StaticATokenLMHarness:POOL=SymbolicLendingPoolL1 \
           AToken:POOL=SymbolicLendingPoolL1 \
           StaticATokenLMHarness:_aToken=AToken \
           StaticATokenLMHarness:_aTokenUnderlying=DummyERC20_aTokenUnderlying \
           AToken:_incentivesController=RewardsControllerHarness \
    --solc solc8.10 \
    --optimistic_loop \
    --optimistic_hashing \
    --settings  -t=1400,-mediumTimeout=800,-depth=15    \
    --staging  \
    --packages aave-v3-core=lib/aave-v3-core \
               @aave/core-v3=lib/aave-v3-core \
               aave-v3-periphery=lib/aave-v3-periphery \
               solidity-utils=lib/solidity-utils/src \
               openzeppelin-contracts=lib/openzeppelin-contracts \
    --send_only \
    --rule inv_atoken_scaled_balanceOf_leq_totalSupply \
    --msg " inv_atoken_scaled_balanceOf_leq_totalSupply   "


