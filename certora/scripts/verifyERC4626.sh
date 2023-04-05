
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
    certora/harness/RewardsControllerHarness.sol \
    certora/harness/SymbolicLendingPoolL1.sol \
    certora/harness/TransferStrategyHarness.sol \
    certora/harness/DummyERC20_aTokenUnderlying.sol \
    certora/harness/DummyERC20_rewardToken.sol \
    --verify StaticATokenLMHarness:certora/specs/erc4626.spec \
    --link StaticATokenLMHarness:INCENTIVES_CONTROLLER=RewardsControllerHarness \
           StaticATokenLMHarness:POOL=SymbolicLendingPoolL1 \
           StaticATokenLMHarness:_aToken=AToken \
           StaticATokenLMHarness:_aTokenUnderlying=DummyERC20_aTokenUnderlying \
           AToken:POOL=SymbolicLendingPoolL1 \
           AToken:_underlyingAsset=DummyERC20_aTokenUnderlying \
    --solc solc8.10 \
    --optimistic_loop \
    --packages aave-v3-core=certora/munged/lib/aave-v3-core \
               @aave/core-v3=certora/munged/lib/aave-v3-core \
               aave-v3-periphery=certora/munged/lib/aave-v3-periphery \
               solidity-utils=certora/munged/lib/solidity-utils/src \
               openzeppelin-contracts=lib/openzeppelin-contracts \
    --cloud \
    --optimistic_hashing \
    --settings -t=10000 \
    $RULE \
    --msg "StaticAToken - $RULE $MSG  "
