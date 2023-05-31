import "../methods/methods_base.spec"

/////////////////// Methods ////////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// Properties ///////////////////////

ghost uint256 SumOfBalances {
    init_state axiom SumOfBalances == 0;
}

hook Sstore balanceOf[KEY address a] uint new_value (uint old_value) STORAGE {
    SumOfBalances = SumOfBalances + new_value - old_value;
}

invariant TotalSupplyIsSumOfBalances()
    totalSupply() == SumOfBalances
    filtered { f -> !harnessOnlyMethods(f) }
    {
        preserved with (env e) {
                setup(e, e.msg.sender);
                single_RewardToken_setup();
        }
    }

rule TransferShouldNotDecreaseUnclaimedRewards(
    env e,
    address to,
    uint256 amount
) {
    setup(e, e.msg.sender);
    single_RewardToken_setup();
    rewardsController_reward_setup();


    uint256 _UnclaimedRewards = getUnclaimedRewards(e.msg.sender, getRewardToken(0));
    transfer(e, to, amount);
    uint256 UnclaimedRewards_ = getUnclaimedRewards(e.msg.sender, getRewardToken(0));

    assert _UnclaimedRewards <= UnclaimedRewards_, "unclaimedRewards decreased";
}


//TODO rule additveWithdrawl() // 2*withdraw(x) == withdraw(2*x)
//rule redeem(underlying==true) <= maxRedeemUnderlying()
rule CannotRedeemMoreUnderlyingThanMaxRedeemUnderlying(
    env e,
    uint256 shares,
    address recipient,
    address owner,
    bool toUnderlying
) {
    //FIXME remove this
    require owner == e.msg.sender;
    require owner == recipient;
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


    require toUnderlying == true;

    storage init_state = lastStorage;


    // function calls
    uint256 max_shares = maxRedeemUnderlying(e, owner);

    uint256 amt_shares;
    uint256 amt_assets;
    amt_shares, amt_assets = redeem(e, shares, recipient, owner, toUnderlying) at init_state;

    // asserts
    //assert amt_assets <= convertToShares(e, max_shares);
    assert amt_shares <= max_shares+1;
}