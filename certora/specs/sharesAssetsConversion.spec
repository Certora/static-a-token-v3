import "methods_base.spec"

/// Latest run succeeded (with rule_sanity): job-id=`9c3c36b91b594b0f9a57c21e2d667979`

methods
{
	// envfree
	// -------
	rate() returns (uint256) envfree
	convertToShares(uint256 amount) returns (uint256) envfree
	convertToAssets(uint256 amount) returns (uint256) envfree
}
	

definition RAY() returns uint256 = (10 ^ 27);


/**
 * @notice A note on the conversion functions
 * ------------------------------------------
 * The conversion functions are:
 * - assets to shares = `S(a) = (a * R) // r`
 * - shares to assets = `A(s) = (s * r) // R`
 * where a=assets, s=shares, R=RAY, r=rate.
 * 
 * These imply:
 * - `a * R - r <= S(a) * r <= a * R    a*R/r - 1 <= S(a) <= a*R/r`
 * - `s * r - R <= A(s) * R <= s * r    s*r/R - 1 <= A(s) <= s*r/R`
 * 
 * Hence:
 * - `A(S(a)) >= S(a)*r/R - 1 >= (a*R/r - 1)*r/R - 1 = (a*R - r)/R - 1 = a - r/R - 1`
 * - `S(A(s)) >= A(s)*R/r - 1 >= (s*r/R - 1)*R/r - 1 = (s*r - R)/r - 1 = s - R/r - 1`
 */


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
/// @formula The precision depends on the ratio `rate/RAY`.
rule amountConversionPreserved(uint256 amount) {
 	mathint mathamount = to_mathint(amount);
 	mathint converted = to_mathint(convertToAssets(convertToShares(amount)));

	// That `converted <= mathamount` was proved in `amountConversionRoundedDown`
 	assert mathamount - converted <= 1 + rate() / RAY(), "Too few converted assets";
 }
 

// Converting shares to amount and back to shares is preserved up to RAY.
/// @formula The precision depends on the ratio `RAY/rate`.
rule sharesConversionPreserved(uint256 shares) {
	mathint mathshares = to_mathint(shares);
	uint256 amount = convertToAssets(shares);
	mathint converted = to_mathint(convertToShares(amount));

	// That converted <= mathshare was proved in sharesConversionRoundedDown.
	assert mathshares - converted <= 1 + RAY() / rate(), "Too few converted shares";
}


/* Joining and splitting accounts provides limited advantage.
 * This rule verifies that joining accounts (by combining shares), and splitting accounts
 * (by splitting shares between accounts) provides limited advantage when converting to
 * asset amounts.
 */
rule accountsJoiningSplittingIsLimited(uint256 shares1, uint256 shares2) {
    uint256 amount1 = convertToAssets(shares1);
    uint256 amount2 = convertToAssets(shares2);
    uint256 jointShares = shares1 + shares2;
    require jointShares >= shares1 + shares2;  // Prevent overflow
    uint256 jointAmount = convertToAssets(jointShares);

    assert jointAmount >= amount1 + amount2, "Found advantage in combining accounts";
    assert jointAmount < amount1 + amount2 + 2, "Found advantage in splitting accounts";
    // The following assertion fails (as expected):
    // assert jointAmount < amount1 + amount2 + 1, "Found advantage in splitting accounts";
}

// Similar rule as above for shares
rule convertSumOfAssetsPreserved(uint256 assets1, uint256 assets2) {
    uint256 shares1 = convertToShares(assets1);
    uint256 shares2 = convertToShares(assets2);
    uint256 sumAssets = assets1 + assets2;
	require sumAssets >= assets1 + assets2; // Prevent overflow
    uint256 jointShares = convertToShares(sumAssets);

	assert jointShares >= shares1 + shares2, "Convert sum of assets bigger than parts";
	assert jointShares < shares1 + shares2 + 2, "Convert sum of assets far smaller than parts";
}

// Ensure that maxWithdraw and maxRedeem are in line with the conversion functions.
rule maxWithdrawRedeemCompliance(address owner) {
    uint256 shares = balanceOf(owner);
    uint256 amountConverted = convertToAssets(shares);

    assert maxWithdraw(owner) <= amountConverted, "Can withdraw more than converted amount";
    assert maxRedeem(owner) <= shares, "Can redeem more than available shares)";
}


