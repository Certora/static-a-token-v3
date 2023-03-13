/* ConvertToShares (from EIP4626)
 * X Must not be inclusive of any fees (not tested)
 * Must not be dependent on the caller
 * X Must not reflect slippage and other on-chain conditions (not tested)
 * Must not revert except for overflow
 * Must round down towards 0
 
 * ConvertToAssets (from EIP4626)
 * X Must not be inclusive of any fees(not tested)
 * Should be independent of the user
 * X Must not reflect slippage and other on-chain conditions (not tested)
 * Must not revert unless due to integer overflow
 * Must round down
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

/* Latest run:
 * https://vaas-stg.certora.com/output/98279/c838a5cdad104424a0596cc54e61a64c?anonymousKey=4eb91f83d983728e03d016fa80b6b28fa9b76ff7
 * toAssetsDoesNotRevert and toSharesDoesNotRevert fail, since we get overflow
 * on part of the calculation, even though the final result is fine. In essence
 * we compute x = (a * b) / c, even though x does not overflow (a * b) does overflow.
 */

definition RAY() returns uint256 = (10 ^ 27);


// ConvertToShares must not be dependent on the caller
rule toSharesCallerIndependent(uint256 assets) {
	env e1;
	env e2;

	require e1.block.timestamp < 2^32;  // Avoid down casting issues
	require e2.block.timestamp < 2^32;  // Avoid down casting issues
	require e1.block.timestamp == e2.block.timestamp;
	require e1.block.number == e2.block.number;

	uint256 shares1 = convertToShares(e1, assets);
	uint256 shares2 = convertToShares(e2, assets);
	assert shares1 == shares2, "ConvertToShares depend on sender";
}


// ConvertToShares must not revert except for overflow
rule toSharesDoesNotRevert(uint256 assets) {
	env e;

	// Prevent revert due to overflow.
	// Roughly speaking ConvertToShares returns assets * RAY / rate().
	mathint ray_math = to_mathint(RAY());
	mathint rate_math = to_mathint(rate(e));
	mathint assets_math = to_mathint(assets);
	require (assets_math * ray_math) < rate_math * 2^256;

	uint256 shares = convertToShares@withrevert(e, assets);
	bool reverted = lastReverted;

	assert !reverted, "Conversion to shares reverted";
}


// ConvertToShares must round down towards 0
// This was already verified in sharesAssetsConversion.spec in rule sharesConversionRoundedDown,
// we do it here as well for completeness.
rule toSharesRoundsDown(uint256 assets) {
	env e;
	uint256 shares = convertToShares(e, assets);
	assert convertToAssets(e, shares) <= assets, "Too many converted shares";
}


// ConvertToAssets Should be independent of the user
rule toAssetsCallerIndependent(uint256 shares) {
	env e1;
	env e2;

	require e1.block.timestamp < 2^32;  // Avoid down casting issues
	require e2.block.timestamp < 2^32;  // Avoid down casting issues
	require e1.block.timestamp == e2.block.timestamp;
	require e1.block.number == e2.block.number;

	uint256 assets1 = convertToAssets(e1, shares);
	uint256 assets2 = convertToAssets(e2, shares);
	assert assets1 == assets2, "ConvertToAssets depends on sender";
}


// ConvertToAssets must not revert unless due to integer overflow
rule toAssetsDoesNotRevert(uint256 shares) {
	env e;

	// Prevent revert due to overflow.
	// Roughly speaking ConvertToAssets returns shares * rate() / RAY.
	mathint ray_math = to_mathint(RAY());
	mathint rate_math = to_mathint(rate(e));
	mathint shares_math = to_mathint(shares);
	require (shares_math * rate_math) < ray_math * 2^256;

	uint256 assets = convertToAssets@withrevert(e, shares);
	bool reverted = lastReverted;

	assert !reverted, "Conversion to assets reverted";
}


// ConvertToShares must round down
// This was already verified in sharesAssetsConversion.spec in rule amountConversionRoundedDown,
// we do it here as well for completeness.
rule toAssetsRoundsDown(uint256 shares) {
	env e;
	uint256 assets = convertToAssets(e, shares);
	assert convertToShares(e, assets) <= shares, "Too many converted assets";
}
