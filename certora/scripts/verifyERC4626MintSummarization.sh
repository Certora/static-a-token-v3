
if [[ "$1" ]]
then
    RULE="--rule $1"
fi

if [[ "$2" ]]
then
    MSG="- $2"
fi

certoraRun certora/harness/StaticATokenLMHarness.sol \
    certora/munged/lib/aave-v3-core/contracts/protocol/tokenization/AToken.sol \
    certora/munged/lib/aave-v3-periphery/contracts/rewards/RewardsController.sol \
    certora/harness/RewardsControllerHarness.sol \
    certora/harness/SymbolicLendingPoolL1.sol \
    certora/harness/TransferStrategyHarness.sol \
    certora/harness/DummyERC20_aTokenUnderlying.sol \
    certora/harness/DummyERC20_rewardToken.sol \
    --verify StaticATokenLMHarness:certora/specs/erc4626MintSummarization.spec \
    --link StaticATokenLMHarness:INCENTIVES_CONTROLLER=RewardsController \
           StaticATokenLMHarness:POOL=SymbolicLendingPoolL1 \
            StaticATokenLMHarness:_aToken=AToken \
           StaticATokenLMHarness:_aTokenUnderlying=DummyERC20_aTokenUnderlying \
           AToken:POOL=SymbolicLendingPoolL1 \
    --solc solc8.10 \
    --optimistic_loop \
    --packages aave-v3-core=lib/aave-v3-core \
               @aave/core-v3=lib/aave-v3-core \
               aave-v3-periphery=lib/aave-v3-periphery \
               solidity-utils=lib/solidity-utils/src \
    --rule_sanity basic \
    --staging master\
    --send_only \
    --optimistic_hashing \
    --settings -t=10000 \
    $RULE \
    --msg "StaticAToken - $RULE $MSG  "

    # --settings -optimisticUnboundedHashing=true \
    # --settings -hashingLengthBound=224 \
#link _aToken _aTokenUnderlying _aToken
#           StaticATokenLM:_aToken=DummyERC20_aToken \
#           StaticATokenLM:_aTokenUnderlying=DummyERC20_aTokenUnderlying \
#           StaticATokenLM:_rewardToken=DummyERC20_rewardToken \
#    certora/harness/ScaledBalanceTokenHarness.sol \
#    lib/aave-v3-periphery/contracts/rewards/transfer-strategies/StakedTokenTransferStrategy.sol \
#    lib/aave-v3-periphery/contracts/rewards/transfer-strategies/PullRewardsTransferStrategy.sol \
    