import "erc20.spec"


methods
{
	// envfree
	// -------
	asset() returns (address) envfree
    // balanceOf(address owner) returns (uint256) envfree
    maxWithdraw(address owner) returns (uint256) envfree
    maxRedeem(address owner) returns (uint256) envfree

    // Pool.sol
	// --------
    // In RewardsDistributor.sol called by RewardsController.sol
    getAssetIndex(address, address) returns (uint256, uint256) =>  DISPATCHER(true)

    // In RewardsDistributor.sol called by RewardsController.sol
    finalizeTransfer(address, address, address, uint256, uint256, uint256) => NONDET  

    // In ScaledBalanceTokenBase.sol called by getAssetIndex
    scaledTotalSupply() returns (uint256)  => DISPATCHER(true) 
    
    // RewardsController.sol
	// ---------------------
    // Called by IncentivizedERC20.sol and by StaticATokenLM.sol
    handleAction(address,uint256,uint256) => DISPATCHER(true)

    // Called by rewardscontroller.sol
    // Defined in scaledbalancetokenbase.sol
    getScaledUserBalanceAndSupply(address) returns (uint256, uint256) => DISPATCHER(true)

    // Called by RewardsController._transferRewards()
    // Defined in TransferStrategyHarness as simple transfer() 
    performTransfer(address,address,uint256) returns (bool) =>  DISPATCHER(true)
 }
