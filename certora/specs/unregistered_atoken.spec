import "erc20.spec"


using AToken as _AToken 
using DummyERC20_rewardToken as _DummyERC20_rewardToken
using DummyERC20_aTokenUnderlying as _DummyERC20_aTokenUnderlying 
using RewardsControllerHarness as _RewardsController


methods
{
    /*******************
    *     envfree      *
    ********************/
	asset() returns (address) envfree
	getUnclaimedRewards(address, address) returns (uint256) envfree
	isRegisteredRewardToken(address) returns (bool) envfree
    getUserRewardsData(address, address) returns (uint128) envfree

	_AToken.balanceOf(address user) returns (uint256) envfree
	_AToken.UNDERLYING_ASSET_ADDRESS() returns (address) envfree

    _RewardsController.getAvailableRewardsCount(address) returns (uint128) envfree
    _RewardsController.getRewardsByAsset(address, uint128) returns (address) envfree

    /*******************
    *     Pool.sol     *
    ********************/

    //in RewardsDistributor.sol called by RewardsController.sol
    getAssetIndex(address, address) returns (uint256, uint256) =>  DISPATCHER(true)

    //in RewardsDistributor.sol called by RewardsController.sol
    finalizeTransfer(address, address, address, uint256, uint256, uint256) => NONDET  

    //in ScaledBalanceTokenBase.sol called by getAssetIndex
    scaledTotalSupply() returns (uint256)  => DISPATCHER(true)

    /*****************************
    *     OZ ERC20Permit.sol     *
    ******************************/
    permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => DISPATCHER(true)

    /*********************
    *     AToken.sol     *
    **********************/
    mint(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
    burn(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
    getIncentivesController() returns (address) => CONSTANT
    
    /**********************************
    *     RewardsController.sol     *
    **********************************/
    //call by RewardsController.IncentivizedERC20.sol and also by StaticATokenLM.sol
    handleAction(address,uint256,uint256) => DISPATCHER(true)

    // called by  StaticATokenLM.claimRewardsToSelf --> RewardsController._getUserAssetBalances
    // get balanceOf and totalSupply of _aToken
    // todo - link to the actual token.
    getScaledUserBalanceAndSupply(address) returns (uint256, uint256) => DISPATCHER(true)

    // called by StaticATokenLM.collectAndUpdateRewards --> RewardsController._transferRewards()
    //implemented as simple transfer() in TransferStrategyHarness
    performTransfer(address,address,uint256) returns (bool) =>  DISPATCHER(true)

 }


rule new_token() {
    require _RewardsController.getAvailableRewardsCount(_AToken) == 1;
	require _RewardsController.getRewardsByAsset(_AToken, 0) == _DummyERC20_rewardToken;
    require !isRegisteredRewardToken(_DummyERC20_rewardToken);

    env e;
    require getUserRewardsData(e.msg.sender, _DummyERC20_rewardToken) == 0;
    require getUnclaimedRewards(e.msg.sender, _DummyERC20_rewardToken) == 0;
    
    uint256 total = getTotalClaimableRewards(e, _DummyERC20_rewardToken);
    uint256 claimable = getClaimableRewards(e, e.msg.sender, _DummyERC20_rewardToken);
    assert claimable <= total, "Too much claimable";
}
