import "erc20.spec"


using AToken as _AToken 


methods
{
    /*******************
    *     envfree      *
    ********************/
	asset() returns (address) envfree
	_AToken.balanceOf(address user) returns (uint256) envfree

    /*******************
    *     Pool.sol     *
    ********************/
    // can we assume a fixed index? 1 ray?
    // getReserveNormalizedIncome(address) returns (uint256) => DISPATCHER(true)

    //in RewardsDistributor.sol called by RewardsController.sol
    getAssetIndex(address, address) returns (uint256, uint256) =>  DISPATCHER(true)
    //deposit(address,uint256,address,uint16) => DISPATCHER(true)
    //withdraw(address,uint256,address) returns (uint256) => DISPATCHER(true)
    finalizeTransfer(address, address, address, uint256, uint256, uint256) => NONDET  

    //in ScaledBalanceTokenBase.sol called by getAssetIndex
    scaledTotalSupply() returns (uint256)  => DISPATCHER(true) 
    
    //IAToken.sol
    mint(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
    burn(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)

    /*******************************
    *     RewardsController.sol    *
    ********************************/
   // claimRewards(address[],uint256,address,address) => NONDET
     
   /*****************************
    *     OZ ERC20Permit.sol     *
    ******************************/
    permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => NONDET

    /*********************
    *     AToken.sol     *
    **********************/
    getIncentivesController() returns (address) => CONSTANT
    UNDERLYING_ASSET_ADDRESS() returns (address) => CONSTANT
    
    /**********************************
    *     RewardsDistributor.sol     *
    **********************************/
    getRewardsList() returns (address[]) => NONDET

    /**********************************
    *     RewardsController.sol     *
    **********************************/
    //call by RewardsController.IncentivizedERC20.sol and also by StaticATokenLM.sol
    handleAction(address,uint256,uint256) => DISPATCHER(true)

    // called by  StaticATokenLM.claimRewardsToSelf  -->  RewardsController._getUserAssetBalances
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
 * Passed (except for the functions above which failed sanity check):
 * https://vaas-stg.certora.com/output/98279/af4681b5391643afb8c6541d5932c455?anonymousKey=d5d1abf1195403b24ea8cd3a901bb6112f90d363
 */
rule aTokenBalanceIsFixed(method f) {
	require _AToken == asset();
	
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
