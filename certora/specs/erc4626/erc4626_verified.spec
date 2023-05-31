import "erc4626_base.spec"

// The following spec implements erc4626 properties according to the official eip described here:
// https://eips.ethereum.org/EIPS/eip-4626

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

// MINT

// passes
rule PreviewMintShouldMimicMint(
    env e,
    uint256 shares,
    address receiver
) {
    setup(e, receiver);

    requireInvariant TotalSupplyIsSumOfBalances();
    storage initalState = lastStorage;

    uint256 previewedAmount = previewMint(e, shares);
    uint256 mintedAmount = mint(e, shares, receiver) at initalState;

    assert previewedAmount == mintedAmount;
}

rule MintShouldNotAffectOthers(
    env e,
    uint256 shares,
    address receiver,
    address other
)
{
    setup(e, receiver);
    setup(e, other);
    requireInvariant TotalSupplyIsSumOfBalances();
    require other != e.msg.sender && other != receiver;

    // before
    uint256 _balanceOfOther = balanceOf(other);
    uint256 _ATokenBalanceOfOther = _AToken.balanceOf(e, other);

    // function call
    mint(e, shares, receiver);

    // after
    uint256 balanceOfOther_ = balanceOf(other);
    uint256 ATokenBalanceOfOther_ = _AToken.balanceOf(e, other);

    // asserts
    assert _ATokenBalanceOfOther == ATokenBalanceOfOther_, "AToken.balanceOf(other) affected";
    assert _balanceOfOther == balanceOfOther_, "balanceOf(other) affected";

}


// TODO: Check Reverts
    // if (shares > maxMint(receiver) || shares == 0 ) => revert
    //assert (shares > maxMint(receiver) || shares == 0 ) => lastReverted;

rule MintShouldDepositCorrectAmount(
    env e,
    uint256 shares,
    address receiver
) {
    setup(e, receiver);
    require shares <= maxMint(receiver) && shares != 0; // FIXME
    requireInvariant TotalSupplyIsSumOfBalances();

    // before
    uint256 _ATokenBalanceOfThis = _AToken.balanceOf(e, currentContract);

    // function call
    uint256 assetsMinted = mint(e, shares, receiver);

    // after
    uint256 ATokenBalanceOfThis_ = _AToken.balanceOf(e, currentContract);

    // asserts
    assert _ATokenBalanceOfThis + assetsMinted == ATokenBalanceOfThis_,
        "incorrec//x t AToken amount deposited";
}

rule MintShouldSpendCorrectAmount(
    env e,
    uint256 shares,
    address receiver
) {
    setup(e, receiver);
    require shares <= maxMint(receiver) && shares != 0; // FIXME
    requireInvariant TotalSupplyIsSumOfBalances();

    // before
    uint256 _ATokenBalanceOfSender = _AToken.balanceOf(e, e.msg.sender);

    // function call
    uint256 assetsMinted = mint(e, shares, receiver);

    // after
    uint256 ATokenBalanceOfSender_ = _AToken.balanceOf(e, e.msg.sender);

    // asserts
    assert _ATokenBalanceOfSender - assetsMinted == ATokenBalanceOfSender_,
        "sender spent incorrect AToken amount";
}

rule MintShouldIncreaseReceiverBalance(
    env e,
    uint256 shares,
    address receiver
) {
    setup(e, receiver);
    require shares <= maxMint(receiver) && shares != 0; // FIXME
    requireInvariant TotalSupplyIsSumOfBalances();

    // before
    uint256 _balanceOfSender = balanceOf(e.msg.sender);
    uint256 _balanceOfReceiver = balanceOf(receiver);

    // function call
    uint256 assetsMinted = mint(e, shares, receiver);

    // after
    uint256 balanceOfSender_ = balanceOf(e.msg.sender);
    uint256 balanceOfReceiver_ = balanceOf(receiver);

    // asserts
    assert (e.msg.sender != receiver) => (_balanceOfSender == balanceOfSender_),
        "msg.sender's balance changed, when not the intended receiver";
    assert _balanceOfReceiver + shares == balanceOfReceiver_,
        "receiver's balance was not increased by correct amount";
}

rule MintShouldIncreaseTotalSupplyByCorrectAmount(
    env e,
    uint256 shares,
    address receiver
) {
    setup(e, receiver);
    require shares <= maxMint(receiver) && shares != 0; // FIXME
    requireInvariant TotalSupplyIsSumOfBalances();

    // before
    uint256 _totalSupply = totalSupply();

    // function call
    uint256 assetsMinted = mint(e, shares, receiver);

    // after
    uint256 totalSupply_ = totalSupply();

    // assert
    assert _totalSupply + shares == totalSupply_ || _totalSupply + shares == totalSupply_ - 1,
       "totalSupply was not increased by the correct amount";
}