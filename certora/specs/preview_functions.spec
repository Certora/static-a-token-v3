/* Both previewDeposit and deposit should return the same values (provided deposit succeeds).
 * The same goes for other preview functions.
 */

import "erc20.spec"


using DummyERC20_rewardToken as aRewardToken
using RewardsControllerHarness as aRewardsController

using AToken as _AToken 


methods
{
    /*******************
    *     envfree      *
    ********************/
//	getUnclaimedRewards(address user) returns (uint256) envfree
//	rewardToken() returns address envfree
//	aRewardToken.balanceOf(address user) returns (uint256) envfree
//	incentivesController() returns (address) envfree
//
//    aRewardsController.getAvailableRewardsCount(address) returns (uint128) envfree
//    aRewardsController.getFirstRewardsByAsset(address) returns (address ) envfree

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

/* Latest run - all rules passed:
 * https://vaas-stg.certora.com/output/98279/644dae37e1044ccf84728e0ed73d32bc?anonymousKey=99273d5e70d8d36b68bc609b95080e0c9cd28254
 */


// Number of shares returned by previewDeposit is the same as deposit.
rule previewDepositSameAsDeposit(uint256 assets, address receiver) {
	env e;
	uint256 previewShares = previewDeposit(e, assets);
	uint256 shares = deposit(e, assets, receiver);
	assert previewShares == shares, "previewDeposit is unequal to deposit";
}


// Number of assets returned by previewRedeem is the same as redeem.
rule previewRedeemSameAsRedeem(uint256 shares, address receiver, address owner) {
	env e;
	uint256 previewAssets = previewRedeem(e, shares);
	uint256 assets = redeem(e, shares, receiver, owner);
	assert previewAssets == assets, "previewRedeem is unequal to redeem";
}


// Number of shares returned by previewWithdraw is the same as withdraw.
rule previewWithdrawSameAsWithdraw(uint256 assets, address receiver, address owner) {
	env e;
	uint256 previewShares = previewWithdraw(e, assets);
	uint256 shares = withdraw(e, assets, receiver, owner);
	assert previewShares == shares, "previewWithdraw is unequal to withdraw";
}


// Number of assets returned by previewMint is the same as mint.
rule previewMintSameAsMint(uint256 shares, address receiver) {
	env e;
	uint256 previewAssets = previewMint(e, shares);
	uint256 assets = mint(e, shares, receiver);
	assert previewAssets == assets, "previewMint is unequal to mint";
}
