import "erc20.spec"

using StaticATokenLMHarness as _StaticATokenLM
using SymbolicLendingPool as _SymbolicLendingPool
using RewardsControllerHarness as _RewardsController
using TransferStrategyHarness as _TransferStrategy
using DummyERC20_aTokenUnderlying as _DummyERC20_aTokenUnderlying 
using AToken as _AToken
using DummyERC20_rewardToken as _DummyERC20_rewardToken 

/////////////////// Methods ////////////////////////

methods
{
    // static aToken
	// -------------
        asset() returns (address) envfree
        totalAssets() returns (uint256)
        maxWithdraw(address owner) returns (uint256)
        maxRedeem(address owner) returns (uint256) envfree
        previewWithdraw(uint256) returns (uint256)
        previewRedeem(uint256) returns (uint256)
        maxDeposit(address) returns (uint256) envfree
        previewMint(uint256) returns (uint256)
        maxMint(address) returns (uint256) envfree
        rate() returns (uint256)
        getUnclaimedRewards(address, address) returns (uint256) envfree
        rewardTokens() returns (address[]) envfree
        isRegisteredRewardToken(address) returns (bool) envfree
        
    // static aToken harness
    // ---------------------
        getStaticATokenUnderlying() returns (address) envfree
        getRewardsIndexOnLastInteraction(address, address) returns (uint128) envfree
        getRewardTokensLength() returns (uint256) envfree 
        getRewardToken(uint256) returns (address) envfree
        getReserveData_AToken() returns (address) envfree

    // erc20
    // -----
        transferFrom(address,address,uint256) returns (bool) => DISPATCHER(true)

    // pool
    // ----
        _SymbolicLendingPool.getReserveNormalizedIncome(address) returns (uint256)
        getReserveData(address) returns ((uint256),uint128,uint128,uint128,uint128,uint128,uint40,uint16,address,address,address,address,uint128,uint128,uint128) envfree => CONSTANT
        _SymbolicLendingPool.getATokenAddress() returns (address) envfree
        _SymbolicLendingPool.reserveIsActive() returns (bool) envfree
        _SymbolicLendingPool.assetIsPaused() returns (bool) envfree
        _SymbolicLendingPool.reserveIsFrozen() returns (bool) envfree
	
    // rewards controller
	// ------------------
        // In RewardsDistributor.sol called by RewardsController.sol
        getAssetIndex(address, address) returns (uint256, uint256) => DISPATCHER(true)
        // In ScaledBalanceTokenBase.sol called by getAssetIndex
        scaledTotalSupply() returns (uint256)  => DISPATCHER(true) 
        // Called by RewardsController._transferRewards()
        // Defined in TransferStrategyHarness as simple transfer() 
        performTransfer(address,address,uint256) returns (bool) =>  DISPATCHER(true)

        // harness methods of the rewards controller
        _RewardsController.getRewardsIndex(address,address)returns (uint256) envfree
        _RewardsController.getAvailableRewardsCount(address) returns (uint128) envfree
        _RewardsController.getRewardsByAsset(address, uint128) returns (address) envfree
        _RewardsController.getAssetListLength() returns (uint256) envfree
        _RewardsController.getAssetByIndex(uint256) returns (address) envfree
        _RewardsController.getDistributionEnd(address, address)  returns (uint256) envfree
        _RewardsController.getUserAccruedRewards(address, address) returns (uint256) envfree
        _RewardsController.getUserAccruedReward(address, address, address) returns (uint256) envfree
        _RewardsController.getAssetDecimals(address) returns (uint8) envfree
        _RewardsController.getRewardsData(address,address) returns (uint256,uint256,uint256,uint256) envfree
        _RewardsController.getUserAssetIndex(address,address, address) returns (uint256) envfree

    // underlying token
    // ----------------
        _DummyERC20_aTokenUnderlying.balanceOf(address) returns(uint256) envfree

    // aToken
	// ------
        _AToken.balanceOf(address) returns (uint256)
        _AToken.totalSupply() returns (uint256)
        _AToken.allowance(address, address) returns (uint256) envfree
        _AToken.UNDERLYING_ASSET_ADDRESS() returns (address) envfree
        _AToken.scaledBalanceOf(address) returns (uint256) envfree
        _AToken.scaledTotalSupply() returns (uint256) envfree
        
        // called in aToken
        finalizeTransfer(address, address, address, uint256, uint256, uint256) => NONDET  
        // Called by rewardscontroller.sol
        // Defined in scaledbalancetokenbase.sol
        getScaledUserBalanceAndSupply(address) returns (uint256, uint256) => DISPATCHER(true)

    // reward token
    // ------------
        _DummyERC20_rewardToken.balanceOf(address) returns (uint256) envfree
        _DummyERC20_rewardToken.totalSupply() returns (uint256) envfree

        UNDERLYING_ASSET_ADDRESS() returns (address) envfree => CONSTANT UNRESOLVED

    // ReserveConfiguration
        getActive((uint256)) returns (bool) => CONSTANT
        getPaused((uint256)) returns (bool) => CONSTANT
        getFrozen((uint256)) returns (bool) => CONSTANT
        getDecimals((uint256)) returns (bool) => CONSTANT
        getSupplyCap((uint256)) returns (bool) => CONSTANT
 }

