#!/bin/sh
certoraRun  certora/harness/StaticATokenLMHarness.sol \
    certora/harness/RewardsControllerHarness.sol \
    certora/harness/SymbolicLendingPoolL1.sol \
    lib/aave-v3-core/contracts/protocol/tokenization/AToken.sol \
    certora/harness/TransferStrategyHarness.sol \
    certora/harness/ScaledBalanceTokenHarness.sol \
    certora/harness/DummyERC20_aTokenUnderlying.sol \
    certora/harness/DummyERC20_rewardToken.sol \
    --verify StaticATokenLMHarness:certora/specs/StaticATokenLM.spec \
    --link StaticATokenLMHarness:INCENTIVES_CONTROLLER=RewardsControllerHarness \
           StaticATokenLMHarness:POOL=SymbolicLendingPoolL1 \
           AToken:POOL=SymbolicLendingPoolL1 \
            StaticATokenLMHarness:_aToken=AToken \
           StaticATokenLMHarness:_aTokenUnderlying=DummyERC20_aTokenUnderlying \
           AToken:_incentivesController=RewardsControllerHarness \
    --solc solc8.10 \
    --optimistic_loop \
    --optimistic_hashing \
    --settings -t=2000,-mediumTimeout=900,-depth=14   \
    --staging \
    --packages aave-v3-core=lib/aave-v3-core \
               @aave/core-v3=lib/aave-v3-core \
               aave-v3-periphery=lib/aave-v3-periphery \
               solidity-utils=lib/solidity-utils/src \
    --send_only \
    --rule totalAssets_stable_after_collectAndUpdateRewards_zero_accrued_valid_asset \
    --msg "totalAssets_stable_after_collectAndUpdateRewards_zero_accrued_valid_asset"


#           StaticATokenLM:_rewardToken=DummyERC20_rewardToken \
# -t=1500,-mediumTimeout=60,-depth=30 for inv_atoken_balanceOf_leq_totalSupply 2 hours
# -t=1200,-mediumTimeout=1200,-depth=10 - best for   getClaimableRewards_increase_after_deposit_8 (25 min)
# -t=600,-mediumTimeout=40,-depth=45  - best for getClaimableRewards_decrease_after_deposit_7 (25)
# -t=1500,-mediumTimeout=60,-depth=30 - getClaimableRewards_decrease_after_deposit finished after 15 minutes
# -t=1000,-mediumTimeout=100,-depth=10 \
# 
#    --rule inv_balanceOf_leq_totalSupply inv_atoken_balanceOf_leq_totalSupply sumAllBalance_eq_totalSupply sumAllATokenBalance_eq_totalSupply inv_atoken_scaled_balanceOf_leq_totalSupply\
#    --rule getClaimableRewardsBefore_geq_calimed_claimRewardsOnBehalf getClaimableRewardsBefore_eq_calimed_claimRewardsOnBehalf getClaimableRewardsBefore_leq_calimed_claimRewardsOnBehalf\

    