/* Both previewDeposit and deposit should return the same values (provided deposit succeeds).
 * The same goes for other preview functions.
 */

import "erc20.spec"


methods
{
    /*******************
    *     envfree      *
    ********************/

    /*******************
    *     Pool.sol     *
    ********************/

    //in RewardsDistributor.sol called by RewardsController.sol
    getAssetIndex(address, address) returns (uint256, uint256) =>  DISPATCHER(true)

    //in RewardsDistributor.sol called by RewardsController.sol
    finalizeTransfer(address, address, address, uint256, uint256, uint256) => NONDET  

    //in ScaledBalanceTokenBase.sol called by getAssetIndex
    scaledTotalSupply() returns (uint256)  => DISPATCHER(true) 

    /*********************
    *     AToken.sol     *
    **********************/
    //mint(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
    //burn(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
    //getIncentivesController() returns (address) => CONSTANT
    //UNDERLYING_ASSET_ADDRESS() returns (address) => CONSTANT
    
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
 * https://vaas-stg.certora.com/output/98279/a445d0abe25046e2bb6272a338121ca7?anonymousKey=c554bbe2893b4d5735fa4d8b6c3e1b2624b9bbd8
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