///////////////// DEFINITIONS //////////////////////

    definition RAY() returns uint256 = 10^27;

    /// @notice Claim rewards methods
    definition claimFunctions(method f) returns bool = 
        (f.selector == claimRewardsToSelf(address[]).selector ||
        f.selector == claimRewards(address, address[]).selector ||
        f.selector == claimRewardsOnBehalf(address, address,address[]).selector);
                
    definition collectAndUpdateFunction(method f) returns bool =
        f.selector == collectAndUpdateRewards(address).selector;

    definition harnessOnlyMethods(method f) returns bool =
        (harnessMethodsMinusHarnessClaimMethods(f) ||
        f.selector == claimSingleRewardOnBehalf(address, address, address).selector ||
        f.selector == claimDoubleRewardOnBehalfSame(address, address, address).selector);
        
    definition harnessMethodsMinusHarnessClaimMethods(method f) returns bool =
        (f.selector == getStaticATokenUnderlying().selector ||
        f.selector == getRewardTokensLength().selector ||
        f.selector == getRewardToken(uint256).selector ||
        f.selector == getRewardsIndexOnLastInteraction(address, address).selector ||
        f.selector == getLastUpdatedIndex(address).selector);

////////////////// FUNCTIONS //////////////////////

    /**
    * @title Single reward setup
    * Setup the `StaticATokenLM`'s rewards so they contain a single reward token
    * which is` _DummyERC20_rewardToken`.
    */
    function single_RewardToken_setup() {
        require getRewardTokensLength() == 1;
        require getRewardToken(0) == _DummyERC20_rewardToken;
    }

    /**
    * @title Single reward setup in RewardsController
    * Sets (in `_RewardsController`) the first reward for `_AToken` as
    * `_DummyERC20_rewardToken`.
    */
    function rewardsController_reward_setup() {
        require _RewardsController.getAvailableRewardsCount(_AToken) > 0;
        require _RewardsController.getRewardsByAsset(_AToken, 0) == _DummyERC20_rewardToken;
    }

    /// @title Assumptions that should hold in any run
    /// @dev Assume that RewardsController.configureAssets(RewardsDataTypes.RewardsConfigInput[] memory rewardsInput) was called
    function setup(env e, address user)
    {
        require getRewardTokensLength() > 0;
        require _RewardsController.getAvailableRewardsCount(_AToken)  > 0;
        require _RewardsController.getRewardsByAsset(_AToken, 0) == _DummyERC20_rewardToken;
        require currentContract != e.msg.sender;
        require currentContract != user;
    
        require _AToken != user;
        require _RewardsController !=  user;
        require _DummyERC20_aTokenUnderlying  != user;
        require _DummyERC20_rewardToken != user;
        require _SymbolicLendingPool != user;
        require _TransferStrategy != user;
        require _TransferStrategy != user;
        require getReserveData_AToken() == _AToken;
    }