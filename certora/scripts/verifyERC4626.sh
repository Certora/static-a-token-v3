
if [[ "$1" ]]
then
    RULE="--rule $1"
fi

if [[ "$2" ]]
then
    MSG="- $2"
fi

certoraRun certora/harness/StaticATokenLMHarness.sol \
    lib/aave-v3-periphery/contracts/rewards/RewardsController.sol \
    certora/harness/SymbolicLendingPoolL1.sol \
    lib/aave-v3-core/contracts/protocol/tokenization/AToken.sol \
    certora/harness/RewardsDistributorHarness.sol \
    certora/harness/TransferStrategyHarness.sol \
    certora/harness/DummyERC20_aTokenUnderlying.sol \
    certora/harness/DummyERC20_rewardToken.sol \
    --verify StaticATokenLMHarness:certora/specs/erc4626.spec \
    --link StaticATokenLMHarness:_incentivesController=RewardsController \
           StaticATokenLMHarness:_pool=SymbolicLendingPoolL1 \
           AToken:POOL=SymbolicLendingPoolL1 \
            StaticATokenLMHarness:_aToken=AToken \
           StaticATokenLMHarness:_aTokenUnderlying=DummyERC20_aTokenUnderlying \
           StaticATokenLMHarness:_rewardToken=DummyERC20_rewardToken \
    --solc solc8.10 \
    --optimistic_loop \
    --packages aave-v3-core=lib/aave-v3-core \
               @aave/core-v3=lib/aave-v3-core \
               aave-v3-periphery=lib/aave-v3-periphery \
               solidity-utils=lib/solidity-utils/src \
    --send_only \
    --staging \
    --rule_sanity basic \
    --settings -optimisticUnboundedHashing=true \
    --settings -hashingLengthBound=224 \
    $RULE \
    --msg "StaticAToken - $RULE $MSG  "

#link _aToken _aTokenUnderlying _aToken
#           StaticATokenLM:_aToken=DummyERC20_aToken \
#           StaticATokenLM:_aTokenUnderlying=DummyERC20_aTokenUnderlying \
#           StaticATokenLM:_rewardToken=DummyERC20_rewardToken \
#    certora/harness/ScaledBalanceTokenHarness.sol \
#    lib/aave-v3-periphery/contracts/rewards/transfer-strategies/StakedTokenTransferStrategy.sol \
#    lib/aave-v3-periphery/contracts/rewards/transfer-strategies/PullRewardsTransferStrategy.sol \
    