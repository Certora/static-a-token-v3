#!/bin/sh
certoraRun src/StaticATokenLM.sol \
    lib/aave-v3-periphery/contracts/rewards/RewardsController.sol \
    certora/harness/SymbolicLendingPoolL1.sol \
    lib/aave-v3-core/contracts/protocol/tokenization/AToken.sol \
    certora/harness/RewardsDistributorHarness.sol \
    certora/harness/TransferStrategyHarness.sol \
    certora/harness/DummyERC20_aTokenUnderlying.sol \
    certora/harness/DummyERC20_rewardToken.sol \
    --verify StaticATokenLM:certora/specs/StaticATokenLM.spec \
    --link StaticATokenLM:_incentivesController=RewardsController \
           StaticATokenLM:_pool=SymbolicLendingPoolL1 \
           AToken:POOL=SymbolicLendingPoolL1 \
            StaticATokenLM:_aToken=AToken \
           StaticATokenLM:_aTokenUnderlying=DummyERC20_aTokenUnderlying \
           StaticATokenLM:_rewardToken=DummyERC20_rewardToken \
    --solc solc8.10 \
    --optimistic_loop \
    --optimistic_hashing \
    --staging \
    --packages aave-v3-core=lib/aave-v3-core \
               @aave/core-v3=lib/aave-v3-core \
               aave-v3-periphery=lib/aave-v3-periphery \
               solidity-utils=lib/solidity-utils/src \
    --send_only \
    --msg "getClaimableRewards_stable_after_transfer_should_fail --optimistic_hashing "

#    --settings -optimisticUnboundedHashing=true \
#link _aToken _aTokenUnderlying _aToken
#           StaticATokenLM:_aToken=DummyERC20_aToken \
#           StaticATokenLM:_aTokenUnderlying=DummyERC20_aTokenUnderlying \
#           StaticATokenLM:_rewardToken=DummyERC20_rewardToken \
#    certora/harness/ScaledBalanceTokenHarness.sol \
#    lib/aave-v3-periphery/contracts/rewards/transfer-strategies/StakedTokenTransferStrategy.sol \
#    lib/aave-v3-periphery/contracts/rewards/transfer-strategies/PullRewardsTransferStrategy.sol \
    