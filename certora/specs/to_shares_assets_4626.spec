import "methods_base.spec"


methods
{
	// AToken
	// ------
    // These are only needed for `nonDecreasingRate` rule.
    mint(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
    burn(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
}


/*
 * Rate rule
 * ---------
 */


/**
 * @title Rate is non-decreasing
 * Ensure `rate` is non-decreasing (except for `initialize` method).
 * From `IStaticATokenLM` documentation:
 * > "Returns the Aave liquidity index of the underlying `aToken`, denominated
 * > rate here as it can be considered as an ever-increasing exchange rate ..."
 *
 * Except for `initialize` and `metaDeposit`, all other methods passed (with rule sanity)
 * in: job-id=`ed29d522b6de4fe2a5b1cc638b2f7b26`.
 *
 * @notice `metaDeposit` seems to be vacuous, i.e. *always* fails on a require statement.
 */
rule nonDecreasingRate(method f) {
	require f.selector != initialize(address, string, string).selector;

	env e1;
	env e2;
	require e1.block.timestamp < 2^32;
	require e2.block.timestamp < 2^32;
	require e1.block.timestamp <= e2.block.timestamp;

	uint256 earlyRate = rate(e1);

	calldataarg args;
	f(e1, args);

	uint256 postRate = rate(e1);
	uint256 lateRate = rate(e2);

	assert earlyRate <= postRate, "rate declines after method";
	assert postRate <= lateRate, "rate declines with time";
}


/*
 * Shares Assets 4626 Conversion Rules
 * -----------------------------------
 * The rules below deal with conversion of shares to/from assets according to EIP4626.
 * - Latest run for these rules (except for `toAssetsDoesNotRevert` and `toSharesDoesNotRevert`):
 *   job-id=`e275f83f426046c58ab89d72f9652c16`
 * - Both `toAssetsDoesNotRevert` and `toSharesDoesNotRevert` passed in:
 *   job-id=`35677d80cb8744408968063e7efbe3b9`
 *
 * Properties of `ConvertToShares` (from EIP4626):
 * - Must not be dependent on the caller
 * - Must not revert except for overflow
 * - Must round down towards 0
     This was already verified in sharesAssetsConversion.spec in rule sharesConversionRoundedDown
 * - *Not Tested:* Must not be inclusive of any fees (not tested)
 * - *Not Tested:* Must not reflect slippage and other on-chain conditions (not tested)
 
 * Properties of `ConvertToAssets` (from EIP4626):
 * - Should be independent of the user
 * - Must not revert unless due to integer overflow
 * - Must round down
 *   This was already verified in sharesAssetsConversion.spec in rule amountConversionRoundedDown.
 * - *Not Tested:* Must not be inclusive of any fees(not tested)
 * - *Not Tested:* Must not reflect slippage and other on-chain conditions (not tested)
 */


definition RAY() returns uint256 = (10 ^ 27);


/// @title ConvertToShares must not be dependent on the caller
rule toSharesCallerIndependent(uint256 assets) {
	env e1;
	env e2;

	require e1.block.timestamp < 2^32;  // Avoid down casting issues
	require e1.block.timestamp == e2.block.timestamp;
	require e1.block.number == e2.block.number;

	uint256 shares1 = convertToShares(e1, assets);
	uint256 shares2 = convertToShares(e2, assets);
	assert shares1 == shares2, "ConvertToShares depend on sender";
}

/**
 * @title ConvertToShares must not revert except for overflow
 * From EIP4626:
 * > MUST NOT revert unless due to integer overflow caused by an unreasonably large input.
 * We define large input as `10^50`. To be precise, we need that `RAY * assets < 2^256`, since
 * `2^256~=10^77` and `RAY=10^27` we get that `assets < 10^50`.
 * 
 * Note. *We also require that:* **`rate > 0`**.
 */
rule toSharesDoesNotRevert(uint256 assets) {
	require assets < 10^50;
	env e;

	// Prevent revert due to overflow.
	// Roughly speaking ConvertToShares returns assets * RAY / rate().
	mathint ray_math = to_mathint(RAY());
	mathint rate_math = to_mathint(rate(e));
	mathint assets_math = to_mathint(assets);
	require rate_math > 0;

	uint256 shares = convertToShares@withrevert(e, assets);
	bool reverted = lastReverted;

	assert !reverted, "Conversion to shares reverted";
}


/// @title ConvertToAssets Should be independent of the user
rule toAssetsCallerIndependent(uint256 shares) {
	env e1;
	env e2;

	require e1.block.timestamp < 2^32;  // Avoid down casting issues
	require e1.block.timestamp == e2.block.timestamp;
	require e1.block.number == e2.block.number;

	uint256 assets1 = convertToAssets(e1, shares);
	uint256 assets2 = convertToAssets(e2, shares);
	assert assets1 == assets2, "ConvertToAssets depends on sender";
}

/**
 * @title ConvertToAssets must not revert unless due to integer overflow
 * From EIP4626:
 * > MUST NOT revert unless due to integer overflow caused by an unreasonably large input.
 * We define large input as 10^45. To be precise we need that `shares * rate < 2^256 ~= 10^77`,
 * hence we require that:
 * - `shares < 10^45`
 * - `rate < 10^32`
 */
rule toAssetsDoesNotRevert(uint256 shares) {
	require shares < 10^45;
	env e;

	// Prevent revert due to overflow.
	// Roughly speaking ConvertToAssets returns shares * rate() / RAY.
	mathint ray_math = to_mathint(RAY());
	mathint rate_math = to_mathint(rate(e));
	mathint shares_math = to_mathint(shares);
	require rate_math < 10^32;

	uint256 assets = convertToAssets@withrevert(e, shares);
	bool reverted = lastReverted;

	assert !reverted, "Conversion to assets reverted";
}


/*
 * Preview functions rules
 * -----------------------
 * The rules below prove that preview functions (e.g. `previewDeposit`) return the same
 * values as their non-preview counterparts (e.g. `deposit`).
 * The rules below passed with rule sanity: job-id=`2b196ea03b8c408dae6c79ae128fc516`
 */

/// Number of shares returned by `previewDeposit` is the same as `deposit`.
rule previewDepositSameAsDeposit(uint256 assets, address receiver) {
	env e;
	uint256 previewShares = previewDeposit(e, assets);
	uint256 shares = deposit(e, assets, receiver);
	assert previewShares == shares, "previewDeposit is unequal to deposit";
}


/// Number of assets returned by `previewRedeem` is the same as `redeem`.
rule previewRedeemSameAsRedeem(uint256 shares, address receiver, address owner) {
	env e;
	uint256 previewAssets = previewRedeem(e, shares);
	uint256 assets = redeem(e, shares, receiver, owner);
	assert previewAssets == assets, "previewRedeem is unequal to redeem";
}


/// Number of shares returned by `previewWithdraw` is the same as `withdraw`.
rule previewWithdrawSameAsWithdraw(uint256 assets, address receiver, address owner) {
	env e;
	uint256 previewShares = previewWithdraw(e, assets);
	uint256 shares = withdraw(e, assets, receiver, owner);
	assert previewShares == shares, "previewWithdraw is unequal to withdraw";
}


/// Number of assets returned by `previewMint` is the same as `mint`.
rule previewMintSameAsMint(uint256 shares, address receiver) {
	env e;
	uint256 previewAssets = previewMint(e, shares);
	uint256 assets = mint(e, shares, receiver);
	assert previewAssets == assets, "previewMint is unequal to mint";
}
