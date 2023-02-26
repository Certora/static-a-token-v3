#!/bin/sh
certoraRun src/StaticATokenLM.sol \
    certora/harness/RewardsControllerHarness.sol \
    certora/harness/SymbolicLendingPoolL1.sol \
    lib/aave-v3-core/contracts/protocol/tokenization/AToken.sol \
    certora/harness/TransferStrategyHarness.sol \
    certora/harness/DummyERC20_aTokenUnderlying.sol \
    certora/harness/DummyERC20_rewardToken.sol \
    --verify StaticATokenLM:certora/specs/StaticATokenLM.spec \
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
    --settings -t=1200,-mediumTimeout=1200,-depth=10  \
    --staging \
    --packages aave-v3-core=lib/aave-v3-core \
               @aave/core-v3=lib/aave-v3-core \
               aave-v3-periphery=lib/aave-v3-periphery \
               solidity-utils=lib/solidity-utils/src \
    --send_only \
    --rule getClaimableRewards_increase_after_deposit_8 \
    --msg "getClaimableRewards_increase_after_deposit_8 wo handleAction"

# 
#certora/harness/RewardsDistributorHarness.sol \
   # -t=1200,-mediumTimeout=1200,-depth=10 - best for   getClaimableRewards_increase_after_deposit_8 (25 min)
#  -t=600,-mediumTimeout=40,-depth=45  - best for getClaimableRewards_decrease_after_deposit_7 (25)
# --settings -t=1500,-mediumTimeout=60,-depth=30 - getClaimableRewards_decrease_after_deposit finished after 15 minutes
#    --rule inv_balanceOf_leq_totalSupply inv_atoken_balanceOf_leq_totalSupply sumAllBalance_eq_totalSupply sumAllATokenBalance_eq_totalSupply inv_atoken_scaled_balanceOf_leq_totalSupply\

#    --optimistic_hashing \
#    --settings -t=1000,-mediumTimeout=100,-depth=10 \
#    --settings -optimisticUnboundedHashing=true \
#link _aToken _aTokenUnderlying _aToken
#           StaticATokenLM:_aToken=DummyERC20_aToken \
#           StaticATokenLM:_aTokenUnderlying=DummyERC20_aTokenUnderlying \
#           StaticATokenLM:_rewardToken=DummyERC20_rewardToken \
#    certora/harness/ScaledBalanceTokenHarness.sol \
#    lib/aave-v3-periphery/contracts/rewards/transfer-strategies/StakedTokenTransferStrategy.sol \
#    lib/aave-v3-periphery/contracts/rewards/transfer-strategies/PullRewardsTransferStrategy.sol \
    