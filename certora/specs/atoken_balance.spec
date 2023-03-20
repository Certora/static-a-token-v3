import "erc20.spec"


using AToken as _AToken 
using DummyERC20_rewardToken as _DummyERC20_rewardToken
using DummyERC20_aTokenUnderlying as _DummyERC20_aTokenUnderlying 


methods
{
    /*******************
    *     envfree      *
    ********************/
	asset() returns (address) envfree
	_AToken.balanceOf(address user) returns (uint256) envfree
	_AToken.UNDERLYING_ASSET_ADDRESS() returns (address) envfree

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

/* During interaction with the static Atoken, a user’s Atoken balance should
 * not be changed, except for:
 * - withdraw
 * - deposit
 * - redeem
 * - mint
 * - metaDeposit
 * - metaWithdraw
 *
 * NOTE: rewards methods are special cases handled in other rules below.
 *
 * Single reward version passed (except for the functions above which failed
 * sanity check, and the claim rewards functions):
 * https://vaas-stg.certora.com/output/98279/af4681b5391643afb8c6541d5932c455?anonymousKey=d5d1abf1195403b24ea8cd3a901bb6112f90d363
 *
 * Multi reward version (no rule sanity check):
 * Parametric rule passed in:
 * https://vaas-stg.certora.com/output/98279/32053979ea0a43fab920d4f00bd49866?anonymousKey=49d0f2484bd42083390a30535163e57e584a5c9c
 *
 * Five claim rewards rules passed in:
 * https://vaas-stg.certora.com/output/98279/6b0053710ff6425fbec86e3b2408a0e2?anonymousKey=8d559431fec4fcba7c87ff990102dc6a3e4e8a2e
 */
rule aTokenBalanceIsFixed(method f) {
	require _AToken == asset();
	require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
	
	// Limit f values
	require (
		(f.selector != deposit(uint256,address).selector) &&
		(f.selector != deposit(uint256,address,uint16,bool).selector) &&
		(f.selector != withdraw(uint256,address,address).selector) &&
		(f.selector != redeem(uint256,address,address).selector) &&
		(f.selector != redeem(uint256,address,address,bool).selector) &&
		(f.selector != mint(uint256,address).selector) &&
		(f.selector != metaDeposit(
			address,address,uint256,uint16,bool,uint256,
			(address,address,uint256,uint256,uint8,bytes32,bytes32),
			(uint8, bytes32, bytes32)
		).selector) &&
		(f.selector != metaWithdraw(
			address,address,uint256,uint256,bool,uint256,
			(uint8, bytes32, bytes32)
		).selector)
	);

	// Exclude reward related methods
	require (
		(f.selector != collectAndUpdateRewards(address).selector) &&
		(f.selector != claimRewardsOnBehalf(address,address,address[]).selector) &&
		(f.selector != claimSingleRewardOnBehalf(address,address,address).selector) &&
		(f.selector != claimRewardsToSelf(address[]).selector) &&
		(f.selector != claimRewards(address,address[]).selector)
	);

	env e;

	// Limit sender
	require e.msg.sender != currentContract;
	require e.msg.sender != _AToken;

	uint256 preBalance = _AToken.balanceOf(e.msg.sender);

	calldataarg args;
	f(e, args);

	uint256 postBalance = _AToken.balanceOf(e.msg.sender);
	assert preBalance == postBalance, "aToken balance changed by static interaction";
}


rule aTokenBalanceIsFixed_for_collectAndUpdateRewards() {
	require _AToken == asset();
	require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
	require _AToken != _DummyERC20_rewardToken;

	env e;

	// Limit sender
	require e.msg.sender != currentContract;
	require e.msg.sender != _AToken;
	require e.msg.sender != _DummyERC20_rewardToken;

	uint256 preBalance = _AToken.balanceOf(e.msg.sender);

	collectAndUpdateRewards(e, _DummyERC20_rewardToken);

	uint256 postBalance = _AToken.balanceOf(e.msg.sender);
	assert preBalance == postBalance, "aToken balance changed by collectAndUpdateRewards";
}


rule aTokenBalanceIsFixed_for_claimRewardsOnBehalf(address onBehalfOf, address receiver) {
	require _AToken == asset();
	require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
	require _AToken != _DummyERC20_rewardToken;

	// Create a rewards array
	address[] _rewards;
	require _rewards[0] == _DummyERC20_rewardToken;
	require _rewards.length == 1;

	env e;

	// Limit sender
	require (
		(e.msg.sender != currentContract) &&
		(onBehalfOf != currentContract) &&
		(receiver != currentContract)
	);
	require (
		(e.msg.sender != _DummyERC20_rewardToken) &&
		(onBehalfOf != _DummyERC20_rewardToken) &&
		(receiver != _DummyERC20_rewardToken)
	);
	require (e.msg.sender != _AToken) && (onBehalfOf != _AToken) && (receiver != _AToken);

	uint256 preBalance = _AToken.balanceOf(e.msg.sender);

	claimRewardsOnBehalf(e, onBehalfOf, receiver, _rewards);

	uint256 postBalance = _AToken.balanceOf(e.msg.sender);
	assert preBalance == postBalance, "aToken balance changed by claimRewardsOnBehalf";
}


rule aTokenBalanceIsFixed_for_claimSingleRewardOnBehalf(address onBehalfOf, address receiver) {
	require _AToken == asset();
	require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
	require _AToken != _DummyERC20_rewardToken;

	env e;

	// Limit sender
	require (
		(e.msg.sender != currentContract) &&
		(onBehalfOf != currentContract) &&
		(receiver != currentContract)
	);
	require (
		(e.msg.sender != _DummyERC20_rewardToken) &&
		(onBehalfOf != _DummyERC20_rewardToken) &&
		(receiver != _DummyERC20_rewardToken)
	);
	require (e.msg.sender != _AToken) && (onBehalfOf != _AToken) && (receiver != _AToken);

	uint256 preBalance = _AToken.balanceOf(e.msg.sender);

	claimSingleRewardOnBehalf(e, onBehalfOf, receiver, _DummyERC20_aTokenUnderlying);

	uint256 postBalance = _AToken.balanceOf(e.msg.sender);
	assert preBalance == postBalance, "aToken balance changed by claimSingleRewardOnBehalf";
}


rule aTokenBalanceIsFixed_for_claimRewardsToSelf() {
	require _AToken == asset();
	require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
	require _AToken != _DummyERC20_rewardToken;

	// Create a rewards array
	address[] _rewards;
	require _rewards[0] == _DummyERC20_rewardToken;
	require _rewards.length == 1;

	env e;

	// Limit sender
	require e.msg.sender != currentContract;
	require e.msg.sender != _AToken;
	require e.msg.sender != _DummyERC20_rewardToken;

	uint256 preBalance = _AToken.balanceOf(e.msg.sender);

	claimRewardsToSelf(e, _rewards);

	uint256 postBalance = _AToken.balanceOf(e.msg.sender);
	assert preBalance == postBalance, "aToken balance changed by claimRewardsToSelf";
}


rule aTokenBalanceIsFixed_for_claimRewards(address receiver) {
	require _AToken == asset();
	require _AToken.UNDERLYING_ASSET_ADDRESS() == _DummyERC20_aTokenUnderlying;
	require _AToken != _DummyERC20_rewardToken;

	// Create a rewards array
	address[] _rewards;
	require _rewards[0] == _DummyERC20_rewardToken;
	require _rewards.length == 1;

	env e;

	// Limit sender
	require (e.msg.sender != currentContract) && (receiver != currentContract);
	require (
		(e.msg.sender != _DummyERC20_rewardToken) && (receiver != _DummyERC20_rewardToken)
	);
	require (e.msg.sender != _AToken) && (receiver != _AToken);

	uint256 preBalance = _AToken.balanceOf(e.msg.sender);

	claimRewards(e, receiver, _rewards);

	uint256 postBalance = _AToken.balanceOf(e.msg.sender);
	assert preBalance == postBalance, "aToken balance changed by claimRewards";
}
