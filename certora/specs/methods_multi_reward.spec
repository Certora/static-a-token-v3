import "erc20.spec"


using AToken as _AToken 
using DummyERC20_rewardTokenA as _rewardTokenA
using DummyERC20_rewardTokenB as _rewardTokenB
using DummyERC20_aTokenUnderlying as _DummyERC20_aTokenUnderlying 
using RewardsControllerHarness as _RewardsController


/////////////////// Methods ////////////////////////

/// @dev Using mostly `NONDET` in the methods block, to speed up verification.

    methods {
        // envfree
        // -------
        getUnclaimedRewards(address, address) returns (uint256) envfree
        rewardTokens() returns (address[]) envfree
        isRegisteredRewardToken(address) returns (bool) envfree
        
        // getters from munged/harness
        getRewardTokensLength() returns (uint256) envfree 
        getRewardToken(uint256) returns (address) envfree

        // AToken
        _AToken.UNDERLYING_ASSET_ADDRESS() returns (address) envfree

        // Reward tokens
        _rewardTokenA.balanceOf(address user) returns (uint256) envfree
        _rewardTokenB.balanceOf(address user) returns (uint256) envfree

        // RewardsController
        _RewardsController.getAvailableRewardsCount(address) returns (uint128) envfree
        _RewardsController.getRewardsByAsset(address, uint128) returns (address) envfree

        // Pool.sol
        // --------
        // In RewardsDistributor.sol called by RewardsController.sol
        getAssetIndex(address, address) returns (uint256, uint256) => NONDET

        // In RewardsDistributor.sol called by RewardsController.sol
        finalizeTransfer(address, address, address, uint256, uint256, uint256) => NONDET  

        // In ScaledBalanceTokenBase.sol called by getAssetIndex
        scaledTotalSupply() returns (uint256) => NONDET
        
        // ERC20Permit
        // -----------
        permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => NONDET

        // AToken.sol
        // ----------
        mint(address,address,uint256,uint256) returns (bool) => NONDET
        burn(address,address,uint256,uint256) returns (bool) => NONDET
        
        // RewardsController.sol
        // ---------------------
        // Called by IncentivizedERC20.sol and by StaticATokenLM.sol
        handleAction(address,uint256,uint256) => NONDET

        // Called by rewardscontroller.sol
        // Defined in scaledbalancetokenbase.sol
        getScaledUserBalanceAndSupply(address) returns (uint256, uint256) => NONDET

        // Called by RewardsController._transferRewards()
        // Defined in TransferStrategyHarness as simple transfer() 
        performTransfer(address,address,uint256) returns (bool) => NONDET
     }
