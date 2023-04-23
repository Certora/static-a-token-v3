import "methods_base.spec"

// The following spec implements erc4626 properties according to the official eip described here:
// https://eips.ethereum.org/EIPS/eip-4626

///////////////// Properties ///////////////////////
    /********************************
    *        previewWithdraw        *
    *********************************/

        ///@title previewWithdraw independent of maxWithdraw
        ///@notice This rule checks that the value returned by previewWithdraw is independent of the value returned by maxWithdraw.
        rule previewWithdrawIndependentOfMaxWithdraw(env e){
            env e1;
            env e2;
            address user;
            uint256 maxWithdraw1 = maxWithdraw(user);
            uint256 assets1;
            uint256 shares1;
            uint256 shares2;

            require assets1 > maxWithdraw1;
            uint256 previewShares1 = previewWithdraw(assets1);

            mint(e1, shares1, user);

            uint256 maxWithdraw2 = maxWithdraw(user);
            require assets1 ==  maxWithdraw2;
            uint256 previewShares2 = previewWithdraw(assets1);
            
            mint(e2, shares2, user);

            uint256 maxWithdraw3 = maxWithdraw(user);
            require assets1 <  maxWithdraw3;
            uint256 previewShares3 = previewWithdraw(assets1);

            assert previewShares1 == previewShares2 && previewShares2 == previewShares3,"preview withdraw should be independent of allowance";
        }

    /*****************************
    *      convertToAssets      *
    *****************************/

		/// @title Converting amount to shares is properly rounded down
        rule amountConversionRoundedDown(uint256 amount) {
			env e;
            uint256 shares = convertToShares(e, amount);
            assert convertToAssets(e, shares) <= amount, "Too many converted shares";

            /* The next assertion shows that the rounding in `convertToAssets` is tight. This
            * protects the user. For example, a function `convertToAssets` that always returns 
            * zero would have passed the previous assertion, but not the next one.
            */
            assert convertToAssets(e, shares + 1) >= amount, "Too few converted shares";
        }

    /*****************************
    *      convertToShares      *
    *****************************/
        
		/// @title Converting shares to amount is properly rounded down
        rule sharesConversionRoundedDown(uint256 shares) {
			env e;
            uint256 amount = convertToAssets(e, shares);
            assert convertToShares(e, amount) <= shares, "Amount converted is too high";

            /* The next assertion shows that the rounding in `convertToShares` is tight.
            * For example, a function `convertToShares` that always returns zero
            * would have passed the previous assertion, but not the next one.
            */
            assert convertToShares(e, amount + 1) >= shares, "Amount converted is too low";
        }

    /**********************
    *      maxRedeem      *
    ***********************/

        // maxRedeem must not revert
        rule maxRedeemMustntRevert(address user){
            maxRedeem@withrevert(user);
            assert !lastReverted;
        }