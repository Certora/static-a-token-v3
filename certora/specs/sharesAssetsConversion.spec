import "methods_base.spec"

//// @dev Latest run succeeded (without rule_sanity): job-id=`f2935fc2c0234b6e9710f40e20d5dc07`

/////////////////// Methods ////////////////////////

    methods
    {
        // envfree
        // -------
        rate() returns (uint256) envfree
        convertToShares(uint256 amount) returns (uint256) envfree
        convertToAssets(uint256 amount) returns (uint256) envfree
    }

///////////////// Definition ///////////////////////

    definition RAY() returns uint256 = (10 ^ 27);

///////////////// Properties ///////////////////////

    /*** 
	* #### A note on the conversion functions
    * The conversion functions are:
    * - assets to shares = `S(a) = (a * R) // r`
    * - shares to assets = `A(s) = (s * r) // R`
    * where a=assets, s=shares, R=RAY, r=rate.
    * 
    * These imply:
    * - `a * R - r < S(a) * r <= a * R    a*R/r - 1 < S(a) <= a*R/r`
    * - `s * r - R < A(s) * R <= s * r    s*r/R - 1 < A(s) <= s*r/R`
    * 
    * Hence:
    * - `A(S(a)) > S(a)*r/R - 1 > (a*R/r - 1)*r/R - 1 = (a*R - r)/R - 1 = a - r/R - 1`
    * - `S(A(s)) > A(s)*R/r - 1 > (s*r/R - 1)*R/r - 1 = (s*r - R)/r - 1 = s - R/r - 1`
    */

    /*****************************
    *       rounding range       *
    ******************************/

        /**
		 * @title Ensure `previewWithdraw` tightly rounds up shares
		 * The lower bound (i.e. `previewWithdraw <= convertToShares`) follows from ERC4626. The upper bound
		 * is based on the current implementation.
		 */
        rule previewWithdrawRoundingRange(uint256 assets) {
            env e;
            uint256 shares = convertToShares(assets);

            assert previewWithdraw(e, assets) >= shares, "Preview withdraw takes less shares than converted";
            assert previewWithdraw(e, assets) <= shares + 1, "Preview withdraw costs too many shares";
        }

        /**
		 * @title Ensure `previewRedeem` tightly rounds down assets
		 * The upper bound (i.e. `previewRedeem >= convertToAssets`) follows from ERC4626. The lower bound
		 * is based on the current implementation.
		 */
        rule previewRedeemRoundingRange(uint256 shares) {
            env e;
            uint256 assets = convertToAssets(shares);

            assert previewRedeem(e, shares) <= assets, "Preview redeem yields more assets than converted";
            assert previewRedeem(e, shares) + 1 + rate() / RAY() >= assets, "Preview redeem yields too few assets";
        }

        /**
        * @title Inequality for conversion of amount to shares and back
        * Note the precision depends on the ratio **`rate / RAY`**.
        */
        rule amountConversionPreserved(uint256 amount) {
            mathint mathamount = to_mathint(amount);
            mathint converted = to_mathint(convertToAssets(convertToShares(amount)));

            // That `converted <= mathamount` was proved in `amountConversionRoundedDown`
            assert mathamount - converted <= 1 + rate() / RAY(), "Too few converted assets";
        }
        
        /**
        * @title Inequality for conversion of shares to amount and back
        * Note the precision depends on the ratio **`RAY / rate`**.
        */
        rule sharesConversionPreserved(uint256 shares) {
            mathint mathshares = to_mathint(shares);
            uint256 amount = convertToAssets(shares);
            mathint converted = to_mathint(convertToShares(amount));

            // That `converted <= mathshare` was proved in `sharesConversionRoundedDown`
            assert mathshares - converted <= 1 + RAY() / rate(), "Too few converted shares";
        }

        /** 
        * @title Joining and splitting shares provides limited advantage
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

            /* Example as to why the following assertion should be true. Suppose conversion of shares
            * to assets is division by 2 rounded down, and suppose shares1 = shares2 = 11.
            * Then amount1 + amount2 = 5 + 5 = 10, but jointAmount = 22 // 2 = 11.
            */
            assert jointAmount < amount1 + amount2 + 2, "Found advantage in splitting accounts";

            /* The following assertion fails (as expected):
            * assert jointAmount < amount1 + amount2 + 1, "Found advantage in splitting accounts";
            */
        }

        /** 
        * @title Joining and splitting assets provides limited advantage
        * Similar to `accountsJoiningSplittingIsLimited` rule.
        */
        rule convertSumOfAssetsPreserved(uint256 assets1, uint256 assets2) {
            uint256 shares1 = convertToShares(assets1);
            uint256 shares2 = convertToShares(assets2);
            uint256 sumAssets = assets1 + assets2;
            require sumAssets >= assets1 + assets2; // Prevent overflow
            uint256 jointShares = convertToShares(sumAssets);

            assert jointShares >= shares1 + shares2, "Convert sum of assets bigger than parts";
            assert jointShares < shares1 + shares2 + 2, "Convert sum of assets far smaller than parts";
        }

        /// @title Redeeming sum of assets is nearly equal to sum of redeeming
        rule redeemSum(uint256 shares1, uint256 shares2) {
            env e;
            address owner = e.msg.sender;  // Handy alias

            uint256 assets1 = redeem(e, shares1, owner, owner);
            uint256 assets2 = redeem(e, shares2, owner, owner);
            uint256 assetsSum = redeem(e, shares1 + shares2, owner, owner);

            assert assetsSum >= assets1 + assets2, "Redeemed sum smaller than parts";

            /* See `accountsJoiningSplittingIsLimited` rule for why the following assertion
            * is correct.
            */
            assert assetsSum < assets1 + assets2 + 2, "Redeemed sum far larger than parts";
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
