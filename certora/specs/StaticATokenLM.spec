import "erc20.spec"


methods
{

    /*******************
    *     Pool.sol     *
    ********************/
    getReserveNormalizedIncome(address) returns (uint256) => NONDET
    getAssetIndex(address, address) returns (uint256, uint256) => NONDET
    deposit(address,uint256,address,uint16) => NONDET
    withdraw(address,uint256,address) returns (uint256) => NONDET

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

    
    //ScaledBalanceTokenBase.sol
    //debug -- todo fix packages path
    getScaledUserBalanceAndSupply(address) returns (uint256, uint256) => NONDET
    //debug
    performTransfer(address,address,uint256) returns (bool) => NONDET
}
rule sanity(method f)
{
	env e;
	calldataarg args;
	f(e,args);
	assert false;
}

