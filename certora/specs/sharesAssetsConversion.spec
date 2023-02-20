import "erc20.spec"


methods
{
    /*******************
    *     envfree      *
    ********************/
	rate() returns (uint256) envfree
	convertToShares(uint256 amount) returns (uint256) envfree
	convertToAssets(uint256 amount) returns (uint256) envfree

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
    getScaledUserBalanceAndSupply(address) returns (uint256, uint256) => NONDET

    // called by StaticATokenLM.collectAndUpdateRewards --> RewardsController._transferRewards()
    //implemented as simple transfer() in TransferStrategyHarness
    performTransfer(address,address,uint256) returns (bool) =>  DISPATCHER(true)

 }


definition RAY() returns uint256 = (10 ^ 27);


// Converting amount to shares is rounded down.
rule amountConversionRoundedDown(uint256 amount) {
	uint256 shares = convertToShares(amount);
	assert convertToAssets(shares) <= amount, "Too many converted shares";
	assert convertToAssets(shares + 1) >= amount, "Too few converted shares";
}


// Converting shares to amount is rounded down.
rule sharesConversionRoundedDown(uint256 shares) {
	uint256 amount = convertToAssets(shares);
	assert convertToShares(amount) <= shares, "Amount converted is too high";
	assert convertToShares(amount + 1) >= shares, "Amount converted is too low";
}


// Converting amount to shares and back to amount is preserved (up to rounding).
/* NOTE: This fails when rate() > RAY, since conversion to shares formula is:
 * (a * R) // r, where a=amount, R=RAY and r=rate().
 */
rule amountConversionPreserved(uint256 amount) {
 	require rate() <= RAY();
 	mathint mathamount = to_mathint(amount);
 	mathint converted = to_mathint(convertToAssets(convertToShares(amount)));

	// That converted <= mathamount was proved in amountConversionRoundedDown,
 	assert mathamount - converted <= 1, "Too few converted assets";
 }
 

// Converting shares to amount and back to shares is preserved up to RAY.
/* NOTE: This implies that convertToAssets(shares)==0 whenever shares<RAY.
 * So this is probably A BUG OR A MISTAKE. This happens because the formula
 * for converting shares to assets is: (s * r) // R, where a=amount, R=RAY
 * and r=rate().
 */
rule sharesConversionPreserved(uint256 shares) {
	mathint mathshares = to_mathint(shares);
	uint256 amount = convertToAssets(shares);
	mathint converted = to_mathint(convertToShares(amount));

	// That converted <= mathshare was proved in sharesConversionRoundedDown.
	assert mathshares - converted < RAY(), "Too few converted shares";
}
