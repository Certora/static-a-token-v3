#!/bin/sh
certoraRun src/StaticATokenLM.sol \
    lib/aave-v3-periphery/contracts/rewards/RewardsController.sol \
    lib/aave-v3-periphery/contracts/rewards/transfer-strategies/PullRewardsTransferStrategy.sol \
    lib/aave-v3-periphery/contracts/rewards/transfer-strategies/StakedTokenTransferStrategy.sol \
    --verify StaticATokenLM:certora/specs/StaticATokenLM.spec \
    --link StaticATokenLM:_incentivesController=RewardsController \
    --solc solc8.10 \
    --optimistic_loop \
    --staging \
    --packages aave-v3-core=lib/aave-v3-core \
               @aave/core-v3=lib/aave-v3-core \
               aave-v3-periphery=lib/aave-v3-periphery \
               solidity-utils=lib/solidity-utils/src \
    --send_only \
    --msg "StaticATokenLM rules"
