import "erc20.spec"

using SymbolicLendingPool as _SymbolicLendingPool
using RewardsControllerHarness as _RewardsController
using DummyERC20_aTokenUnderlying as _DummyERC20_aTokenUnderlying 
using AToken as _AToken
using DummyERC20_rewardToken as _DummyERC20_rewardToken
using DummyERC20_rewardTokenB as _DummyERC20_rewardTokenB

/////////////////// Methods ////////////////////////

/// @dev Using mostly `NONDET` in the methods block, to speed up verification.

    methods {
        // static aToken
	    // -------------
            getCurrentRewardsIndex(address reward) returns (uint256) => CONSTANT
            getUnclaimedRewards(address, address) returns (uint256) envfree
            rewardTokens() returns (address[]) envfree
            isRegisteredRewardToken(address) returns (bool) envfree
        
        // static aToken harness
        // ---------------------
            getRewardTokensLength() returns (uint256) envfree 
            getRewardToken(uint256) returns (address) envfree
    
        // pool
        // ----
            // In RewardsDistributor.sol called by RewardsController.sol
            getAssetIndex(address, address) returns (uint256, uint256) => NONDET

            // In RewardsDistributor.sol called by RewardsController.sol
            finalizeTransfer(address, address, address, uint256, uint256, uint256) => NONDET  

            // In ScaledBalanceTokenBase.sol called by getAssetIndex
            scaledTotalSupply() returns (uint256) => NONDET

        // rewards controller
	    // ------------------
            _RewardsController.getAvailableRewardsCount(address) returns (uint128) envfree
            _RewardsController.getRewardsByAsset(address, uint128) returns (address) envfree
            // Called by IncentivizedERC20.sol and by StaticATokenLM.sol
            handleAction(address,uint256,uint256) => NONDET
            // Called by rewardscontroller.sol
            // Defined in scaledbalancetokenbase.sol
            getScaledUserBalanceAndSupply(address) returns (uint256, uint256) => NONDET
            // Called by RewardsController._transferRewards()
            // Defined in TransferStrategyHarness as simple transfer() 
            performTransfer(address,address,uint256) returns (bool) => NONDET

        // aToken
	    // ------
            _AToken.UNDERLYING_ASSET_ADDRESS() returns (address) envfree
            mint(address,address,uint256,uint256) returns (bool) => NONDET
            burn(address,address,uint256,uint256) returns (bool) => NONDET
        
        // reward token
        // ------------
            _DummyERC20_rewardToken.balanceOf(address user) returns (uint256) envfree
            _DummyERC20_rewardTokenB.balanceOf(address user) returns (uint256) envfree
        
        permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => NONDET
    }

///////////////// Definition ///////////////////////

    /// @title Set up a single reward token
    function single_RewardToken_setup() {
        require isRegisteredRewardToken(_DummyERC20_rewardToken);
        require getRewardTokensLength() == 1;
    }

    /// @title Set up a single reward token for `_AToken` in the `INCENTIVES_CONTROLLER`
    function rewardsController_arbitrary_single_reward_setup() {
        require _RewardsController.getAvailableRewardsCount(_AToken) == 1;
        require _RewardsController.getRewardsByAsset(_AToken, 0) == _DummyERC20_rewardToken;
    }
