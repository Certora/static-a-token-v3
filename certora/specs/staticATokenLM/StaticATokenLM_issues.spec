import "StaticATokenLM_base.spec"

/////////////////// Methods ////////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// Properties ///////////////////////

//rule redeem(underlying==true) <= maxRedeemUnderlying()
rule CannotRedeemMoreUnderlyingThanMaxRedeemUnderlying(
    env e,
    uint256 shares,
    address recipient,
    address owner
) {
    bool toUnderlying = true;
    setup(e, recipient);
    single_RewardToken_setup();
    requireInvariant TotalSupplyIsSumOfBalances();

    address pool_atoken = _SymbolicLendingPool.getATokenAddress();
    require _AToken == pool_atoken;

    // pre-assume active and !paused
    require _SymbolicLendingPool.reserveIsActive() == true;
    require _SymbolicLendingPool.assetIsPaused() == false;

    //requireInvariant SolvencyOfATokenContract();
    require _AToken.totalSupply(e) == _DummyERC20_aTokenUnderlying.balanceOf(_AToken);

    storage init_state = lastStorage;

    // function calls
    uint256 max_shares = maxRedeemUnderlying(e, owner);
    uint256 max_assets = convertToAssets(e, max_shares) at init_state;

    uint256 amt_shares;
    uint256 amt_assets;
    amt_shares, amt_assets = redeem(e, shares, recipient, owner, toUnderlying) at init_state;

    // asserts
    assert (amt_shares <= max_shares) || (amt_assets <= max_assets) || (amt_assets <= 1 && amt_shares <=1);
}