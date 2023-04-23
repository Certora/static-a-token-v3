certoraRun certora/harness/StaticATokenLMHarness.sol \
        certora/harness/pool/SymbolicLendingPool.sol \
        certora/harness/rewards/RewardsControllerHarness.sol \
        certora/harness/rewards/TransferStrategyHarness.sol \
        certora/harness/tokens/DummyERC20_aTokenUnderlying.sol \
        certora/munged/lib/aave-v3-core/contracts/protocol/tokenization/AToken.sol \
        certora/harness/tokens/DummyERC20_rewardToken.sol \
    --verify StaticATokenLMHarness:certora/specs/StaticATokenLM_verified.spec \
    --link StaticATokenLMHarness:POOL=SymbolicLendingPool \
            StaticATokenLMHarness:INCENTIVES_CONTROLLER=RewardsControllerHarness \
            StaticATokenLMHarness:_aTokenUnderlying=DummyERC20_aTokenUnderlying \
            StaticATokenLMHarness:_aToken=AToken \
            StaticATokenLMHarness:_reward_A=DummyERC20_rewardToken \
            SymbolicLendingPool:underlyingToken=DummyERC20_aTokenUnderlying \
            SymbolicLendingPool:aToken=AToken \
            TransferStrategyHarness:INCENTIVES_CONTROLLER=RewardsControllerHarness \
            TransferStrategyHarness:REWARD=DummyERC20_rewardToken \
            AToken:POOL=SymbolicLendingPool \
            AToken:_incentivesController=RewardsControllerHarness \
            AToken:_underlyingAsset=DummyERC20_aTokenUnderlying \
    --packages aave-v3-core=certora/munged/lib/aave-v3-core \
                @aave/core-v3=certora/munged/lib/aave-v3-core \
                aave-v3-periphery=certora/munged/lib/aave-v3-periphery \
                solidity-utils=certora/munged/lib/solidity-utils/src \
                openzeppelin-contracts=certora/munged/lib/openzeppelin-contracts \
    --solc solc8.10 \
    --optimistic_loop \
        --loop_iter 1 \
    --optimistic_hashing \
    --staging \
    --msg "Rewards related properties"
    # --rules "${@}" \
