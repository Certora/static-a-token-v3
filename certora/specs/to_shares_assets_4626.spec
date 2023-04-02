import "methods_base.spec"

/// @dev Passed in: job-id=`2323dee6646842f38b0bee32bf24b175`

/////////////////// Methods ////////////////////////
    methods
    {
        // AToken
        // ------
        // These are only needed for `nonDecreasingRate` rule.
        mint(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
        burn(address,address,uint256,uint256) returns (bool) => DISPATCHER(true)
    }

///////////////// Definition ///////////////////////

    definition RAY() returns uint256 = (10 ^ 27);

///////////////// Properties ///////////////////////

    /**************************
    *       Monotonicity      *
    ***************************/

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
    * Preview functions rules
    * -----------------------
    * The rules below prove that preview functions (e.g. `previewDeposit`) return the same
    * values as their non-preview counterparts (e.g. `deposit`).
    * The rules below passed with rule sanity: job-id=`2b196ea03b8c408dae6c79ae128fc516`
    */
    
    /*****************************
    *       previewDeposit      *
    *****************************/

        /// Number of shares returned by `previewDeposit` is the same as `deposit`.
        rule previewDepositSameAsDeposit(uint256 assets, address receiver) {
            env e;
            uint256 previewShares = previewDeposit(e, assets);
            uint256 shares = deposit(e, assets, receiver);
            assert previewShares == shares, "previewDeposit is unequal to deposit";
        }

    /*****************************
    *        previewMint        *
    *****************************/

        /// Number of assets returned by `previewMint` is the same as `mint`.
        rule previewMintSameAsMint(uint256 shares, address receiver) {
            env e;
            uint256 previewAssets = previewMint(e, shares);
            uint256 assets = mint(e, shares, receiver);
            assert previewAssets == assets, "previewMint is unequal to mint";
        }

    /*********************************
    *        previewWithdraw        *
    *********************************/

        /// Number of shares returned by `previewWithdraw` is the same as `withdraw`.
        rule previewWithdrawSameAsWithdraw(uint256 assets, address receiver, address owner) {
            env e;
            uint256 previewShares = previewWithdraw(e, assets);
            uint256 shares = withdraw(e, assets, receiver, owner);
            assert previewShares == shares, "previewWithdraw is unequal to withdraw";
        }

    /*******************************
    *        previewRedeem        *
    *******************************/

        /// Number of assets returned by `previewRedeem` is the same as `redeem`.
        rule previewRedeemSameAsRedeem(uint256 shares, address receiver, address owner) {
            env e;
            uint256 previewAssets = previewRedeem(e, shares);
            uint256 assets = redeem(e, shares, receiver, owner);
            assert previewAssets == assets, "previewRedeem is unequal to redeem";
        }
