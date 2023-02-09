#!/bin/sh
certoraRun src/StaticATokenLM.sol \
    --verify StaticATokenLM:certora/specs/complexity.spec \
    --solc solc8.10 \
    --optimistic_loop \
    --staging \
    --packages aave-v3-core=lib/aave-v3-core \
                aave-v3-periphery=lib/aave-v3-periphery \
                solidity-utils/contracts=lib/solidity-utils/src/contracts \
    --send_only \
    --msg "StaticATokenLM complexity check"