// Ensure that previewWithdraw and previewRedeem are in line with the conversion functions.
rule previewWithdrawRedeemCompliance(uint256 value) {
    env e;
    uint256 assets = convertToAssets(value);
    uint256 shares = convertToShares(value);

    assert previewWithdraw(e, value) >= shares, "Preview withdraw takes less shares than converted";
    assert previewRedeem(e, value) <= assets, "Preview redeem yields more assets than converted";

	// The following rules protect the client.
    assert previewWithdraw(e, value) <= shares + 1, "Preview withdraw costs too many shares";
	assert previewRedeem(e, value) + 1 + rate() / RAY() >= assets, "Preview redeem yields too few assets";
}


/**
 * @notice From ERC4626:
 * > previewWithdraw ... MUST return as close to and no fewer than the exact amount of Vault 
 * > shares that would be burned in a withdraw call in the same transaction. I.e. withdraw
 * > should return the same or fewer shares as previewWithdraw if called in the same
 * > transaction.
 */
rule previewWithdrawNearlyWithdraw(uint256 assets) {
    env e;
	address owner = e.msg.sender;  // Handy alias
	uint256 previewShares = previewWithdraw(e, assets);
	uint256 withdrawShares = withdraw(e, assets, owner, owner);

	assert withdrawShares <= previewShares, "Withdraw returns more shares than preview";
	assert withdrawShares + 1 >= previewShares, "Withdraw returns far less shares than preview";
}


/**
 * @notice From ERC4626:
 * > previewRedeem ... MUST return as close to and no more than the exact amount
 * >  of assets that would be withdrawn in a redeem call in the same transaction.
 * >  I.e. redeem should return the same or more assets as previewRedeem if called
 * > in the same transaction.
 */
rule previewRedeemNearlyRedeem(uint256 shares) {
    env e;
	address owner = e.msg.sender;  // Handy alias
	uint256 previewAssets = previewRedeem(e, shares);
	uint256 redeemAssets = redeem(e, shares, owner, owner);

	assert redeemAssets >= previewAssets, "Redeem returns less assets than preview";
	assert redeemAssets <= previewAssets + 1, "Redeem returns far more assets than preview";
}


/* The commented out rule below (withdrawSum) timed out after 6994 seconds (see link below).
 * However, we can deduce worse bounds from previous rules, here is the proof.
 * TODO: should we try for better bounds?
 * Let w = withdraw(assets), p = previewWithdraw(assets), s = convertToShares(assets),
 * then:
 *     p - 1 <= w <= p -- by previewWithdrawNearlyWithdraw
 *     s <= p <= s + 1 -- by previewWithdrawRedeemCompliance
 * Hence: s - 1 <= w <= s + 1
 * 
 * Let w1 = withdraw(assets1), s1 = convertToShares(assets1)
 *     w2 = withdraw(assets2), s2 = convertToShares(assets2)
 *      w = withdraw(assets1 + assets2), s = convertToShares(assets1 + assets2)
 * By convertSumOfAssetsPreserved:
 *    s1 + s2 <= s <= s1 + s2 + 1
 * Therefore:
 *    w1 + w2 - 3 <= s1 + s2 - 1 <= s - 1 <= w <= s + 1 <= s1 + s2 + 2 <= w1 + w2 + 4
 *    w1 + w2 - 3 <= w <= w1 + w2 + 4
 *
 * The following run of withdrawSum timed out:
 * https://vaas-stg.certora.com/output/98279/8f5d36ea63ba4a4ca1d23f781ec8dfa6?anonymousKey=11d8393da339881d925ad4e087252951d1da512d
 */
//rule withdrawSum(uint256 assets1, uint256 assets2) {
//    env e;
//	address owner = e.msg.sender;  // Handy alias
//
//	// Additional requirement to speed up calculation
//	require balanceOf(owner) > convertToShares(2 * (assets1 + assets2));
//
//	uint256 shares1 = withdraw(e, assets1, owner, owner);
//	uint256 shares2 = withdraw(e, assets2, owner, owner);
//	uint256 sharesSum = withdraw(e, assets1 + assets2, owner, owner);
//
//	assert sharesSum <= shares1 + shares2, "Withdraw sum larger than its parts";
//	assert sharesSum + 2 > shares1 + shares2, "Withdraw sum far smaller than it sparts";
//}


// Redeeming sum of assets is nearly equal to sum of redeeming
rule redeemSum(uint256 shares1, uint256 shares2) {
    env e;
	address owner = e.msg.sender;  // Handy alias

	uint256 assets1 = redeem(e, shares1, owner, owner);
	uint256 assets2 = redeem(e, shares2, owner, owner);
	uint256 assetsSum = redeem(e, shares1 + shares2, owner, owner);

	assert assetsSum >= assets1 + assets2, "Redeemed sum smaller than parts";
	assert assetsSum < assets1 + assets2 + 2, "Redeemed sum far larger than parts";
}
